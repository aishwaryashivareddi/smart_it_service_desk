import json 
from utils import log_event 

def check_repeated_issues(tickets):
    issue_count = {}
    
    
    for ticket in tickets:
        issue = ticket["issue_description"] 
        issue_count[issue] = issue_count.get(issue, 0) + 1
        
    problems = []
    
    try:
        with open("data/problems.json", "r") as f:
            problems = json.load(f)
    except:
        pass 
    
    for issue, count in issue_count.items():
        if count >= 5:
            if issue not in [p["issue"] for p in problems]:
                problems.append({"issue": issue, "count": count}) 
                log_event(f"Problem created: {issue}", "WARNING") 
                
    with open("data/problems.json", "w") as f:
        json.dump(problems, f, indent=4)