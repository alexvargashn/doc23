from enum import Enum


class AllowedTypes:
    PDF = {"application/pdf"}
    DOCX = {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
    TXT = {"text/plain"}
    RTF = {"application/rtf", "text/rtf"}
    ODT = {"application/vnd.oasis.opendocument.text"}
    MARKDOWN = {"text/markdown"}
    IMAGE = {
        "image/png",
        "image/jpeg",
        "image/jpg",
        "image/tiff",
        "image/bmp",
        "image/gif"
    }

    @classmethod
    def is_allowed(cls, mime_type: str) -> bool:
        """Check if a MIME type is allowed."""
        return any(mime_type in allowed_types for allowed_types in cls.__dict__.values())
