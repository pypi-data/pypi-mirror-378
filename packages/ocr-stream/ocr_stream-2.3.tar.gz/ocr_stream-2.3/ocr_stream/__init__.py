#!/usr/bin/env python3

from ocr_stream.modules import *
from ocr_stream.bin_tess import BinTesseract, get_path_tesseract_sys
from ocr_stream.ocr import TesseractOcr, TextRecognized, DEFAULT_LIB_OCR
from ocr_stream.recognize import RecognizeImage, RecognizePdf
from soup_files import File, Directory, InputFiles, LibraryDocs, CreatePbar, ProgressBarAdapter
from convert_stream import ImageObject, PdfStream, DocumentPdf, ConvertPdfToImages


def read_images(
            images: list[ImageObject], *,
            pbar: ProgressBarAdapter = CreatePbar().get()
        ) -> DocumentPdf:
    pbar.start()
    print()
    max_num = len(images)
    pages = []
    rec = RecognizeImage()
    for idx, image in enumerate(images):
        pbar.update(
            ((idx + 1) / max_num) * 100,
            f'[OCR] {idx + 1} / {max_num}',
        )
        out = rec.image_recognize(image).to_page_pdf()
        pages.append(out)
    tmp_doc = DocumentPdf.create_from_pages(pages)
    print()
    pbar.stop()
    return tmp_doc


def read_document(
            document: DocumentPdf, *,
            dpi: int = 300,
            pbar: ProgressBarAdapter = CreatePbar().get()
        ) -> DocumentPdf:
    pbar.start()
    print()
    convert = ConvertPdfToImages.create(document)
    convert.set_pbar(pbar)
    images = convert.to_images(dpi=dpi)
    print()
    return read_images(images, pbar=pbar)







