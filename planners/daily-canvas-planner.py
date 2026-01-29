#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Canvas Assignment Planner with AI-Powered Action Plans
Automatically fetches today's Canvas assignments, uses GPT-4o-mini to generate intelligent action plans,
and sends Telegram notifications.
"""

import json
import requests
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import os
import sys
import re
import importlib.util
from pathlib import Path

# Fix Windows console encoding for emojis
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

# Load credentials
CREDENTIALS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "credentials")
AUTO_CANVAS_ROOT = Path(__file__).resolve().parents[1]

def load_json(filename):
    """Load JSON credentials file"""
    path = os.path.join(CREDENTIALS_DIR, filename)
    with open(path, 'r') as f:
        return json.load(f)

# Load all credentials
canvas_creds = load_json("canvas.json")
telegram_creds = load_json("telegram.json")
openai_creds = load_json("openai.json")

# Canvas API Setup
CANVAS_INSTANCES = canvas_creds["instances"]

# Telegram Setup (use Canvas Planner bot)
TELEGRAM_BOT_TOKEN = telegram_creds["bots"]["canvas_planner"]["bot_token"]
TELEGRAM_CHAT_ID = telegram_creds["bots"]["canvas_planner"]["chat_id"]

# OpenAI Setup
OPENAI_API_KEY = openai_creds["credentials"]["api_key"]

def send_telegram_message(message):
    """Send a message via Telegram bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        return False

