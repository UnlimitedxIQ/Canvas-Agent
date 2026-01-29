#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test script to debug quiz question fetching"""

import json
import requests
from datetime import datetime, timezone
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
print("QUIZ QUESTION FETCHING DEBUG")
print("=" * 80)
print()

# Use first instance (UO Academic)
instance = canvas_creds["instances"][0]
canvas_url = instance['url']
api_token = instance['api_token']
headers = {"Authorization": f"Bearer {api_token}"}

print(f"Canvas: {instance['name']}")
print(f"URL: {canvas_url}")
print()

# Get active courses
print("Fetching active courses...")
courses_url = f"{canvas_url}/api/v1/courses?enrollment_state=active&per_page=10"
courses_response = requests.get(courses_url, headers=headers)

if courses_response.status_code == 200:
    courses = courses_response.json()
    print(f"Found {len(courses)} courses")
    print()

    # Pick first course with MGMT in name
    target_course = None
    for course in courses:
        if 'MGMT' in course.get('name', ''):
            target_course = course
            break

    if not target_course:
        target_course = courses[0]

    course_name = target_course.get('name', 'Unknown')
    course_id = target_course['id']

    print(f"Testing with course: {course_name}")
    print(f"Course ID: {course_id}")
    print()

    # Try Method 1: Get quizzes
    print("Method 1: Fetching from /quizzes endpoint...")
    quizzes_url = f"{canvas_url}/api/v1/courses/{course_id}/quizzes?per_page=50"
    quizzes_response = requests.get(quizzes_url, headers=headers)
    print(f"Status: {quizzes_response.status_code}")

    if quizzes_response.status_code != 200:
        print(f"Error: {quizzes_response.text[:200]}")

    print()

    # Try Method 2: Get assignments (quizzes are often assignments)
    print("Method 2: Fetching quiz assignments...")
    assignments_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments?per_page=50"
    assignments_response = requests.get(assignments_url, headers=headers)

    if assignments_response.status_code == 200:
        assignments = assignments_response.json()
        print(f"Found {len(assignments)} assignments total")

        # Filter to quiz-type assignments
        quiz_assignments = [a for a in assignments if 'quiz' in a.get('name', '').lower() or a.get('submission_types', []) == ['online_quiz']]

        print(f"Found {len(quiz_assignments)} quiz assignments")
        print()

        for assignment in quiz_assignments[:5]:
            name = assignment.get('name', 'Unnamed')
            assign_id = assignment.get('id')
            quiz_id = assignment.get('quiz_id')
            submission_types = assignment.get('submission_types', [])
            external_tool_tag = assignment.get('external_tool_tag_attributes', {})

            print(f"\nQuiz Assignment: {name}")
            print(f"   Assignment ID: {assign_id}")
            print(f"   Quiz ID: {quiz_id}")
            print(f"   Submission types: {submission_types}")
            print(f"   External tool: {external_tool_tag.get('url', 'N/A')[:100]}")

            # Method A: Try getting assignment submission (for external_tool type)
            print(f"\n   Method A: Check assignment submissions...")
            assignment_sub_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments/{assign_id}/submissions/self"
            assignment_sub_response = requests.get(assignment_sub_url, headers=headers)
            print(f"   Status: {assignment_sub_response.status_code}")

            if assignment_sub_response.status_code == 200:
                submission = assignment_sub_response.json()
                print(f"   Workflow state: {submission.get('workflow_state')}")
                print(f"   Submission type: {submission.get('submission_type')}")
                print(f"   Preview URL: {submission.get('preview_url', 'N/A')[:100]}")

            # Method B: Try to fetch full assignment details
            print(f"\n   Method B: Full assignment details...")
            assignment_details_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments/{assign_id}"
            assignment_details_response = requests.get(assignment_details_url, headers=headers)

            if assignment_details_response.status_code == 200:
                details = assignment_details_response.json()
                print(f"   Has description: {bool(details.get('description'))}")
                print(f"   HTML URL: {details.get('html_url', 'N/A')}")

                # Check if there's a quiz URL in the description
                description = details.get('description', '')
                if 'quiz' in description.lower():
                    print(f"   Description mentions quiz!")

            # Method C: If it has quiz_id, try classic quiz API
            if quiz_id:
                print(f"\n   Method C: Classic Quiz API (quiz_id={quiz_id})...")
                quiz_url = f"{canvas_url}/api/v1/courses/{course_id}/quizzes/{quiz_id}"
                quiz_response = requests.get(quiz_url, headers=headers)
                print(f"   Status: {quiz_response.status_code}")

                if quiz_response.status_code == 200:
                    quiz_data = quiz_response.json()
                    print(f"   Quiz title: {quiz_data.get('title')}")
                    print(f"   Question count: {quiz_data.get('question_count')}")

            # Method D: Try New Quizzes API (for external_tool submissions)
            print(f"\n   Method D: New Quizzes API...")
            # New Quizzes uses different endpoints
            new_quiz_url = f"{canvas_url}/api/quiz/v1/courses/{course_id}/quizzes"
            new_quiz_response = requests.get(new_quiz_url, headers=headers)
            print(f"   Status: {new_quiz_response.status_code}")

            if new_quiz_response.status_code == 200:
                print(f"   Response preview: {str(new_quiz_response.json())[:200]}")

            print()

    else:
        print(f"Error fetching assignments: {assignments_response.status_code}")

else:
    print(f"Error fetching courses: {courses_response.status_code}")

print("=" * 80)
