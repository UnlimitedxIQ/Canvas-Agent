# Canvas Automation Project

## Overview
This project is an automated Canvas LMS assignment tracker and study guide generator. It connects to Canvas (university learning management system), fetches upcoming assignments, and sends notifications via Telegram. When midterms or finals are detected, it automatically generates AI-powered study guides.

## Core Components

### 1. Telegram Bot Listener (`telegram-bot-listener.py`)
- Runs as a persistent server that listens for Telegram commands
- Responds to commands like `TEST`, `/status`, `/help`
- When `TEST` is received, triggers the daily canvas planner pipeline
- Streams pipeline output to the terminal in real-time
- Configured to start automatically on Windows login via Startup folder shortcut

### 2. Daily Canvas Planner (`daily-canvas-planner.py`)
The main pipeline that:
- Connects to Canvas instances (UO Academic and Community Canvas)
- Fetches assignments from both the Planner API and Assignments API
- Filters to show only assignments due in the next 3 days
- Detects midterms/finals based on keywords (midterm, final, exam) and Respondus LockDown Browser
- Generates AI action plans for each assignment using GPT-4o-mini
- Sends a consolidated summary to Telegram
- Auto-generates comprehensive study guides for detected exams

### 3. Auto Study Guide Generator (`auto-study-guide-generator.py`)
- Downloads all course materials (modules, files, pages) before the exam date
- Uses AI to generate comprehensive study guides with:
  - Key concepts organized by topic
  - Important theories and ideas
  - 70-100 multiple choice practice questions
  - Answer key
- Saves as .docx file and sends via Telegram

## Supporting Files

### Startup & Configuration
- `start_bot.bat` - Batch file to launch the Telegram bot server
- `setup_autostart.ps1` - Creates Windows Task Scheduler task (requires admin)
- `create_startup_shortcut.ps1` - Creates Startup folder shortcut (no admin needed)
- `Secrets/.env` - Contains Telegram bot token and chat ID

### Credentials (stored in `~/.claude/credentials/`)
- `canvas.json` - Canvas API tokens for each instance
- `telegram.json` - Telegram bot tokens and chat IDs
- `openai.json` - OpenAI API key for GPT-4o-mini

### Debug & Testing Scripts
- `debug-assignments.py` - Debug Canvas assignment fetching
- `scan-next-3-days.py` - Test the 3-day filter logic
- `test-*.py` - Various test scripts for quizzes and GraphQL

## How It Works

1. **User sends `TEST` to Telegram bot**
2. **Bot triggers the pipeline**
3. **Pipeline connects to Canvas:**
   - Fetches from Planner API (dashboard items)
   - Fetches from Assignments API (all published assignments)
   - Scans each active course
4. **Filters assignments:**
   - Only keeps assignments due in next 3.5 days
   - Sorts by due date (earliest first)
5. **Checks for exams:**
   - Looks for keywords: midterm, final, exam
   - Checks for Respondus LockDown Browser mentions
   - High point value exams (50+ points)
6. **Generates study guides for exams:**
   - Downloads course materials
   - Calls OpenAI API to create comprehensive guide
   - Saves as .docx file
7. **Sends Telegram notifications:**
   - Summary of all upcoming assignments grouped by date
   - Study guide files attached for any detected exams

## Terminal Output
When running, the terminal shows:
- Canvas connection status
- Number of assignments found per course
- Filtered assignments with due dates
- Detected midterms/finals
- Study guide generation progress
- Telegram notification status

## File Locations
- Study guides saved to: `C:\Users\bryso\Documents\Canvas Study Guides\`
- Bot runs from: `C:\Users\bryso\.claude\automations\auto_canvas\`
