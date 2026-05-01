#!/usr/bin/env python3
"""
AutoPoster-Agent Master Orchestrator (Agent Loop)
Automatically outlines, generates, and evaluates academic posters.
Includes a retry mechanism (MAX_RETRIES) using problem.md feedback.
"""

import os
import sys
import argparse
import subprocess

MAX_RETRIES = 3
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def run_command(cmd_list, description):
    print(f"\n[{description}]")
    print(" ".join(cmd_list))
    result = subprocess.run(cmd_list)
    if result.returncode != 0:
        print(f"❌ Error during {description}.")
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="AutoPoster-Agent Master Loop")
    parser.add_argument("source", help="Path to LaTeX source file/dir OR existing outline.md.")
    parser.add_argument("--figures-dir", default=None, help="Directory containing images.")
    parser.add_argument("--model", default="gpt-4o", help="LLM Model.")
    parser.add_argument("--base-url", default=None, help="Custom API Endpoint.")
    args = parser.parse_args()

    print("=========================================")
    print("  🚀 AutoPoster-Agent Autonomous Loop")
    print("=========================================")

    outline_file = "outline.md"
    tex_file = "poster.tex"
    problem_file = "problem.md"

    # Step 1: Outliner (if source is not already an outline.md)
    if os.path.isdir(args.source) or args.source.endswith(".tex"):
        print("\n--- STEP 1: Academic Synthesizer (Outliner) ---")
        cmd = [sys.executable, os.path.join(SCRIPT_DIR, "step1_outliner.py"), args.source, "-o", outline_file, "--model", args.model]
        if args.base_url: cmd.extend(["--base-url", args.base_url])
        if not run_command(cmd, "Generating Outline"): sys.exit(1)
    else:
        outline_file = args.source
        print(f"\n--- STEP 1 SKIP: Using existing outline ({outline_file}) ---")

    # The Retry Loop (Steps 2 & 3)
    attempt = 1
    while attempt <= MAX_RETRIES:
        print(f"\n=========================================")
        print(f"  🔄 LOOP ITERATION {attempt} / {MAX_RETRIES}")
        print(f"=========================================")

        # Step 2: Generator
        print("\n--- STEP 2: LaTeX Typesetter (Generator) ---")
        cmd = [sys.executable, os.path.join(SCRIPT_DIR, "step2_generator.py"), outline_file, "-o", tex_file, "--problem", problem_file, "--model", args.model]
        if args.figures_dir: cmd.extend(["--figures-dir", args.figures_dir])
        if args.base_url: cmd.extend(["--base-url", args.base_url])
        if not run_command(cmd, "Generating LaTeX & Compiling"):
            # If tectonic fails completely, it's still worth evaluating to see why.
            print("⚠️ Generator had issues (possibly compilation failed). Continuing to Evaluator...")

        # Step 3: Evaluator
        print("\n--- STEP 3: Reviewer (Evaluator) ---")
        cmd = [sys.executable, os.path.join(SCRIPT_DIR, "step3_evaluator.py"), tex_file, outline_file, "-o", problem_file, "--model", args.model]
        if args.base_url: cmd.extend(["--base-url", args.base_url])
        run_command(cmd, "Evaluating Poster")

        # Step 4: Check Results
        if os.path.isfile(problem_file):
            with open(problem_file, 'r', encoding='utf-8') as f:
                content = f.read()
            if content.strip().startswith("PASS"):
                print("\n🎉 SUCCESS: The poster passed all rigorous audits!")
                print(f"📄 Final output: {tex_file.replace('.tex', '.pdf')}")
                # Clean up problem.md on success
                os.remove(problem_file)
                sys.exit(0)
            else:
                print(f"\n⚠️ Evaluator found issues. (See {problem_file})")
                print("   Feedback will be provided to the Generator in the next iteration.")
        
        attempt += 1

    print(f"\n❌ MAX RETRIES REACHED ({MAX_RETRIES}).")
    print("The agent could not perfectly fix the poster within the limit. Preserving the last attempt.")
    sys.exit(1)

if __name__ == "__main__":
    main()
