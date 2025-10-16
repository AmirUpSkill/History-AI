import logging 
from typing import Optional , Tuple , Dict , Any 
from app.utils import (
    build_card_generation_prompt,
    build_copilot_prompt,
    build_bias_judge_prompt,
    GeminiClient,
    parse_json_response,
    validate_card_structure,
    validate_bias_response,
    ResponseParseError,
    CardValidationError,
    BiasValidationError,
)
# --- Set Up Logger ---
logger = logging.getLogger(__name__)

class AIServiceError(Exception):
    """
        Custom Exeption for AI Service errors . 
    """
    pass 
class AIService:
    """
        Service class for handling AI interactions with Gemini API . 
    """
    def __init__(self, api_key:str):
        """
            Initialize AI Service 
        """
        try:
            self.gemini_client = GeminiClient(api_key)
            logger.info("AI Service initialized successfully")
        except Exception as e:
            raise AIServiceError(f"Failed to initialize AI Service: {e}")
    # --- The Method For AI Card Generation ---
    def generate_card(
        self,
        title:str ,
        system_prompt: str,
        topics_to_cover: str,
        context_text: Optional[str] = None

    ) -> Dict[str , Any]:
        """
            Generate a new historical event card using AI . 
        """
        try:
            # --- Build prompt ---
            prompt = build_card_generation_prompt(
                title=title,
                system_prompt=system_prompt,
                topics_to_cover=topics_to_cover,
                context_text=context_text or "",
                )
            # --- Call API --- 
            response = self.gemini_client.call_with_retry(prompt)
            # --- Parse response ---
            card_data = parse_json_response(response)
            # --- Validate structure --- 
            validate_card_structure(card_data)
            logger.info(f"Card generated: {card_data.get('title')}")
            return card_data
        except (ResponseParseError, CardValidationError) as e:
            logger.error(f"Card generation validation error: {e}")
            raise AIServiceError(f"Card generation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in card generation: {e}")
            raise AIServiceError(f"Unexpected error: {e}")
    # --- Method for AI Copilot Agent --- 
    def copilot_answer(self, question: str , context: str) -> str:
        """
            Generate a Copilot answer 
        """
        try:
            if not question or not context:
                raise AIServiceError("Question and context are required")
            prompt = build_copilot_prompt(question=question, context=context)
            response = self.gemini_client.call_with_retry(prompt)
            
            logger.info("Copilot answer generated")
            return response.strip()
        except Exception as e:
            logger.error(f"Copilot answer error: {e}")
            raise AIServiceError(f"Failed to generate answer: {e}")
    # --- Method for AI Judge ---
    def judge_bias(self,content:str) -> Tuple[float,str]:
        try:
            if not content or len(content) < 50:
                raise AIServiceError("Content must be at least 50 characters")
            
            prompt = build_bias_judge_prompt(content=content)
            response = self.gemini_client.call_with_retry(prompt)
            bias_data = parse_json_response(response)
            
            bias_score, explanation = validate_bias_response(bias_data)
            
            logger.info(f"Bias analysis complete: score={bias_score}")
            return bias_score, explanation
            
        except (ResponseParseError, BiasValidationError) as e:
            logger.error(f"Bias judgment validation error: {e}")
            raise AIServiceError(f"Bias judgment failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in bias judgment: {e}")
            raise AIServiceError(f"Unexpected error: {e}")
    

