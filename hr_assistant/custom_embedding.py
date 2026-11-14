# AVANZAMENTO 5

from chromadb.api.types import EmbeddingFunction
import ollama

from .config import Config


class CustomEmbeddingFunction(EmbeddingFunction):
    """
    Genera embedding utilizzando un modello locale tramite Ollama.
    """

    def __init__(self):
        self.model_name = Config.EMBEDDING_MODEL
        print(f"Usando modello Ollama per gli embedding: {self.model_name}")

    def name(self) -> str:
        return "ollama"

    def __call__(self, texts):
        """
        Genera un embedding per ogni testo ricevuto.
        """
        embeddings = []

        for text in texts:
            response = ollama.embed(
                model=self.model_name,
                input=text
            )
            embeddings.append(response.embeddings[0])

        return embeddings
