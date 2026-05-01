#!/usr/bin/env python3
"""
Step 3: Evaluator Agent (Judge)
Reads the generated poster.tex and checks it against deterministic rules
(forbidden syntax, missing figures) and LLM-based rubric checks.
Outputs PASS or a list of issues to problem.md.
"""

import os
import sys
import re
import argparse
from openai import OpenAI
import keyring

SERVICE_NAME = "AutoPoster-Agent"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

def deterministic_checks(tex_content, outline_content):
    """Run Python-based deterministic checks."""
    problems = []

    # 1. Ghost Padding checks (Forbidden syntax)
    if r"\begin{figure}" in tex_content:
        problems.append("FATAL ERROR: Found `\\begin{figure}` in poster.tex. This causes ghost padding. Use `\\begin{center}\\begin{minipage}` instead.")
    if r"\begin{table}" in tex_content:
        problems.append("FATAL ERROR: Found `\\begin{table}` in poster.tex. This causes ghost padding. Use `\\begin{center}\\begin{tabularx}` instead.")

    # 2. Extract expected figures from outline and check if they are in tex
    expected_figures = re.findall(r'`(figures/[^`]+)`', outline_content)
    # also try to find lines like "- figures/xxx.png"
    expected_figures += re.findall(r'- (figures/[^\s]+)', outline_content)
    expected_figures = list(set(expected_figures))

    for fig in expected_figures:
        # Strip extensions to be safe since \includegraphics might not use extension
        fig_base = os.path.splitext(fig)[0]
        if fig_base not in tex_content:
            problems.append(f"MISSING FIGURE: The outline requested `{fig}` but it is not included in poster.tex via `\\includegraphics`.")

    return problems

def evaluate_poster(tex_file, outline_file, output_file, model="gpt-4o", base_url=None):
    tex_content = load_file(tex_file)
    outline_content = load_file(outline_file)
    rubric_content = load_file(os.path.join(SCRIPT_DIR, "templates", "prompt_sops", "rubric_evaluator.md"))

    if not tex_content:
        print(f"❌ Error: {tex_file} not found.")
        sys.exit(1)

    print("🔍 Running Python Deterministic Checks...")
    problems = deterministic_checks(tex_content, outline_content)

    api_key = keyring.get_password(SERVICE_NAME, "OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: API Key not found.")
        sys.exit(1)

    prompt = f"""You are the Evaluator Agent. Evaluate the following generated LaTeX code against the Rubric and Outline.

RUBRIC:
{rubric_content}

USER OUTLINE:
{outline_content}

GENERATED LATEX:
```latex
{tex_content}
```

PYTHON DETERMINISTIC CHECK RESULTS (If any, you MUST include these in your FAIL report):
{chr(10).join(problems) if problems else "None."}

TASK:
Decide if the poster passes all Rubric constraints and Python checks.
If it passes everything, output exactly: PASS
If it fails, output `FAIL` on the first line, and list the issues to fix.
"""

    print(f"⚖️  Calling Evaluator Agent ({model}) for Rubric verification...")
    client_kwargs = {"api_key": api_key}
    if base_url:
        client_kwargs["base_url"] = base_url
    client = OpenAI(**client_kwargs)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=2000,
        )

        evaluation = response.choices[0].message.content.strip()

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(evaluation + "\n")

        if evaluation.startswith("PASS"):
            print(f"✅ Evaluator Agent: PASS")
            return True
        else:
            print(f"❌ Evaluator Agent: FAIL. Issues written to {output_file}")
            return False

    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Step 3: Evaluate generated poster.")
    parser.add_argument("tex_file", help="Path to generated .tex file.")
    parser.add_argument("outline_file", help="Path to outline file.")
    parser.add_argument("-o", "--output", default="problem.md", help="Output problem file.")
    parser.add_argument("--model", default="gpt-4o", help="LLM model.")
    parser.add_argument("--base-url", default=None, help="Custom API endpoint.")
    
    args = parser.parse_args()
    evaluate_poster(args.tex_file, args.outline_file, args.output, args.model, args.base_url)
