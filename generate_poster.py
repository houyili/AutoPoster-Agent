import os
import sys
import subprocess
import keyring
from openai import OpenAI

SERVICE_NAME = "AutoPoster-Agent"

def load_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: File not found - {filepath}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_poster.py <path_to_outline.md>")
        sys.exit(1)
        
    outline_path = sys.argv[1]
    output_tex = "poster.tex"
    
    print("=========================================")
    print("AutoPoster-Agent: Generating Poster")
    print("=========================================")
    
    # 1. Get API Key from Keychain
    api_key = keyring.get_password(SERVICE_NAME, "OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OpenAI API Key not found in the System Keychain.")
        print("Please run 'python setup_keychain.py' first.")
        sys.exit(1)
        
    # 2. Load Assets
    print(f"📄 Loading outline from: {outline_path}...")
    outline_content = load_file(outline_path)
    sop_content = load_file("templates/prompt_sops/agent_sop.md")
    template_content = load_file("templates/academic_poster_template.tex")
    
    # 3. Call LLM
    print("🤖 Calling OpenAI API (gpt-4o)...")
    client = OpenAI(api_key=api_key)
    
    prompt = f"""
You are an expert LaTeX typesetter and academic poster designer.
I have provided you with a Standard Operating Procedure (SOP) and a LaTeX template.

Here is the SOP:
{sop_content}

Here is the template:
```latex
{template_content}
```

Here is my outline:
{outline_content}

TASK:
Generate the final LaTeX code for the poster by filling in the template using the outline.
Adhere strictly to the SOP rules (especially regarding layout overflow and no hallucinations).
Output ONLY the raw LaTeX code block. Do not include markdown formatting or explanations.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        
        # Clean markdown code blocks if the model wrapped it
        latex_code = response.choices[0].message.content
        if latex_code.startswith("```latex"):
            latex_code = latex_code[8:]
        if latex_code.startswith("```"):
            latex_code = latex_code[3:]
        if latex_code.endswith("```"):
            latex_code = latex_code[:-3]
            
        with open(output_tex, 'w', encoding='utf-8') as f:
            f.write(latex_code.strip())
            
        print(f"✅ Generated LaTeX successfully saved to: {output_tex}")
        
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        sys.exit(1)
        
    # 4. Compile
    print("🔨 Compiling PDF with Tectonic...")
    try:
        subprocess.run(["tectonic", output_tex], check=True)
        print("🎉 Success! PDF compiled successfully.")
    except subprocess.CalledProcessError:
        print("⚠️ Warning: Tectonic compilation failed. Please check the terminal output for LaTeX errors.")
    except FileNotFoundError:
        print("⚠️ Warning: 'tectonic' not found. Please compile the poster.tex manually.")

if __name__ == "__main__":
    main()
