import re
import uuid
import json
from pathlib import Path

class SemanticChunker:
    def __init__(self, chunk_size=2500, chunk_overlap=300):
        """
        Initializes the chunker.
        chunk_size: Target size of each chunk in characters (approximate to tokens for now).
        chunk_overlap: Number of characters to overlap between chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text, metadata=None):
        """
        Splits text into chunks using recursive character splitting logic.
        Tries to split on paragraphs, then sentences, then spaces.
        """
        if metadata is None:
            metadata = {}

        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            # End is start + chunk_size
            end = min(start + self.chunk_size, text_len)
            
            # If not at the end of the text, try to find a good breaking point
            if end < text_len:
                # Try to find last paragraph break (\n\n)
                last_para = text.rfind("\n\n", start, end)
                if last_para != -1 and last_para > start + (self.chunk_size // 2):
                    end = last_para + 2
                else:
                    # Try to find last sentence break (. )
                    last_sent = text.rfind(". ", start, end)
                    if last_sent != -1 and last_sent > start + (self.chunk_size // 2):
                        end = last_sent + 2
                    else:
                        # Try to find last space
                        last_space = text.rfind(" ", start, end)
                        if last_space != -1 and last_space > start + (self.chunk_size // 2):
                            end = last_space + 1

            chunk_content = text[start:end].strip()
            
            # Inject metadata as per plan 3.3
            header_context = self._extract_header_context(text, start)
            formatted_metadata = {**metadata, "header_context": header_context}
            
            # Prepend metadata to text as per plan 3.3
            # Metadata Injection: Every chunk is prepended with its hierarchical context
            context_string = f"Context: {header_context}\n\n" if header_context else ""
            final_content = context_string + chunk_content

            chunks.append({
                "chunk_id": str(uuid.uuid4()),
                "content": final_content,
                "metadata": formatted_metadata
            })

            # Move start forward, accounting for overlap
            start = end - self.chunk_overlap
            if start < 0: start = 0
            if start >= end: # Prevent infinite loop if overlap >= size
                start = end

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
