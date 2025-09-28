import google.generativeai as genai

# ✅ Configure Gemini API
genai.configure(api_key="AIzaSyBif5c4kQOeJKpo-aRNQva86h1ldss_ggE")

def get_model():
    return genai.GenerativeModel("gemini-2.0-flash")

def translate_tamil_to_hindi(text):
    model = get_model()
    prompt = f"Translate this Tamil sentence to Hindi without explanation: '{text}'"
    response = model.generate_content(prompt)
    return response.text.strip()
