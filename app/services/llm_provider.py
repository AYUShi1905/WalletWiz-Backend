import os
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import settings

# LangChain's Google GenAI integration expects the Google API key to be set 
# in the environment as GOOGLE_API_KEY. We bind it here from our settings.
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY

def get_llm(temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    """
    Factory function that instantiates and returns a LangChain ChatGoogleGenerativeAI 
    model using the verified gemini-2.5-flash model.
    
    A temperature of 0.0 is used by default for precise extraction and deterministic 
    query tool executions.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=temperature,
        max_output_tokens=1024
    )
