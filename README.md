# 🤖 Canvas Automation System

Complete AI-powered Canvas LMS automation with daily notifications and on-demand study guides.

## 🌟 Two Main Features

### 1️⃣ **Daily Canvas Planner** (Automatic)
Runs at 7:00 AM every day

### 2️⃣ **AI Study Guide Generator** (On-Demand)
Creates comprehensive study guides for tests

---

## 🎯 Daily Planner - What It Does

Every day at **7:00 AM**, this automation:

1. ✅ Connects to **both** your Canvas instances (Academic + Community)
2. 📊 Fetches all assignments due in **next 3 days**
3. 🚨 **Identifies and highlights tests/exams** with priority symbols
4. ⏰ Shows **countdown timers** ("Due in 6 hours", "Due tomorrow at 3 PM")
5. 🤖 For each assignment:
   - Uses **GPT-4o-mini AI** to analyze the requirements
   - Estimates realistic completion time
   - Generates a personalized step-by-step action plan
   - Provides pro tips for maximizing your grade
6. 📱 Sends you a Telegram message with:
   - **Priority symbol** (🚨 for tests, ⚠️ for urgent, 📌 for tomorrow, 📋 for normal)
   - **Human-readable countdown** ("Due in 2 days at 3:00 PM")
   - Assignment name, course, and points
   - **AI-generated time estimate**
   - Quick summary
   - **AI-generated personalized action plan**
   - **AI pro tips for maximizing your grade**
   - **Study guide prompt** for tests/exams
   - Direct link to Canvas

---

## 📚 Study Guide Generator - How It Works

**When you see a test/exam notification, generate an AI study guide:**

```powershell
cd $env:USERPROFILE\.claude\automations
.\\scripts\\ask-canvas.ps1 "Midterm Exam"
.\\scripts\\ask-canvas.ps1 "Chapter 5 Quiz"
```

**What it does:**
1. 🔍 Searches Canvas for your test/exam
2. 📚 Fetches all course resources (slides, practice tests, readings)
3. 🤖 Uses GPT-4o-mini to create comprehensive study guide
4. 📄 Generates professional Word document (.docx)
5. 📱 Sends Telegram notification with file location

**Study guide includes:**
- Key topics to master (5-8 main concepts)
- Recommended study timeline (3-7 days)
- Focus areas and priorities
- Practice strategies
- Quick reference (formulas, definitions, frameworks)
- Common mistakes to avoid
- Complete list of available course resources

**Saved to:** `C:\Users\bryso\Documents\Canvas Study Guides\`

## 📋 Files

- **`daily-canvas-planner.py`** - Main Python script that does the work
- **`setup-task-scheduler.ps1`** - PowerShell script to set up Windows Task Scheduler
- **`test-canvas-planner.ps1`** - Test script to run manually
- **`README.md`** - This file

## ⚡ Quick Setup (5 minutes)

### Step 1: Install Python Dependencies

```powershell
pip install requests openai
```

### Step 2: Set Up Task Scheduler

Run this PowerShell command **as Administrator**:

```powershell
cd $env:USERPROFILE\.claude\automations
.\setup-task-scheduler.ps1
```

This creates a scheduled task that runs at 7:00 AM every day.

### Step 3: Test It Now

```powershell
.\test-canvas-planner.ps1
```

You should receive a Telegram notification within seconds!

## 🎨 Example Telegram Notification

```
📚 Daily Canvas Update
📅 Saturday, January 25, 2026

⚠️ 2 assignments due today!

---

🎓 MGMT 335: Strategic Consulting & Analysis
📋 Problem Memo & Pitch

⏰ Due: 2026-01-25T10:00:00Z
⭐ Points: 80
⏱️ Estimated Time: 2-4 hours

📝 Summary:
Create a comprehensive problem memo identifying a strategic issue
and propose a solution with supporting analysis...

🎯 Action Plan:
1. 📖 Review assignment requirements and rubric
2. 📝 Research topic and gather sources
3. ✍️ Create outline and thesis statement
4. 🖊️ Write first draft
5. 🔍 Revise and proofread
6. 🚀 Submit before deadline

