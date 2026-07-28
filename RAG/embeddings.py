from langchain_google_genai import GoogleGenerativeAIEmbeddings


class EmbeddingModel:
    """
    Loads the embedding model used throughout the RAG pipeline.
    """

    def __init__(
        self,
        model_name: str = "models/gemini-embedding-001"
    ):
        self.model_name = model_name

        self.embedding_model = GoogleGenerativeAIEmbeddings(
            model=self.model_name
        )

    def get_embeddings(self):
        """
        Returns the initialized embedding model.
        """
        return self.embedding_model