import requests
import json
import re


OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:1.5b"  



def _query_ollama(prompt: str, model: str = OLLAMA_MODEL, timeout: int = 60):

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=timeout
        )
        
        if response.status_code == 500:

            return json.dumps({
                "score": 75,
                "summary": "Analiza nu a putut fi completată din cauza unei erori la modelul AI. Vă rugăm verificați configurația Ollama.",
                "issues": [
                    {
                        "type": "system",
                        "message": "Modelul AI nu este disponibil - eroare internă server",
                        "recommendation": "Restartați serviciul Ollama sau verificați log-urile pentru detalii"
                    }
                ]
            })
            
        response.raise_for_status()
        raw_response = response.json().get("response", "").strip()
        

        if raw_response.startswith("```json"):
            json_start = raw_response.find("{")
            json_end = raw_response.rfind("}") + 1
            if json_start != -1 and json_end != -1:
                return raw_response[json_start:json_end]
        elif raw_response.startswith("```"):
            json_start = raw_response.find("{")
            json_end = raw_response.rfind("}") + 1
            if json_start != -1 and json_end != -1:
                return raw_response[json_start:json_end]
        
        return raw_response
    except requests.exceptions.RequestException as e:
        return json.dumps({
            "score": 50,
            "summary": f"Eroare de conexiune cu Ollama: {str(e)}",
            "issues": [
                {
                    "type": "connection",
                    "message": f"Nu se poate conecta la Ollama: {str(e)}",
                    "recommendation": "Verificați dacă Ollama rulează pe http://127.0.0.1:11434"
                }
            ]
        })
    except Exception as e:
        return json.dumps({
            "score": 50,
            "summary": f"Eroare neașteptată: {str(e)}",
            "issues": [
                {
                    "type": "system",
                    "message": f"Eroare neașteptată: {str(e)}",
                    "recommendation": "Verificați log-urile sistemului pentru detalii"
                }
            ]
        })



def ask_ai(findings):

    prompt = f"""You are a code reviewer. Analyze these issues:

{json.dumps(findings, indent=1, ensure_ascii=False)}

Respond with JSON only:
{{
  "score": 0-100,
  "summary": "Brief quality assessment",
  "issues": [
    {{
      "type": "bug|security|performance|style|improvement",
      "message": "Problem description",
      "recommendation": "Specific fix suggestion"
    }}
  ]
}}

Keep it short. Max 5 issues. No extra text.
"""

    raw_output = _query_ollama(prompt)


    try:
        # First try to parse directly
        try:
            return json.loads(raw_output)
        except:
            pass
            
        # Try to find JSON in response
        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            return {"score": 75, "summary": raw_output, "issues": []}
    except Exception:
        return {"score": 75, "summary": raw_output, "issues": []}



def get_ai_analysis(prompt):

    raw_output = _query_ollama(prompt)

    try:
        try:
            parsed = json.loads(raw_output)

            if isinstance(parsed, dict) and 'score' in parsed:
                return parsed
        except:
            pass
            
        # Try to find JSON in response
        json_match = re.search(r"\{.*\}", raw_output, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group(0))
            if isinstance(parsed, dict) and 'score' in parsed:
                return parsed
        

        return raw_output
    except Exception:
        return raw_output



if __name__ == "__main__":
    test_findings = [
        {"file": "main.py", "issue": "Unused import os", "severity": "low"},
        {"file": "api/routes.py", "issue": "Possible SQL injection risk", "severity": "high"}
    ]
    result = ask_ai(test_findings)
    print("\n--- AI Code Review ---")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n--- Direct Query Test ---")
    test_prompt = "Explain the purpose of a FastAPI backend in simple terms."
    print(get_ai_analysis(test_prompt))
