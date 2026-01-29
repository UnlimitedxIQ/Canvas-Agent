#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug script to see all assignments and their due dates"""

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

print("🔍 COMPLETE ASSIGNMENT DEBUG")
print("=" * 80)
print()

# Use Pacific timezone
pacific_tz = ZoneInfo("America/Los_Angeles")
today = datetime.now(pacific_tz)
print(f"📅 Today is (Pacific): {today.strftime('%Y-%m-%d %I:%M %p')}")
print()

all_assignments = []

for instance in canvas_creds["instances"]:
    print(f"📡 Connecting to: {instance['name']}")
    print(f"   URL: {instance['url']}")
    headers = {"Authorization": f"Bearer {instance['api_token']}"}

    try:
        courses_url = f"{instance['url']}/api/v1/courses"
        courses_response = requests.get(courses_url, headers=headers)
        courses = courses_response.json()

        print(f"   ✅ Found {len(courses)} courses")

        course_count = 0
        for course in courses:
            if 'id' not in course:
                continue

            course_count += 1
            assignments_url = f"{instance['url']}/api/v1/courses/{course['id']}/assignments"
            assignments_response = requests.get(assignments_url, headers=headers)

            if assignments_response.status_code == 200:
                assignments = assignments_response.json()
                print(f"      - {course.get('name', 'Unknown')}: {len(assignments)} assignments")

                for assignment in assignments:
                    assignment['course_name'] = course.get('name', 'Unknown')
                    assignment['instance_name'] = instance['name']
                    all_assignments.append(assignment)

        print(f"   ✅ Checked {course_count} courses")

    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

print(f"📊 TOTAL ASSIGNMENTS FOUND: {len(all_assignments)}")
print(f"📊 Assignments with due dates: {sum(1 for a in all_assignments if a.get('due_at'))}")
print()

# Parse and categorize
overdue = []
upcoming = []
future = []
no_date = []

for a in all_assignments:
    if not a.get('due_at'):
        no_date.append(a)
        continue

    try:
        # Parse UTC and convert to Pacific
        due_datetime_utc = datetime.strptime(a['due_at'], "%Y-%m-%dT%H:%M:%SZ")
        due_datetime_utc = due_datetime_utc.replace(tzinfo=timezone.utc)
        due_datetime_pacific = due_datetime_utc.astimezone(pacific_tz)
        a['due_datetime_parsed'] = due_datetime_pacific
        a['due_date_parsed'] = due_datetime_pacific.date()

        if due_datetime_pacific < today:
            overdue.append(a)
        elif (due_datetime_pacific.date() - today.date()).days <= 30:
            upcoming.append(a)
        else:
            future.append(a)
    except Exception as e:
        print(f"⚠️  Failed to parse: {a.get('name')}: {a.get('due_at')}")

# Sort
overdue.sort(key=lambda x: x['due_datetime_parsed'], reverse=True)
upcoming.sort(key=lambda x: x['due_datetime_parsed'])

print()
print("🔴 OVERDUE ASSIGNMENTS")
print("-" * 80)
if overdue:
    for idx, a in enumerate(overdue[:10], 1):  # Show first 10
        due_dt = a['due_datetime_parsed']
        days_overdue = (today.date() - due_dt.date()).days

        print(f"{idx}. ⚠️ {days_overdue} DAYS OVERDUE")
        print(f"   🏫 {a['instance_name']}")
        print(f"   📚 {a['course_name']}")
        print(f"   📝 {a['name']}")
        print(f"   📅 Was due: {due_dt.strftime('%Y-%m-%d %I:%M %p')}")
        print(f"   ⭐ Points: {a.get('points_possible', 'N/A')}")
        print()
else:
    print("✅ No overdue assignments!")
    print()

print()
print("🟢 UPCOMING ASSIGNMENTS (Next 30 Days)")
print("-" * 80)
if upcoming:
    for idx, a in enumerate(upcoming, 1):
        due_dt = a['due_datetime_parsed']
        days_until = (due_dt.date() - today.date()).days

        if days_until == 0:
            emoji = "🔴"
            time_str = "DUE TODAY"
        elif days_until == 1:
            emoji = "🟡"
            time_str = "DUE TOMORROW"
        elif days_until <= 3:
            emoji = "🟢"
            time_str = f"DUE IN {days_until} DAYS"
        elif days_until <= 7:
            emoji = "🔵"
            time_str = f"Due in {days_until} days"
        else:
            emoji = "⚪"
            time_str = f"Due in {days_until} days"

        print(f"{idx}. {emoji} {time_str}")
        print(f"   🏫 {a['instance_name']}")
        print(f"   📚 {a['course_name']}")
        print(f"   📝 {a['name']}")
        print(f"   📅 Due: {due_dt.strftime('%Y-%m-%d %I:%M %p')}")
        print(f"   ⭐ Points: {a.get('points_possible', 'N/A')}")
        print()
else:
    print("✅ No assignments due in next 30 days!")
    print()

print("=" * 80)
print("📊 SUMMARY:")
print(f"   🔴 Overdue: {len(overdue)}")
print(f"   🟢 Due in next 30 days: {len(upcoming)}")
print(f"   ⚪ Future (30+ days): {len(future)}")
print(f"   ❓ No due date: {len(no_date)}")
print(f"   📝 TOTAL: {len(all_assignments)}")
