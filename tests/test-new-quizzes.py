#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Canvas New Quizzes API access"""

import json
import requests
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
print("CANVAS NEW QUIZZES API TEST")
print("=" * 80)
print()

instance = canvas_creds["instances"][0]
canvas_url = instance['url']
api_token = instance['api_token']
headers = {"Authorization": f"Bearer {api_token}"}

course_id = 270660
assignment_id = 1971155  # Ch 2 Prep Quiz

print(f"Testing: Ch 2 Prep Quiz (Assignment {assignment_id})")
print()

# Method 1: Try to get the LTI launch data
print("Method 1: Assignment with external tool content...")
assign_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments/{assignment_id}"
assign_response = requests.get(assign_url, headers=headers)

if assign_response.status_code == 200:
    assignment = assign_response.json()

    print(f"Name: {assignment.get('name')}")
    print(f"External tool: {assignment.get('external_tool_tag_attributes', {})}")
    print()

# Method 2: Get assignment submission with attempt history
print("Method 2: Submission attempts...")
submission_url = f"{canvas_url}/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions/self?include[]=submission_history"
submission_response = requests.get(submission_url, headers=headers)

if submission_response.status_code == 200:
    submission = submission_response.json()

    print(f"Workflow: {submission.get('workflow_state')}")
    print(f"Score: {submission.get('score')}")
    print(f"Submission history: {len(submission.get('submission_history', []))} attempts")

    # Check submission history
    for idx, attempt in enumerate(submission.get('submission_history', [])[:3], 1):
        print(f"\n  Attempt {idx}:")
        print(f"    External tool URL: {attempt.get('external_tool_url', 'N/A')[:100]}")
        print(f"    URL: {attempt.get('url', 'N/A')[:100]}")
        print(f"    Preview URL: {attempt.get('preview_url', 'N/A')[:100]}")

print()

# Method 3: Try GraphQL API (New Quizzes uses GraphQL)
print("Method 3: GraphQL API (New Quizzes native)...")
graphql_url = f"{canvas_url}/api/graphql"

# Query for quiz attempt data
graphql_query = """
query GetQuizAttempt($assignmentId: ID!) {
  assignment(id: $assignmentId) {
    name
    quizzes {
      edges {
        node {
          id
          title
          questions {
            edges {
              node {
                id
                questionText
              }
            }
          }
        }
      }
    }
  }
}
"""

graphql_payload = {
    "query": graphql_query,
    "variables": {
        "assignmentId": str(assignment_id)
    }
}

graphql_response = requests.post(graphql_url, headers=headers, json=graphql_payload)
print(f"GraphQL Status: {graphql_response.status_code}")

if graphql_response.status_code == 200:
    print(f"GraphQL Response: {graphql_response.json()}")
else:
    print(f"GraphQL Error: {graphql_response.text[:300]}")

print()

# Method 4: Try to access quiz through external tool content tag
print("Method 4: External tool content tag...")
external_tools_url = f"{canvas_url}/api/v1/courses/{course_id}/external_tools"
external_tools_response = requests.get(external_tools_url, headers=headers)

print(f"External tools status: {external_tools_response.status_code}")
if external_tools_response.status_code == 200:
    tools = external_tools_response.json()
    print(f"Found {len(tools)} external tools")

    for tool in tools:
        if 'quiz' in tool.get('name', '').lower():
            print(f"\n  Quiz Tool: {tool.get('name')}")
            print(f"    ID: {tool.get('id')}")
            print(f"    URL: {tool.get('url', 'N/A')[:100]}")

print()
print("=" * 80)
