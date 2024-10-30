from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class MultiModalRagRequest(BaseModel):
    user_question: str = Field(..., description="The user question about the PDF")
    generate_summary: bool = Field(None, description="Boolean to determine whether summary must be generated or not (optional)")