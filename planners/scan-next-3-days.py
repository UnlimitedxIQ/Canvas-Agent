#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan Canvas for everything due in next 3 days"""

import json
import requests
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import os
import sys

if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

CREDENTIALS_DIR = os.path.join(os.path.expanduser("~"), ".claude", "credentials")

def load_json(filename):
    path = os.path.join(CREDENTIALS_DIR, filename)
    with open(path, 'r') as f:
        return json.load(f)

canvas_creds = load_json("canvas.json")

print("=" * 80)
print("SCANNING CANVAS - NEXT 3 DAYS")
print("=" * 80)
print()

# Use Pacific timezone
pacific_tz = ZoneInfo("America/Los_Angeles")
now = datetime.now(pacific_tz)
today = now.date()
three_days = today + timedelta(days=3)

print(f"Current time (Pacific): {now.strftime('%Y-%m-%d %I:%M %p')}")
print(f"Today: {today}")
print(f"3 days from now: {three_days}")
print()

all_assignments = []

for instance in canvas_creds["instances"]:
    print(f"📡 Scanning: {instance['name']}")
    headers = {"Authorization": f"Bearer {instance['api_token']}"}

    # Get active courses only
    courses_url = f"{instance['url']}/api/v1/courses?enrollment_state=active&per_page=100"
    courses = requests.get(courses_url, headers=headers).json()

    active_courses = []
    for course in courses:
        if 'id' not in course:
            continue

        workflow_state = course.get('workflow_state', '')
        if workflow_state in ['completed', 'deleted']:
            continue

        # Skip courses that ended more than 60 days ago
        end_at = course.get('end_at')
        if end_at:
            try:
                end_date_utc = datetime.strptime(end_at, "%Y-%m-%dT%H:%M:%SZ")
                end_date_utc = end_date_utc.replace(tzinfo=timezone.utc)
                end_date_pacific = end_date_utc.astimezone(pacific_tz)
                if end_date_pacific < now - timedelta(days=60):
                    continue
            except:
                pass

        active_courses.append(course)

    print(f"   Found {len(active_courses)} active courses")

    for course in active_courses:
        assignments_url = f"{instance['url']}/api/v1/courses/{course['id']}/assignments"
        assignments_response = requests.get(assignments_url, headers=headers)

        if assignments_response.status_code == 200:
            for assignment in assignments_response.json():
                assignment['course_name'] = course.get('name', 'Unknown')
                assignment['instance_name'] = instance['name']
                all_assignments.append(assignment)

print()
print(f"Total assignments found: {len(all_assignments)}")
print()

# Filter to next 3 days
due_next_3_days = []

for a in all_assignments:
    if not a.get('due_at'):
        continue

    try:
        # Parse UTC and convert to Pacific
        due_datetime_utc = datetime.strptime(a['due_at'], "%Y-%m-%dT%H:%M:%SZ")
        due_datetime_utc = due_datetime_utc.replace(tzinfo=timezone.utc)
        due_datetime_pacific = due_datetime_utc.astimezone(pacific_tz)
        due_date = due_datetime_pacific.date()

        # Skip overdue
        if due_datetime_pacific < now:
            continue

        # Check if in next 3 days
        if today <= due_date <= three_days:
            a['due_datetime_parsed'] = due_datetime_pacific
            a['due_date_parsed'] = due_date
            due_next_3_days.append(a)
    except Exception as e:
        pass

# Sort by due date
due_next_3_days.sort(key=lambda x: x['due_datetime_parsed'])

print("=" * 80)
print(f"ASSIGNMENTS DUE IN NEXT 3 DAYS: {len(due_next_3_days)}")
print("=" * 80)
print()

if len(due_next_3_days) == 0:
    print("✅ Nothing due in next 3 days!")
else:
    for idx, a in enumerate(due_next_3_days, 1):
        name = a.get('name', 'Unnamed')
        course = a.get('course_name', 'Unknown')
        due_dt = a['due_datetime_parsed']
        points = a.get('points_possible', 0)

        # Detect exam/test
        name_lower = name.lower()
        is_exam = False
        exam_type = ""

        if 'midterm' in name_lower:
            is_exam = True
            exam_type = "MIDTERM"
        elif 'final' in name_lower:
            is_exam = True
            exam_type = "FINAL"
        elif 'exam' in name_lower:
            is_exam = True
            exam_type = "EXAM"
        elif 'test' in name_lower:
            is_exam = True
            exam_type = "TEST"

        days_until = (due_dt.date() - today).days

        if days_until == 0:
            urgency = "🔴 DUE TODAY"
        elif days_until == 1:
            urgency = "🟡 DUE TOMORROW"
        elif days_until == 2:
            urgency = "🟢 DUE IN 2 DAYS"
        else:
            urgency = f"🔵 DUE IN {days_until} DAYS"

        print(f"{idx}. {urgency}")
        if is_exam:
            print(f"   🚨 {exam_type}: {name}")
        else:
            print(f"   📝 {name}")
        print(f"   📚 {course}")
        print(f"   📅 Due: {due_dt.strftime('%A, %B %d, %Y at %I:%M %p')}")
        print(f"   ⭐ Points: {points}")
        print(f"   🏫 {a['instance_name']}")
        print()

print("=" * 80)
