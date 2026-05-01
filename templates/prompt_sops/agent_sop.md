# SKILL: Agentic Academic Poster Generation SOP

This document serves as a Standard Operating Procedure (SOP) for AI Agents (like GPT-4o, Claude 3.5, Gemini 1.5, etc.) to construct a highly professional, 185x90cm Beamer-based academic poster based on an original LaTeX paper source and an outline.

## 1. Prerequisites
- **Source Material**: You must use the user-provided `outline.md` as the authoritative narrative structure, and any provided data files (e.g., `results.csv`, `data.xlsx`) for absolute data fidelity.
- **Template**: Use `academic_poster_template.tex` as the starting codebase. Do not reinvent the LaTeX Beamer block structure.

## 2. Strict Layout Rules & Pitfall Avoidance
During previous poster construction phases, severe rendering and formatting issues ("坑") were encountered. **You MUST adhere to these rules**:

### Ghost Padding & Overfull \vbox Crashing
1. **NEVER use the `\begin{table}` environment inside a Beamer `\begin{block}`.** The floating `table` environment injects massive, invisible `\abovecaptionskip` padding that breaks columns and pushes text off the page.
2. **Use `\begin{center}` + `\begin{tabularx}` instead.** If you need a table, wrap it in a `center` environment.
3. **Use Negative Vspace**: To tightly pack elements and counteract Beamer's default baseline paddings, strategically use `\vspace{-1ex}` to `\vspace{-3ex}`.
4. **Minipage for Figures**: Never use `\begin{figure}` floats for side-by-side images. Use `minipage` inside a block to guarantee horizontal fit.

### Aesthetic Branding & Alignment
1. **Header Alignment**: For badges in the header (like an "Oral" or "Spotlight" badge), use a `tcolorbox`. To perfectly align it with the main title, use negative vertical spacing right before the `tcolorbox`, and scale the inner text appropriately.
2. **Footer Overlap Tricks**: To create a modern overlap for a Contact QR code, use a nested raisebox: `\raisebox{-3.3cm}[0pt][0pt]{...}`. This allows elements to visually overlap without throwing `Overfull \vbox` errors.
3. **Professionalism**: Keep professional QR codes (like LinkedIn or GitHub) straight, large, and clean. Do not tilt or rotate them.

### Visual Cohesion & Readability
1. **Reference Formatting**: Place references at the *very bottom* of Column 1 (use `\vspace{-1cm}` before them to avoid dead space). Number them `[1]`, `[2]`, `[3]` and use inline citations in the text.
2. **Linking Split Blocks**: When a logical block spans multiple columns, explicitly label them as `(P1: Method)` and `(P2: Results)`. Use `\scalebox` to ensure titles maintain equal visual weight across columns.
3. **Data Metric Highlights**: When designing numeric callout cards (`tcolorbox`), avoid blinding pure red (`red!80!black`). Use a sophisticated highlight color (e.g., burnt orange, deep teal) to pop out against the main theme. Ensure the main numbers are massive (`\LARGE`).

## 3. Audit & Verification (Data Integrity & Zero Hallucination)
Before finalizing the poster, the AI Agent MUST perform a rigorous self-audit:

1. **Numerical Cross-Check**: Every single number, decimal point, and data table must strictly match the provided source documents. Do not round numbers differently than the source.
2. **Grammar & Typo Correction**: If the user-provided outline contains typos, you must silently correct the grammar/spelling in the poster but **never invent or alter empirical experimental data**.
3. **Citation Audit**: Ensure all references have their full author list and accurate identifiers (e.g., `arXiv` ID, DOI) verified before inclusion.
4. **Visual Build Audit**: After running `tectonic` or `pdflatex`, you MUST check the terminal output for `Overfull \vbox` or `Undefined control sequence` errors. A successful exit code (0) is not enough; warnings about layout vertical overflow must be addressed by tuning `\vspace` or `\scalebox`.

## 4. Automation Scripts (Embedded Tools)

### A. Figure Background Cleanser (`clean_figure_backgrounds.py`)
Screenshots or extracted PDFs often have ugly light-gray/yellowish backgrounds. A standalone Python utility script (`clean_figure_backgrounds.py`) is provided in the `tools/` directory.

You MUST run this script to force backgrounds to pure white (`255, 255, 255`) and strip alpha channels before embedding them in the poster.

```bash
python3 tools/clean_figure_backgrounds.py raw_figure1.png raw_figure2.png
```

### B. Build Pipeline
Use the `tectonic` engine to compile the LaTeX, as it automatically fetches required packages. Use macOS `sips`, Linux `pdftoppm`, or ImageMagick to verify the output.

```bash
# Compile LaTeX
tectonic poster.tex

# Convert PDF to PNG for visual verification (macOS)
sips -s format png poster.pdf --out poster.png

# Convert PDF to PNG (Linux / ImageMagick)
convert -density 300 poster.pdf poster.png
```

By following this skill prompt and utilizing the provided template, you will produce a flawlessly aligned, structurally sound, and data-accurate academic poster.
