import asyncio
import shutil
import subprocess
import sys
from pathlib import Path

import requests
from tqdm import tqdm

from docviz.constants import (
    BASE_MODELS_URL,
    DEFAULT_CHUNK_SIZE,
    DOWNLOAD_TIMEOUT_SECONDS,
    REQUIRED_MODELS,
    TESSERACT_ADDITIONAL_WIN_PATHS,
    TESSERACT_DEFAULT_WIN_PATH,
    TESSERACT_WIN_SETUP_FILENAME,
    TESSERACT_WIN_SETUP_URL,
    get_docviz_directory,
    get_models_path,
)
from docviz.logging import get_logger

logger = get_logger(__name__)


async def download_file(url: str, path: Path, chunk_size: int = DEFAULT_CHUNK_SIZE) -> None:
    """Download a file from a URL to a local path with progress bar.

    Args:
        url: The URL of the file to download.
        path: The local path to save the file.
        chunk_size: Size of chunks to download at once.

    Raises:
        requests.RequestException: If download fails.
        OSError: If file cannot be written.
    """
    logger.debug(f"Starting download from {url} to {path}")

    try:
        response = requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT_SECONDS)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)

        with (
            open(path, "wb") as file,
            tqdm(
                desc=f"Downloading {path.name}",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as progress_bar,
        ):
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))

        logger.info(f"Download completed: {path}")

    except requests.RequestException as e:
        logger.error(f"Failed to download {url}: {e}")
        raise
    except OSError as e:
        logger.error(f"Failed to write file {path}: {e}")
        raise


def find_tesseract_executable() -> Path | None:
    """Find the Tesseract executable on the system.

    Returns:
        Path to tesseract executable if found, None otherwise.
    """
    # Check if tesseract is in PATH using shutil.which
    import shutil

    tesseract_path = shutil.which("tesseract")
    if tesseract_path:
        p = Path(tesseract_path)
        if p.exists():
            return p

    # Check common installation paths
    possible_paths = [TESSERACT_DEFAULT_WIN_PATH, *TESSERACT_ADDITIONAL_WIN_PATHS]

    for path in possible_paths:
        p = Path(path)
        if p.exists():
            return p

    return None


async def install_tesseract_windows(docviz_dir: Path) -> None:
    """Download and install Tesseract OCR Installer for Windows platform.

    Args:
        docviz_dir: Directory to store the installer.
    """
    setup_path = docviz_dir / TESSERACT_WIN_SETUP_FILENAME

    try:
        if not setup_path.exists():
            logger.info("Downloading Tesseract installer...")
            await download_file(TESSERACT_WIN_SETUP_URL, setup_path)

        logger.info("Launching Tesseract installer...")
        logger.info(
            "Please complete the installation process. The installer will be removed automatically."
        )

        # Launch installer
        command = ["cmd", "/c", "start", setup_path.as_posix()]
        subprocess.Popen(command, shell=True)

        # Wait a bit for installer to start
        await asyncio.sleep(2)

        # Clean up installer
        if setup_path.exists():
            setup_path.unlink()
            logger.debug("Installer file removed")

        logger.error("Tesseract installation required. Please restart after installation.")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Failed to install Tesseract: {e}")
        if setup_path.exists():
            setup_path.unlink()


async def install_tesseract_linux(docviz_dir: Path) -> None:
    """Download and install Tesseract OCR for Linux platform.

    Args:
        docviz_dir: Directory to store the installer.
    """

    try:
        logger.info("Installing Tesseract OCR for Linux platform...")
        command = ["sudo", "apt-get", "install", "tesseract-ocr"]
        subprocess.run(command, check=True)
        logger.info("Tesseract OCR installed successfully")
    except Exception as e:
        logger.error(f"Failed to install Tesseract OCR: {e}")
        raise RuntimeError(
            "Failed to install Tesseract OCR! Please install it manually using 'sudo apt-get install tesseract-ocr'"
        ) from e


