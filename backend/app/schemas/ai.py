from pydantic import BaseModel, Field

# --- Our Copilot Schema Input ---
class CopilotRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    context: str = Field(..., min_length=10)

# --- Our Copilot Schema Output ---
class CopilotResponse(BaseModel):
    answer: str

# --- Our Judge AI Agent ---
class BiasJudgeRequest(BaseModel):
    blog_content: str = Field(..., min_length=50)

# --- Our Judge AI Agent Output ---
class BiasJudgeResponse(BaseModel):
    bias_score: float = Field(..., ge=0.0, le=100.0)
    explanation: str