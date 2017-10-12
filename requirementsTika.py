from jira import JIRA
import json
import time
import csv
jira = JIRA('https://issues.apache.org/jira/')
issues = jira.search_issues('project = TIKA AND issuetype = "New Feature" AND status in (Resolved, Closed) ORDER BY resolved ASC', maxResults=10000000)

issuesopen = jira.search_issues('project = TIKA AND issuetype = "New Feature" AND status in (Open, "In Progress", Reopened) ORDER BY updated ASC, resolved ASC', maxResults=10000000)

i = 0
with open('tikarequirements.csv', 'wb+') as csvfile:
	filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', 				quoting=csv.QUOTE_MINIMAL)
	filewriter.writerow(['Requirement Number', 'Requirement'])
	for issue in issues: 
		filewriter.writerow([i, issue.fields.summary.encode('utf-8').strip()])
		i+=1
		print i
	for issue in issuesopen:
		filewriter.writerow([i, issue.fields.summary.encode('utf-8').strip()])
		i+=1
		print i
	

