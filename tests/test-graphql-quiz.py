#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test GraphQL queries for New Quizzes"""

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

instance = canvas_creds["instances"][0]
canvas_url = instance['url']
api_token = instance['api_token']
headers = {"Authorization": f"Bearer {api_token}"}

course_id = 270660
assignment_id = 1971155

print("=" * 80)
print("GRAPHQL QUIZ QUERY TEST")
print("=" * 80)
print()

graphql_url = f"{canvas_url}/api/graphql"

# Try different GraphQL queries
queries = [
    # Query 1: Try accessing quiz field (singular)
    {
        "name": "Query 1: Assignment.quiz field",
        "query": """
query GetQuiz($assignmentId: ID!) {
  assignment(id: $assignmentId) {
    name
    quiz {
      id
      title
    }
  }
}
""",
        "variables": {"assignmentId": str(assignment_id)}
    },

    # Query 2: Try accessing through legacy node
    {
        "name": "Query 2: Legacy quiz node",
        "query": """
query GetLegacyQuiz($courseId: ID!) {
  course(id: $courseId) {
    name
    quizzesConnection {
      nodes {
        _id
        title
      }
    }
  }
}
""",
        "variables": {"courseId": str(course_id)}
    },

    # Query 3: Try direct node query
    {
        "name": "Query 3: Direct node",
        "query": """
{
  legacyNode(_id: "270660", type: Course) {
    ... on Course {
      name
      _id
    }
  }
}
"""
    }
]

for q in queries:
    print(f"\n{q['name']}")
    print("-" * 60)

    payload = {
        "query": q["query"]
    }

    if "variables" in q:
        payload["variables"] = q["variables"]

    response = requests.post(graphql_url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if "errors" in result:
            print(f"Errors: {result['errors']}")
        if "data" in result:
            print(f"Data: {json.dumps(result['data'], indent=2)}")
    else:
        print(f"Error: {response.text[:300]}")

print()
print("=" * 80)
