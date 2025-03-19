from dataclasses import dataclass
from enum import Enum
from io import BytesIO
import io
import logging
import mimetypes
from pathlib import Path
import re
import shutil
from typing import IO, BinaryIO, Union
import zipfile
from docx import Document
import magic
from pdf2image import convert_from_bytes
import pdfplumber
import docx2txt
import pytesseract
from docx.shared import Inches
from striprtf.striprtf import rtf_to_text
from odf.opendocument import load
from PIL import Image as PILImage
from odf.draw import Frame
from odf.text import P
from odf.draw import Image
import markdown

from doc23.allowed_types import AllowedTypes
from doc23.config_tree import Config


class Doc23:

    ALLOWED_TYPES = AllowedTypes

    def __init__(self, file: Union[str, Path, IO[bytes]], config: Config):
        """Doc23 class to parse a document and extract the information based on the configuration.

        Args:
            file (Union[str, Path, IO[bytes]]): The file to be parsed.
            config (Config): The patterns to be found, the structure of the output, and the fields to be used.
        """
        self._file = file
        self._config = config
        self._text = ""

    def extract_text(self, scan_or_image: str | bool = False) -> str:
        """Extract text from the file

        Args:
            scan_or_image (str | bool, optional): The file contains image or is scanned_. Defaults to False.

        Raises:
            ValueError: If the file is not any of the ALLOWED_TYPES, return an error unsupported document type.

        Returns:
            str: The text extracted from file
        """
        doc_type = AllowedTypes(self.get_doc_type())  # Convert string to Enum
        match doc_type:
            case self.ALLOWED_TYPES.PDF:
                return self.extract_text_pdf(scan_or_image)
            case self.ALLOWED_TYPES.TXT:
                return self.extract_text_txt()
            case self.ALLOWED_TYPES.DOCX:
                return self.extract_text_docx(scan_or_image)
            case self.ALLOWED_TYPES.RTF:
                return self.extract_text_rtf(scan_or_image)
            case self.ALLOWED_TYPES.ODT:
                return self.extract_text_odt(scan_or_image)
            case self.ALLOWED_TYPES.MD:
                return self.extract_text_md(scan_or_image)
            case (
                self.ALLOWED_TYPES.PNG
                | self.ALLOWED_TYPES.JPEG
                | self.ALLOWED_TYPES.TIFF
                | self.ALLOWED_TYPES.BMP
            ):
                return self.extract_text_from_image()
            case _:
                raise ValueError(f"Unsupported document type: {doc_type}")

    def prune(self, config: Config = None, text: str = None):
        config = config or self._config
        text = text or self.extract_text()

        if config is None:
            raise ValueError("Config object is required to prune the doc")
        if not text.strip():
            raise ValueError("Text is required to prune the doc")

        structure = {
            self._config["root_name"]: {
                self._config["sections_field"]: [],  # Ensure sections exist at the root
                self._config["description_field"]: "",
            }
        }
        stack = [(structure, None)]  # Stack of levels
        current_article = None

        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            for level, details in self._config["levels"].items():
                match = re.match(details["pattern"], line)
                if match:
                    # Create a new section with custom names
                    new_section = {
                        details["title_field"]: match.group(0),
                        details["description_field"]: "",
                        details.get("sections_field", "sections"): [],
                    }
                    if "paragraph_field" in details:
                        new_section[details["paragraph_field"]] = []

                    # Find which level must to be inserted the current section
                    while stack and stack[-1][1] not in (None, details.get("parent")):
                        stack.pop()  # Back through the hierarchy until found where to fit

                    parent, _ = stack[-1]

                    sections_field = self._config.get("sections_field", "sections")

                    if sections_field not in parent:
                        parent[sections_field] = []  # Ensure the sections list exists

                    parent[sections_field].append(new_section)

                    stack.append((new_section, level))

                    if "paragraph_field" in details:
                        current_article = new_section
                    else:
                        current_article = None
                    break
            else:
                # If not a new section fit like content
                if current_article:
                    current_article[self._config["description_field"]] += " " + line
                elif stack[-1][0]:
                    description_field = self._config.get("description_field", "content")

                    if description_field not in stack[-1][0]:
                        stack[-1][0][
                            description_field
                        ] = ""  # Ensure the key exists before appending

                    stack[-1][0][description_field] += " " + line

        return structure

    def pdf_contain_text(self) -> bool:
        """Check if the PDF file contains text.

        Returns:
            bool: True if the PDF file contains text, False otherwise.
        """
        with pdfplumber.open(
            str(self._file) if isinstance(self._file, Path) else self._file
        ) as pdf:
            return any(page.extract_text() for page in pdf.pages)
        return False

    def extract_text_pdf(self, scan_or_image: str | bool = False) -> str:
        """Extract the text of a PDF file.
        Args                                :
        scan_or_image (str | bool, optional): The method to extract the text from the PDF file.
            If False, the text is extracted assuming the file is only text.
            If True, the text is extracted assuming the file is scanned or contain images with text.
            If 'auto', the text is extracted assuming the file contain both, text and scanned pages or images with text.
            Defaults to False.
        Returns:
            str: The text of the PDF file.
        """
        match scan_or_image:

            case False:
                with pdfplumber.open(
                    str(self._file) if isinstance(self._file, Path) else self._file
                ) as pdf:
                    return "\n".join(page.extract_text() or "" for page in pdf.pages)
            case True:
                return self.extract_text_from_scanned_pdf()
            case "auto":
                return self.extract_text_from_mix_pdf()
            case _:
                raise ValueError("scan_or_image must be a boolean or 'auto'.")

    def extract_text_txt(self) -> str:
        """Extract the text of a TXT file.

        Returns:
            str: The text of the TXT file.
        """
        if isinstance(self._file, (str, Path)):
            with open(self._file, "r", encoding="utf-8") as file:
                return file.read().strip()

        if isinstance(self._file, BytesIO):
            return self._file.read().decode("utf-8").strip()

        raise ValueError("The file must be a path, a string, or a BytesIO object.")

    def extract_text_docx(self, scan_or_image) -> str:
        """Extract the text of a DOC file.

        Returns:
            str: The text of the DOC file.
        """
        match scan_or_image:
            case False:
                if isinstance(self._file, (str, Path)):
                    return docx2txt.process(self._file).strip()

                if isinstance(self._file, BytesIO):
                    temp_path = "/tmp/temp.docx"
                    with open(temp_path, "wb") as temp_file:
                        temp_file.write(self._file.read())

                    Path(temp_path).unlink(missing_ok=True)
                    return docx2txt.process(temp_path).strip()
            case True:
                return self.extract_text_from_scanned_docx()
            case "auto":
                return (
                    self.extract_text_from_mix_pdf()
                    if not self.pdf_contain_text()
                    else self.extract_text_pdf(False)
                )
            case _:
                raise ValueError("is_scanned must be a boolean or 'auto'.")

        raise ValueError("The file must be a path or a BytesIO object.")

    def extract_text_rtf(self) -> str:
        """Extract the text of a RTF file.

        Returns:
            str: The text of the RTF file.
        """
        if isinstance(self._file, (str, Path)):
            with open(self._file, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
        elif isinstance(self._file, BytesIO):
            content = self._file.read().decode("utf-8", errors="ignore")
        else:
            raise ValueError("The file must be a path, a string, or a BytesIO object.")

        return rtf_to_text(content).strip()

    def extract_text_odt(self, scan_or_image: str | bool = False) -> str:
        """Extract the text of an ODT file (LibreOffice, OpenOffice).

        Returns:
            str: The text of the ODT file.
        """
        match scan_or_image:
            case False:
                if isinstance(self._file, (str, Path, BytesIO)):
                    odt_doc = load(self._file)

                    return "\n".join(
                        [
                            p.firstChild.data
                            for p in odt_doc.getElementsByType(P)
                            if p.firstChild
                        ]
                    ).strip()

                else:
                    raise ValueError(
                        "The file must be a path, a string, or a BytesIO object."
                    )
            case True:
                return self.extract_text_from_scanned_odt()
            case "auto":
                return self.extract_text_from_mix_odt()
            case _:
                raise ValueError("is_scanned must be a boolean or 'auto'.")

    def extract_text_md(self) -> str:
        """Extract the text of a MD file.

        Returns:
            str: The text of the MD file.
        """
        if isinstance(self._file, (str, Path)):
            with open(self._file, "r", encoding="utf-8") as file:
                content = file.read()
        elif isinstance(self._file, BytesIO):
            content = self._file.read().decode("utf-8")
        else:
            raise ValueError("The file must be a path, a string, or a BytesIO object.")

        return markdown.markdown(content).strip()

    # Scanned PDF
    def extract_text_from_scanned_pdf(self) -> str:
        """Extract the text from a scanned PDF file.

        Returns:
        str    : The text of the scanned PDF file.
        """
        if not self.available_tesseract():
            raise RuntimeError(
                "Tesseract OCR is not available. Please install it on this server."
            )

        if isinstance(self._file, (str, Path)):
            with open(self._file, "rb") as file:
                pages = convert_from_bytes(file.read())
        elif isinstance(self._file, BytesIO):
            pages = convert_from_bytes(self._file.read())
        else:
            raise ValueError("The file must be a path, a string, or a BytesIO object.")
        extracted_text = [pytesseract.image_to_string(page) for page in pages]
        return "\n".join(extracted_text).strip()

    def extract_text_from_mix_pdf(self) -> str:
        """Extract the text from a mixed PDF file (scanned and text).

        Returns:
            str: The text of the mixed PDF file.
        """
        if not self.available_tesseract():
            raise RuntimeError(
                "Tesseract OCR is not available. Please install it on this server."
            )

        with pdfplumber.open(
            str(self._file) if isinstance(self._file, Path) else self._file
        ) as pdf:
            extracted_text = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text.append(text)
                else:
                    try:
                        image = page.to_image().original
                        ocr_text = pytesseract.image_to_string(image, lang="eng")
                        extracted_text.append(ocr_text)
                    except Exception as e:
                        logging.warning(
                            f"Error processing page {page.page_number}: {e}"
                        )
        return "\n".join(extracted_text).strip()

    # Scanned docx
    def extract_text_from_scanned_docx(self) -> str:
        """Extract the text from a scanned DOCX file.

        Returns:
            str: The text of the scanned DOCX file.
        """
        if not self.available_tesseract():
            raise RuntimeError(
                "Tesseract OCR is not available. Please install it on this server."
            )

        doc = Document(self._file)
        extracted_text = []

        for shape in doc.inline_shapes:
            if shape._inline.graphic.graphicData.pic.blipFill:
                blip = shape._inline.graphic.graphicData.pic.blipFill.blip
                rId = blip.embed
                image_part = doc.part.related_parts[rId]
                image_data = image_part.blob

                image = Image.open(io.BytesIO(image_data))
                extracted_text.append(pytesseract.image_to_string(image))

        return "\n".join(extracted_text).strip()

    # Scanned ODT
    def extract_text_from_scanned_odt(self) -> str:
        """Extract the text from a scanned ODT file.

        Returns:
            str: The text of the scanned ODT file.
        """
        if not self.available_tesseract():
            raise RuntimeError(
                "Tesseract OCR is not available. Please install it on this server."
            )

        odt_doc = load(self._file)
        extracted_text = []

        with zipfile.ZipFile(self._file) as z:
            for frame in odt_doc.getElementsByType(Frame):
                image_elements = frame.getElementsByType(Image)
                for image_element in image_elements:
                    image_href = image_element.getAttribute("href").replace(
                        "Pictures/", ""
                    )
                    if image_href:
                        try:
                            with z.open(f"Pictures/{image_href}") as image_file:
                                img = PILImage.open(image_file)
                                ocr_text = pytesseract.image_to_string(img, lang="eng")
                                extracted_text.append(ocr_text)
                        except Exception as e:
                            print(f"Error processing image {image_href}: {e}")

        return "\n".join(extracted_text).strip()

    def extract_text_from_mix_odt(self) -> str:
        """Extract the text from a mixed ODT file (scanned and text).
        Args                 :
            file_obj (io.BytesIO): The ODT file object.
        Returns              :
            str                  : The text of the mixed ODT file.
        """

        if not self.available_tesseract():
            raise RuntimeError(
                "Tesseract OCR is not available. Please install it on this server."
            )

        odt_doc = load(self._file)
        extracted_text = []

        with zipfile.ZipFile(self._file) as z:
            for elem in odt_doc.body.childNodes:
                if isinstance(elem, P):
                    if elem.firstChild:
                        extracted_text.append(elem.firstChild.data)

                elif isinstance(elem, Frame):
                    image_elements = elem.getElementsByType(Image)
                    for image_element in image_elements:
                        image_href = image_element.getAttribute("href").replace(
                            "Pictures/", ""
                        )
                        if image_href:
                            try:
                                with z.open(f"Pictures/{image_href}") as image_file:
                                    img = PILImage.open(image_file)
                                    ocr_text = pytesseract.image_to_string(
                                        img, lang="eng"
                                    )
                                    extracted_text.append(ocr_text)
                            except Exception as e:
                                print(f"Error processing image {image_href}: {e}")

        return "\n".join(extracted_text).strip()

    # Images
    def extract_text_from_image(self) -> str:
        """Extract

        Returns:
            str    : Extracted text from image.
        """
        if not self.available_tesseract():
            raise RuntimeError(
                "Tesseract OCR is not available. Please install it on this server."
            )

        try:
            if isinstance(self._file, io.BytesIO):
                image = Image.open(self._file)
            else:
                image = Image.open(str(self._file))

            ocr_text = pytesseract.image_to_string(image, lang="eng")

            return ocr_text.strip()

        except Exception as e:
            raise RuntimeError(f"Error processing image: {e}")

    def get_doc_type(self) -> str:
        """Get the type of the document.

        Returns:
            str: The type of the document.
        """
        # Check the document type if the file is an IO memory object
        mime = magic.Magic(mime=True)
        if isinstance(self._file, IO):
            doc_type = mime.from_buffer(self._file.read(2048))
            self._file.seek(0)
            return doc_type

        file_path = Path(self._file) if isinstance(self._file, (str, Path)) else None
        if file_path is None:
            raise ValueError("The file must be a path, a string or a file object.")

        ext_type = mimetypes.guess_type(file_path)[0]
        real_type = mime.from_file(str(file_path))
        _type = ext_type or real_type
        print(_type)
        return _type

    def available_tesseract(self) -> bool:
        """Check if Tesseract OCR is available.

        Returns:
            bool: True if Tesseract OCR is available, False otherwise.
        """
        return shutil.which("tesseract") is not None


obj = Doc23("doc23.py", Config())
