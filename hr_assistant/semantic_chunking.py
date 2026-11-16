# AVANZAMENTO 5

import re
import numpy as np

from .custom_embedding import CustomEmbeddingFunction


class SemanticChunking:

    def __init__(self, breakpoint_percentile=70, buffer_size=1):
        self.embedding_function = CustomEmbeddingFunction()
        self.breakpoint_percentile = breakpoint_percentile
        self.buffer_size = buffer_size

    def _split_into_sentences(self, text):
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())

        if len(sentences) == 1 and len(text) > 100:
            delimiters = r"([.!?\n;:])"
            parts = re.split(delimiters, text.strip())
            sentences = []

            for i in range(0, len(parts) - 1, 2):
                if parts[i].strip():  
                    sentences.append(parts[i].strip() + parts[i + 1])

            if len(sentences) == 1:
                sentences = [s.strip() + "," for s in text.split(",") if s.strip()]

                if sentences:  
                    sentences[-1] = sentences[-1][:-1] + "."

        sentences = [s for s in sentences if s.strip()]

        if not sentences:
            sentences = [text + "."]

        return sentences
    
    def _process_sentences(self, text):
        """Divide il testo in frasi e aggiunge il contesto circostante."""

        raw_sentences = self._split_into_sentences(text)
        sentences = [
            {"sentence": sentence, "index": i}
            for i, sentence in enumerate(raw_sentences)
            if sentence.strip()
        ]

        for i, current in enumerate(sentences):
            context_range = range(
                max(0, i - self.buffer_size),
                min(len(sentences), i + self.buffer_size + 1),
            )

            current["combined_sentence"] = " ".join(
                sentences[j]["sentence"] for j in context_range
            )

        return sentences

    def _calculate_distances(self, sentences):
        """Calcola la distanza semantica tra frasi consecutive."""

        embeddings = self.embedding_function(
            [sentence["combined_sentence"] for sentence in sentences]
        )

        distances = []

        for i in range(len(embeddings) - 1):
            first = np.asarray(embeddings[i])
            second = np.asarray(embeddings[i + 1])
            denominator = np.linalg.norm(first) * np.linalg.norm(second)
            similarity = np.dot(first, second) / denominator if denominator else 0.0

            distances.append(1 - similarity)

        return distances

    def chunk_text(self, text):
        """Crea blocchi in base ai cambiamenti semantici."""

        if not text or not text.strip():
            return []

        sentences = self._process_sentences(text)

        if len(sentences) <= 1:
            return [text.strip()]

        distances = self._calculate_distances(sentences)

        threshold = np.percentile(
            distances,
            self.breakpoint_percentile
        )

        split_points = [
            i for i, distance in enumerate(distances)
            if distance > threshold
        ]

        chunks = []
        start = 0

        for point in split_points + [len(sentences) - 1]:
            chunk = " ".join(
                sentence["sentence"]
                for sentence in sentences[start:point + 1]
            )

            if chunk.strip():
                chunks.append(chunk.strip())

            start = point + 1

        return chunks
