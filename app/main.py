import base64
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from google.oauth2 import service_account
import json
from pydantic import BaseModel, Field
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.vision_models import Image, ImageCaptioningModel
import os
from dotenv import load_dotenv
load_dotenv()
from typing_extensions import Annotated
from uuid_extensions import uuid7, uuid7str

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def root():
    return  """
    <html>
        <head>
            <title>Jenna API</title>
        </head>
        <body>
            <p>Welcome to the Jenna API! 🤖</p>
        </body>
    </html>
    """