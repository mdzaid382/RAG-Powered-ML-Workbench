import json

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from RAG.vectorstore import VectorStoreManager
from Logger import logging


class RAGIngestor:
    """
    Converts JSON reports into LangChain Documents
    and stores them inside FAISS.
    """

    def __init__(self):

        try:
            logging.info(
                "Initializing RAGIngestor."
            )

            self.vector_manager = VectorStoreManager()

            logging.info(
                "RAGIngestor initialized successfully."
            )

        except Exception:
            logging.exception(
                "Failed to initialize RAGIngestor."
            )
            raise


    # Load JSON Report

    def load_json(self, json_path: str):

        try:
            logging.info(
                f"Loading JSON report from '{json_path}'."
            )

            with open(
                json_path,
                "r",
                encoding="utf-8"
            ) as file:

                report = json.load(file)

            logging.info(
                "JSON report loaded successfully."
            )

            return report

        except Exception:
            logging.exception(
                f"Failed to load JSON report: '{json_path}'."
            )
            raise


    # Convert Dictionary to Text

    def dict_to_text(self, data):

        return json.dumps(
            data,
            indent=4
        )


    # Create Document

    def create_document(
        self,
        report,
        report_type
    ):

        text = self.dict_to_text(report)

        document = Document(

            page_content=text,
            metadata={

                "report_type": report_type,
                "dataset_name":
                report.get(
                    "dataset_name",
                    "Unknown"
                )

            }
        )

        return document


    # Add Report to Vector Store

    def add_report(
        self,
        json_path,
        report_type
    ):

        try:
            logging.info(
                f"Adding '{report_type}' report to vector store."
            )

            report = self.load_json(
                json_path
            )

            document = self.create_document(
                report,
                report_type
            )
            vectorstore = self.vector_manager.load()

            vectorstore.add_documents(
                [document]
            )

            self.vector_manager.save(
                vectorstore
            )

            logging.info(
                f"'{report_type}' report added successfully."
            )

        except Exception:
            logging.exception(
                f"Failed to add '{report_type}' report."
            )
            raise


    # Add User PDF

    def add_pdf(
        self,
        documents
    ):

        try:
            logging.info(
                "Chunking uploaded PDF."
            )

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )

            chunks = splitter.split_documents(
                documents
            )

            logging.info(
                f"Generated {len(chunks)} chunks."
            )

            vectorstore = self.vector_manager.load()
 
            vectorstore.add_documents(
                chunks
            )

            self.vector_manager.save(
                self.vectorstore
            )

            logging.info(
                "PDF added to vector store successfully."
            )

            return len(chunks)

        except Exception:
            logging.exception(
                "Failed to ingest uploaded PDF."
            )
            raise