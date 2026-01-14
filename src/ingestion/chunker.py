import re
import uuid
import json
from pathlib import Path
import time
from tqdm import tqdm

class SemanticChunker:
    def __init__(self, chunk_size=2500, chunk_overlap=300, timeout=10):
        """
        Initializes the chunker.
        chunk_size: Target size of each chunk in characters.
        chunk_overlap: Number of characters to overlap.
        timeout: Seconds to wait for a chunk to be created before aborting.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.timeout = timeout

    def chunk_text(self, text, metadata=None):
        if metadata is None: metadata = {}
        chunks = []
        start = 0
        text_len = len(text)
        
        pbar = tqdm(total=text_len, desc="Chunking Text", unit="chars")
        last_pos = 0
        
        last_activity = time.time()

        while start < text_len:
            # Check timeout
            if time.time() - last_activity > self.timeout:
                pbar.close()
                raise TimeoutError(f"Chunking stalled at position {start}/{text_len}")

            # End is start + chunk_size
            end = min(start + self.chunk_size, text_len)
            
            if end < text_len:
                last_para = text.rfind("\n\n", start, end)
                if last_para != -1 and last_para > start + (self.chunk_size // 2):
                    end = last_para + 2
                else:
                    last_sent = text.rfind(". ", start, end)
                    if last_sent != -1 and last_sent > start + (self.chunk_size // 2):
                        end = last_sent + 2
                    else:
                        last_space = text.rfind(" ", start, end)
                        if last_space != -1 and last_space > start + (self.chunk_size // 2):
                            end = last_space + 1

            chunk_content = text[start:end].strip()
            header_context = self._extract_header_context(text, start)
            formatted_metadata = {**metadata, "header_context": header_context}
            context_string = f"Context: {header_context}\n\n" if header_context else ""
            final_content = context_string + chunk_content

            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "content": final_content,
                "metadata": formatted_metadata
            })
            
            # Reset timeout on successful chunk
            last_activity = time.time()

            # If we reached the end of the text, stop
            if end == text_len:
                pbar.update(text_len - last_pos)
                break

            prev_start = start
            start = end - self.chunk_overlap
            if start < 0: start = 0
            if start >= end: start = end
            
            advance = start - prev_start
            if advance > 0:
                pbar.update(advance)
                last_pos = start

        pbar.update(text_len - last_pos)
        pbar.close()
        return chunks

    def _extract_header_context(self, text, current_pos):
        """
        Attempts to find the current section/header context by looking backwards.
        Simple implementation: looks for lines starting with #.
        """
        # Search backwards for headers
        lines = text[:current_pos].split("\n")
        context = []
        
        # This is a very basic heuristic for Markdown headers
        # It finds the most recent #, ##, ### etc.
        current_level = 7
        for line in reversed(lines):
            match = re.match(r"^(#+)\s+(.*)", line)
            if match:
                level = len(match.group(1))
                if level < current_level:
                    context.insert(0, match.group(2))
                    current_level = level
            if current_level == 1:
                break
                
        return " > ".join(context)

if __name__ == "__main__":
    chunker = SemanticChunker(chunk_size=500, chunk_overlap=50)
    sample_text = "# Chapter 1\n## Section 1.1\nThis is some sample text. " * 20
    chunks = chunker.chunk_text(sample_text, {"source": "test.pdf"})
    for i, c in enumerate(chunks):
        print(f"Chunk {i} (Context: {c['metadata']['header_context']}): {len(c['content'])} chars")
        # print(c['content'][:50] + "...")