def send_telegram_document(file_path, caption=""):
    """Send a document file via Telegram bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"

    try:
        with open(file_path, 'rb') as file:
            files = {'document': file}
            data = {
                'chat_id': TELEGRAM_CHAT_ID,
                'caption': caption,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, files=files, data=data)
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error sending Telegram document: {e}")
        return False

def get_canvas_all_items(canvas_url, api_token):
    """Fetch ALL assignments from Canvas (planner + assignments APIs)"""
    headers = {"Authorization": f"Bearer {api_token}"}
    all_items = []
    seen_items = set()  # Track duplicates

    try:
        # Method 1: Planner API (gets dashboard items)
        print("   [1/2] Fetching from Planner API...")
        now = datetime.now()
        start_date = now.strftime('%Y-%m-%d')
        end_date = (now + timedelta(days=7)).strftime('%Y-%m-%d')

        planner_url = f"{canvas_url}/api/v1/planner/items?start_date={start_date}&end_date={end_date}"
        planner_response = requests.get(planner_url, headers=headers)

        if planner_response.status_code == 200:
            planner_items = planner_response.json()
            print(f"         Found {len(planner_items)} planner items")

            for item in planner_items:
                plannable = item.get('plannable', {})

                assignment = {
                    'name': plannable.get('title', 'Unnamed'),
                    'due_at': item.get('plannable_date'),
                    'points_possible': plannable.get('points_possible', 0),
                    'course_name': item.get('context_name', 'Unknown'),
                    'html_url': plannable.get('html_url', '#'),
                    'description': plannable.get('description', ''),
                }

                # Track to avoid duplicates
                item_key = f"{assignment['name']}_{assignment['due_at']}"
                if item_key not in seen_items:
                    seen_items.add(item_key)
                    all_items.append(assignment)

        # Method 2: Assignments API (gets published assignments, including ones not in planner)
        print("   [2/2] Fetching from Assignments API...")
        courses_url = f"{canvas_url}/api/v1/courses?enrollment_state=active&per_page=100"
        courses_response = requests.get(courses_url, headers=headers)

        if courses_response.status_code == 200:
            courses = courses_response.json()
            print(f"         Scanning {len(courses)} courses...")

            for course in courses:
                if 'id' not in course:
                    continue

                # Skip old courses
                workflow_state = course.get('workflow_state', '')
                if workflow_state in ['completed', 'deleted']:
                    continue

                course_name = course.get('name', 'Unknown')
                # Get assignments
                assignments_url = f"{canvas_url}/api/v1/courses/{course['id']}/assignments?per_page=100"
                assignments_response = requests.get(assignments_url, headers=headers)

                if assignments_response.status_code == 200:
                    course_assignments = assignments_response.json()
                    added_count = 0
                    for a in course_assignments:
                        if not a.get('due_at'):
                            continue

                        assignment = {
                            'name': a.get('name', 'Unnamed'),
                            'due_at': a.get('due_at'),
                            'points_possible': a.get('points_possible', 0),
                            'course_name': course.get('name', 'Unknown'),
                            'html_url': a.get('html_url', '#'),
                            'description': a.get('description', ''),
                        }

                        # Only add if not already from planner
                        item_key = f"{assignment['name']}_{assignment['due_at']}"
                        if item_key not in seen_items:
                            seen_items.add(item_key)
                            all_items.append(assignment)
                            added_count += 1

                    if added_count > 0:
                        print(f"         + {course_name}: {added_count} assignments")

        return all_items
    except Exception as e:
        print(f"Error fetching Canvas items: {e}")
        return []

def filter_due_next_3_days(assignments):
    """Filter assignments due in the next 3 days (includes early morning on day 4)"""
    print("\n--- Filtering assignments due in next 3 days ---")
    # Get current time in Pacific timezone
    pacific_tz = ZoneInfo("America/Los_Angeles")
    now = datetime.now(pacific_tz)
    today = now.date()

    # Include up to 3.5 days to catch early morning assignments (like 1:50 AM on day 4)
    cutoff_datetime = now + timedelta(days=3, hours=12)
    print(f"   Cutoff: {cutoff_datetime.strftime('%Y-%m-%d %I:%M %p')}")

    due_soon = []

    for assignment in assignments:
        if not assignment.get('due_at'):
            continue

        try:
            # Parse Canvas date format (UTC): 2026-01-25T10:00:00Z
            due_datetime_utc = datetime.strptime(assignment['due_at'], "%Y-%m-%dT%H:%M:%SZ")
            due_datetime_utc = due_datetime_utc.replace(tzinfo=timezone.utc)

            # Convert to Pacific time
            due_datetime_pacific = due_datetime_utc.astimezone(pacific_tz)

            # Skip overdue assignments (due in the past)
            if due_datetime_pacific < now:
                continue

            # Include assignments due within next 3.5 days
            if due_datetime_pacific <= cutoff_datetime:
                assignment['due_datetime_parsed'] = due_datetime_pacific
                assignment['due_date_parsed'] = due_datetime_pacific.date()
                due_soon.append(assignment)
        except Exception as e:
            print(f"Error parsing date for {assignment.get('name')}: {e}")

    # Sort by due date (earliest first)
    due_soon.sort(key=lambda x: x['due_datetime_parsed'])

    # Show what was found
    print(f"\n   Upcoming assignments ({len(due_soon)}):")
    for a in due_soon:
        due_dt = a.get('due_datetime_parsed')
        due_str = due_dt.strftime('%b %d %I:%M %p') if due_dt else 'N/A'
        print(f"      - {a['name'][:40]:<40} | {due_str}")

    return due_soon

def clean_html(text):
    """Remove HTML tags from text"""
    if not text:
        return ""
    # Remove HTML tags
    clean = re.sub('<[^<]+?>', '', text)
    # Remove extra whitespace
    clean = re.sub(r'\s+', ' ', clean)
    return clean.strip()

def generate_ai_action_plan(assignment):
    """Use GPT-4o-mini to generate a SHORT, simple action plan"""

    # Prepare assignment details
    name = assignment.get('name', 'Unnamed Assignment')
    course = assignment.get('course_name', 'Unknown Course')
    points = assignment.get('points_possible', 0)
    description = clean_html(assignment.get('description', ''))

    # Build the prompt for GPT
    prompt = f"""You are helping a college student with their assignment. Be brief and concise.