async def install_tesseract(docviz_dir: Path) -> None:
    """Download and install Tesseract OCR.

    Args:
        docviz_dir: Directory to store the installer.
    """
    logger.info("Tesseract not found. Starting installation process...")

    if sys.platform == "win32":
        await install_tesseract_windows(docviz_dir)
    elif sys.platform == "linux":
        await install_tesseract_linux(docviz_dir)
    else:
        raise RuntimeError(
            f"Unsupported platform: {sys.platform}. You need to install Tesseract OCR manually."
        )


def test_tesseract_installation() -> None:
    """Test if Tesseract is properly installed and working.

    Raises:
        RuntimeError: If Tesseract is not working properly.
    """
    try:
        import pytesseract

        # Find tesseract executable
        tesseract_path = find_tesseract_executable()
        if not tesseract_path:
            raise RuntimeError("Tesseract executable not found")

        # Test with a simple image if available
        test_image_path = (
            Path(__file__).parent.parent.parent.parent / "examples" / "data" / "image.png"
        )
        if test_image_path.exists():
            logger.debug("Testing Tesseract with sample image...")
            result = pytesseract.image_to_string(str(test_image_path))
            logger.debug(f"Tesseract test successful. Extracted text length: {len(result)}")
        else:
            logger.debug("No test image found, skipping Tesseract test")

    except ImportError as e:
        raise RuntimeError(
            "pytesseract is not installed. Please install it using 'pip install pytesseract'"
        ) from e
    except Exception as e:
        raise RuntimeError(f"Tesseract test failed: {e}") from e


async def ensure_models_available(models_dir: Path) -> None:
    """Ensure all required models are downloaded and available.

    Args:
        models_dir: Directory to store models.
    """
    logger.debug(f"Checking models in {models_dir}")

    # Create models directory if it doesn't exist
    models_dir.mkdir(parents=True, exist_ok=True)

    # Check and download missing models
    missing_models = []
    for model_name in REQUIRED_MODELS:
        model_path = models_dir / model_name
        if not model_path.exists():
            missing_models.append(model_name)
        else:
            logger.debug(f"Model {model_name} already exists")

    # Download missing models
    if missing_models:
        logger.info(f"Downloading {len(missing_models)} missing models...")
        for model_name in missing_models:
            model_url = f"{BASE_MODELS_URL}/{model_name}"
            model_path = models_dir / model_name
            logger.info(f"Downloading {model_name}...")
            await download_file(model_url, model_path)
    else:
        logger.info("All required models are already available")


async def check_dependencies() -> None:
    """Check and ensure all dependencies are available.

    This function:
    1. Checks if Tesseract OCR is installed and working
    2. Downloads and tries to install Tesseract if needed
    3. Ensures all required detection models are downloaded

    Raises:
        RuntimeError: If Tesseract is not working properly or if any required model is missing.
        KeyboardInterrupt: If the user cancels the installation process.
        Exception: If any other error occurs during the dependency check.
    """
    logger.info("Checking dependencies...")

    try:
        # Get docviz directory
        docviz_dir = get_docviz_directory()
        logger.debug(f"Using docviz directory: {docviz_dir}")

        # Check Tesseract installation
        try:
            test_tesseract_installation()
            logger.info("Tesseract OCR is properly installed and working")
        except RuntimeError as e:
            logger.warning(f"Tesseract issue: {e}")
            await install_tesseract(docviz_dir)

        # Ensure models are available
        await ensure_models_available(get_models_path())

        logger.info("All dependencies are ready")

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to check dependencies: {e}")
        raise


def reset_docviz_cache(graceful: bool = False) -> None:
    """Reset the docviz cache.

    This function should be called when the user wants to delete all
    cached configurations, models, and information about the dependencies.

    Args:
        graceful: If True, the function will try to reset the cache gracefully, trying to remove each file one by one.
            If False, the function will raise an exception if the directory is used by another process.

    Raises:
        Exception: If any error occurs during the reset process. For example,
            if directory is used by another process.
    """
    logger.info("Resetting docviz cache...")
    try:
        docviz_dir = get_docviz_directory()
        if graceful:
            for file in docviz_dir.glob("*"):
                file.unlink()
            docviz_dir.rmdir()
        else:
            shutil.rmtree(docviz_dir)
    except Exception as e:
        logger.error(f"Failed to reset docviz cache: {e}")
        raise
    logger.info("Docviz cache reset successfully")
