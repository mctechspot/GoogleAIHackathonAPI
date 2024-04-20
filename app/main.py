import base64
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from google.oauth2 import service_account
import json
from pydantic import BaseModel, Field
import vertexai
from vertexai.generative_models import GenerativeModel, Part
import os
from dotenv import load_dotenv
load_dotenv()

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