Assignment: {name}
Course: {course}
Points: {points}
Description: {description[:500]}

Provide a SHORT action plan (3-4 steps max) and 1-2 quick tips. Be extremely brief.

Format:
ACTION_PLAN:
1. [step]
2. [step]
3. [step]

TIPS:
• [tip 1]
• [tip 2]"""

    try:
        # Call OpenAI API
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a concise academic assistant. Keep responses brief."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        result = response.json()

        ai_response = result['choices'][0]['message']['content']

        # Parse the response
        action_plan = ""
        tips = ""

        if "ACTION_PLAN:" in ai_response:
            plan_section = ai_response.split("ACTION_PLAN:")[1]
            if "TIPS:" in plan_section:
                action_plan = plan_section.split("TIPS:")[0].strip()
                tips = plan_section.split("TIPS:")[1].strip()
            else:
                action_plan = plan_section.strip()

        return {
            "action_plan": action_plan,
            "tips": tips
        }

    except Exception as e:
        print(f"Error generating AI action plan: {e}")
        # Fallback to basic
        return {
            "action_plan": "1. Review requirements\n2. Complete work\n3. Submit",
            "tips": "• Start early\n• Check rubric"
        }

def is_major_test(assignment):
    """Determine if assignment is a MAJOR test (midterm/final/exam)"""
    name = assignment.get('name', '').lower()
    description = str(assignment.get('description', '')).lower()

    # Midterm, final, or major exams
    major_keywords = ['midterm', 'final exam', 'final test', 'midterm exam']

    for keyword in major_keywords:
        if keyword in name:
            return True

    # Also check for "exam" with high point value
    if 'exam' in name and assignment.get('points_possible', 0) >= 50:
        return True

    # Check for Respondus LockDown Browser (indicates major test)
    if 'respondus' in description or 'lockdown browser' in description:
        return True

    return False

def get_priority_symbol(assignment):
    """Get priority symbol based on assignment type and due date"""
    if is_major_test(assignment):
        return "🚨"  # High priority for midterms/finals only

    # Check how soon it's due
    due_date = assignment.get('due_date_parsed')
    if due_date:
        today = datetime.now().date()
        days_until_due = (due_date - today).days

        if days_until_due == 0:
            return "⚠️"  # Due today
        elif days_until_due == 1:
            return "📌"  # Due tomorrow

    return "📋"  # Normal assignment

def get_time_until_due(assignment):
    """Calculate human-readable time until assignment is due"""
    due_datetime = assignment.get('due_datetime_parsed')
    if not due_datetime:
        return "Unknown"

    now = datetime.now()
    time_diff = due_datetime - now

    days = time_diff.days
    hours = time_diff.seconds // 3600

    if days == 0:
        if hours == 0:
            minutes = time_diff.seconds // 60
            return f"Due in {minutes} minutes"
        return f"Due in {hours} hours"
    elif days == 1:
        return f"Due tomorrow at {due_datetime.strftime('%I:%M %p')}"
    else:
        return f"Due in {days} days ({due_datetime.strftime('%b %d at %I:%M %p')})"

def create_telegram_summary(assignment):
    """Create SHORT, simple Telegram message for assignment"""
    course = assignment.get('course_name', 'Unknown Course')
    name = assignment.get('name', 'Unnamed Assignment')
    points = assignment.get('points_possible', 0)

    # Get due date/time
    due_datetime = assignment.get('due_datetime_parsed')
    due_str = due_datetime.strftime('%b %d at %I:%M %p') if due_datetime else 'No due date'

    # Check if it's a MAJOR test (midterm/final only)
    major_test = is_major_test(assignment)
    priority_icon = "🚨 " if major_test else ""

    # Generate AI action plan
    print(f"   🤖 Generating AI action plan for: {name}")
    ai_plan = generate_ai_action_plan(assignment)

    # Study guide prompt ONLY for midterms/finals
    study_guide_prompt = ""
    if major_test:
        study_guide_prompt = f"\n\n_Reply 'study guide' for AI study materials_"

    # Format message - SHORT and simple
    message = f"""
{priority_icon}*{name}* - Due {due_str}
📚 {course}
⭐ Points: {points}

