from dataclasses import dataclass, field
from typing import Optional

@dataclass
class MessageData:
    group_name: str
    type: str
    content: str
    sender: str
    msg_id: str
    quote_id: str = ""
    quote_content: str = ""
    recall_id: str = ""
    image_url: str = ""
    have_checked: str = "true"
    status: str = ""
    img_md5: str = ""
    timestamp: str = ""

@dataclass
class SendMessageData:
    sender: str
    sender_number:str
    receiver: str
    position: str
    sequence: str
    channel: str
    type: str
    image: str
    reply: str
    content: str
