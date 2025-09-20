import gc
import json
import tempfile
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any, cast

import cv2
import numpy as np

from docviz.constants import (
    DEFAULT_CHART_SUMMARIZER_RETRIES,
    DEFAULT_CHART_SUMMARIZER_TIMEOUT,
    DEFAULT_MEMORY_CLEANUP_INTERVAL,
    TMP_DIR_PREFIX,
)
from docviz.lib.detection import Detector
from docviz.lib.extraction.utils import filter_detections
from docviz.lib.image import ChartSummarizer, extract_regions, fill_regions_with_color
from docviz.lib.pdf import (
    # TODO: remove these imports once we have a better way to handle PDF analysis or otherwise uncomment and implement fully
    # analyze_pdf,
    # extract_pdf_page_text,
    # extract_pdf_text_excluding_regions,
    extract_text_from_image,
    pdf_to_pngs,
)
from docviz.lib.pdf.pdf_analyzer import (
    analyze_pdf,
    extract_pdf_page_text,
    extract_pdf_text_excluding_regions,
)
from docviz.logging import get_logger
from docviz.types import (
    DetectionConfig,
    DetectionResult,
    ExtractionConfig,
    ExtractionType,
    LLMConfig,
    OCRConfig,
    RectangleTuple,
    RectangleUnion,
)

logger = get_logger(__name__)


def pipeline(
    document_path: Path,
    output_dir: Path,
    detection_config: DetectionConfig,
    extraction_config: ExtractionConfig,
    ocr_config: OCRConfig,
    llm_config: LLMConfig,
    includes: list[ExtractionType],
    progress_callback: Callable[[int], None] | None = None,
    memory_cleanup_interval: int = 10,
) -> list[dict[str, Any]]:
    """
    Full pipeline: convert PDF to PNG, detect charts, extract text, and summarize.

    Args:
        document_path: Path to the input PDF document.
        output_dir: Directory to save outputs.
        detection_config: Configuration for detection.
        extraction_config: Configuration for extraction.
        ocr_config: Configuration for OCR.
        llm_config: Configuration for LLM.
        includes: List of extraction types to include.
        progress_callback: Optional callback for progress tracking.
        memory_cleanup_interval: Interval for explicit garbage collection (pages).

    Returns:
        List[Dict[str, Any]]: List of dicts for each page, each containing a list of elements (charts and text).
    """
    logger.info("Starting document processing pipeline")

    model_name = llm_config.model
    base_url = llm_config.base_url
    api_key = llm_config.api_key

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        logger.debug(f"Created temporary directory: {temp_path}")

        logger.info("Converting PDF to PNG images")
        image_paths = pdf_to_pngs(
            pdf_path=str(document_path),
            output_dir=str(temp_path),
            zoom_x=extraction_config.zoom_x,
            zoom_y=extraction_config.zoom_y,
        )
        logger.info(f"Converted PDF to {len(image_paths)} PNG images")

        logger.info("Analyzing PDF pages for native text and images")
        try:
            page_analyses = analyze_pdf(document_path)
            logger.info("PDF analysis completed successfully")
        except Exception as exc:
            logger.warning(
                f"PDF analysis failed with error: {exc}. Falling back to OCR-only text extraction."
            )
            page_analyses = [None] * len(image_paths)

        # Initialize models
        logger.info("Initializing detection and summarization models")
        detector = Detector(
            config=detection_config,
        )
        summarizer = ChartSummarizer(
            model_name=model_name,
            base_url=base_url,
            api_key=api_key or "",
            retries=3,
            timeout=5,
            custom_prompt=llm_config.custom_prompt,
        )
        logger.info("Models initialized successfully")

        # Process each page with lazy loading
        results: list[dict[str, Any]] = []
        for idx, img_path in enumerate(image_paths):
            if progress_callback is not None:
                progress_callback(idx + 1)

            if extraction_config.page_limit is not None and idx >= extraction_config.page_limit:
                logger.info(
                    f"Page limit of {extraction_config.page_limit} reached, stopping processing."
                )
                break

            logger.info(f"Processing page {idx + 1}/{len(image_paths)}")

            img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
            if img is None:
                logger.error(f"Could not load image {img_path}")
                raise FileNotFoundError(f"Could not load image {img_path}")

            # Run layout detection once so we can both (a) exclude regions in PDF text and (b) reuse in processing
            detections = detector.parse_layout(img)

            # Remove unneeded detections based of includes
            detections = filter_detections(
                detections,
                include=[inc.to_canonical_label() for inc in includes],
            )

            analysis = page_analyses[idx]
            prefer_pdf_text = extraction_config.prefer_pdf_text
            fast_text: str | None = None
            if (
                analysis is not None
                and prefer_pdf_text
                and analysis.has_text
                and not analysis.is_full_page_image
            ):
                # Merge exclusion regions: image regions from analysis + labels_to_exclude regions from detections
                excluded_label_detections = filter_detections(
                    detections, # type: ignore
                    extraction_config.labels_to_exclude,  
                )
                excluded_bboxes = [
                    (
                        float(b[0]),
                        float(b[1]),
                        float(b[2]),
                        float(b[3]),
                    )
                    for b in (detection.bbox for detection in excluded_label_detections)  # type: ignore
                ]
                combined_excludes = list(analysis.image_rects) + excluded_bboxes

                if combined_excludes:
                    logger.debug(
                        f"Excluding {len(combined_excludes)} regions from PDF text on page {idx + 1}"
                    )
                    fast_text = extract_pdf_text_excluding_regions(
                        document_path, analysis.page_index, combined_excludes
                    )
                else:
                    fast_text = extract_pdf_page_text(document_path, analysis.page_index)

                if fast_text and len(fast_text) < extraction_config.pdf_text_threshold_chars:
                    fast_text = None
                    logger.debug(
                        f"Discarded short PDF text below threshold; will use OCR for page {idx + 1}"
                    )
                else:
                    length = 0 if fast_text is None else len(fast_text)
                    logger.info(f"Using PDF-native text for page {idx + 1} (length={length})")

            page_result = process_single_page(
                image=img,
                includes=includes,
                page_number=idx + 1,
                detections=detections,  # type: ignore
                summarizer=summarizer,
                ocr_lang=ocr_config.lang,
                charts_labels=ocr_config.chart_labels,
                ocr_noise_labels=ocr_config.labels_to_exclude,
                pre_extracted_text=fast_text,
            )
            results.append(page_result)

            with open(Path(output_dir) / f"page_{idx + 1}.json", "w") as f:
                json.dump(page_result, f)

            # Explicitly free memory after processing each page
            del img

            # Force garbage collection at specified intervals to prevent memory buildup
            if (idx + 1) % memory_cleanup_interval == 0:
                gc.collect()

    logger.info("Pipeline completed successfully")
    logger.info(
        f"Processed {len(results)} pages with total elements: {sum(len(page['elements']) for page in results)}"
    )
    return results


