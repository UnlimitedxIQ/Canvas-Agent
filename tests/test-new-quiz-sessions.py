#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Try to access New Quizzes session data"""

import json
import requests
import os
import sys
import re

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

instance = canvas_creds["instances"][0]
canvas_url = instance['url']
api_token = instance['api_token']
headers = {"Authorization": f"Bearer {api_token}"}

course_id = 270660
assignment_id = 1971155

print("=" * 80)
print("NEW QUIZZES SESSION DATA TEST")
print("=" * 80)
print()

# Get submission to extract session IDs
print("Getting submission data...")
submission_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/self?include[]=submission_history"
submission_response = requests.get(submission_url, headers=headers)

if submission_response.status_code == 200:
    submission = submission_response.json()

    history = submission.get('submission_history', [])
    print(f"Found {len(history)} attempts\n")

    # Extract session IDs from URLs
    for idx, attempt in enumerate(history[:2], 1):
        url = attempt.get('url', '')
        print(f"Attempt {idx}:")
        print(f"  Full URL: {url}")

        # Extract participant_session_id and quiz_session_id
        participant_match = re.search(r'participant_session_id=([^&]+)', url)
        quiz_match = re.search(r'quiz_session_id=([^&]+)', url)

        if participant_match:
            participant_id = participant_match.group(1)
            print(f"  Participant Session ID: {participant_id}")

        if quiz_match:
            quiz_session_id = quiz_match.group(1)
            print(f"  Quiz Session ID: {quiz_session_id}")

        # Try to access New Quizzes API endpoints
        new_quiz_base = "https://uoregon.quiz-lti-iad-prod.instructure.com"

        # Try various API endpoints
        endpoints_to_try = [
            f"{new_quiz_base}/api/quiz/participant_sessions/{participant_id if participant_match else ''}",
            f"{new_quiz_base}/api/v1/participant_sessions/{participant_id if participant_match else ''}",
            f"{canvas_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/quiz_sessions",
        ]

        for endpoint in endpoints_to_try:
            if not participant_match and "participant" in endpoint:
                continue

            print(f"\n  Trying: {endpoint[:80]}...")
            try:
                resp = requests.get(endpoint, headers=headers, timeout=5)
                print(f"    Status: {resp.status_code}")

                if resp.status_code == 200:
                    print(f"    Success! Data: {str(resp.json())[:200]}")
                elif resp.status_code in [401, 403]:
                    print(f"    Access denied")
                else:
                    print(f"    Error: {resp.text[:100]}")
            except Exception as e:
                print(f"    Exception: {str(e)[:50]}")

        print()

print("=" * 80)
