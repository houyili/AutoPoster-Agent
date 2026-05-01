#!/usr/bin/env python3
"""
Step 1: Outliner Agent
Reads a LaTeX paper source directory or file, and generates a structured outline.md
that determines which sections, figures, and tables to include in the poster.
"""

import os
import sys
import glob
import argparse
from openai import OpenAI
import keyring

SERVICE_NAME = "AutoPoster-Agent"

def load_tex_files(source_path):
    """Load all .tex files from a directory or a single file."""
    content = ""
    if os.path.isfile(source_path) and source_path.endswith('.tex'):
        with open(source_path, 'r', encoding='utf-8') as f:
            content += f"--- {os.path.basename(source_path)} ---\n"
            content += f.read() + "\n\n"
    elif os.path.isdir(source_path):
        tex_files = glob.glob(os.path.join(source_path, '**/*.tex'), recursive=True)
        for tf in tex_files:
            try:
                with open(tf, 'r', encoding='utf-8') as f:
                    content += f"--- {os.path.basename(tf)} ---\n"
                    content += f.read() + "\n\n"
            except Exception as e:
                print(f"Warning: Could not read {tf}: {e}")
    else:
        print(f"❌ Error: {source_path} is neither a .tex file nor a directory.")
        sys.exit(1)
    
    # Truncate if too massive (rough token limit protection)
    if len(content) > 300000:
        print("⚠️ Warning: Source paper is extremely large, truncating to ~100k tokens.")
        content = content[:300000]
        
    return content

def generate_outline(paper_content, output_file, model="gpt-4o", base_url=None):
    api_key = keyring.get_password(SERVICE_NAME, "OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: API Key not found in keychain. Run 'python setup_keychain.py'.")
        sys.exit(1)

    prompt = f"""You are an expert Academic Poster Synthesizer Agent.
Your task is to read the raw LaTeX source code of an academic paper and generate a concise, high-impact `outline.md` for a 4-column landscape poster.

### Task Requirements:
1. **Paper Metadata**: Extract Title, Authors, and Affiliations.
2. **Core Sections**:
   - Motivation & Research Question (extract the most critical gap).
   - Methodology (summarize the core steps).
   - Key Results (extract the absolute most important findings).
   - Conclusion (takeaways).
3. **Data Integrity (CRITICAL)**: If you extract metrics, accuracies, or numbers, you MUST quote them exactly as they appear in the paper. Do NOT hallucinate.
4. **Figures & Tables**:
   - Identify the most important figures (e.g., main architecture, main scaling curves) and explicitly list their filenames (e.g., `figures/main_result.png`).
   - Identify the most important summary table and include it in Markdown format.

### Output Format:
Output ONLY valid Markdown. Use the following structure:
```markdown
## Paper Metadata
- **Title**: ...
- **Authors**: ...

## 1. Motivation
...

## 2. Methodology
...

## 3. Key Results
...

## 4. Conclusion
...

## Figures to Include
- `figures/xxx.pdf` — Description
- `figures/yyy.png` — Description
```

### Raw Paper LaTeX Source:
{paper_content}
"""

    print(f"🤖 Calling Outliner Agent ({model})...")
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=4000,
        )

        outline_content = response.choices[0].message.content
        
        # Strip markdown code fences if present
        if outline_content.startswith("```markdown\n"):
            outline_content = outline_content[12:]
        if outline_content.endswith("\n```"):
            outline_content = outline_content[:-4]

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(outline_content.strip() + "\n")

        print(f"✅ Outline successfully generated and saved to: {output_file}")
        return True

    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 1: Generate outline from LaTeX source.")
    parser.add_argument("source", help="Path to LaTeX file or directory containing .tex files.")
    parser.add_argument("-o", "--output", default="outline.md", help="Output outline file.")
    parser.add_argument("--model", default="gpt-4o", help="LLM model.")
    parser.add_argument("--base-url", default=None, help="Custom API endpoint.")
    
    args = parser.parse_args()
    content = load_tex_files(args.source)
    if content:
        generate_outline(content, args.output, args.model, args.base_url)
