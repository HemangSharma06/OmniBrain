import os
import fitz
from zipfile import ZipFile

#  PDF FILES IMAGE EXTRACTOR
def extract_pdf_images(pdf_path: str, output_dir: str):
    """
    Extract images from PDF file.

    Arguments:
        pdf_path (str): Path of PDF file.
        output_dir (str): Folder where images will be saved.

    Returns:
        list[str]: Extracted image paths.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}"
        )

    os.makedirs(output_dir, exist_ok=True)

    image_paths = []

    pdf_document = fitz.open(pdf_path)

    for page_number in range(len(pdf_document)):

        page = pdf_document[page_number]
        images = page.get_images(full=True)

        for image_index, image in enumerate(images):

            xref = image[0]
            base_image = pdf_document.extract_image(xref)

            image_bytes = base_image["image"]
            image_extension = base_image["ext"]

            image_name = (
                f"page_{page_number+1}_"
                f"image_{image_index+1}."
                f"{image_extension}"
            )

            image_path = os.path.join(
                output_dir,
                image_name
            )

            with open(image_path, "wb") as f:
                f.write(image_bytes)
            image_paths.append(image_path)

    pdf_document.close()
    return image_paths

# WORD FILES IMAGE EXTRACTOR
def extract_docx_images(docx_path: str, output_dir: str):
    """
    Extract images from DOCX file.
    Arguments:
        docx_path (str): Path of DOCX file.
        output_dir (str): Folder where images will be saved.
    Return Type:
        list[str]: Extracted image paths.
    """

    if not os.path.exists(docx_path):
        raise FileNotFoundError(
            f"DOCX not found: {docx_path}"
        )

    os.makedirs(output_dir, exist_ok=True)
    image_paths = []
    docx_document = ZipFile(docx_path)

    for file_name in docx_document.namelist():
        if file_name.startswith("word/media/"):

            image_name = os.path.basename(file_name)
            image_path = os.path.join(
                output_dir,
                image_name
            )

            image_bytes = docx_document.read(file_name)
            with open(image_path, "wb") as f:
                f.write(image_bytes)

            image_paths.append(image_path)
    docx_document.close()
    return image_paths