def process_single_page(
    image: np.ndarray,
    includes: list[ExtractionType],
    page_number: int,
    detections: list[DetectionResult],
    summarizer: ChartSummarizer,
    charts_labels: list[str],
    ocr_noise_labels: list[str],
    ocr_lang: str,
    pre_extracted_text: str | None = None,
) -> dict[str, Any]:
    """
    Process a single page image: detect elements, extract chart and text data.

    Args:
        image (np.ndarray): Image to process.
        detector (Detector): Detector instance for layout detection.
        summarizer (ChartSummarizer): Summarizer for chart elements.
        ocr_lang (str): Language for OCR.
        pre_extracted_text (Optional[str]): Text already extracted from PDF; if present, OCR is skipped.

    Returns:
        Dict[str, Any]: Dictionary containing page number and extracted elements.
    """
    chart_elements = []
    text_elements = []

    if ExtractionType.FIGURE in includes:
        # Filter detections to only include chart elements
        # to extract regions with them from the image
        chart_detections = filter_detections(detections, include=charts_labels)
        chart_elements = process_chart_elements(
            image=image,
            chart_detections=chart_detections,  # type: ignore
            page_number=page_number,
            summarizer=summarizer,
        )

    if ExtractionType.TEXT in includes:
        # Get detections that are not allowed to be included in
        # raw extracted text (e.g., tables, figures, ?footnotes?, etc.)
        excluded_regions = filter_detections(
            detections, include=ocr_noise_labels, return_bboxes=True
        )

        text_elements = process_text_elements(
            image=image,
            excluded_bboxes=excluded_regions,  # type: ignore
            ocr_lang=ocr_lang,
            page_number=page_number,
            pre_extracted_text=None,
        )
    print(chart_elements, text_elements, sep="\n\n")
    return {
        "page_number": page_number,
        "elements": chart_elements + text_elements,
    }


