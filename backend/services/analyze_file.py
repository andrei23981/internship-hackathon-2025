import os
import mimetypes
import base64
from services.ollama_client import get_ai_analysis

def analyze_single_file(file_path: str):

    try:

        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        file_size = os.path.getsize(file_path)
        

        mime_type, _ = mimetypes.guess_type(file_path) or (None, None)
        

        content, processing_info = extract_file_content(file_path, file_name, file_ext, mime_type or "")
        

        prompt = create_analysis_prompt(file_name, file_ext, mime_type or "", file_size, content, processing_info)
        

        analysis_result = get_ai_analysis(prompt)
        

        import json
        import re
        try:

            try:
                result = json.loads(analysis_result)
                return result
            except:
                pass
                

            json_match = re.search(r"\{.*\}", analysis_result, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return {
                    "score": 75,
                    "summary": analysis_result,
                    "issues": []
                }
        except json.JSONDecodeError:

            return {
                "score": 75,
                "summary": analysis_result,
                "issues": []
            }
            
    except Exception as e:
        raise RuntimeError(f"Eroare la analiza fișierului: {str(e)}")

def extract_file_content(file_path: str, file_name: str, file_ext: str, mime_type: str):

    content = ""
    processing_info = ""
    

    text_extensions = {'.txt', '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs', 
                      '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.html', '.htm', 
                      '.css', '.sql', '.sh', '.bash', '.yaml', '.yml', '.json', '.xml', '.md',
                      '.markdown', '.log', '.ini', '.cfg', '.conf', '.toml', '.dockerfile',
                      '.gitignore', '.env', '.csv', '.tsv', '.r', '.m', '.pl', '.lua', '.vim',
                      '.emacs', '.el', '.lisp', '.hs', '.ml', '.fs', '.fsx', '.dart', '.scala',
                      '.clj', '.cljs', '.ex', '.exs', '.erl', '.hrl', '.elm', '.purs', '.idr',
                      '.agda', '.lhs', '.rkt', '.scm', '.ss', '.lsp', '.fun', '.moon', '.wren',
                      '.zig', '.nim', '.v', '.vsh', '.vir', '.cr', '.ecr', '.slang', '.sln',
                      '.csproj', '.vb', '.pas', '.pp', '.d', '.di', '.m', '.mm', '.swift',
                      '.kt', '.kts', '.gradle', '.properties', '.jsp', '.asp', '.aspx', '.php',
                      '.phtml', '.twig', '.mustache', '.hbs', '.handlebars', '.ejs', '.jade',
                      '.pug', '.slim', '.haml', '.sass', '.scss', '.less', '.styl', '.stylus',
                      '.postcss', '.pcss', '.css.map', '.js.map', '.ts.map', '.jsx.map',
                      '.tsx.map', '.coffee', '.litcoffee', '.iced', '.ls', '.ts', '.d.ts',
                      '.jsx', '.tsx', '.vue', '.svelte', '.astro', '.mdx', '.mdx', '.json',
                      '.jsonc', '.json5', '.jsonl', '.ndjson', '.toml', '.yaml', '.yml',
                      '.xml', '.xhtml', '.xslt', '.xsd', '.dtd', '.svg', '.mathml', '.rss',
                      '.atom', '.opml', '.xaml', '.axaml', '.wxaml', '.plist', '.bplist',
                      '.strings', '.storyboard', '.xib', '.nib', '.car', '.xcassets',
                      '.bundle', '.framework', '.dylib', '.so', '.dll', '.exe', '.msi',
                      '.dmg', '.pkg', '.deb', '.rpm', '.apk', '.ipa', '.app', '.appimage',
                      '.snap', '.flatpak', '.bin', '.run', '.sh', '.bash', '.zsh', '.fish',
                      '.csh', '.tcsh', '.ksh', '.pdksh', '.mksh', '.dash', '.ash', '.busybox',
                      '.powershell', '.ps1', '.psm1', '.psd1', '.ps1xml', '.psc1', '.pssc',
                      '.bat', '.cmd', '.com', '.sys', '.inf', '.reg', '.reg', '.reg',
                      '.vbs', '.vbe', '.js', '.jse', '.wsf', '.wsh', '.ws', '.wsc',
                      '.py', '.pyw', '.pyc', '.pyo', '.pyd', '.pyi', '.pyx', '.pxd',
                      '.pyz', '.pyzw', '.r', '.rdata', '.rds', '.rda', '.rhistory',
                      '.rprofile', '.renviron', '.rs', '.rlib', '.rb', '.rbw', '.gem',
                      '.ru', '.erb', '.rhtml', '.rjs', '.rxml', '.rake', '.rakefile',
                      '.gemspec', '.lock', '.podspec', '.podfile', '.swift', '.swiftinterface',
                      '.kt', '.kts', '.java', '.class', '.jar', '.war', '.ear', '.aar',
                      '.jsp', '.jspx', '.tag', '.tagx', '.tld', '.jspf', '.jspx', '.tag',
                      '.tagx', '.tld', '.jspf', '.scala', '.sc', '.sbt', '.go', '.mod',
                      '.sum', '.work', '.test', '.prof', '.trace', '.out', '.6', '.8',
                      '.c', '.h', '.cc', '.cpp', '.cxx', '.c++', '.hpp', '.hxx', '.h++',
                      '.o', '.a', '.so', '.lo', '.la', '.pc', '.m4', '.ac', '.am',
                      '.in', '.rej', '.orig', '.patch', '.diff', '.d', '.di', '.o',
                      '.a', '.so', '.dll', '.dylib', '.lib', '.obj', '.exe', '.com',
                      '.sys', '.drv', '.scr', '.cpl', '.msc', '.msp', '.msi', '.msu',
                      '.cab', '.wim', '.esd', '.appx', '.appxbundle', '.msix',
                      '.msixbundle', '.cer', '.crt', '.der', '.p7b', '.p7c', '.p7m',
                      '.p7s', '.pfx', '.p12', '.spc', '.sst', '.stl', '.csr', '.key',
                      '.pvk', '.pem', '.pub', '.sig', '.rlib', '.pdb', '.ilk', '.exp',
                      '.lib', '.def', '.idb', '.pch', '.tmp', '.temp', '.bak', '.backup',
                      '.old', '.orig', '.save', '.swp', '.swo', '.un~', '.lock', '.lck'}
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.svg', '.ico', '.icon'}
    

    if file_ext in text_extensions or (mime_type and mime_type.startswith('text/')):
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            processing_info = f"Fișier text citit direct ({len(content)} caractere)"
        except Exception as e:
            processing_info = f"Eroare la citirea fișierului text: {str(e)}"
    

    elif file_ext in image_extensions or (mime_type and mime_type.startswith('image/')):
        try:

            content = f"[IMAGINE: {file_name} - Tip: {mime_type or 'necunoscut'}]"
            processing_info = f"Fișier imagine detectat: {file_ext}, MIME: {mime_type}"
        except Exception as e:
            processing_info = f"Eroare la procesarea imaginii: {str(e)}"
    

    elif file_ext == '.pdf' or (mime_type == 'application/pdf'):
        try:
            content = f"[PDF: {file_name} - Document PDF detectat]"
            processing_info = "Fișier PDF detectat (conținutul nu poate fi extras direct)"
        except Exception as e:
            processing_info = f"Eroare la procesarea PDF: {str(e)}"
    

    else:
        try:

            with open(file_path, 'rb') as f:
                binary_content = f.read(1024)  

                try:
                    text_sample = binary_content.decode('utf-8', errors='ignore')
                    if len(text_sample.strip()) > 0:
                        content = f"[FIȘIER BINAR/TEXT: {file_name}]\nPrimele 1024 bytes:\n{text_sample[:500]}..."
                    else:
                        content = f"[FIȘIER BINAR: {file_name} - Dimensiune: {file_size} bytes]"
                except:
                    content = f"[FIȘIER BINAR: {file_name} - Dimensiune: {file_size} bytes]"
            processing_info = f"Fișier binar detectat: {file_ext}, MIME: {mime_type}, Dimensiune: {file_size} bytes"
        except Exception as e:
            processing_info = f"Eroare la procesarea fișierului binar: {str(e)}"
    
    return content, processing_info

def create_analysis_prompt(file_name: str, file_ext: str, mime_type: str, file_size: int, content: str, processing_info: str):


    max_content_length = 1500
    truncated_content = content[:max_content_length] + ("..." if len(content) > max_content_length else "")
    
    base_prompt = f"""File: {file_name} ({file_ext})
Size: {file_size} bytes
Content:
{truncated_content}

JSON response:
{{
  "score": 0-100,
  "summary": "Brief analysis",
  "issues": [
    {{
      "type": "bug|security|performance|style|improvement",
      "message": "Issue",
      "recommendation": "Fix"
    }}
  ]
}}

Max 3 issues. JSON only.
"""
    
    return base_prompt