{ai_plan['action_plan']}

💡 {ai_plan['tips']}
{study_guide_prompt}

[Open in Canvas]({assignment.get('html_url', '#')})
"""

    return message

def main():
    """Main execution function"""
    print("\n" + "=" * 50)
    print("🤖 Daily Canvas Planner Starting...")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
    print("=" * 50)

    all_assignments = []

    # Fetch from all Canvas instances using planner + assignments APIs
    print("\n--- Fetching Canvas Assignments ---")
    for instance in CANVAS_INSTANCES:
        print(f"\n📡 Connecting to: {instance['name']}")
        print(f"   URL: {instance['url']}")
        assignments = get_canvas_all_items(instance['url'], instance['api_token'])
        all_assignments.extend(assignments)
        print(f"   Retrieved: {len(assignments)} assignments")

    print(f"\n📊 Total assignments found: {len(all_assignments)}")

    # Filter to next 3 days assignments
    due_soon = filter_due_next_3_days(all_assignments)

    print(f"\n🎯 Result: {len(due_soon)} assignments due in next 3 days")

    # Check for midterms/finals
    print("\n--- Checking for Midterms/Finals ---")
    major_tests = [a for a in due_soon if is_major_test(a)]
    if major_tests:
        for t in major_tests:
            print(f"   🚨 DETECTED: {t['name']} ({t['course_name']})")
    else:
        print("   No midterms or finals detected")

    # Auto-generate study guides for midterms/finals
    study_guides_generated = []

    for assignment in due_soon:
        if is_major_test(assignment):
            print(f"\n--- Generating Study Guide ---")
            print(f"   Exam: {assignment['name']}")
            print("   Fetching course materials...")

            # Find which Canvas instance this assignment belongs to
            for instance in CANVAS_INSTANCES:
                # Extract course ID from course name if available
                course_name = assignment.get('course_name', '')

                # Search for this course in this instance
                headers = {"Authorization": f"Bearer {instance['api_token']}"}
                courses_url = f"{instance['url']}/api/v1/courses?enrollment_state=active&per_page=100"

                try:
                    courses_response = requests.get(courses_url, headers=headers)
                    if courses_response.status_code == 200:
                        courses = courses_response.json()

                        for course in courses:
                            if course.get('name') == course_name:
                                # Found the course! Generate study guide
                                course_id = course['id']

                                # Load the study guide generator module
                                study_guide_path = AUTO_CANVAS_ROOT / "study_guides" / "auto-study-guide-generator.py"
                                spec = importlib.util.spec_from_file_location(
                                    "auto_study_guide",
                                    str(study_guide_path)
                                )
                                study_guide_module = importlib.util.module_from_spec(spec)
                                spec.loader.exec_module(study_guide_module)

                                # Generate study guide
                                print("   Calling AI to generate study guide...")
                                output_path = study_guide_module.generate_study_guide(
                                    assignment,
                                    instance['url'],
                                    course_id,
                                    instance['api_token']
                                )

                                if output_path:
                                    study_guides_generated.append({
                                        'exam': assignment['name'],
                                        'path': output_path
                                    })
                                    print(f"   ✅ Study guide saved: {output_path}")

                                break
                except Exception as e:
                    print(f"   Error generating study guide: {e}")
                    continue

    # Send study guide notifications if any were generated
    if study_guides_generated:
        study_guide_msg = "\n\n📚 *Auto-Generated Study Guides:*\n"
        for sg in study_guides_generated:
            study_guide_msg += f"✅ {sg['exam']}\n   `{sg['path']}`\n"

    print("\n--- Sending Telegram Notification ---")
    if len(due_soon) == 0:
        # Send "all clear" message
        print("   No assignments due - sending 'all clear' message")
        message = f"""
