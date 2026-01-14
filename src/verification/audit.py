# src/verification/audit.py

import numpy as np
import logging
from sentence_transformers import SentenceTransformer, util
import re

logger = logging.getLogger(__name__)

class CoverageAuditor:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        """
        Initializes the embedding model for coverage audit.
        'all-MiniLM-L6-v2' is fast and efficient for local use.
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)

    def split_sentences(self, text):
        """
        Splits text into individual sentences for auditing.
        """
        # Basic sentence splitting heuristic
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]

    def audit_coverage(self, source_text, flashcards, threshold=0.85):
        """
        Implements the 'Reverse RAG' algorithm from Section 6.1.
        Returns a list of sentences that are NOT covered.
        """
        source_sentences = self.split_sentences(source_text)
        if not source_sentences:
            return [], 1.0

        # Encode source sentences
        source_embeddings = self.model.encode(source_sentences, convert_to_tensor=True)
        
        # Encode flashcard answers (the 'back' of the card)
        card_answers = [card['back'] for card in flashcards]
        if not card_answers:
            return source_sentences, 0.0
            
        card_embeddings = self.model.encode(card_answers, convert_to_tensor=True)

        # Compute cosine similarity matrix
        # (num_source_sentences, num_cards)
        cosine_scores = util.cos_sim(source_embeddings, card_embeddings)

        # For each source sentence, find the max similarity with any card
        max_scores = cosine_scores.max(dim=1).values
        
        uncovered = []
        scores = []
        for i, score in enumerate(max_scores):
            score_val = score.item()
            scores.append(score_val)
            if score_val < threshold:
                uncovered.append(source_sentences[i])

        coverage_score = np.mean(scores)
        return uncovered, coverage_score

class FactChecker:
    def __init__(self, model_name="cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        Initializes the Cross-Encoder for factual consistency checking.
        """
        from sentence_transformers import CrossEncoder
        logger.info(f"Loading Cross-Encoder: {model_name}")
        self.model = CrossEncoder(model_name)

    def verify_consistency(self, flashcard):
        """
        Verifies if the flashcard is supported by its source_quote.
        """
        question = flashcard.get('front', '')
        answer = flashcard.get('back', '')
        quote = flashcard.get('source_quote', '')
        
        if not quote:
            return 0.5 # Unknown
            
        # Cross-encoders take pairs: (Context/Quote, Hypothesis/Answer)
        score = self.model.predict([quote, f"{question} {answer}"])
        return score
