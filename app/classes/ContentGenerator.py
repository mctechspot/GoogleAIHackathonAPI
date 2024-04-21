import base64
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

class ContentGenerator:
    def __init__(self):
        self.GCP_SA_KEY_STRING = os.environ.get("GCP_SA_KEY_STRING")
        self.gcp_decoded_sa_key_string = base64.b64decode(self.GCP_SA_KEY_STRING)
        self.gcp_sa_key_json = json.loads(self.gcp_decoded_sa_key_string)
        self.credentials = service_account.Credentials.from_service_account_info(self.gcp_sa_key_json)
        self.project_id = os.environ.get("GCP_PROJECT_ID")
        self.location = os.environ.get("GCP_LOCATION")
        self.GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
        genai.configure(api_key=self.GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel('gemini-pro-vision')
        vertexai.init(project = self.project_id, credentials = self.credentials, location = self.location)
        self.vertex_pro_vision_model = GenerativeModel(model_name="gemini-1.0-pro-vision")
        self.vertex_image_captioning_model = ImageCaptioningModel.from_pretrained("imagetext@001")

    """
    Function to accept an image file and return a list of captions
    Parameters:
        - prompt: text prompt specified by user to assist in generating text content
        - content_type: number string to indicate if generated text should be a story, poem or song
    """
    def generate_text_content(self, prompt, content_type):
        try:
            warnings = []
            

            # Use gemini pro vision model to generate text from image based on prompt
            genai.configure(api_key=self.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro-vision')

            # Specify in prompt if the text should be a story, poem or song
            if content_type == "1":
                content_type_string = "story"
            elif content_type == "2":
                content_type_string = "poem"
            else:
                content_type_string = "song that rhymes"

            final_prompt = f"Write a {content_type_string} with the following prompt: {prompt}."

            """
            vertexai.init(project=project_id, credentials=credentials, location=location)
            model = GenerativeModel(model_name="gemini-1.0-pro-vision")
            """
            response = self.vertex_pro_vision_model.generate_content(final_prompt)

            response_texts = []

            for candidate in response.candidates:
                response_texts = [part.text for part in candidate.content.parts]

            # Return warning if the model is unable to generate text content for prompt
            if len(response_texts) == 0:
                warnings.append("Sorry. We are having trouble generating text content for this image. Try again.")
                return {
                    "warnings": warnings
                }
            
            # Return successful response
            return {
                "response": response_texts[0]
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
    async def generate_image_captions(self, image):
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
            
            """
            vertexai.init(project=project_id, credentials=credentials, location=location)
            model = ImageCaptioningModel.from_pretrained("imagetext@001")
            """

            # Create temporary image path in /tmp directory to write file
            # Append a UUID (version 7) to the end of the file name to prevent collisions
            temp_image_path = f"/tmp/image_temp_{uuid7()}.jpeg"
            with open(temp_image_path, "wb") as buffer:
                buffer.write(await image.read())

            # Load image in appropriate format for vertex to handle
            image = Image.load_from_file(temp_image_path)

            # Get captions for image
            captions = self.vertex_image_captioning_model.get_captions(
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
    Function to accept an image and prompt to generate text about an image with a prompt
    Parameters:
        - image: File uploaded by user
        - image: Prompt to generate text from image
    """    
    async def generate_text_from_image(self, image, content_type, prompt):
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
            
            # Create temporary image path in /tmp directory to write file
            # Append a UUID (version 7) to the end of the file name to prevent collisions
            temp_image_path = f"/tmp/image_temp_{uuid7()}.jpeg"
            with open(temp_image_path, "wb") as buffer:
                buffer.write(await image.read())
            
            # Load image in appropriate format for vertex to handle
            image = Image.load_from_file(temp_image_path)
            
            # Use gemini pro vision model to generate text from image based on prompt
            """
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro-vision')
            """

            # Specify in prompt if the text should be a story, poem or song
            if content_type == "1":
                content_type_string = "story"
            elif content_type == "2":
                content_type_string = "poem"
            else:
                content_type_string = "song that rhymes"

            final_prompt = f"Write a {content_type_string} about this image with the following prompt: {prompt}."

            response = self.gemini_model.generate_content([final_prompt, PIL.Image.open(temp_image_path)])
            response_texts = []

            # Remove file from /tmp directory
            os.remove(temp_image_path)

            for candidate in response.candidates:
                response_texts = [part.text for part in candidate.content.parts]

            # Return warning if the model is unable to generate content for the image
            if len(response_texts) == 0:
                warnings.append("Sorry. We are having trouble generating text content for this image. Try again.")
                return {
                    "warnings": warnings
                }
            
            # Return successful response
            return {
                "response": response_texts[0]
            }

        # Return exception error
        except Exception as error:
            return {
                "error": str(error)
            }