✅ *Daily Canvas Update*
📅 {datetime.now().strftime('%A, %B %d, %Y')}

🎉 *No assignments due in the next 3 days!*

Enjoy your free time or get ahead on upcoming work! 💪

_Powered by AI via GPT-4o-mini_ 🤖
"""
        send_telegram_message(message)
        print("   ✅ 'All clear' notification sent")
    else:
        # Group assignments by date
        from collections import defaultdict
        assignments_by_date = defaultdict(list)

        for assignment in due_soon:
            due_datetime = assignment.get('due_datetime_parsed')
            if due_datetime:
                date_key = due_datetime.date()
                assignments_by_date[date_key].append(assignment)

        # Build assignment list grouped by date
        assignment_lines = []

        # Sort dates
        sorted_dates = sorted(assignments_by_date.keys())

        for date in sorted_dates:
            # Format date header (Jan 27th:)
            day = date.day
            if 4 <= day <= 20 or 24 <= day <= 30:
                suffix = "th"
            else:
                suffix = ["st", "nd", "rd"][day % 10 - 1]
            date_header = date.strftime(f'%b {day}{suffix}:')
            assignment_lines.append(date_header)

            # Add assignments for this date
            for assignment in assignments_by_date[date]:
                name = assignment.get('name', 'Unnamed')
                course = assignment.get('course_name', 'Unknown')
                due_datetime = assignment.get('due_datetime_parsed')

                # Extract course code (e.g., "MGMT311" from "MGMT 311 (Winter 2026; 23330)")
                course_code = course.split('(')[0].strip() if '(' in course else course
                course_code = course_code.replace(' ', '')  # Remove spaces: MGMT311

                # Format time
                time_str = due_datetime.strftime('%I:%M %p').lstrip('0') if due_datetime else ''

                # Only add emoji for major tests (midterms/finals)
                if is_major_test(assignment):
                    line = f"🚨 {name}, {course_code}, {time_str}"
                else:
                    line = f"{name}, {course_code}, {time_str}"

                assignment_lines.append(line)

            # Add blank line after each date group
            assignment_lines.append("")

        # Build complete message
        message = f"""📚 Daily Canvas Update
📅 {datetime.now().strftime('%A, %B %d, %Y')}

{chr(10).join(assignment_lines)}
AI-powered action plans generated by GPT-4o-mini 🤖"""

        # Add study guide info if any were generated
        if study_guides_generated:
            message += "\n📚 Auto-Generated Study Guides:\n"
            for sg in study_guides_generated:
                message += f"✅ {sg['exam']}\n"

        print(f"   Sending assignment summary ({len(due_soon)} assignments)...")
        send_telegram_message(message)
        print(f"   ✅ Assignment notification sent!")

        # Send study guide files via Telegram
        if study_guides_generated:
            print(f"\n--- Sending Study Guide Files ---")
            for sg in study_guides_generated:
                print(f"   Uploading: {sg['exam']}...")
                # Send the actual .docx file
                caption = f"""📖 *Study Guide: {sg['exam']}*

✅ AI-generated with:
• Key concepts organized by topic
• Key ideas & theories
• 70-100 multiple choice practice questions
• Answer key on last page
• All course materials reviewed

Download and open on your phone! 🎓"""

                send_telegram_document(sg['path'], caption)
                print(f"   ✅ Study guide uploaded: {sg['exam']}")

    print("\n" + "=" * 50)
    print("✨ Daily Canvas Planner Complete!")
    print("=" * 50)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # Send error notification
        error_message = f"❌ *Error in Daily Canvas Planner*\n\n{str(e)}"
        send_telegram_message(error_message)
        print(f"Error: {e}")
        sys.exit(1)
