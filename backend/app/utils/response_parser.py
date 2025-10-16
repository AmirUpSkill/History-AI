import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ResponseParseError(Exception):
    """Exception raised when response parsing fails."""
    pass

def parse_json_response(response_text: str) -> Dict[str, Any]:
    """
    Parse JSON from Gemini response, handling markdown formatting.
    
    Gemini sometimes wraps JSON in markdown code blocks (```json...```).
    This function cleanly extracts and parses the JSON.
    
    Args:
        response_text: The raw response text from Gemini
    
    Returns:
        Parsed JSON as dictionary
    
    Raises:
        ResponseParseError: If JSON parsing fails
    """
    try:
        response_text = response_text.strip()
        
        # --- Remove markdown code blocks if present ----
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        elif response_text.startswith("```"):
            response_text = response_text[3:]
        
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        parsed = json.loads(response_text)
        return parsed
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}\nResponse: {response_text}")
        raise ResponseParseError(f"Failed to parse Gemini response as JSON: {e}")
    except Exception as e:
        logger.error(f"Unexpected error parsing response: {e}")
        raise ResponseParseError(f"Unexpected error parsing response: {e}")