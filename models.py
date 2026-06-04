# surveybot/models.py
# Pydantic models for survey extraction validation

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional


# ---------------------------------------------------------------------------
# Base response types
# ---------------------------------------------------------------------------

class SingleResponse(BaseModel):
    value: Optional[int] = None
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class ScaleResponse(BaseModel):
    """1-5 rating scale question."""
    value: Optional[int] = Field(None, ge=1, le=5)
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class MultiResponse(BaseModel):
    """Multi-select question (Q6, Q16, Q17)."""
    value: Optional[List[int]] = None
    confidence: str = Field(..., pattern="^(high|medium|low)$")

    @field_validator('value', mode='before')
    @classmethod
    def coerce_comma_string(cls, v):
        """Handle cases where model returns '1,2' instead of [1, 2]."""
        if isinstance(v, str):
            try:
                return [int(x.strip()) for x in v.split(',') if x.strip()]
            except ValueError:
                return None
        return v

# Explicit bounded single-response classes (avoids type expression errors)
class Q1Response(BaseModel):
    value: Optional[int] = Field(None, ge=1, le=5)
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class Q2Response(BaseModel):
    value: Optional[int] = Field(None, ge=1, le=7)
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class Q3Response(BaseModel):
    value: Optional[int] = Field(None, ge=1, le=7)
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class Q4Response(BaseModel):
    value: Optional[int] = Field(None, ge=1, le=5)
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class Q5Response(BaseModel):
    value: Optional[int] = Field(None, ge=1, le=2)
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class Q7Response(BaseModel):
    value: Optional[int] = Field(None, ge=1, le=2)
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class Q8Response(BaseModel):
    value: Optional[int] = Field(None, ge=1, le=5)
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class Q12Response(BaseModel):
    value: Optional[int] = Field(None, ge=1, le=5)
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class Q13Response(BaseModel):
    value: Optional[int] = Field(None, ge=1, le=5)
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class Q14Response(BaseModel):
    value: Optional[int] = Field(None, ge=1, le=5)
    confidence: str = Field(..., pattern="^(high|medium|low)$")

class Q15Response(BaseModel):
    value: Optional[int] = Field(None, ge=1, le=5)
    confidence: str = Field(..., pattern="^(high|medium|low)$")


# ---------------------------------------------------------------------------
# Main survey result model
# ---------------------------------------------------------------------------

class SurveyResult(BaseModel):
    # Metadata
    # survey_id:    str
    # likely_voter: str
    survey_id: Optional[str] = None
    likely_voter: Optional[str] = None

    
    # Outside front (Q1-Q4)
    Q1: Q1Response
    Q2: Q2Response
    Q3: Q3Response
    Q4: Q4Response

    # Inside (Q5-Q12)
    Q5:  Q5Response
    Q6:  MultiResponse
    Q7:  Q7Response
    Q8:  Q8Response
    Q9a: ScaleResponse
    Q9b: ScaleResponse
    Q9c: ScaleResponse
    Q9d: ScaleResponse
    Q9e: ScaleResponse
    Q9f: ScaleResponse
    Q10a: ScaleResponse
    Q10b: ScaleResponse
    Q10c: ScaleResponse
    Q10d: ScaleResponse
    Q10e: ScaleResponse
    Q10f: ScaleResponse
    Q10g: ScaleResponse
    Q11a: ScaleResponse
    Q11b: ScaleResponse
    Q11c: ScaleResponse
    Q11d: ScaleResponse
    Q12: Q12Response

    # Outside back (Q13-Q17) — null if last survey in batch
    Q13: Optional[Q13Response] = None
    Q14: Optional[Q14Response] = None
    Q15: Optional[Q15Response] = None
    Q16: Optional[MultiResponse] = None
    Q17: Optional[MultiResponse] = None

    # @field_validator('likely_voter')
    # @classmethod
    # def validate_voter_type(cls, v):
    #     if v not in ('L', 'U'):
    #         raise ValueError(f"likely_voter must be 'L' or 'U', got '{v}'")
    #     return v
    @field_validator('likely_voter')
    @classmethod
    def validate_voter_type(cls, v):
        if v is None:
            return v
        if v not in ('L', 'U'):
            raise ValueError(f"likely_voter must be 'L' or 'U', got '{v}'")
        return v
    
    @model_validator(mode='after')
    def validate_voter_matches_id(self):
        if self.survey_id and self.likely_voter:
            expected = self.survey_id[0].upper()
            if expected in ('L', 'U') and expected != self.likely_voter:
                raise ValueError(
                    f"likely_voter '{self.likely_voter}' doesn't match "
                    f"survey_id '{self.survey_id}' (expected '{expected}')"
                )
        return self

    def get_flags(self) -> list:
        """Return list of field names with low/medium confidence."""
        flags = []
        for field_name in self.model_fields:
            val = getattr(self, field_name)
            if hasattr(val, 'confidence'):
                if val.confidence == 'low':
                    flags.append(field_name)
                elif val.confidence == 'medium':
                    flags.append(f"{field_name}?")
        return flags

    def to_flat_dict(self) -> dict:
        """Flatten to simple key→value dict for Excel writing."""
        flat = {
            'survey_id':    self.survey_id,
            'likely_voter': self.likely_voter,
        }
        q_fields = [f for f in self.model_fields if f.startswith('Q')]
        for field_name in q_fields:
            val = getattr(self, field_name)
            if val is None:
                flat[field_name] = None
            elif isinstance(val.value, list):
                flat[field_name] = ','.join(str(v) for v in val.value) if val.value else None
            else:
                flat[field_name] = val.value
        return flat


# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------

def parse_and_validate(raw_dict: dict):
    """Parse raw Claude JSON into validated SurveyResult. Returns (result, errors)."""
    try:
        result = SurveyResult(**raw_dict)
        return result, []
    except Exception as e:
        return None, [str(e)]