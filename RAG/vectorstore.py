from pathlib import Path
import shutil

from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
import faiss

from RAG.embeddings import EmbeddingModel
from Logger import logging


class VectorStoreManager:
    """
    Manages the FAISS vector database.
    """

    def __init__(self, vectorstore_path: str = "vectorstore"):

        try:
            logging.info(
                f"Initializing VectorStoreManager at '{vectorstore_path}'."
            )

            self.vectorstore_path = Path(vectorstore_path)

            self.vectorstore_path.mkdir(
                parents=True,
                exist_ok=True
            )

            self.embedding_model = (
                EmbeddingModel().get_embeddings()
            )

            logging.info(
                "VectorStoreManager initialized successfully."
            )

        except Exception:
            logging.exception(
                "Failed to initialize VectorStoreManager."
            )
            raise

  
    # Create Empty VectorStore

    def create(self):
    
        try:
    
            logging.info(
                "Creating new empty FAISS vector store."
            )
    
            dimension = len(
                self.embedding_model.embed_query("test")
            )
    
            index = faiss.IndexFlatL2(dimension)
    
            vectorstore = FAISS(
                embedding_function=self.embedding_model,
                index=index,
                docstore=InMemoryDocstore(),
                index_to_docstore_id={}
            )
    
            logging.info(
                "Empty FAISS vector store created successfully."
            )
    
            return vectorstore
    
        except Exception:
    
            logging.exception(
                "Failed to create FAISS vector store."
            )
    
            raise

    # Load Existing VectorStore

    def load(self):

        try:
            index_file = (
                self.vectorstore_path / "index.faiss"
            )

            if not index_file.exists():

                logging.info(
                    "Vector store not found. Creating a new one."
                )

                vectorstore = self.create()

                self.save(vectorstore)

                return vectorstore

            logging.info(
                "Loading existing FAISS vector store."
            )

            vectorstore = FAISS.load_local(
                folder_path=str(self.vectorstore_path),
                embeddings=self.embedding_model,
                allow_dangerous_deserialization=True
            )

            logging.info(
                "FAISS vector store loaded successfully."
            )

            return vectorstore

        except Exception:
            logging.exception(
                "Failed to load FAISS vector store."
            )
            raise


    # Save VectorStore

    def save(self, vectorstore):

        try:
            logging.info(
                "Saving FAISS vector store."
            )

            vectorstore.save_local(
                folder_path=str(self.vectorstore_path)
            )

            logging.info(
                "FAISS vector store saved successfully."
            )

        except Exception:
            logging.exception(
                "Failed to save FAISS vector store."
            )
            raise

    #reset vectorstore

    def reset(self):
   
           try:
               logging.info(
                   "Resetting FAISS vector store."
               )
   
               if self.vectorstore_path.exists():
   
                   shutil.rmtree(
                       self.vectorstore_path
                   )
   
                   logging.info(
                       "Existing vector store deleted."
                   )
   
               self.vectorstore_path.mkdir(
                   parents=True,
                   exist_ok=True
               )
   
               vectorstore = self.create()
   
               self.save(vectorstore)
   
               logging.info(
                   "New empty FAISS vector store created successfully."
               )
   
               return vectorstore
   
           except Exception:
               logging.exception(
                   "Failed to reset FAISS vector store."
               )
               raise