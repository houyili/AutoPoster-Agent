#!/usr/bin/env python3
"""
AutoPoster-Agent Step 2: Generator Agent

Reads your outline, retrieves your API key, and calls an LLM to populate 
the LaTeX template following the SOP. If a problem.md file exists (from Step 3), 
it will use it to correct the previous mistakes.

Supports any OpenAI-compatible API endpoint (OpenAI, Anthropic via proxy,
local vLLM, Ollama, etc.) via --base-url.
"""

import os
import sys
import glob
import argparse
import subprocess
import shutil

try:
    import keyring
except ImportError:
    print("❌ Error: 'keyring' not installed. Run: pip install keyring")
    sys.exit(1)

try:
    from openai import OpenAI
except ImportError:
    print("❌ Error: 'openai' not installed. Run: pip install openai")
    sys.exit(1)

SERVICE_NAME = "AutoPoster-Agent"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_file(filepath):
    """Load a text file, exit with error if not found."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: File not found - {filepath}")
        sys.exit(1)


def discover_figures(figures_dir):
    """Scan a directory for image files, copy them to local 'figures/', and return listing."""
    if not figures_dir or not os.path.isdir(figures_dir):
        return ""
    
    local_fig_dir = "figures"
    os.makedirs(local_fig_dir, exist_ok=True)
    
    extensions = ("*.png", "*.jpg", "*.jpeg", "*.pdf", "*.svg")
    files = []
    for ext in extensions:
        files.extend(glob.glob(os.path.join(figures_dir, ext)))
    if not files:
        return ""
    
    copied_files = []
    for f in files:
        basename = os.path.basename(f)
        dest_path = os.path.join(local_fig_dir, basename)
        shutil.copy2(f, dest_path)
        copied_files.append(basename)
        
    listing = "\n".join(f"  - figures/{f}" for f in sorted(copied_files))
    return f"\n\nAVAILABLE FIGURES (use these exact filenames in \\includegraphics):\n{listing}\n"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Step 2: Generate an academic poster from an outline."
    )
    parser.add_argument("outline", help="Path to the outline markdown file.")
    parser.add_argument("--problem", default="problem.md", help="Path to feedback file from Step 3.")
    parser.add_argument(
        "-o", "--output", default="poster.tex",
        help="Output .tex filename (default: poster.tex)"
    )
    parser.add_argument(
        "--model", default="gpt-4o",
        help="LLM model name (default: gpt-4o). Works with any OpenAI-compatible API."
    )
    parser.add_argument(
        "--base-url", default=None,
        help="Custom API base URL for OpenAI-compatible endpoints "
             "(e.g., http://localhost:8000/v1 for vLLM, or Anthropic proxy)."
    )
    parser.add_argument(
        "--figures-dir", default=None,
        help="Directory containing figure images to embed. "
             "Filenames will be listed in the prompt so the LLM references them correctly."
    )
    parser.add_argument(
        "--api-key", default=None,
        help="API key (overrides keychain). NOT recommended — use keychain instead."
    )
    parser.add_argument(
        "--no-compile", action="store_true",
        help="Skip automatic PDF compilation with tectonic."
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("=========================================")
    print("  Step 2: Generator Agent")
    print("=========================================")

    # 1. Get API Key
    api_key = args.api_key
    if not api_key:
        api_key = keyring.get_password(SERVICE_NAME, "OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: API Key not found in keychain or OPENAI_API_KEY env var. Run 'python setup_keychain.py'.")
        print("   Option 2: Pass --api-key <KEY> (not recommended for security).")
        sys.exit(1)

    # 2. Load Assets
    print(f"📄 Loading outline: {args.outline}")
    outline_content = load_file(args.outline)

    sop_path = os.path.join(SCRIPT_DIR, "templates", "prompt_sops", "agent_sop.md")
    template_path = os.path.join(SCRIPT_DIR, "templates", "academic_poster_template.tex")
    sop_content = load_file(sop_path)
    template_content = load_file(template_path)

    # 3. Discover figures
    figures_listing = discover_figures(args.figures_dir)
    if figures_listing:
        print(f"🖼️  Found figures in: {args.figures_dir}")

    # 3.5 Read problem.md if it exists
    problem_feedback = ""
    if os.path.isfile(args.problem):
        problem_content = load_file(args.problem)
        if problem_content.strip() and problem_content.strip() != "PASS":
            print(f"⚠️  Found feedback in {args.problem}, adapting prompt to fix previous errors.")
            problem_feedback = f"""
CRITICAL FEEDBACK FROM PREVIOUS ATTEMPT:
Your previous output failed the evaluator's checks. You MUST fix these issues in this iteration:
---
{problem_content}
---
Ensure you do not repeat the mistakes listed above!
"""

    # 4. Build prompt
    prompt = f"""You are an expert LaTeX typesetter and academic poster designer.

STANDARD OPERATING PROCEDURE (follow strictly):
{sop_content}

LATEX TEMPLATE (fill in the placeholders):
```latex
{template_content}
```

USER'S POSTER OUTLINE:
{outline_content}
{figures_listing}
{problem_feedback}

TASK:
1. Read the SOP rules carefully — especially the anti-patterns around ghost padding.
2. Fill in the LaTeX template using the outline content.
3. Replace ALL {{{{PLACEHOLDER}}}} variables with real content from the outline.
4. Reference actual figure filenames from the AVAILABLE FIGURES list above.
5. Output ONLY raw LaTeX code. No markdown fences, no explanations.
"""

    # 5. Call LLM
    print(f"🤖 Calling {args.model}...")
    client_kwargs = {"api_key": api_key}
    if args.base_url:
        client_kwargs["base_url"] = args.base_url
    client = OpenAI(**client_kwargs)

    try:
        response = client.chat.completions.create(
            model=args.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=16384,
        )

        latex_code = response.choices[0].message.content

        # Strip markdown code fences if present
        for fence in ("```latex\n", "```tex\n", "```\n"):
            if latex_code.startswith(fence):
                latex_code = latex_code[len(fence):]
                break
        if latex_code.rstrip().endswith("```"):
            latex_code = latex_code.rstrip()[:-3]

        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(latex_code.strip() + "\n")

        print(f"✅ LaTeX saved to: {args.output}")

    except Exception as e:
        print(f"❌ API Error: {e}")
        sys.exit(1)

    # 6. Compile
    if not args.no_compile:
        print("🔨 Compiling PDF with tectonic...")
        try:
            result = subprocess.run(
                ["tectonic", args.output],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                # Check for Overfull warnings (SOP rule 3.4)
                if "Overfull" in result.stderr:
                    print("⚠️  Compiled successfully, but Overfull warnings detected:")
                    for line in result.stderr.splitlines():
                        if "Overfull" in line:
                            print(f"   {line.strip()}")
                else:
                    pdf_name = args.output.replace(".tex", ".pdf")
                    print(f"🎉 Success! PDF generated: {pdf_name}")
            else:
                print("⚠️  Compilation failed. Errors:")
                print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
        except FileNotFoundError:
            print("⚠️  'tectonic' not found. Please compile manually:")
            print(f"   tectonic {args.output}")
    else:
        print("⏭️  Skipping compilation (--no-compile).")


if __name__ == "__main__":
    main()
