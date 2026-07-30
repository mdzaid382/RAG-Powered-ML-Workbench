from langchain_google_genai import GoogleGenerativeAIEmbeddings

from Logger import logging
from dotenv import load_dotenv

load_dotenv()

class EmbeddingModel:
    """
    Loads the embedding model used throughout the RAG pipeline.
    """

    def __init__(
        self,
        model_name: str = "models/gemini-embedding-001",
    ):
        try:
            logging.info(
                f"Initializing embedding model: {model_name}"
            )

            self.model_name = model_name

            self.embedding_model = GoogleGenerativeAIEmbeddings(
                model=self.model_name
            )

            logging.info(
                "Embedding model initialized successfully."
            )

        except Exception:
            logging.exception(
                "Failed to initialize embedding model."
            )
            raise

    def get_embeddings(self):
        """
        Returns the initialized embedding model.
        """
        return self.embedding_model