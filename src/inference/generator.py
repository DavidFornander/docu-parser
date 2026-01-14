# src/inference/generator.py

import json
import logging
from vllm import LLM, SamplingParams
from inference.prompts import SYSTEM_PROMPT, EXTRACTION_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

class FlashcardGenerator:
    def __init__(self, model_name="meta-llama/Meta-Llama-3-8B-Instruct", gpu_memory_utilization=0.7):
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
        # Combining system and user prompt for Llama-3 chat format
        # This format might change slightly depending on the model used.
        return f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{SYSTEM_PROMPT}<|eot_id|>" \
               f"<|start_header_id|>user<|end_header_id|>\n\n{EXTRACTION_PROMPT_TEMPLATE.format(text=text)}<|eot_id|>" \
               f"<|start_header_id|>assistant<|end_header_id|>\n\n"

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
