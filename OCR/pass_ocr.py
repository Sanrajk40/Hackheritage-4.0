import os
from google import genai
from google.genai import types

API_KEY = ""
client = genai.Client(api_key=API_KEY)

def backend_passport_ocr(file_bytes,mime_type):
    try:
        image_part=types.Part.from_bytes(
            data=file_bytes,
            mime_type=mime_type
        )

        response = client.models.generate_content(model='gemini-2.5-flash',contents=[image_part,"Analyze this passport picture.Read the Machine Readable Zone(MRZ) text lines at the bottom.""Extract: Passport Number,Country Code,Date of birth(DDMMYY),Expiry Date(DDMMYY),Issue Date(DDMMYY),Gender,Nationality""Output these things strictly as a single raw python dictionary structure named  nothing else"])
        return{'success':True, "Passport Details":response.text}
    except:
        return {'success':False}

