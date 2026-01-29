# ⚡ Canvas Automation - Quick Start Guide

## 🎯 What This Does

Every morning at 7 AM, you get a Telegram message with:
- ✅ All assignments due in next 3 days
- ✅ 🚨 Tests/exams highlighted with priority symbol
- ✅ AI-generated action plans for each assignment
- ✅ Countdown timers ("Due in 6 hours")
- ✅ Pro tips for maximizing grades

**Plus:** On-demand AI study guide generator for tests!

---

## 🚀 Quick Commands

### Daily Check (Manual)
```powershell
cd $env:USERPROFILE\.claude\automations
.\test-canvas-planner.ps1
```
*Get instant update of what's due in next 3 days*

### Create Study Guide
```powershell
.\\scripts\\ask-canvas.ps1 "midterm exam"
.\\scripts\\ask-canvas.ps1 "chapter 5 quiz"
.\\scripts\\ask-canvas.ps1 "final"
```
*Generates AI study guide as Word document*

---

## 📱 What You'll Get in Telegram

### Example: Normal Assignment
```
📋 MGMT 335: Strategic Consulting
📋 Weekly Discussion Post

⏰ Due tomorrow at 11:59 PM
⭐ Points: 10
⏱️ Estimated Time: 30-45 minutes

🎯 Action Plan:
1. 💬 Read this week's prompt
2. 📚 Review 2-3 peer posts
3. ✍️ Draft 250-word response
4. 🤝 Reply to 2 classmates

💡 Pro Tips:
• Reference course readings
• Use specific examples
```

### Example: Test/Exam
```
🚨 ACCT 382: Accounting Systems
📋 Midterm Exam

⏰ Due in 2 days (Jan 27 at 2:00 PM)
⭐ Points: 100
⏱️ Estimated Time: 3-4 hours study

🎯 Action Plan:
[AI-generated study plan]

💡 Pro Tips:
[Grade-maximizing tips]

💬 Type: TEST/EXAM
Reply 'study guide for Midterm Exam' for AI materials!
```

---

## 📚 Study Guide Generator

When you see a test notification, generate a study guide:

```powershell
.\\scripts\\ask-canvas.ps1 "Midterm Exam"
```

**What happens:**
1. 🔍 Searches Canvas for that test
2. 📚 Fetches all course resources (slides, practice tests, chapters)
3. 🤖 AI analyzes and creates comprehensive study guide
4. 📄 Saves as Word document in `Documents/Canvas Study Guides/`
5. 📱 Sends you Telegram notification with file path

**Study guide includes:**
- Key topics to master (5-8 concepts)
- 5-7 day study timeline
- Focus areas (what to prioritize)
- Practice strategies
- Quick reference (formulas, definitions)
- Common mistakes to avoid
- Full list of course resources

---

## 🎨 Priority Symbols

| Symbol | What It Means |
|--------|---------------|
| 🚨 | **TEST/EXAM** - Study guide available |
| ⚠️ | **Due TODAY** - Urgent! |
| 📌 | **Due tomorrow** - Start now |
| 📋 | **Regular assignment** |

---

## ⚙️ One-Time Setup (Already Done!)

✅ Daily planner runs automatically at 7 AM
✅ Telegram bot configured
✅ Canvas API connected (both instances)
✅ OpenAI GPT-4o-mini integrated

---

## 💡 Best Practices

### Sunday Night Routine
1. Run `.\test-canvas-planner.ps1` manually
2. See what's due this week
3. Generate study guides for any tests
4. Plan your week!

### When You See a Test
```powershell
.\\scripts\\ask-canvas.ps1 "name of test"
```
Generate study guide 5-7 days early for best results.

### Customization
Want notifications at different time? Edit `setup-task-scheduler.ps1`
Want 7-day lookahead instead of 3? Edit `daily-canvas-planner.py`

---

## 📞 Quick Support

**No Telegram notification?**
- Check you messaged the bot first
- Verify in `C:\Users\bryso\.claude\credentials\telegram.json`

**Study guide says "not found"?**
- Try shorter search: "midterm" instead of "accounting midterm exam"
- Check Canvas to see if assignment is published

**Want to test it now?**
```powershell
.\test-canvas-planner.ps1
```

---

## 🎯 Full Documentation

See `FEATURES.md` for complete details!

**Happy studying!** 🤖
