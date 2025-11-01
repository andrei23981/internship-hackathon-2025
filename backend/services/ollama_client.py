import requests, json

def ask_ai(issues):
    prompt = f"Rezumă aceste erori și oferă sugestii pentru corectare:\n{json.dumps(issues[:5], indent=2)}"
    res = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "mistral", "prompt": prompt}
    )
    return res.json().get("response", "Nu s-au găsit sugestii.")