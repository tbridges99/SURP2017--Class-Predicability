from jira import JIRA
from git import Repo
import json
import time
import csv
import subprocess
import os
import re
#class for Classes
class Class:
	creationDate = ""
	authors = []
	bugfixes = []
	waschanged = ""
	def __init__(self, name):
		self.name = name

#Requirement Class
class Requirement:
	#classes that were available in requirement
	classes = []
	#classes that were changed due to requirement
	waschanged = []
	#hashes of all commits involved in requirement
	commitHashes = []
	def __init__(self, name):
		self.name = name
	def addClass(self, classname, changed):
		classes.append(classname)
		waschanged.append(changed)

#Function to convert Month numbers to abbrev values
def NumToMonth(shortMonth):

	return{
		'01' : 'Jan',
		'02' : 'Feb',
		'03' : 'Mar',
		'04' : 'Apr',
		'05' : 'May',
		'06' : 'Jun',
		'07' : 'Jul',
		'08' : 'Aug',
		'09' : 'Sep', 
		'10':'Oct',
		'11':'Nov',
		'12':'Dec'
	}[shortMonth]

#Changes directory to that of the project in which the git files are located
#Must be adjusted depending on the environment being worked on
#ADD FUNCTIONALITY TO SPECIFY DIRECTORY
os.chdir("/home/tmula/tika")
#output = subprocess.check_output("git log --since=2007-09-27 --until=2013-09-27", shell=True)

#print output
#Specifies the path the repository for the project is in
#Uses this repository to gather statistics
repo = Repo("/home/tmula/tika")
assert not repo.bare

##tree = repo.heads.master.commit.tree
##for files in list(tree.traverse()):
	##if ".java" in files.name:	
		##print files.name

#Go through every commit in the repo and add it to a list of commits
for commit in list(repo.iter_commits()):
	vals = []
	vals.append(commit)
	##for key, value in vals.iteritems():
		##print key
#print vals