🔗 [Open in Canvas](https://uoregon.instructure.com/...)
```

## 🔧 Customization

### Change the Time

Edit the trigger in `setup-task-scheduler.ps1`:

```powershell
$Trigger = New-ScheduledTaskTrigger -Daily -At 6:00AM  # Change to 6 AM
```

Then re-run the setup script.

### Change Time Estimates

Edit the `estimate_time_to_complete()` function in `daily-canvas-planner.py`:

```python
# Adjust the heuristic
hours = (points / 100) * 3  # Make estimates longer
```

### Customize Action Outlines

Edit the `generate_action_outline()` function to add/change steps based on assignment type.

## 🛠️ Troubleshooting

### "Python not found"

Install Python:
```powershell
winget install Python.Python.3.12
```

### "Module 'requests' not found"

Install dependencies:
```powershell
pip install requests
```

### "No assignments found" (but you know there are)

Check that:
1. Your Canvas API tokens are valid (`C:\Users\bryso\.claude\credentials\canvas.json`)
2. Assignments are published by instructors
3. Due dates are set correctly in Canvas

### "Telegram message not received"

1. Check your bot token and chat ID in `C:\Users\bryso\.claude\credentials\telegram.json`
2. Make sure you've started a conversation with your bot
3. Run the test script to see error messages

### Task not running automatically

1. Open Task Scheduler (Windows + R, type `taskschd.msc`)
2. Find "DailyCanvasPlanner" task
3. Right-click → Properties
4. Ensure "Run whether user is logged on or not" is checked
5. Ensure "Wake the computer to run this task" is checked

## 📊 Viewing Task History

1. Open Task Scheduler
2. Find "DailyCanvasPlanner"
3. Click "History" tab to see all runs

## 🔒 Security Notes

- ✅ Credentials are stored locally in `~/.claude/credentials/`
- ✅ Never committed to git (`.gitignore` is set)
- ✅ Only you have access to your Telegram bot
- ✅ Canvas API tokens are read-only

## 🚀 Advanced Features

### Run Multiple Times Per Day

Add more triggers to the task:

```powershell
$Trigger1 = New-ScheduledTaskTrigger -Daily -At 7:00AM
$Trigger2 = New-ScheduledTaskTrigger -Daily -At 12:00PM
$Trigger3 = New-ScheduledTaskTrigger -Daily -At 6:00PM

Register-ScheduledTask -TaskName $TaskName `
    -Action $Action `
    -Trigger @($Trigger1, $Trigger2, $Trigger3) `
    ...
```

### Check Upcoming Assignments (Next 7 Days)

Modify the `filter_due_today()` function to check a date range:

```python
def filter_due_this_week(assignments):
    today = datetime.now().date()
    week_from_now = today + timedelta(days=7)
    # ... filter logic
```

### Integrate with Project Architect

The script can be enhanced to call Claude API with the project-architect agent to generate even more detailed plans. (Future enhancement)

---

**Created:** 2026-01-25
**Maintained by:** Claude Code Automation


## Credentials

### Canvas API Keys
1. Sign in to each Canvas instance you want to monitor, go to **Account > Settings > Approved Integrations (Access Tokens)**, and click **+ New Access Token**.
2. Give it a descriptive name (e.g., "daily-canvas") and copy the token immediately; Canvas only shows it once.
3. Save the tokens in `~/.claude/credentials/canvas.json` using this structure (add one entry per Canvas instance):

```json
{
  "instances": [
    {
      "name": "UO Academic Canvas",
      "url": "https://uoregon.instructure.com",
      "api_token": "<paste-your-token-here>"
    },
    {
      "name": "UO Community Canvas",
      "url": "https://community.uoregon.edu",
      "api_token": "<token>"
    }
  ]
}
```
4. Keep the file private (it is already ignored by `.gitignore`) and never commit the tokens.

### OpenAI API Key
1. Visit https://platform.openai.com/account/api-keys, create a new API key, and copy it securely.
2. Save it inside `~/.claude/credentials/openai.json` like this:

```json
{
  "credentials": {
    "api_key": "sk-..."
  }
}
```
3. This key powers the GPT-4o-mini responses for both the planner and study guide generator. Keep it private.
