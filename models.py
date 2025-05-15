from pydantic import BaseModel

class AuditResponses(BaseModel):
    responses: dict[str, str]