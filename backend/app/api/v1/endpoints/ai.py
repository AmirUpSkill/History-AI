from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.ai import (
    CopilotRequest, CopilotResponse,
    BiasJudgeRequest, BiasJudgeResponse
)
from app.services.ai_service import AIService, AIServiceError
from app.dependencies import get_ai_service

# --- Get the Router Instance --- 
router = APIRouter()

@router.post(
    "/copilot",
    response_model=CopilotResponse,
    summary="AI Copilot Assistant"
)
def get_copilot_response(
    request: CopilotRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
        Provides context-aware to user questions about a specific text . 
        This is a stateless endpoint 
    """
    try:
        answer = ai_service.copilot_answer(
            question=request.question,
            context=request.context
        )
        return CopilotResponse(answer=answer)
    except AIServiceError as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate copilot answer: {e}"

        )
@router.post(
    "/bias-judge",
    response_model=BiasJudgeResponse,
    summary="AI Bias Judge"
)
def analyze_bias(
    request: BiasJudgeRequest,
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Analyzes a given text for neutrality and potential bias.
    This is a stateless endpoint.
    """
    try:
        bias_score, explanation = ai_service.judge_bias(
            content=request.blog_content
        )
        return BiasJudgeResponse(bias_score=bias_score, explanation=explanation)
    except AIServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to analyze for bias: {e}"
        )