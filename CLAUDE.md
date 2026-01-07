# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Grade-Pipeline is an automated homework grading system for programming assignments. It uses OpenAI's GPT models to grade student code submissions and generates detailed reports.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Grade all students in a homework set
python main.py homework/week15

# Grade specific students (regrade mode)
python main.py homework/week15 -r 2021001 2021002

# Regrade failed submissions
python main.py homework/week15 -f

# Custom output directory
python main.py homework/week15 -o output/
```

## Configuration

Copy `.env.example` to `.env` and set:
- `OPENAI_API_KEY` (required)
- `OPENAI_BASE_URL` (optional, for proxy services)
- `OPENAI_MODEL` (default: gpt-4)
- `MAX_TOKENS`, `TEMPERATURE` (optional tuning)

## Architecture

```
src/
├── pipeline.py      # GradingPipeline - orchestrates the grading workflow
├── grader.py        # Grader - calls OpenAI API, GradingResult dataclass
├── config.py        # Config - env-based configuration, grading prompt template
├── file_reader.py   # File reading utilities for homework and submissions
├── output_writer.py # JSON and Markdown report generation
└── result_manager.py # Result tracking, merging for regrade operations
```

**Flow**: `main.py` → `GradingPipeline.run()` → `Grader.grade_assignment()` per student → results saved as JSON + Markdown

## Homework Directory Structure

```
homework/weekN/
├── statements/          # Problem description
│   ├── homework.md      # Required: assignment description with grading criteria
│   └── *.h/*.cpp        # Optional: attachment files
├── assignments/         # Student submissions
│   ├── student_id_1/
│   └── student_id_2/
└── results/             # Generated output
    ├── results.json
    └── report.md
```

## Key Implementation Details

- Grader uses structured JSON prompts and parses responses with regex fallbacks for robustness
- Regrade mode (`-r`, `-f`) merges new results with existing `results.json` rather than replacing
- Exponential backoff retry (up to 3 attempts) for API failures
- Progress bar via tqdm during batch grading
