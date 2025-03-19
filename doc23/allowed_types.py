from enum import Enum


class AllowedTypes(Enum):

    PDF = "application/pdf"
    TXT = "text/plain"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    RTF = "application/rtf"
    ODT = "application/vnd.oasis.opendocument.text"
    MD = "text/markdown"
    PNG = "image/png"
    JPEG = "image/jpeg"
    TIFF = "image/tiff"
    BMP = "image/bmp"

    def __str__(self):
        return self.value
