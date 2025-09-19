"""
PDFDancer Python Client

A Python client library for the PDFDancer PDF manipulation API.
Provides a clean, Pythonic interface for PDF operations that closely
mirrors the Java client structure and functionality.
"""

from .client_v1 import ClientV1
from .exceptions import (
    PdfDancerException, FontNotFoundException, ValidationException,
    HttpClientException, SessionException
)
from .models import (
    ObjectRef, Position, ObjectType, Font, Color, Image, BoundingRect, Paragraph,
    PositionMode, ShapeType, Point
)
from .paragraph_builder import ParagraphBuilder

__version__ = "1.0.0"
__all__ = [
    "ClientV1",
    "ParagraphBuilder",
    "ObjectRef",
    "Position",
    "ObjectType",
    "Font",
    "Color",
    "Image",
    "BoundingRect",
    "Paragraph",
    "PositionMode",
    "ShapeType",
    "Point",
    "PdfDancerException",
    "FontNotFoundException",
    "ValidationException",
    "HttpClientException",
    "SessionException"
]
