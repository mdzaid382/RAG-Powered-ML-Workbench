from RAG.vectorstore import VectorStoreManager
from Logger import logging


class RAGRetriever:
    """
    Retrieves relevant documents from the FAISS vector store.
    """

    def __init__(self):

        logging.info(
            "Initializing RAGRetriever."
        )


    def get_retriever(
        self,
        k: int = 4
    ):

        try:

            logging.info(
                "Loading latest FAISS vector store."
            )

            vectorstore = VectorStoreManager().load()

            retriever = vectorstore.as_retriever(

                search_type="similarity",

                search_kwargs={
                    "k": k
                }

            )

            return retriever

        except Exception:

            logging.exception(
                "Failed to create retriever."
            )

            raise


    def retrieve(
        self,
        question: str,
        k: int = 4
    ):

        try:

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