def process_chart_elements(
    image: np.ndarray,
    chart_detections: list[DetectionResult],
    page_number: int,
    summarizer: ChartSummarizer,
    prompt: str | None = None,
    extra_context: str | None = None,
) -> list[dict[str, Any]]:
    """
    Process chart elements: crop, summarize, and return structured data.

    Args:
        image (np.ndarray): Image to process.
        chart_detections (List[DetectionResult]): Filtered chart detections.
        page_number (int): Current page number.
        summarizer (ChartSummarizer): Chart summarizer instance.
        prompt (Optional[str]): Custom prompt for summarization.
        extra_context (Optional[str]): Extra context for summarization.

    Returns:
        List[Dict[str, Any]]: List of chart elements with summaries.
    """
    logger.info(f"Processing chart elements for page {page_number}")

    if not chart_detections:
        logger.info("No chart detections found, skipping chart processing")
        return []

    extracted_regions = extract_regions(
        image=image,
        regions=[cast(RectangleTuple, tuple(detection.bbox)) for detection in chart_detections],
    )

    if not extracted_regions:
        logger.warning("Failed to extract chart regions")
        return []

    chart_elements: list[dict[str, Any]] = []
    for idx, (detection, region) in enumerate(
        zip(chart_detections, extracted_regions, strict=False)
    ):
        logger.debug(f"Summarizing chart {idx + 1}/{len(extracted_regions)}...")
        summary = summarizer.summarize_charts_from_page(
            image=region,
            prompt=prompt,
            extra_context=extra_context,
        )
        logger.info(
            f"Successfully summarized chart {idx + 1}/{len(extracted_regions)} on page {page_number}"
        )
        chart_elements.append(
            {
                "type": "chart",
                "label": detection.label_name.lower(),
                "summary": summary,
                "bbox": detection.bbox,
            }
        )

    logger.info(f"Successfully processed {len(chart_elements)} chart element(-s)")
    return chart_elements


def process_text_elements(
    image: np.ndarray,
    excluded_bboxes: list[RectangleUnion],
    page_number: int,
    ocr_lang: str,
    pre_extracted_text: str | None = None,
) -> list[dict[str, Any]]:
    """Process text content for a page.

    If ``pre_extracted_text`` is provided, it will be returned directly as a single text
    element that spans the full page. Otherwise, chart regions are masked and OCR is applied.

    Args:
        image (np.ndarray): Page image to extract text from.
        excluded_bboxes (List[RectangleUnion]): Regions to exclude from OCR (e.g., charts).
        page_number (int): Current page number.
        ocr_lang (str): OCR language code.
        pre_extracted_text (Optional[str]): If provided, skip OCR and return this text.

    Returns:
        List[Dict[str, Any]]: List of text elements with extracted content.
    """
    logger.info(f"Processing text elements for page {page_number}")

    # If we already have text from the PDF, just use it and skip OCR
    if pre_extracted_text is not None and pre_extracted_text.strip():
        text = pre_extracted_text.strip()
        height, width = image.shape[:2]
        logger.debug(f"Using pre-extracted PDF text for page {page_number} (chars={len(text)})")
        return [
            {
                "type": "text",
                "text": text,
                "bbox": (0, 0, width, height),
            }
        ]

    filled_image = fill_regions_with_color(
        image=image,
        regions=excluded_bboxes,
        color=(255, 255, 255),
    )
    # Extract text from the entire processed image
    logger.debug("Extracting text from processed image via OCR")
    text = extract_text_from_image(
        image=filled_image,
        lang=ocr_lang,
    )

    text_elements: list[dict[str, Any]] = []
    if text.strip():
        height, width = filled_image.shape[:2]
        text_elements.append(
            {
                "type": "text",
                "text": text,
                "bbox": (0, 0, width, height),
            }
        )
        logger.info("Successfully extracted text from processed image")
    else:
        logger.info("No text extracted from processed image")

    logger.info(f"Successfully processed {len(text_elements)} text element(-s)")
    return text_elements


