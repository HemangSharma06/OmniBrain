from PIL import Image
from langchain_core.messages import HumanMessage
from backend.llm.llm import vision_llm
import time

def vision_agent(state: dict) -> dict:
    print("\n[Vision Agent]: Analyzing images using Vision-Language Model...")
    start = time.time()
    user_query = state.get("query", "").strip()
    image_paths = state.get("image_paths", [])

    if not image_paths:
        raise ValueError("No image_paths found in state.")

    analyses = []

    for image_path in image_paths:

        try:
            image = Image.open(image_path)

            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": user_query
                    },
                    {
                        "type": "image",
                        "image": image
                    }
                ]
            )

            response = vision_llm.invoke([message])

            if hasattr(response, "content"):

                if isinstance(response.content, list):

                    text = []

                    for block in response.content:

                        if (
                            isinstance(block, dict)
                            and block.get("type") == "text"
                        ):
                            text.append(block["text"])

                    result = "\n".join(text).strip()

                else:
                    result = str(response.content).strip()

            else:
                result = str(response)

            analyses.append(
                f"Image: {image_path}\n{result}"
            )

        except Exception as e:
            analyses.append(
                f"Image: {image_path}\nError: {str(e)}"
            )

    print(f"[Vision Agent]: Analyzed {len(image_paths)} image(s).")
    
    print(f"\n|---- Time Taken = {time.time()-start : .2f} ----|")
    return {
        "vision_context": analyses
    }