#Regex to extract the SHA-1 hashes from commit messages
commitHashRegex = r'\b([a-f0-9]{40})\b'
#Regex to extract the Author of the commit from commit messages
commitAuthorRegex = r'Author: ([ a-zA-Z]*)'
#Sets Jira instance in order to gather requirements from
jira = JIRA('https://issues.apache.org/jira/')
#Gets all the issues from a Jira instance that are requirements and resolved
issues = jira.search_issues('project = TIKA AND issuetype = "New Feature" AND status in (Resolved, Closed) ORDER BY resolved ASC', maxResults=10000000)
#Gets all the issues from a Jira instance that are requirements and not complete
issuesopen = jira.search_issues('project = TIKA AND issuetype = "New Feature" AND status in (Open, "In Progress", Reopened) ORDER BY updated ASC, resolved ASC', maxResults=10000000)
#List to store all project requirements
projectRequirements = []
#Set the name of the project here
#ADD Command Line arguments to specify project name
project = 'Tika'
#open a csv to write Class changes for a project and its requirements
with open('tikaclasschanges.csv', 'wb+') as csvfile:
	#Write Row to CSV
	filewriter = csv.writer(csvfile, delimiter=',', quotechar='|', 				quoting=csv.QUOTE_MINIMAL)
	filewriter.writerow(['Project ID', 'Requirement ID', 'Class ID',  'Changed'])
	#Go through every requirement in Jira
	for issue in issues: 
		#Get the requirement name from the Jira issue
		requirement = Requirement(issue.key.encode('utf-8').strip())
		#Get the creation date of the requirement from the Jira issue
		creationDate = (issue.fields.created.encode('utf-8').strip()).split('-')
		#Get the resolution date of the requirement from the Jira issue
		resolutionDate = (issue.fields.resolutiondate.encode('utf-8').strip()).split('-')
		
		##print "This is the requirment name" + requirement.name + ":\n\n"
		#print creationDate

		#Format the dates
		creationDate[2] = creationDate[2][:2]
		resolutionDate[2] = resolutionDate[2][:2]
		reqCreationDate = creationDate[0] + "-" + creationDate[1] + "-" + 			creationDate[2] 
		reqResolutionDate = resolutionDate[0] + "-" + resolutionDate[1] + "-" + resolutionDate[2]
		
		#print "git log --since=" + reqCreationDate + " --until=" + reqResolutionDate + " --grep=\'" + requirement.name + "\'"
		#print reqCreationDate
		#print reqResolutionDate

		#Get the commits from the start of the project to the date the issue was created in Jira
		#ADD command line arguments for the beginning of project or save first issue date
		output = subprocess.check_output("git log -1 --pretty=format:\'%H\' --since=2007-05-31 --until=" + reqCreationDate, shell=True)
		#Checkout the project from the most first commit for the requirement
		subprocess.check_output("git checkout -f " + output, shell=True)	
		#Get all the files in that are available in the project at a given requirement state
		files = subprocess.check_output("git ls-tree --name-only --full-tree -r HEAD | grep \'\.java\' || true", shell=True)
		#Split the output off at new line to get a list of classes
		files = files.split('\n')
		#Go thru every class in the list of classes
		for classes in files :

			#print classes
			#Check if class is just the new line character
			if (classes != '\n'):
				#Create a new Class object 		
				newclass = Class(classes)
				#At this point we do not know that the class was changed so default the value to NO
				newclass.waschanged = "NO"	
				#Add class to list of classes associated with a given requirement
				requirement.classes.append(newclass)
		#Check out the master branch again to go backwards in the gitlog
		subprocess.check_output("git checkout -f master", shell=True)	
		#Get all the commits since creation of the requirment to its resolution	
		output = subprocess.check_output("git log --since=" + reqCreationDate + " --until=" + reqResolutionDate + " --grep=\'" + requirement.name + "\'", shell=True)
		
		#for i in range(0, len(requirement.classes)):
			#print requirement.classes[i] + " " + requirement.waschanged[i]
		
		#Search the commits and find all the SHA-1 hashes of each commit and put them in a list
		commits = re.findall(commitHashRegex, output)
		
		print "Requirement name " + requirement.name
		print reqCreationDate
		print reqResolutionDate
		print "Number of commits " + str(len(commits))
		
		done = False
		#Check for the number of commits to be atleast 1
		if (len(commits) > 0):
			commitmessages = output.split('\n\n')
			#Go through each commit in requirement
			for commit in commits:
				i = 0
				print commitmessages[i]
				#Add to the list of hashes for a commit in a requirement
				requirement.commitHashes.append(commit)
				#Get all the classes in changed in a commit
				classes = subprocess.check_output("git diff-tree --no-commit-id --name-only -r " + commit + " | grep \'\.java\' || true" , shell=True)
				classes = classes.split('\n')
				#Go thru the classes
				for name in classes:
					#Check if the class is already in requirement class list
					#Meaning check if class was already in the project at start of requiremnt or not
					for classname in requirement.classes:
						if (name != '\n' and  classname.name == name):
							print classname.name  
							print name 
						#Check to make sure class isn't just a newline character
						#Extract author's name from commit
						#If class in list then changed its state
							author = re.search(commitAuthorRegex, commitmessages[i])
							requirement.classes[classes.index(name)].waschanged = "YES"
							if author is not None and  author not in requirement.classes[classes.index(name)].authors:
								requirement.classes[classes.index(name)].authors.append(author.group(1))
								print requirement.classes[classes.index(name)].authors
							done = True
							break
				if (name != '\n' and  done == False):
					#Check to make sure class isn't just a newline character
					#Extract author's name from commit
					author = re.sub(commitAuthorRegex, commitmessages[i])
					#Create a new Class object for this class	
					newclass = Class(name)
					#Change the value of whether the class was changed to YES
					newclass.waschanged = "YES"
					#Check if author is in the list of authors for the class if not then append
					if author is not None and not author in newclass.authors:
						print author	
						newclass.authors.append(author.group(1))
					##print newclass.authors
					requirement.classes.append(newclass)
					newclass = None
					author. 

				i += 1
		#print requirement.name + "\nCommits:\n" 
		#print requirement.commitHashes
		#print requirement.classes
		#print requirement.waschanged

		#Add row to csv
		filewriter.writerow([project, issue.key.encode('utf-8').strip(), requirement.classes[0].name, requirement.classes[0].waschanged])
		#For all the classes in a requirement write them, the author and whether it was changed
		for i in range(1, len(requirement.classes)):
			filewriter.writerow(["", "", requirement.classes[i].authors, requirement.classes[i].name, requirement.classes[i].waschanged])
		#For issues in issuesopen write them to csv
		#Implement this part
		for issue in issuesopen:
			filewriter.writerow([project, issue.key.encode('utf-8').strip()])
	

