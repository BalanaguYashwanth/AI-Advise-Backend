import os
import json
import requests
import datetime
from config import pb, db
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from Bard import Chatbot
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from starlette.responses import StreamingResponse
import google.generativeai as palm
from database import get_db
from schema import MessageItemSchema
from models import Recent_Title, Message_Item
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

app = FastAPI()
handler = Mangum(app)
palm.configure(api_key=os.environ['BARD_API_KEY'])
db = Depends(get_db)

origins = [
    ###### we should allow only frontend url ########
    "http://localhost:3000",
    "https://multi-chat-ai.web.app",
    "https://knowr.co",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextInput(BaseModel):
    message: str


@app.get("/")
async def status():
    return {'status': 'healthy'}


@app.post("/save/history")
async def postMessages(request: Request):
    jsonData = await request.json()
    uid = jsonData['uid']
    title = jsonData['title']
    messages = jsonData['messages']
    try:
        db.collection(uid).document(title).set({'messages': messages})
        return {'response': 'response'}, 200
    except Exception as e:
        return f'{e}', 400


@app.post('/fetch/history/title')
async def getMessages(request: Request):
    doc_ids = []
    index = 0
    jsonData = await request.json()
    uid = jsonData['uid']
    try:
        collectionData = db.collection(uid).get()

        for doc in collectionData:
            timestamp = getUnixTimeFromDocSnapShot(doc.update_time)
            doc_id = doc.id
            updated_doc_obj = getDocumentsArray(index, doc_id, timestamp)
            doc_ids.append(updated_doc_obj)
            index = index+1
        return {'response': doc_ids}
    except Exception as e:
        return f'{e}', 400


def getDocumentsArray(index, doc_id, timestamp):
    doc_obj = {}
    doc_obj['id'] = index
    doc_obj['title'] = doc_id
    doc_obj['updated_time'] = timestamp
    return doc_obj


def getUnixTimeFromDocSnapShot(doc_time):
    updated_time_str = doc_time.strftime('%Y-%m-%d %H:%M:%S')
    time_obj = datetime.datetime.strptime(
        updated_time_str, "%Y-%m-%d %H:%M:%S")
    formatted_unix_time = int(time_obj.timestamp())
    return formatted_unix_time


@app.post('/fetch/history')
async def getHistoryItem(request: Request):
    jsonData = await request.json()
    uid = jsonData['uid']
    doc_title = jsonData['title']
    try:
        data = db.collection(uid).document(doc_title).get()
        return {'response': data.to_dict()}
    except Exception as e:
        return f'{e}', 400


@app.post('/v1/chat/completions')
async def completions(contents: Request):

    open_ai_key = os.environ['OPENAI_API_KEY']
    open_ai_url = os.environ['OPENAI_API_URL']

    OpenAIHeaders = {
        "Content-Type": "application/json",
        "Authorization":  f'Bearer {open_ai_key}',
    }
    try:
        request_info = await contents.json()
        requestedOpenAIJsonObject = json.dumps(request_info)
        response = requests.post(f'{open_ai_url}/v1/chat/completions',
                                 requestedOpenAIJsonObject, stream=True, headers=OpenAIHeaders)
        return StreamingResponse(response.iter_content(chunk_size=1024), media_type='text/event-stream')
    except Exception as e:
        return f'{e}', 400


@app.post("/ask")
async def ask(contents: TextInput):
    try:
        response = palm.chat(messages=contents.message)
        return response.last
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error {e}")


@app.get('/recent_titles/{uid}')
async def getRecentTitles(uid: str, db: Session = Depends(get_db)):
    try:
        return db.query(Recent_Title).filter(Recent_Title.uid == uid).all()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error {e}")


@app.post('/recent_title')
async def saveRecentTitle(recent_title: Request, db: Session = Depends(get_db)):
    try:
        response = await recent_title.json()
        db_title = Recent_Title(uid=response['uid'], title=response['title'])
        db.add(db_title)
        db.commit()
        for doc in db:
            response['id'] = doc.id
        db.refresh(db_title)
        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error {e}")

@app.post('/message')
async def saveMessage(message: MessageItemSchema, db: Session = Depends(get_db)):
    try:
        db_msg = Message_Item(user=message.user, chatgpt=message.chatgpt,
                              bard=message.bard, recent_title_id=message.recent_title_id)
        db.add(db_msg)
        db.commit()
        db.refresh(db_msg)
        return db_msg
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error {e}")