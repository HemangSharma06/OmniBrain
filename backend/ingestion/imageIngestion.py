import os
import warnings
warnings.filterwarnings('ignore')

import easyocr
from langchain_core.documents import Document

from dotenv import load_dotenv

load_dotenv()

# Loading
def loadImageDocuments(document_path):

    if not os.path.exists(document_path):
        raise FileNotFoundError(f"Path not found in the System: {document_path}")
    reader = easyocr.Reader(['en'], gpu=False)
    documents = []
    for file in os.listdir(document_path):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):

            image_path = os.path.join(document_path, file)
            result = reader.readtext(image_path, detail=0)
            text = "\n".join(result)
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": image_path}
                )
            )
    if not documents:
        raise FileNotFoundError("No image files found in the directory")

    return documents