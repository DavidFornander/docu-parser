# src/inference/generator.py

import json
import logging
from vllm import LLM, SamplingParams
from inference.prompts import SYSTEM_PROMPT, EXTRACTION_PROMPT_TEMPLATE
from utils.logger import setup_logger

logger = setup_logger("FlashcardGenerator")

class FlashcardGenerator:
    def __init__(self, model_name="Qwen/Qwen2.5-0.5B-Instruct", gpu_memory_utilization=0.7):
        # Previous high-quality model: casperhansen/llama-3-8b-instruct-awq
        """
        Initializes the vLLM engine.
        model_name: Path or HuggingFace ID of the model.
        gpu_memory_utilization: Fraction of GPU memory to reserve for vLLM. 
                                0.7 leaves room for embedding models.
        """
        logger.info(f"Loading vLLM model: {model_name}")
        # Note: This requires the model to be downloaded.
        # For a 12GB GPU, we might need quantization (e.g., use a -AWQ version)
        self.llm = LLM(
            model=model_name,
            gpu_memory_utilization=gpu_memory_utilization,
            trust_remote_code=True,
            enforce_eager=True,
            # max_model_len=8192 # Adjust based on needs
        )
        self.sampling_params = SamplingParams(
            temperature=0.1, # Low temperature for factual extraction
            top_p=0.95,
            max_tokens=2048,
            repetition_penalty=1.05
        )

    def generate_cards(self, text):
        """
        Generates flashcards for a given text chunk.
        """
        prompt = self.build_prompt(text)
        
        # vLLM supports batching, but for a single chunk we pass a list of one
        outputs = self.llm.generate([prompt], self.sampling_params)
        
        generated_text = outputs[0].outputs[0].text
        
        return self.parse_json_output(generated_text)

    def build_prompt(self, text):
        # Generic Chat Format (works reasonably well for Qwen, Mistral, Llama)
        # For production, consider using the model's specific tokenizer.apply_chat_template()
        return f"System: {SYSTEM_PROMPT}\n\n" \
               f"User: {EXTRACTION_PROMPT_TEMPLATE.format(text=text)}\n\n" \
               f"Assistant:\n"

    def parse_json_output(self, text):
        """
        Extracts JSON from the model's response.
        """
        try:
            # Look for the JSON block
            json_match = text[text.find("{"):text.rfind("}")+1]
            return json.loads(json_match)
        except Exception as e:
            logger.error(f"Failed to parse JSON from output: {e}")
            logger.debug(f"Raw output: {text}")
            return {"flashcards": [], "error": "JSON parsing failed"}

if __name__ == "__main__":
    # Test script (requires model weights)
    # gen = FlashcardGenerator("casperhansen/llama-3-8b-instruct-awq")
    # print(gen.generate_cards("The mitochondria is the powerhouse of the cell."))
    pass
