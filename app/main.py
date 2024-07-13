from fastapi import FastAPI, HTTPException, Body, Query
from fastapi.middleware.cors import CORSMiddleware
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field
from mangum import Mangum
from enum import Enum

import uvicorn
import boto3
import uuid

app = FastAPI(title="Chatbot API",
              description="A simple chatbot API using Amazon Bedrock Runtime",
              version="0.0.1",
              contact={
                  "name": "Andrei Arkhipov",
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
table_name = 'ChatSessions'
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


class ChatResponse(BaseModel):
    message: Message
    chat_id: str = Field(default=None, examples=[
                         "12345678-1234-5678-1234-567812345678"])


class Chat(BaseModel):
    messages: list[Message]


def save_chat_to_dynamodb(chat_id: str, chat: Chat):
    table.put_item(
        Item={
            'chat_id': chat_id,
            'messages': [message.model_dump() for message in chat.messages]
        }
    )


def get_chat_from_dynamodb(chat_id: str) -> Chat | None:
    response = table.get_item(Key={'chat_id': chat_id})
    if 'Item' not in response:
        return None
    return Chat(messages=[Message(**msg) for msg in response['Item']['messages']])


@app.post('/chat')
async def chat_with_the_model(
    prompt: str = Body(media_type="text/plain", example="Hello!"),
    chat_id: str | None = Query(
        default=None,
        description="A unique identifier for the chat session. This ID is generated when a new chat session is created and is used to retrieve and continue the chat session in future requests.",
        examples=["12345678-1234-5678-1234-567812345678"]
    )
) -> ChatResponse:
    if chat_id is None:
        chat_id = str(uuid.uuid4())
        chat = Chat(messages=[])
        save_chat_to_dynamodb(chat_id, chat)
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
    save_chat_to_dynamodb(chat_id, chat)

    return ChatResponse(message=response["output"]["message"], chat_id=chat_id)


@app.get('/chat/{chat_id}')
async def get_chat_history(chat_id: str) -> list[Message]:
    chat = get_chat_from_dynamodb(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail=f"Chat not found")
    return chat.messages


@app.get('/chats')
async def get_all_chats_ids() -> list[str]:
    response = table.scan(ProjectionExpression="chat_id")
    return [item['chat_id'] for item in response['Items']]

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
else:
    handler = Mangum(app, lifespan="off")
