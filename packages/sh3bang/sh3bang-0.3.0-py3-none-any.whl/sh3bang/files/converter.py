from docx2pdf import convert as docx2pdf_convert
from pdf2docx import Converter as pdf2docx_convert


def pdf_to_docx(pdf_path: str, docx_path: str):
    """Convert PDF -> DOCX"""
    cv = pdf2docx_convert(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()


def docx_to_pdf(docx_path: str, pdf_path: str = None):
    """Convert DOCX -> PDF"""
    docx2pdf_convert(docx_path, pdf_path)
