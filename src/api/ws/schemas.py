from pydantic import BaseModel
from typing import Literal, Optional

# WebSocket 메시지의 기본 구조
class WebSocketMessage(BaseModel):
    action: Literal["generate"]
    payload: Optional[dict]

# "generate" 액션의 payload 구조
class GeneratePayload(BaseModel):
    input_text: str
    setting_id: int

# "generate" 메시지 모델 (WebSocketMessage를 확장)
class GenerateMessage(WebSocketMessage):
    action: Literal["generate"]
    payload: GeneratePayload
