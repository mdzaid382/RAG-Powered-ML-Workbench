from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from Logger import logging


class ChatMemory:
    """
    Manages conversation history for each user session.
    """

    def __init__(self):

        try:
            self.sessions = {}

            logging.info(
                "ChatMemory initialized successfully."
            )

        except Exception:
            logging.exception(
                "Failed to initialize ChatMemory."
            )
            raise


    # Get Session History

    def get_session(
        self,
        session_id: str
    ):

        try:

            if session_id not in self.sessions:

                logging.info(
                    f"Creating new chat session: {session_id}"
                )

                self.sessions[session_id] = (
                    InMemoryChatMessageHistory()
                )

            return self.sessions[session_id]

        except Exception:
            logging.exception(
                f"Failed to get session: {session_id}"
            )
            raise


    # Add User Message

    def add_user_message(
        self,
        session_id: str,
        message: str
    ):

        try:

            history = self.get_session(
                session_id
            )

            history.add_message(
                HumanMessage(
                    content=message
                )
            )

            logging.info(
                f"User message added to session: {session_id}"
            )

        except Exception:
            logging.exception(
                f"Failed to add user message for session: {session_id}"
            )
            raise


    # Add AI Message

    def add_ai_message(
        self,
        session_id: str,
        message: str
    ):

        try:

            history = self.get_session(
                session_id
            )

            history.add_message(
                AIMessage(
                    content=message
                )
            )

            logging.info(
                f"AI message added to session: {session_id}"
            )

        except Exception:
            logging.exception(
                f"Failed to add AI message for session: {session_id}"
            )
            raise


    # Get Messages

    def get_messages(
        self,
        session_id: str
    ):

        try:

            messages = (
                self.get_session(session_id)
                .messages
            )

            logging.info(
                f"Retrieved {len(messages)} messages from session: {session_id}"
            )

            return messages

        except Exception:
            logging.exception(
                f"Failed to retrieve messages from session: {session_id}"
            )
            raise


    # Clear Chat Memory

    def clear_all(
        self,
    ):

        """
        Clears chat memory.
        """

        try:

            total_sessions = len(
                self.sessions
            )
            self.sessions.clear()
            logging.info(
                f"Cleared all chat sessions. Removed {total_sessions} session(s)."
            )

        except Exception:

            logging.exception(
                "Failed to clear chat memory."
            )
            raise