
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class User(BaseModel):
    user_id: str = Field(alias="userGuid")
    first_name: Optional[str] = Field(None, alias="firstName")
    last_name: Optional[str] = Field(None, alias="lastName")
    username: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool = Field(False, alias="isVerified")

class Message(BaseModel):
    message_id: str = Field(alias="messageId")
    text: Optional[str] = None
    sender_id: str = Field(alias="senderGuid")
    chat_id: str = Field(alias="chatGuid")
    date: int
    # Add more fields as needed based on Rubika API response

class Chat(BaseModel):
    chat_id: str = Field(alias="chatGuid")
    title: str
    type: str # e.g., User, Group, Channel
    last_message: Optional[Message] = Field(None, alias="lastMessage")
    # Add more fields as needed

class AuthData(BaseModel):
    auth_key: str = Field(alias="authKey")
    private_key: str = Field(alias="privateKey")
    # Add other necessary authentication details

class ApiResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

# Add more models as needed for other API objects (e.g., Group, Channel, File, etc.)

