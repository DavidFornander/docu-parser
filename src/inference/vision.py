import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import logging

logger = logging.getLogger(__name__)

class ImageDescriber:
    def __init__(self, model_id="vikhyatk/moondream2", device="cuda"):
        logger.info(f"Loading VLM: {model_id} on {device}...")
        self.device = device
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, 
            trust_remote_code=True,
            torch_dtype=torch.float16
        ).to(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)

    def describe(self, image_path):
        try:
            image = Image.open(image_path)
            enc_image = self.model.encode_image(image)
            # Prompt optimized for educational diagrams
            prompt = "Describe this educational diagram or image in detail. Focus on labels, arrows, and relationships."
            answer = self.model.answer_question(enc_image, prompt, self.tokenizer)
            return answer
        except Exception as e:
            logger.error(f"Failed to describe image {image_path}: {e}")
            return "Image processing failed."

if __name__ == "__main__":
    # Test
    vlm = ImageDescriber()
    # print(vlm.describe("assets/test.jpg"))
