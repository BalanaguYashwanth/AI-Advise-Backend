import os
import json
import requests
from fastapi import FastAPI,Request
from pydantic import BaseModel
from Bard import Chatbot
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from starlette.responses import StreamingResponse
import google.generativeai as palm

app = FastAPI()
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
    message:str

@app.get("/")
async def status():
    return {'status':'healthy'}

@app.post('/v1/chat/completions')
async def completions(contents:Request):

    open_ai_key =  os.environ['OPENAI_API_KEY']
    open_ai_url =  os.environ['OPENAI_API_URL']

    OpenAIHeaders = {
     "Content-Type": "application/json",
      "Authorization":  f'Bearer {open_ai_key}',
    }

    request_info = await contents.json()
    requestedOpenAIJsonObject = json.dumps(request_info)
    response = requests.post(f'{open_ai_url}/v1/chat/completions', requestedOpenAIJsonObject, stream= True,headers = OpenAIHeaders)
    return StreamingResponse(response.iter_content(chunk_size=1024), media_type='text/event-stream')

@app.post("/ask")
async def ask(contents: TextInput):
    try:
       response = palm.chat(messages=contents.message)
       return response.last
    except Exception as e:
      print("An exception occurred",e)