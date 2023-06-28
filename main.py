import os
import json
import requests
from fastapi import FastAPI
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

@app.post('/v1/chat/completions')
async def completions(contents: TextInput):

    open_ai_key =  os.environ['OPENAI_API_KEY']
    open_ai_url =  os.environ['OPENAI_API_URL']

    OpenAIHeaders = {
     "Content-Type": "application/json",
      "Authorization":  f'Bearer {open_ai_key}',
    }

    # get whole object from frontend
    OpenAIRequestData = {
      "model": "gpt-3.5-turbo",
      "messages": [
        {
          "role": "user",
          "content": contents.message,
        },
      ],
      # "max_tokens": 100, #due to max tokens asnwers are limited response
      "stream": True,
    }

    requestedOpenAIJsonObject = json.dumps(OpenAIRequestData)
  
    response = requests.post(f'{open_ai_url}/v1/chat/completions', requestedOpenAIJsonObject, stream= True,headers = OpenAIHeaders)
    return StreamingResponse(response.iter_content(chunk_size=1024), media_type='text/event-stream')
  

@app.get("/")
async def status():
    return {'status':'healthy'}

# @app.post("/ask")
# async def ask(request: Request, message: TextInput):
#     # Get the user-defined auth key from the environment variables
#     user_auth_key = os.environ.get('USER_AUTH_KEY')
#     session_id = os.environ['SESSION_ID']

#     # Check if the user has defined an auth key,
#     # If so, check if the auth key in the header matches it.
#     if user_auth_key and user_auth_key != request.headers.get('Authorization'):
#         raise HTTPException(status_code=401, detail='Invalid authorization key')

#     # Execute your code without authenticating the resource
#     try:
#       chatbot = Chatbot(session_id)
#       response = chatbot.ask(message.message)
#       return response
#     except Exception as e:
#       print("An exception occurred",e)

# @app.post("/ask")
# async def ask(contents: TextInput):
#     # Get the user-defined auth key from the environment variables
#     bard_ai_key =  os.environ['BARD_API_KEY']
#     bard_api_url = os.environ['BARD_API_URL']

#     requestPayload = {
#       "prompt": {
#           "text": contents.message
#       }
#     }

#     requestPayload = json.dumps(requestPayload)
#     try:
#       response = requests.post(f'{bard_api_url}?key={bard_ai_key}',requestPayload)
#       return JSONResponse(response.json())
#     except Exception as e:
#       print("An exception occurred",e)

@app.post("/ask")
async def ask(contents: TextInput):
    try:
       response = palm.chat(messages=contents.message)
       return response.last
    except Exception as e:
      print("An exception occurred",e)