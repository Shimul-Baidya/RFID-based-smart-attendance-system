from pydantic import BaseModel

class DashboardResponse(BaseModel):
    role: str
    message: str
    permissions: list[str]

