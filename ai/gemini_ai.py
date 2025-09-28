from config import get_model
import re

def clean_response(text):
    # Remove leading bullet characters like "*", "-", etc.
    cleaned_lines = []
    for line in text.splitlines():
        cleaned_line = re.sub(r"^\s*[\\-\•]\s", "", line)  # removes leading bullets with optional whitespace
        cleaned_lines.append(cleaned_line)
    return "\n".join(cleaned_lines)

def get_response(prompt):
    model = get_model()
    response = model.generate_content(prompt)
    return clean_response(response.text)