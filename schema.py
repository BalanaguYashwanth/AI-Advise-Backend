from pydantic import BaseModel

class MessageItemSchema(BaseModel):
    user: str
    bard: str
    chatgpt: str
    recent_title_id: str

    class Config:
        orm_mode = True


class RecentTitleSchema(BaseModel):
    uid: str
    title: str

    class Config:
        orm_mode = True
