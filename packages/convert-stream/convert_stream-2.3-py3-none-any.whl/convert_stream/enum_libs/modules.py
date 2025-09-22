#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Union, TypeAlias, Any
from convert_stream.enum_libs.enums import *

MOD_IMG_PIL: bool = False
MOD_IMG_OPENCV: bool = False
MOD_PYPDF: bool = False
MOD_FITZ: bool = False
MOD_CANVAS: bool = False

#=================================================================#
# Módulos de Imagen, PIL e opencv
#=================================================================#
try:
    import cv2
    from cv2.typing import MatLike
    MOD_IMG_OPENCV = True
except ImportError:
    cv2.typing.MatLike = Any
    MatLike = Any

try:
    from PIL import Image
    from PIL import ImageOps, ImageFilter
    MOD_IMG_PIL = True
except ImportError:
    Image = Any
    Image.Image = Any

if MOD_IMG_OPENCV and MOD_IMG_PIL:
    ModuleImage: TypeAlias = Union[MatLike, Image.Image]
    DEFAULT_LIB_IMAGE = LibImage.OPENCV
elif MOD_IMG_OPENCV:
    ModuleImage: TypeAlias = Union[MatLike]
    DEFAULT_LIB_IMAGE = LibImage.OPENCV
elif MOD_IMG_PIL:
    ModuleImage: TypeAlias = Union[Image.Image]
    DEFAULT_LIB_IMAGE = LibImage.PIL
else:
    DEFAULT_LIB_IMAGE = LibImage.NOT_IMPLEMENTED
    ModuleImage = Any  # fallback para runtime

#=================================================================#
# Módulos para PDF fitz e pypdf
#=================================================================#

try:
    import fitz
    MOD_FITZ = True
except ImportError:
    try:
        import pymupdf as fitz
        MOD_FITZ = True
    except ImportError:
        fitz = Any
        fitz.Page = Any
        fitz.TextPage = Any

try:
    from pypdf import PdfWriter, PdfReader, PageObject
    MOD_PYPDF = True
except ImportError:
    PageObject = Any
    PdfReader = Any
    PdfWriter = Any


if MOD_FITZ and MOD_PYPDF:
    ModPagePdf = Union[PageObject, fitz.Page]
    ModDocPdf = Union[fitz.Document, PdfWriter]
    DEFAULT_LIB_PDF = LibPDF.FITZ
elif MOD_FITZ:
    ModPagePdf = Union[fitz.Page]
    ModDocPdf = Union[fitz.Document]
    DEFAULT_LIB_PDF = LibPDF.FITZ
elif MOD_PYPDF:
    ModPagePdf = Union[PageObject]
    ModDocPdf = Union[PdfWriter]
    DEFAULT_LIB_PDF = LibPDF.PYPDF
else:
    ModPagePdf = Any  # fallback para runtime
    ModDocPdf = Any
    DEFAULT_LIB_PDF = LibPDF.NOT_IMPLEMENTED

#=================================================================#
# Módulos para converter imagem em PDF.
#=================================================================#

try:
    from reportlab.pdfgen import canvas
    from reportlab.pdfgen.canvas import Canvas
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.utils import ImageReader
    MOD_CANVAS = True
except ImportError:
    canvas = Any
    Canvas = Any
    letter = (612, 792)
    ImageReader = Any

if MOD_CANVAS and MOD_FITZ and MOD_IMG_PIL:
    ModImageToPdf: TypeAlias = Union[canvas, fitz.Page, Image]
    DEFAULT_LIB_IMAGE_TO_PDF = LibImageToPdf.IMAGE_TO_PDF_FITZ
elif MOD_FITZ:
    ModImageToPdf: TypeAlias = Union[fitz.Page]
    DEFAULT_LIB_IMAGE_TO_PDF = LibImageToPdf.IMAGE_TO_PDF_FITZ
elif MOD_CANVAS:
    ModImageToPdf: TypeAlias = Union[canvas]
    DEFAULT_LIB_IMAGE_TO_PDF = LibImageToPdf.IMAGE_TO_PDF_CANVAS
elif MOD_IMG_PIL:
    ModImageToPdf: TypeAlias = Union[Image]
    DEFAULT_LIB_IMAGE_TO_PDF = LibImageToPdf.IMAGE_TO_PDF_PIL
else:
    ModImageToPdf = Any
    DEFAULT_LIB_IMAGE_TO_PDF = LibImageToPdf.NOT_IMPLEMENTED

#=================================================================#
# Módulos para converter PDF em imagem
#=================================================================#

if MOD_FITZ:
    DEFAULT_LIB_PDF_TO_IMG = LibPdfToImage.PDF_TO_IMG_FITZ
    ModPdfToImage: TypeAlias = Union[fitz]
else:
    DEFAULT_LIB_PDF_TO_IMG = LibPdfToImage.NOT_IMPLEMENTED
    ModPdfToImage = Any
