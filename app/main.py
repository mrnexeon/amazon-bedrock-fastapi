# Author: Andrew Arkhipov, the.nexeon@gmail.com

from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field
from mangum import Mangum
import uvicorn
import boto3

from enum import Enum
import datetime
import uuid
import json
import os

app = FastAPI(title="Chatbot API",
              description="A simple chatbot API using Amazon Bedrock Runtime",
              version="0.0.1",
              contact={
                  "name": "Andrew Arkhipov",
                  "email": "the.nexeon@gmail.com",
              })

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create an Amazon Bedrock Runtime client in the AWS Region you want to use.
brt = boto3.client("bedrock-runtime", region_name="us-east-1")

# Set the model ID, e.g., Amazon Titan Text G1 - Express.
model_id = "mistral.mistral-large-2402-v1:0"

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table_name = os.environ.get('TABLE_NAME')
table = dynamodb.Table(table_name)


class ChatRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class TextContent(BaseModel):
    text: str = Field(default=None, examples=["Hello!"])


class Message(BaseModel):
    role: ChatRole
    content: list[TextContent]


class ChatSummary(BaseModel):
    id: uuid.UUID = Field(default=None, examples=[
                    "12345678-1234-5678-1234-567812345678"])
    title: str = Field(default=None, examples=["Summer Destinations"])
    created_at: datetime.datetime = Field(
        default=None, examples=["2022-05-18T12:19:51.685496"])
    updated_at: datetime.datetime = Field(
        default=None, examples=["2022-05-18T12:19:51.685496"])


class Chat(ChatSummary):
    messages: list[Message]


class ChatResponse(BaseModel):
    message: Message
    chat: ChatSummary


def save_chat_to_dynamodb(chat: Chat):
    table.put_item(
        Item=json.loads(chat.model_dump_json())
    )


def get_chat_from_dynamodb(chat_id: uuid.UUID) -> Chat | None:
    response = table.get_item(Key={'id': str(chat_id)})
    if 'Item' not in response:
        return None
    return Chat(**response['Item'])

def get_chats_from_dynamodb() -> list[Chat]:
    response = table.scan()
    return [Chat(**item) for item in response['Items']]


def generate_title(text: str) -> str:
    user_message = f"""Give me a title to the text: {text}. 
    Use maximum 2 words. Output only the title. Do not use quotes."""
    conversation = [
        {
            "role": "user",
            "content": [{"text": user_message}],
        }
    ]
    response = brt.converse(
        modelId=model_id,
        messages=conversation,
        inferenceConfig={"maxTokens": 128, "temperature": 0.5, "topP": 0.9},
    )

    title = response["output"]["message"]["content"][0]["text"]
    return title


@app.post('/chat')
async def chat_with_the_model(
    prompt: str = Body(media_type="text/plain", example="Hello!"),
    chat_id: uuid.UUID | None = Query(
        default=None,
        description="A unique identifier for the chat session. This ID is generated when a new chat session is created and is used to retrieve and continue the chat session in future requests.",
        examples=["12345678-1234-5678-1234-567812345678"]
    )
) -> ChatResponse:
    if chat_id is None:
        chat_id = str(uuid.uuid4())
        title = generate_title(prompt)

        chat = Chat(id=chat_id,
                    messages=[],
                    title=title,
                    created_at=datetime.datetime.now().isoformat(),
                    updated_at=datetime.datetime.now().isoformat())

        save_chat_to_dynamodb(chat)
    else:
        chat = get_chat_from_dynamodb(chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")

    chat.messages.append(
        Message(role="user", content=[TextContent(text=prompt)]))

    try:
        response = brt.converse(
            modelId=model_id,
            messages=[message.model_dump() for message in chat.messages],
            inferenceConfig={"maxTokens": 512,
                             "temperature": 0.5, "topP": 0.9},
        )
    except ClientError as e:
        raise HTTPException(status_code=500, detail=str(e))

    chat.messages.append(Message(**response["output"]["message"]))
    chat.updated_at = datetime.datetime.now().isoformat()
    save_chat_to_dynamodb(chat)

    return ChatResponse(message=response["output"]["message"], chat=chat)


@app.get('/chat/{chat_id}')
async def get_chat_history(chat_id: uuid.UUID) -> list[Message]:
    chat = get_chat_from_dynamodb(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail=f"Chat not found")
    return chat.messages


@app.get('/chats')
async def get_all_chats_ids() -> list[ChatSummary]:
    return get_chats_from_dynamodb()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
else:
    handler = Mangum(app, lifespan="off")
