import os
import warnings
warnings.filterwarnings("ignore")

from PIL import Image
import easyocr
from langchain_core.documents import Document

reader = easyocr.Reader(["en"], gpu=False)


def loadVisionDocuments(image_path):
    """
    Loads images and extracts OCR text.
    Stores image path for Vision Agent.
    """

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Path not found: {image_path}")

    supported_formats = (".png", ".jpg", ".jpeg", ".bmp", ".webp")

    documents = []

    for file in os.listdir(image_path):

        if not file.lower().endswith(supported_formats):
            continue

        full_path = os.path.join(image_path, file)

        try:
            # verify image
            img = Image.open(full_path)
            img.verify()

            # OCR
            text = reader.readtext(full_path, detail=0)
            extracted_text = "\n".join(text)

            document = Document(
                page_content=extracted_text,
                metadata={
                    "source": full_path,
                    "type": "image",
                    "image_path": full_path
                }
            )

            documents.append(document)

            print(f"\nImage: {file}")
            print(f"Source: {full_path}")
            print(f"OCR Length: {len(extracted_text)}")
            print(f"Preview: {extracted_text[:100]}")

        except Exception as e:
            print(f"Skipped {file}: {e}")

    if not documents:
        raise FileNotFoundError("No supported image files found.")

    return documents