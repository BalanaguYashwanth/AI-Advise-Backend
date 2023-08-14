from pydantic import BaseModel

class MessageItemSchema(BaseModel):
    pass

class RecentTitleSchema(BaseModel):
    uid:str
    title:str

    class Config:
        orm_mode=True
