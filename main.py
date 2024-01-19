import os
import datetime
from config import db
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
from Bard import Chatbot
from bardapi import Bard
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from starlette.responses import StreamingResponse
import google.generativeai as palm

app = FastAPI()
client = OpenAI()
handler = Mangum(app)
palm.configure(api_key=os.environ['BARD_API_KEY'])

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
    try:
        request_info = await contents.json()
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[{"role": "user", "content": request_info['content']}],
            stream=True,
        )
        def operation(stream):
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end="")
                    yield chunk.choices[0].delta.content
                    
        return StreamingResponse(operation(stream=stream), media_type='text/event-stream')
    except Exception as e:
        return f'{e}', 400


@app.post("/ask")
async def ask(contents: TextInput):
    #todo - write automation which will pickup this token
    try:
       token = 'fQiIVDvU_euUDPFCUB0Cywjf5Zl0xvyRgR0LZue7kV27mdKs3rWNLCaG08p-BXG67M-g4g.'
       bard = Bard(token = token)
       result = bard.get_answer(contents.message)
       return result['content']
    except Exception as e:
        print("An exception occurred", e)
