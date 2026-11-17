
import subprocess
import tempfile
from pathlib import Path
import shutil


SUPPORTED_FORMATS = {
    ".doc": "docx",
    ".xls": "xlsx",
    ".ppt": "pptx"
}


def find_libreoffice():
    """
    Find LibreOffice executable on macOS or other systems.
    """

    executable = (
        shutil.which("libreoffice")
        or shutil.which("soffice")
    )

    if executable:
        return executable

    mac_executable = Path(
        "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    )

    if mac_executable.exists():
        return str(mac_executable)

    raise RuntimeError(
        "LibreOffice is not installed or available on this system."
    )


def convert_legacy_document(file_path):
    """
    Convert legacy Microsoft Office documents
    into modern formats using LibreOffice.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Unsupported legacy format: {extension}"
        )

    output_extension = SUPPORTED_FORMATS[extension]

    libreoffice = find_libreoffice()

    with tempfile.TemporaryDirectory() as temp_dir:

        output_dir = Path(temp_dir)

        command = [
            libreoffice,
            "--headless",
            "--convert-to",
            output_extension,
            "--outdir",
            str(output_dir),
            str(file_path)
        ]

        try:
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
                timeout=120
            )

        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                f"Document conversion failed: {error.stderr}"
            ) from error

        except subprocess.TimeoutExpired as error:
            raise RuntimeError(
                "Document conversion timed out."
            ) from error

        converted_file = (
            output_dir / f"{file_path.stem}.{output_extension}"
        )

        if not converted_file.exists():
            raise RuntimeError(
                "Conversion completed but output file was not created."
            )

        return {
            "filename": converted_file.name,
            "extension": output_extension,
            "content": converted_file.read_bytes()
        }
