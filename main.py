import os
import json
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from Bard import Chatbot
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

app = FastAPI()
handler = Mangum(app)

origins = [
    ###### we should allow only frontend url ########
    "http://localhost:3000",
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

@app.post('/v1/chat/completions')
async def completions(textInput:TextInput):

    open_ai_key =  os.getenv('OPENAI_API_KEY')
    open_ai_url =  os.getenv('OPENAI_API_URL')

    OpenAIRequestData = {
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "user",
          "content": textInput.message,
        },
      ],
    }

    requestedOpenAIJsonObject = json.dumps(OpenAIRequestData)

    OpenAIHeaders = {
      "Content-Type": "application/json",
      "Authorization":  f'Bearer {open_ai_key}',
    }

    r = requests.post(f'{open_ai_url}/v1/chat/completions', requestedOpenAIJsonObject, headers = OpenAIHeaders)
    return r.json()

@app.post("/ask")
async def ask(request: Request, message: TextInput):
    # Get the user-defined auth key from the environment variables
    user_auth_key = os.getenv('USER_AUTH_KEY')
    session_id = os.getenv('SESSION_ID')
    # Check if the user has defined an auth key,
    # If so, check if the auth key in the header matches it.
    if user_auth_key and user_auth_key != request.headers.get('Authorization'):
        raise HTTPException(status_code=401, detail='Invalid authorization key')

    # Execute your code without authenticating the resource
    chatbot = Chatbot(session_id)
    response = chatbot.ask(message.message)
    return response
