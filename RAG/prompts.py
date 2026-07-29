from langchain_core.prompts import ChatPromptTemplate

from Logger import logging


class PromptBuilder:
    """
    Creates the prompt used by the AI Assistant.
    """

    @staticmethod
    def get_prompt():

        try:

            logging.info(
                "Creating AI assistant prompt template."
            )

            prompt = ChatPromptTemplate.from_messages(

                [

                    (
                        "system",

                        """
                        You are an AI Machine Learning Assistant.
                        
                        You help users understand their machine learning workflow.
                        
                        The retrieved context may include:
                        
                        • Dataset profiling report
                        • Data cleaning report
                        • Model training report
                        • Evaluation report
                        
                        Instructions:
                        
                        1. Answer ONLY using the retrieved context.
                        
                        2. If the answer is not available in the context,
                        reply:
                        
                        "I couldn't find that information in the current project."
                        
                        3. Explain concepts clearly.
                        
                        4. When comparing models,
                        mention important metrics like:
                        
                        - Accuracy
                        - Precision
                        - Recall
                        - F1 Score
                        - ROC AUC
                        
                        5. If the user asks for recommendations,
                        give practical suggestions based on the retrieved reports.
                        
                        6. Never invent values.
                        
                        Retrieved Context:
                        
                        {context}
                        
                        """
                    ),

                    (
                        "human",

                        "{question}"

                    )

                ]

            )

            logging.info(
                "AI assistant prompt created successfully."
            )

            return prompt


        except Exception:

            logging.exception(
                "Failed to create AI assistant prompt."
            )

            raise