def pipeline_streaming(
    document_path: Path,
    output_dir: Path,
    detection_config: DetectionConfig,
    extraction_config: ExtractionConfig,
    ocr_config: OCRConfig,
    llm_config: LLMConfig,
    includes: list[ExtractionType],
    progress_callback: Callable[[int], None] | None = None,
    memory_cleanup_interval: int = DEFAULT_MEMORY_CLEANUP_INTERVAL,
) -> Iterator[dict[str, Any]]:
    """
    Streaming version of pipeline: yields page results one by one as they are processed.

    Args:
        document_path: Path to the input PDF document
        output_dir: Directory to save outputs
        detection_config: Configuration for detection
        extraction_config: Configuration for extraction
        ocr_config: Configuration for OCR
        llm_config: Configuration for LLM
        includes: List of extraction types to include
        progress_callback: Optional callback for progress tracking
        memory_cleanup_interval: Interval for explicit garbage collection (pages)

    Yields:
        dict[str, Any]: Page result dict for each processed page
    """
    logger.info("Starting streaming document processing pipeline")

    model_name = llm_config.model
    base_url = llm_config.base_url
    api_key = llm_config.api_key

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix=TMP_DIR_PREFIX) as temp_dir:
        temp_path = Path(temp_dir)
        logger.debug(f"Created temporary directory: {temp_path}")

        logger.info("Converting PDF to PNG images")
        image_paths = pdf_to_pngs(
            pdf_path=str(document_path),
            output_dir=str(temp_path),
            zoom_x=extraction_config.zoom_x,
            zoom_y=extraction_config.zoom_y,
        )
        logger.info(f"Converted PDF to {len(image_paths)} PNG images")

        # TODO: uncomment this once we will fr handle native PDF analysis
        # logger.info("Analyzing PDF pages for native text and images")
        # try:
        #     page_analyses = analyze_pdf(document_path)
        #     logger.info("PDF analysis completed successfully")
        # except Exception as exc:
        #     logger.warning(
        #         f"PDF analysis failed with error: {exc}. Falling back to OCR-only text extraction."
        #     )
        #     page_analyses = [None] * len(image_paths)

        # Initialize models
        logger.info("Initializing detection and summarization models")
        detector = Detector(
            config=detection_config,
        )
        summarizer = ChartSummarizer(
            model_name=model_name,
            base_url=base_url,
            api_key=api_key or "",
            retries=DEFAULT_CHART_SUMMARIZER_RETRIES,
            timeout=DEFAULT_CHART_SUMMARIZER_TIMEOUT,
            custom_prompt=llm_config.custom_prompt,
        )
        logger.info("Models initialized successfully")

        for idx, img_path in enumerate(image_paths):
            if progress_callback is not None:
                progress_callback(idx + 1)

            if extraction_config.page_limit is not None and idx >= extraction_config.page_limit:
                logger.info(
                    f"Page limit of {extraction_config.page_limit} reached, stopping processing."
                )
                break

            logger.info(f"Processing page {idx + 1}/{len(image_paths)}")

            img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
            if img is None:
                logger.error(f"Could not load image {img_path}")
                raise FileNotFoundError(f"Could not load image {img_path}")

            detections = detector.parse_layout(img)

            # TODO: uncomment this code block once we will fr handle native PDF analysis
            # analysis = page_analyses[idx]
            # prefer_pdf_text = extraction_config.prefer_pdf_text
            # fast_text: str | None = None

            # if (
            #     analysis is not None
            #     and prefer_pdf_text
            #     and analysis.has_text
            #     and not analysis.is_full_page_image
            # ):
            #     # Merge exclusion regions: image regions from analysis + labels_to_exclude regions from detections
            #     excluded_label_detections = filter_detections(
            #         detections, labels_to_include=extraction_config.labels_to_exclude
            #     )
            #     excluded_bboxes = [
            #         (
            #             float(b[0]),
            #             float(b[1]),
            #             float(b[2]),
            #             float(b[3]),
            #         )
            #         for b in (detection.bbox for detection in excluded_label_detections)
            #     ]
            #     combined_excludes = list(analysis.image_rects) + excluded_bboxes

            #     if combined_excludes:
            #         logger.debug(
            #             f"Excluding {len(combined_excludes)} regions from PDF text on page {idx + 1}"
            #         )
            #         fast_text = extract_pdf_text_excluding_regions(
            #             document_path, analysis.page_index, combined_excludes
            #         )
            #     else:
            #         fast_text = extract_pdf_page_text(document_path, analysis.page_index)

            #     if fast_text and len(fast_text) < extraction_config.pdf_text_threshold_chars:
            #         fast_text = None
            #         logger.debug(
            #             f"Discarded short PDF text below threshold; will use OCR for page {idx + 1}"
            #         )
            #     else:
            #         length = 0 if fast_text is None else len(fast_text)
            #         logger.info(f"Using PDF-native text for page {idx + 1} (length={length})")

            page_result = process_single_page(
                image=img,
                includes=includes,
                page_number=idx + 1,
                detections=detections,
                summarizer=summarizer,
                ocr_lang=ocr_config.lang,
                charts_labels=ocr_config.chart_labels,
                ocr_noise_labels=ocr_config.labels_to_exclude,
            )

            # Save individual page result to output directory
            with open(Path(output_dir) / f"page_{idx + 1}.json", "w") as f:
                json.dump(page_result, f)

            yield page_result

            # Explicitly free memory after processing each page and force
            # garbage collection at specified intervals to prevent memory buildup
            del img
            if (idx + 1) % memory_cleanup_interval == 0:
                gc.collect()

    logger.info("Streaming pipeline completed successfully")
