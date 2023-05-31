import os
import time
import json
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from Bard import Chatbot
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import sseclient
from starlette.responses import StreamingResponse
# from fastapi.responses import StreamingResponse


app = FastAPI()
handler = Mangum(app)

origins = [
    ###### we should allow only frontend url ########
    "http://localhost:3000",
    "https://multi-chat-ai.web.app"
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
async def completions(message: TextInput):

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
          "content": message.message,
        },
      ],
      "max_tokens": 100,
      "stream": True,
    }

    requestedOpenAIJsonObject = json.dumps(OpenAIRequestData)
  
    response = requests.post(f'{open_ai_url}/v1/chat/completions', requestedOpenAIJsonObject, stream= True,headers = OpenAIHeaders)
    
    # for line in response.iter_content(chunk_size=1024):
    #       completion_reason = line["choices"][0]["finish_reason"]
    #       if "content" in completion_reason["choices"][0].delta:
    #           current_response = completion_reason["choices"][0].delta.content
    #           print(current_response)
    #           yield {"data": current_response}
    #           time.sleep(0.25)

   
    # for chunk in response.iter_content(chunk_size=1024):
    #   if chunk:
    #       print(chunk.decode('utf-8'), end = "", flush = True)

    # client = sseclient.SSEClient(r)
    # for event in client.events():
    #    if event.data != '[DONE]':
    #       print(json.loads(event.data)['choices'][0]['text'],end="", flush=True)

    # for data in response.iter_content(chunk_size=1024):
    #    print(data)
      #  if data != '[DONE]':
      #     print(json.loads(data)['choices'][0]['text'],end="", flush=True)

    # return 'got it'
    return StreamingResponse(response.iter_content(chunk_size=1024), media_type='text/event-stream')
  

@app.get("/")
async def status():
    return {'status':'healthy'}

@app.post("/ask")
async def ask(request: Request, message: TextInput):
    # Get the user-defined auth key from the environment variables
    user_auth_key = os.environ.get('USER_AUTH_KEY')
    session_id = os.environ['SESSION_ID']

    # Check if the user has defined an auth key,
    # If so, check if the auth key in the header matches it.
    if user_auth_key and user_auth_key != request.headers.get('Authorization'):
        raise HTTPException(status_code=401, detail='Invalid authorization key')

    # Execute your code without authenticating the resource
    try:
      chatbot = Chatbot(session_id)
      response = chatbot.ask(message.message)
      return response
    except Exception as e:
      print("An exception occurred",e)

