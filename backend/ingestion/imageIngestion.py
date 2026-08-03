from pathlib import Path
import easyocr
from langchain_core.documents import Document

reader = easyocr.Reader(["en"])
def load_images(data_dir: str):

    docs = []

    image_extensions = [
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".webp"
    ]

    for image_path in Path(data_dir).rglob("*"):
        if image_path.suffix.lower() not in image_extensions:
            continue
        result = reader.readtext(str(image_path))
        extracted_text = "\n".join(
            [item[1] for item in result]
        )
        docs.append(
            Document(
                page_content=extracted_text,
                metadata={
                    "source": str(image_path),
                    "type": "image_ocr"
                }
            )
        )
    print(f"Loaded {len(docs)} images.")
    return docs