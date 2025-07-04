import os
import google.generativeai as genai

# Replace with your actual Google API Key or ensure it's set as an environment variable
# For testing, you can temporarily hardcode it here, but remove it afterwards.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY_HERE")

if GOOGLE_API_KEY == "YOUR_GOOGLE_API_KEY_HERE":
    print("Please set your GOOGLE_API_KEY environment variable or replace 'YOUR_GOOGLE_API_KEY_HERE' in the script.")
    exit()

try:
    genai.configure(api_key=GOOGLE_API_KEY, transport="rest")
    model = genai.GenerativeModel("gemini-1.5-pro-latest") # Or any other Gemini model you have access to
    
    print("Attempting to generate content...")
    response = model.generate_content("Hello, Gemini! Tell me a short story.")
    print("Content generated successfully!")
    print(response.text)
except Exception as e:
    print(f"An error occurred: {e}")
