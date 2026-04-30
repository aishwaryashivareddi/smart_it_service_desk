import json
from datetime import datetime
from utils import log_event, generate_problem_id

def check_repeated_issues(tickets):
    issue_count = {}

    for ticket in tickets:
        issue = ticket["description"]
        issue_count[issue] = issue_count.get(issue, 0) + 1

    try:
        with open("data/problems.json", "r") as f:
            problems = json.load(f)
    except:
        problems = []

    for issue, count in issue_count.items():
        if count >= 5:
            if issue not in [p["description"] for p in problems]:
                problems.append({
                    "problem_id": generate_problem_id(problems),
                    "description": issue,
                    "occurrence_count": count,
                    "status": "Open",
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                log_event(f"Problem created: {issue}", "WARNING")

    with open("data/problems.json", "w") as f:
        json.dump(problems, f, indent=4)