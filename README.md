# AutoPoster-Agent

An open-source, general-purpose AI Agent framework and Beamer template for generating high-fidelity academic conference posters. 

Derived from a rigorous ICLR 2026 submission workflow, this tool provides AI Agents (like GPT-4o, Claude 3.5, Gemini 1.5) with the exact Standard Operating Procedure (SOP) needed to avoid common LaTeX rendering pitfalls, eradicate layout overflows ("Overfull \vbox"), and enforce strict academic data integrity (Zero Hallucination).

## Features

- **Agentic SOP (`agent_sop.md`)**: A battle-tested prompt for your LLMs that teaches them how to perfectly construct a 4-column academic poster without hallucinating numbers or breaking the layout.
- **Battle-Tested Template (`academic_poster_template.tex`)**: A highly polished, robust Beamer template optimized for 185x90cm conference printing. Avoids the "ghost padding" issues common in standard LaTeX templates.
- **Secure API Key Management**: Uses macOS Keychain integration so you never expose your LLM API Keys in plain text `.env` files.
- **Figure Pre-processing Tools**: Included scripts to strip gray/yellow backgrounds from PDF screenshots.

## Installation & Setup

### 1. One-Click Installation
We provide an `install.sh` script that automatically creates a Python virtual environment, installs the requirements, and launches the Keychain setup.

```bash
chmod +x install.sh
./install.sh
```

*(Manual alternative: `pip install -r requirements.txt` and `python setup_keychain.py`)*

*System Dependencies*: You must have a LaTeX compiler installed (we recommend [Tectonic](https://tectonic-typesetting.github.io/)).
```bash
# macOS
brew install tectonic
```

### 2. Secure Your API Keys (System Keychain)
If you ran `install.sh`, you were already prompted. Otherwise, run:
```bash
python setup_keychain.py
```
*You will be prompted to paste your OpenAI API Key. It will be stored securely in your system's Keychain (macOS, Windows, or Linux) under the service name `AutoPoster-Agent`.*

## Usage

### Fully Automated Agent Mode
We provide a Python runner script that reads your outline, grabs your securely stored API key, calls OpenAI (GPT-4o), populates the template according to the SOP, and compiles the LaTeX.

1. Create your `outline.md` summarizing the poster's content.
2. Ensure your `.venv` is activated: `source .venv/bin/activate`
3. Run the generator:
```bash
python generate_poster.py outline.md
```

### Manual IDE Mode (Cursor/Copilot)
1. Open your preferred AI code editor.
2. Include the `templates/prompt_sops/agent_sop.md` file in the Agent's context.
3. Provide the Agent with your `outline.md` and `templates/academic_poster_template.tex`.
4. Instruct the Agent: *"Use the agent_sop.md to fill out the academic_poster_template.tex with my outline."*

### Pre-processing Figures
Academic screenshots often have ugly off-white backgrounds. Clean them before embedding:
```bash
python tools/clean_figure_backgrounds.py path/to/raw_figure.png
```

### Compiling the Poster
Once the Agent generates your `.tex` file, compile it:
```bash
tectonic poster.tex
```

## Contributing
We welcome contributions to expand the SOPs and templates for other top-tier conferences (CVPR, NeurIPS, ACL).

## License
MIT License
