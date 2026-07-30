from uuid import uuid4

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from Logger import logging
from RAG.memory import ChatMemory
from RAG.prompts import PromptBuilder
from RAG.retriever import RAGRetriever
from RAG.vectorstore import VectorStoreManager


class ChatService:
    """
    Handles the complete RAG conversation pipeline.

    Flow

    User Question
          │
          ▼
    Retrieve Documents
          │
          ▼
    Build Prompt
          │
          ▼
    Gemini
          │
          ▼
    Save Chat Memory
          │
          ▼
        Response
    """

    def __init__(self):

        try:

            logging.info(
                "Initializing ChatService."
            )

            self.memory = ChatMemory()

            self.retriever = RAGRetriever()

            self.prompt = PromptBuilder.get_prompt()

            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0
            )

            self.chain = (
                self.prompt
                | self.llm
                | StrOutputParser()
            )

            logging.info(
                "ChatService initialized successfully."
            )

        except Exception:

            logging.exception(
                "Failed to initialize ChatService."
            )

            raise
    

    
    def new_session(self):
    
        try:
    
            logging.info(
                "Starting a new project."
            )
    
            # Remove previous project's vectors
            VectorStoreManager().reset()
    
            # Remove every previous chat session
            self.memory.clear_all()
    
            session_id = str(uuid4())
    
            logging.info(
                f"New session created: {session_id}"
            )
    
            return session_id
    
        except Exception:
    
            logging.exception(
                "Failed creating new session."
            )
    
            raise
        #################################################################
    
    def ask(
        self,
    session_id: str,
    question: str
    ):

        try:

            logging.info(
                f"Question received from session {session_id}"
            )

            documents = self.retriever.retrieve(
                question=question,
                k=4
            )
            
            context = "\n\n".join(
            
                f"""
            Report Type: {doc.metadata.get("report_type", "Unknown")}
            Dataset Name: {doc.metadata.get("dataset_name", "Unknown")}
            
            Report Content:
            
            {doc.page_content}
            """
            
                for doc in documents
            
            )
            
            
            history = self.memory.get_messages(
                session_id
            )

            history_text = ""

            if history:

                history_text = "\n".join(

                    f"{type(msg).__name__}: {msg.content}"

                    for msg in history

                )

            response = self.chain.invoke(

                {

                    "context":
                        f"""
Previous Conversation

{history_text}

Retrieved Context

{context}
                        """,

                    "question": question

                }

            )

            self.memory.add_user_message(
                session_id,
                question
            )

            self.memory.add_ai_message(
                session_id,
                response
            )

            logging.info(
                "Answer generated successfully."
            )

            return {
                "answer": response,
            }

        except Exception:

            logging.exception(
                "Chat failed."
            )

            raise

    #################################################################

    def clear_session(
        self,
        session_id: str
    ):

        try:

            logging.info(
                f"Clearing session {session_id}"
            )

            self.memory.clear(session_id)

            VectorStoreManager().reset()

            logging.info(
                "Session cleared."
            )

        except Exception:

            logging.exception(
                "Failed clearing session."
            )

            raise