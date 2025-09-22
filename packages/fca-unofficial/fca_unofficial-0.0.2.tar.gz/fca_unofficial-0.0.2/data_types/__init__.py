from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class Attachment:
    type: str
    ID: Optional[str] = None
    url: Optional[str] = None
    filename: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    previewUrl: Optional[str] = None
    thumbnailUrl: Optional[str] = None


@dataclass
class Message:
    type: str
    messageID: Optional[str]
    threadID: Optional[str]
    senderID: Optional[str]
    body: str = ""
    timestamp: Optional[str] = None
    isGroup: Optional[bool] = None
    attachments: Optional[List[Attachment]] = None
    messageReactions: Optional[List[Dict[str, Any]]] = None


@dataclass
class ThreadInfo:
    threadID: str
    threadName: Optional[str]
    participantIDs: List[str]
    isGroup: bool
    messageCount: Optional[int] = None
    unreadCount: Optional[int] = None
    adminIDs: Optional[List[str]] = None
    lastMessageTimestamp: Optional[str] = None


@dataclass
class UserInfo:
    id: str
    name: Optional[str]
    firstName: Optional[str]
    lastName: Optional[str]
    vanity: Optional[str]
    profilePicUrl: Optional[str]
    profileUrl: Optional[str]
    gender: Optional[str]
    type: Optional[str]
    isFriend: Optional[bool]
    isBirthday: Optional[bool]
