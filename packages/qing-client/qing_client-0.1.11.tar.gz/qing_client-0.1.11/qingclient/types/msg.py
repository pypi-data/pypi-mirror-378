from dataclasses import dataclass
from typing import List, Optional, Dict, Any

@dataclass
class MailRequest:
    to: List[str]
    text: Optional[str] = None
    html: Optional[str] = None
    from_: Optional[str] = None
    sender: Optional[str] = None
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None
    replyTo: Optional[str] = None
    subject: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None

@dataclass
class FeishuMessage:
    url: str
    elements: List[Dict[str, str]]
    title: Optional[str] = None
    bgColor: Optional[str] = None
    noticeUser: Optional[List[Dict[str, str]]] = None
    actions: Optional[List[Dict[str, str]]] = None