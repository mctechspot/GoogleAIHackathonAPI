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

GCP_SA_KEY_STRING = os.environ.get("GCP_SA_KEY_STRING")
gcp_decoded_sa_key_string = base64.b64decode(GCP_SA_KEY_STRING)
gcp_sa_key_json = json.loads(gcp_decoded_sa_key_string)
credentials = service_account.Credentials.from_service_account_info(gcp_sa_key_json)
project_id = os.environ.get("GCP_PROJECT_ID")
location = os.environ.get("GCP_LOCATION")

# Class that text prompt for text Generation
class TextPrompt(BaseModel):
    prompt: str = Field(description="Field for text prompt")

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
Function to accept an image file and return a list of captions
Parameters:
    - prompt: text prompt specified by user to assist in generating text content
"""
def generate_text_content(prompt):
    try:
        vertexai.init(project=project_id,
                    credentials=credentials, location=location)
        model = GenerativeModel(model_name="gemini-1.0-pro-vision")
        response = model.generate_content(prompt)
        return {
            "response": response.text
        }
    except Exception as error:
        return {
            "error": str(error)
        }
    
"""
Function to accept an image file and return a list of captions
Parameters:
    - image: File uploaded by user
"""
async def generate_image_captions(image):
    try:

        # Initialise an empty list for probable warnings
        warnings = []

        # Check for appropriate file extension
        file_extension = str(image.content_type).split("/")[-1]
        allowed_file_extensions = ["jpeg", "jpg", "png"]
        if file_extension.lower() not in allowed_file_extensions:
            warnings.append("Only images with extensions jpeg, jpg and png are allowed.")

        # Check for appropriate file size
        file_size = image.size
        if file_size >= 27000000:
            warnings.append("File size is too large. Choose a file of a size lower than 20 MB.")

        # Check for image warnings and return warning response if present
        if len(warnings) > 0:
            print("bad")
            return {
                "warnings": warnings
            }
        vertexai.init(project=project_id, credentials=credentials, location=location)
        model = ImageCaptioningModel.from_pretrained("imagetext@001")

        # Create temporary image path in /tmp directory to write file
        # Append a UUID (version 7) to the end of the file name to prevent collisions
        temp_image_path = f"/tmp/image_temp_{uuid7()}.jpeg"
        with open(temp_image_path, "wb") as buffer:
            buffer.write(await image.read())

        # Load image in appropriate format for vertex to handle
        image = Image.load_from_file(temp_image_path)

        # Get captions for image
        captions = model.get_captions(
            image=image,
            number_of_results=3,
            language="en",
        )

        # Remove file from /tmp directory
        os.remove(temp_image_path)

        # Return successful response
        return {
            "response": captions
        }

    # Return exception error
    except Exception as error:
        return {
            "error": str(error)
        }

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
        response = generate_text_content(prompt.prompt)

        # Return successful response
        if "response" in response.keys():
            return {
                "response": response["response"]
            }
        
        # Return warning response
        elif "response" in response.keys():
            return {
                "response": response["response"]
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
        response = generate_text_content(prompt.prompt)

        # Return successful response
        if "response" in response.keys():
            return {
                "response": response["response"]
            }
        
        # Return warning response
        elif "response" in response.keys():
            return {
                "response": response["response"]
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
    - image:image file uploaded by user
"""
@app.post("/generate-image-captions")
async def generate_image_captions_endpoint(image: Annotated[UploadFile, Form()]):
    try:
        # Get response for image captions
        response = await generate_image_captions(image)

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