import logging
import time
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

class GeminiClientError(Exception):
    """Exception raised when Gemini API communication fails."""
    pass

class GeminiClient:
    """
    Wrapper around Gemini API client with retry logic.
    
    Handles:
    - API initialization and configuration
    - Exponential backoff retries
    - Error handling and logging
    """
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: The Gemini API key
            model_name: The model to use (default: gemini-2.5-flash)
        
        Raises:
            GeminiClientError: If API key is not provided
        """
        if not api_key:
            raise GeminiClientError("GEMINI_API_KEY is not set")
        
        genai.configure(api_key=api_key)
        self.client = genai.Client()
        self.model_name = model_name
        self.max_retries = 3
        self.retry_delay = 1  
    
    def call_with_retry(self, prompt: str) -> str:
        """
        Call Gemini API with exponential backoff retry logic.
        
        Strategy:
        1. First attempt immediately
        2. Failed attempt: Wait 1 second, retry
        3. Failed attempt: Wait 2 seconds, retry
        4. Failed attempt: Wait 4 seconds, retry
        5. All failed: Raise error
        
        Args:
            prompt: The prompt to send to Gemini
        
        Returns:
            The response text from Gemini
        
        Raises:
            GeminiClientError: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        top_p=0.9,
                        top_k=40,
                    ),
                )
                
                if response.text:
                    logger.debug(f"Gemini API call successful on attempt {attempt + 1}")
                    return response.text
                else:
                    raise GeminiClientError("Empty response from Gemini")
                    
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Gemini API call failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                
                # --- Exponential backoff for retries ---
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
        
        raise GeminiClientError(
            f"Gemini API call failed after {self.max_retries} attempts: {last_error}"
        )
