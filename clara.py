import requests

# ---------------------------------------------------------
#  CLARA BRAIN (LLAMA3) - WEB VERSION
# ---------------------------------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "dolphin-llama3:8b"


def clara_brain(prompt: str) -> str:
    """
    Core Clara brain: takes a user prompt (string) and returns Clara's reply (string).
    No audio, no motors, no local hardware.
    """
    try:
        system_instructions = (
            "You are CLARA — Companion Left After Retiring Aria. "
            "You speak with calm, confident, refined British clarity. "
            "You NEVER ramble or over-explain. "
            "You answer concisely, intelligently, and directly. "
            "You maintain a smooth, natural conversational flow, similar to JARVIS or FRIDAY. "
            "You follow the user's tone while staying respectful and subtly witty. "
            "You are aware that your name is Clara and that you are a voice assistant.\n\n"
        )

        full_prompt = system_instructions + "User: " + prompt + "\nCLARA:"

        response = requests.post(
            OLLAMA_URL,
            json={
                "model": LLM_MODEL,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=120
        )

        data = response.json()
        reply = data.get("response", "").strip()
        return reply or "I'm not sure how to respond to that."

    except Exception as e:
        print("ERROR (LLM):", e)
        return "I am having trouble connecting to my AI systems."


# ---------------------------------------------------------
#  INTERNET SEARCH (OPTIONAL)
# ---------------------------------------------------------

def web_search(query: str) -> str:
    """
    Simple DuckDuckGo search helper, same logic as your local version,
    but safe for web use (no hardware). 
    """
    try:
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
        r = requests.get(url, params=params, timeout=10)
        data = r.json()

        if data.get("AbstractText"):
            return data["AbstractText"]

        if data.get("RelatedTopics"):
            for item in data["RelatedTopics"]:
                if isinstance(item, dict) and "Text" in item:
                    return item["Text"]

        return "I couldn't find anything useful online."
    except Exception:
        return "I couldn't access the internet."


# ---------------------------------------------------------
#  HIGH-LEVEL ENTRY POINT
# ---------------------------------------------------------

def handle_clara_request(message: str) -> str:
    """
    Single entry point for the web service.
    - Takes a user message (string)
    - Returns Clara's reply (string)
    - You can later add routing here (e.g., detect 'search for ...' and call web_search).
    """
    message = (message or "").strip()
    if not message:
        return "You didn't say anything."

    # Simple search intent hook (optional)
    lowered = message.lower()
    if any(t in lowered for t in ["search for", "look up", "who is", "what is", "tell me about"]):
        # crude extraction, same idea as your local helper 
        for prefix in ["search for", "look up", "who is", "what is", "tell me about"]:
            if prefix in lowered:
                query = lowered.replace(prefix, "", 1).strip()
                if not query:
                    query = message
                result = web_search(query)
                return result

    # Default: let Clara think
    return clara_brain(message)
