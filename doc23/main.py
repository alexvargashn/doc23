from dataclasses import dataclass
from enum import Enum
from io import BytesIO
import io
import logging
import mimetypes
from pathlib import Path
import re
import shutil
from typing import IO, Any, BinaryIO, Dict, Optional, Union
import zipfile
from docx import Document
import magic as python_magic
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
from doc23.config_tree import Config, LevelConfig
from doc23.gardener import Gardener


class Doc23:

    ALLOWED_TYPES = AllowedTypes

    def __init__(self, file: Union[str, Path, IO[bytes]], config: Config):
        """Doc23 class to parse a document and extract the information based on the configuration.

        Args:
            file (Union[str, Path, IO[bytes]]): The file to be parsed.
            config (Config): The patterns to be found, the structure of the output and the fields to be used.
        """
        self._file = file
        self._config = config
        self._text = ""

    def extract_text(self, scan_or_image: str | bool = False) -> str:
        """Extract text from the file

        Args:
            scan_or_image (str | bool, optional): The file contains image or is scanned. Defaults to False.

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

    def prune(self, config: Config = None, text:str = None) -> Dict[str, Any]: 
        """
        Parses the text and returns a nested dictionary structure.
        
        This version replicates the "classic" article insertion logic: 
        If   an 'article' is detected                                : 
          1) If there's a current chapter, attach it there.
          2) Else if there's a current title, attach it there.
          3) Else if there's a current book, attach it there.
          4) Otherwise, attach at root.
        """
        config = self._config
        text   = self.extract_text()

        gardener = Gardener(config)
        return gardener.prune(text)
        
    def pdf_contain_text(self) -> bool:
        """Check if the PDF file contains text.

        Returns:
        bool   : True if the PDF file contains text, False otherwise.
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
        mime = python_magic.Magic(mime=True)
        if isinstance(self._file, BytesIO):
            doc_type = mime.from_buffer(self._file.read(2048))
            self._file.seek(0)
            return doc_type

        file_path = Path(self._file) if isinstance(self._file, (str, Path)) else None
        if file_path is None:
            raise ValueError("The file must be a path, a string or a file object.")

        ext_type = mimetypes.guess_type(file_path)[0]
        real_type = mime.from_file(str(file_path))
        _type = ext_type or real_type
        return _type

    def available_tesseract(self) -> bool:
        """Check if Tesseract OCR is available.

        Returns:
            bool: True if Tesseract OCR is available, False otherwise.
        """
        return shutil.which("tesseract") is not None

    def parse_legal_document(text): 
        # Expresiones regulares para identificar secciones
        book_pattern = r"^(LIBRO|LBRO)\s+[^\n]+"
        title_pattern = r"^TITULO\s+[^\n]+"
        chapter_pattern = r"^CAPITULO\s+[^\n]+"
        article_pattern = r"^ARTICULO\s+(\d+-?[A-Z]?)\.\s*(.+)"

        # Estructura principal
        structure = {"title": "", "description": "", "sections": []}
        current_book = None
        current_title = None
        current_chapter = None
        current_article = None

        for line in text.split("\n"):
            line = line.strip()

            # Detectar libros
            book_match = re.match(book_pattern, line)
            if book_match:
                current_book = {
                    "title": book_match.group(0),
                    "description": "",
                    "sections": [],
                    "articles": [],
                }
                structure["sections"].append(current_book)
                current_title = None
                current_chapter = None
                current_article = None
                continue
            # Solver in the general algorithm
            # Detectar títulos
            title_match = re.match(title_pattern, line)
            if title_match and current_book:
                current_title = {
                    "title": title_match.group(0),
                    "description": "",
                    "sections": [],
                    "articles": [],
                }
                current_book["sections"].append(current_title)
                current_chapter = None
                current_article = None
                continue

            # Detectar capítulos
            chapter_match = re.match(chapter_pattern, line)
            if chapter_match and current_title:
                current_chapter = {
                    "title": chapter_match.group(0),
                    "description": "",
                    "articles": [],
                }
                current_title["sections"].append(current_chapter)
                current_article = None
                continue

            # Detectar artículos (con sufijos opcionales)
            article_match = re.match(article_pattern, line)
            if article_match:
                article = {
                    "title": f"ARTICULO {article_match.group(1)}",
                    "content": article_match.group(
                        2
                    ),  # Captura todo el contenido inicial del artículo
                }

                # Si hay un capítulo actual, agregar el artículo dentro de él
                if current_chapter: 
                    current_chapter["articles"].append(article)
                # Si no hay un capítulo, el artículo pertenece directamente al título
                elif current_title:
                    current_title["articles"].append(article)

                current_article = (
                    article  # Mantener referencia para agregar contenido adicional
                )
                continue

            # Si encontramos contenido adicional para el artículo actual
            if current_article:
                current_article["content"] += (
                    " " + line
                )  # Agregar contenido adicional al artículo
            elif current_chapter:
                current_chapter["description"] += " " + line
            elif current_title:
                current_title["description"] += " " + line
            elif current_book:
                current_book["description"] += " " + line
            else:
                structure["description"] += " " + line

        return structure


    def prune2(self) -> Dict[str, Any]: 
        """
        Parses the text and returns a nested dictionary structure.
        
        This version replicates the "classic" article insertion logic:
        If an 'article' is detected:
          1) If there's a current chapter, attach it there.
          2) Else if there's a current title, attach it there.
          3) Else if there's a current book, attach it there.
          4) Otherwise, attach at root.
        """
        config = self._config
        text = self._text

        # Root structure
        root: Dict[str, Any] = {
            "name": config.root_name,
            config.sections_field: [],
            config.description_field: ""
        }

        # Dictionary to track the most recent node for each level key
        # e.g., current_nodes["title"] = {...}, current_nodes["chapter"] = {...}
        current_nodes: Dict[str, Dict[str, Any]] = {}

        def get_depth(level_key: str) -> int:
            """
            Computes how many parents up the chain exist for this level key.
            A root level has parent=None => depth=0.
            """
            depth = 0
            parent_key = config.levels[level_key].parent
            while parent_key is not None:
                depth += 1
                parent_key = config.levels[parent_key].parent
            return depth

        level_keys_sorted = sorted(config.levels.keys(), key=get_depth)

        def create_node(level_key: str, match_obj: re.Match) -> Dict[str, Any]:
            """
            Creates a dictionary node for a matched level.
            
            Generic approach for capturing groups:
              - If no groups, node[level_cfg.title_field] = group(0).
              - If 1 group, node[level_cfg.title_field] = group(1).
              - If 2 or more groups, first group => title, remainder => joined for paragraph_field.
            """
            level_cfg = config.levels[level_key]
            node: Dict[str, Any] = {}

            groups = match_obj.groups()
            if not groups:
                title_value = match_obj.group(0)
                paragraph_value = ""
            elif len(groups) == 1:
                title_value = groups[0]
                paragraph_value = ""
            else:
                title_value = groups[0]
                leftover = groups[1:]
                paragraph_value = " ".join(leftover)

            node[level_cfg.title_field] = title_value

            if level_cfg.description_field is not None:
                node[level_cfg.description_field] = ""

            if level_cfg.sections_field is not None:
                node[level_cfg.sections_field] = []

            if level_cfg.articles_field is not None:
                node[level_cfg.articles_field] = []

            if level_cfg.paragraph_field is not None:
                node[level_cfg.paragraph_field] = paragraph_value

            return node

        # Helper to insert a node under a parent's sections or articles
        def insert_node(parent_node: Dict[str, Any], parent_cfg: LevelConfig, child_node: Dict[str, Any], child_key: str):
            """
            Inserts 'child_node' either into parent's articles_field or sections_field,
            depending on the child's config, or parent's config, or a custom logic.
            """
            child_cfg = config.levels[child_key]

            # If the child's config has a paragraph_field (usually an article)
            # AND the parent has articles_field, we insert in articles.
            # Otherwise, we insert in sections.
            if parent_cfg.articles_field and child_cfg.paragraph_field and not child_cfg.sections_field:
                parent_node[parent_cfg.articles_field].append(child_node)
            else:
                if parent_cfg.sections_field:
                    parent_node[parent_cfg.sections_field].append(child_node)
                else:
                    # If the parent doesn't define sections_field, we fallback to root sections.
                    root[config.sections_field].append(child_node)

        # Process each line
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue

            matched_key = None
            match_obj = None

            # Try matching from deeper levels to shallower
            for level_key in reversed(level_keys_sorted):
                pattern = config.levels[level_key].pattern
                mo = re.match(pattern, line)
                if mo:
                    matched_key = level_key
                    match_obj = mo
                    break

            if matched_key and match_obj:
                new_node = create_node(matched_key, match_obj)

                # If this is not the "article" level, we do the usual "find_parent_node"
                # But if it *is* the article level, we replicate the "classic" fallback logic.
                if matched_key == "article":
                    # 1) If there's a current 'chapter', attach there
                    if "chapter" in current_nodes:
                        parent_cfg = config.levels["chapter"]
                        parent_node = current_nodes["chapter"]
                        insert_node(parent_node, parent_cfg, new_node, matched_key)
                    # 2) else if there's a current 'title', attach there
                    elif "title" in current_nodes:
                        parent_cfg = config.levels["title"]
                        parent_node = current_nodes["title"]
                        insert_node(parent_node, parent_cfg, new_node, matched_key)
                    # 3) else if there's a current 'book', attach there
                    elif "book" in current_nodes:
                        parent_cfg = config.levels["book"]
                        parent_node = current_nodes["book"]
                        insert_node(parent_node, parent_cfg, new_node, matched_key)
                    else:
                        # 4) fallback => root
                        root[config.sections_field].append(new_node)
                else:
                    # Normal path for book, title, chapter, etc.
                    parent_key = config.levels[matched_key].parent
                    if parent_key is None:
                        # Root level
                        root[config.sections_field].append(new_node)
                    else:
                        parent_node = current_nodes.get(parent_key, root)
                        parent_cfg = config.levels[parent_key]
                        insert_node(parent_node, parent_cfg, new_node, matched_key)

                # Update current node for matched level
                current_nodes[matched_key] = new_node

            else:
                # No pattern matched => treat as additional text
                if current_nodes:
                    # Find the deepest active node
                    deepest_key = max(current_nodes.keys(), key=get_depth)
                    deepest_cfg = config.levels[deepest_key]
                    node = current_nodes[deepest_key]

                    if deepest_cfg.paragraph_field:
                        node[deepest_cfg.paragraph_field] += " " + line
                    elif deepest_cfg.description_field:
                        node[deepest_cfg.description_field] += " " + line
                    else:
                        # ascend parents
                        placed = False
                        parent_key = deepest_cfg.parent
                        while parent_key and not placed:
                            p_cfg = config.levels[parent_key]
                            p_node = current_nodes.get(parent_key)
                            if p_node:
                                if p_cfg.paragraph_field:
                                    p_node[p_cfg.paragraph_field] += " " + line
                                    placed = True
                                elif p_cfg.description_field:
                                    p_node[p_cfg.description_field] += " " + line
                                    placed = True
                            parent_key = p_cfg.parent if p_cfg else None

                        if not placed:
                            root[config.description_field] += " " + line
                else:
                    root[config.description_field] += " " + line

        return root