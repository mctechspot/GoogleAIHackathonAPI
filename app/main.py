import base64
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from google.oauth2 import service_account
import json
import PIL.Image
from pydantic import BaseModel, Field
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from vertexai.preview.vision_models import Image, ImageCaptioningModel, ImageTextModel
import os
from dotenv import load_dotenv
load_dotenv()
from typing_extensions import Annotated
from uuid_extensions import uuid7, uuid7str
from .classes.ContentGenerator import ContentGenerator

content_generator = ContentGenerator()

app = FastAPI()


# Class that provides prompt for text generation
class TextPrompt(BaseModel):
    prompt: str = Field(description="Field for text prompt")
    content_type: str = Field(description="Field for generated text content type (story, poem or song)")

# Class that provides prompt for image generation
class ImageGenerationPrompt(BaseModel):
    prompt: str = Field(description="Field for text prompt to generate image")
    style: str = Field(description="Field for key generated image style")
    orientation: str = Field(description="Field for key of generated image orientation")

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

"""
POST Request to generate text content with given prompt
Payload Type: Application/JSON
    {
        "prompt": represents text prompt to assist in generating text content
    }
"""
@app.post("/generate-text")
async def generate_text_content_endpoint(prompt: TextPrompt):
    try:
        # Get text content generated from prompt
        response = content_generator.generate_text_content(prompt.prompt, prompt.content_type)

        # Return successful response
        if "response" in response.keys():
            return {
                "response": response["response"]
            }
        
        # Return warning response
        elif "warnings" in response.keys():
            return {
                "warnings": response["response"]
            }
        
        # Return error response
        else:
            return {
                "error": response["error"]
            }

    # Return exception error response
    except Exception as error:
        return {
            "error": str(error)
        }

"""
POST Request to generate captions for a provided image
Payload Type: Multipart/form-data
Payload Keys:
    - image: image file uploaded by user
"""
@app.post("/generate-image-captions")
async def generate_image_captions_endpoint(image: Annotated[UploadFile, Form()]):
    try:
        # Get response for image captions
        response = await content_generator.generate_image_captions(image)

        # Return successful response
        if "response" in response.keys():
            return {
                "response": response["response"]
            }
        
        # Return warning response
        elif "warnings" in response.keys():
            return {
                "warnings": response["warnings"]
            }

        # Return error response
        else:
            return {
                "error": response["error"]
            }

    # Return exception error response
    except Exception as error:
        return {
            "error": str(error)
        }

"""
POST Request to generate text for a provided image
Payload Type: Multipart/form-data
Payload Keys:
    - image: image file uploaded by user
    - content_type: key that inidicates type of content to be generated (story, poem, or song)
    - prompt: text provided by user to assist in text content generation
"""
@app.post("/generate-text-from-image")
async def generate_text_from_image_endpoint(
    image: Annotated[UploadFile, Form()], 
    content_type: Annotated[str, Form()], 
    prompt: Annotated[str, Form()]
):
    try:
        # Get response for image captions
        response = await content_generator.generate_text_from_image(image, content_type, prompt)

        # Return successful response
        if "response" in response.keys():
            return {
                "response": response["response"]
            }
        
        # Return warning response
        elif "warnings" in response.keys():
            return {
                "warnings": response["warnings"]
            }

        # Return error response
        else:
            return {
                "error": response["error"]
            }

    # Return exception error response
    except Exception as error:
        return {
            "error": str(error)
        }
    
"""
POST Request to generate image for a provided text
Payload Type: Application/JSON
{
    "prompt": represents text prompt to assist in generating text content,
    "style": represents key for art style,
    "orientation": represents key for image orientation
}
"""
@app.post("/generate-image-from-text")
async def generate_image_from_text_endpoint(prompt: ImageGenerationPrompt):
    try:
        # Get response for image captions
        response = await content_generator.generate_image_from_text(prompt.prompt, prompt.style, prompt.orientation)

        # Return successful response
        if "response" in response.keys():
            return {
                "response": response["response"]
            }
        
        # Return warning response
        elif "warnings" in response.keys():
            return {
                "warnings": response["warnings"]
            }

        # Return error response
        else:
            return {
                "error": response["error"]
            }

    # Return exception error response
    except Exception as error:
        return {
            "error": str(error)
        }
