# AVANZAMENTO 5

import os

from chromadb.api.types import EmbeddingFunction
import ollama

from .config import Config


# class CustomEmbeddingFunction(EmbeddingFunction):
#     """
#     Genera embedding utilizzando un modello locale tramite Ollama.
#     """
#
#     def __init__(self):
#         self.model_name = Config.EMBEDDING_MODEL
#         print(f"Usando modello Ollama per gli embedding: {self.model_name}")
#
#     def name(self) -> str:
#         return "ollama"
#
#     def __call__(self, texts):
#         """
#         Genera un embedding per ogni testo ricevuto.
#         """
#         embeddings = []
#
#         for text in texts:
#             response = ollama.embed(
#                 model=self.model_name,
#                 input=text
#             )
#             embeddings.append(response.embeddings[0])
#
#         return embeddings

# AVANZAMENTO 6.1

class CustomEmbeddingFunction(EmbeddingFunction):
    """
    Genera embedding utilizzando diversi provider:
    - Ollama
    - SentenceTransformer
    - OpenAI
    """

    def __init__(self):
        self.provider = Config.EMBEDDING_PROVIDER
        self.model_name = getattr(
            Config, "MODEL_NAME", Config.EMBEDDING_MODEL
        )

        if self.provider == "ollama":
            print(f"Usando modello Ollama: {self.model_name}")

        elif self.provider == "local":
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]
            except ImportError as exc:
                raise ImportError(
                    "Il provider 'local' richiede il pacchetto "
                    "'sentence-transformers'. Installa con: "
                    "pip install sentence-transformers"
                ) from exc

            self.model_path = Config.MODEL_PATH

            if os.path.exists(self.model_path):
                print(f"Caricamento modello locale: {self.model_path}")
                self.embedding_function = SentenceTransformer(
                    self.model_path
                )
            else:
                print(f"Scaricamento modello: {self.model_name}")
                self.embedding_function = SentenceTransformer(
                    self.model_name
                )

                os.makedirs(os.path.dirname(self.model_path) or ".", exist_ok=True)
                self.embedding_function.save(self.model_path)

        elif self.provider == "openai":
            from openai import OpenAI

            print(f"Usando OpenAI Embeddings: {self.model_name}")

            self.client = OpenAI(
                api_key=Config.OPENAI_EMBEDDINGS_KEY
            )

        else:
            raise ValueError(
                f"Provider di embedding non supportato: {self.provider}"
            )

    def name(self) -> str:
        return self.provider

    def __call__(self, texts):
        """
        Genera gli embedding in base al provider selezionato.
        """

        if self.provider == "ollama":
            embeddings = []

            for text in texts:
                response = ollama.embed(
                    model=self.model_name,
                    input=text
                )
                embeddings.append(response.embeddings[0])

            return embeddings

        elif self.provider == "local":
            return self.embedding_function.encode(texts).tolist()

        elif self.provider == "openai":
            response = self.client.embeddings.create(
                model=self.model_name,
                input=texts
            )

            return [item.embedding for item in response.data]