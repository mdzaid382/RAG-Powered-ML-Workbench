from RAG.vectorstore import VectorStoreManager
from Logger import logging


class RAGRetriever:
    """
    Retrieves relevant documents from the FAISS vector store.
    """

    def __init__(self):

        try:
            logging.info(
                "Initializing RAGRetriever."
            )

            self.vectorstore = (
                VectorStoreManager().load()
            )

            logging.info(
                "RAGRetriever initialized successfully."
            )

        except Exception:
            logging.exception(
                "Failed to initialize RAGRetriever."
            )
            raise


    # Create Retriever

    def get_retriever(
        self,
        k: int = 4
    ):

        try:
            logging.info(
                f"Creating retriever with k={k}."
            )

            retriever = self.vectorstore.as_retriever(

                search_type="similarity",

                search_kwargs={
                    "k": k
                }

            )

            logging.info(
                "Retriever created successfully."
            )

            return retriever

        except Exception:
            logging.exception(
                "Failed to create retriever."
            )
            raise


    # Retrieve Documents

    def retrieve(
        self,
        question: str,
        k: int = 4
    ):

        try:
            logging.info(
                f"Retrieving documents for query: '{question}'"
            )

            retriever = self.get_retriever(k)

            documents = retriever.invoke(question)

            logging.info(
                f"Retrieved {len(documents)} document(s)."
            )

            return documents

        except Exception:
            logging.exception(
                "Failed to retrieve documents."
            )
            raise