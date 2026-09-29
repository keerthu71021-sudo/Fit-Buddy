import os


def generate_gemini_text(model: str, prompt: str) -> str:
    """Call Gemini and return the stripped text of the response."""
    from google import genai  # imported lazily so the app runs without the SDK/key

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(model=model, contents=prompt)
    text = getattr(response, "text", None)
    if not text:
        raise RuntimeError("Gemini returned an empty response")
    return text.strip()
