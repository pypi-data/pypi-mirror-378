from typing import Literal, Optional
from pydantic import BaseModel


class WebCallParams(BaseModel):
    """Parameters for WebCall (Daily.co) integration."""

    media_type: Literal["audio", "text", "hybrid"] = "audio"
    room_url: str
    bot_token: str
    bot_name: str = "RinggBot"
    room_name: Optional[str] = None

    # Optional SmallWebRTC params
    server_url: Optional[str] = None
    room_id: Optional[str] = None
    user_id: Optional[str] = None
