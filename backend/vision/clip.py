from pathlib import Path
from typing import List, Dict

from PIL import Image
import torch
from transformers import CLIPModel, CLIPProcessor


MODEL_NAME = "openai/clip-vit-base-patch32"

model = CLIPModel.from_pretrained(MODEL_NAME)
processor = CLIPProcessor.from_pretrained(MODEL_NAME)

model.eval()


def get_image_embedding(image_path: str) -> List[float]:

    image = Image.open(image_path).convert("RGB")

    inputs = processor(
        images=image,
        return_tensors="pt"
    )

    with torch.no_grad():
        outputs = model.vision_model(
            pixel_values=inputs["pixel_values"]
        )

        pooled_output = outputs.pooler_output

        embedding = model.visual_projection(
            pooled_output
        )

    embedding = embedding / embedding.norm(
        dim=-1,
        keepdim=True
    )

    return embedding.squeeze().tolist()


def get_text_embedding(text: str) -> List[float]:

    inputs = processor(
        text=[text],
        return_tensors="pt",
        padding=True
    )

    with torch.no_grad():

        outputs = model.text_model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"]
        )

        pooled_output = outputs.pooler_output

        embedding = model.text_projection(
            pooled_output
        )

    embedding = embedding / embedding.norm(
        dim=-1,
        keepdim=True
    )

    return embedding.squeeze().tolist()