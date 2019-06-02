import praw
import re

#Data Scrape Global Parameters:
#defaults
fetchSubLimit = 50
commentLim = 50 #500
repMoreLim = 2 #32
tableName = "datatable.csv"

#Signature: List -> Object[Reddit Session]
#Purpose: Do OAUTH2 and gain access to remote Reddit API.
#Note: We do a read only session!
def startredditsession(credFile,readOnly):
	credList = []
	credFP =  open(credFile, "r")
	for line in credFP:
		hold = line.split("::")
		credList.append(hold[1].replace('\n' , '')) #NewLine crashes auth code.
	r = ""
	if (readOnly):
		r = praw.Reddit(client_id=credList[0],
		client_secret=credList[1],user_agent=credList[4])
	else:
		r = praw.Reddit(client_id=credList[0],
		client_secret=credList[1], username=credList[2],  \
		password=credList[3], user_agent=credList[4])
		print(r.user.me()) #wont work in read only mode!

	credFP.close()
	return r
#Signature: List -> list
#Purpose: Take out punctuation from wordList
def clippunct(wordList):
	exceptionString = ' \.,;\[\]\(\)'
	for index in range(0, len(wordList)): #apply some functional programming?
		wordList[index] = re.sub(exceptionString, '', wordList[index])
	return wordList

#Signature: List -> list
#Main filter method that extracts acronyms from comment body.
def commentfilter(wordList):
	retList = []
	pattern = re.compile("[A-Z]{3,7}")
	for word in wordList:
		hold = re.findall(pattern, word)
		for anItem in hold:
			if len(anItem) <= 5:
				retList.append(anItem)
	return retList

#Signature: String -> set
#Purpose: Subcall that takes a comment body, and pumps out an acronym set.
def pullacronyms(commentBody):
	#In this simple case, we just get acronyms by finding capitals
	wordList = commentBody.split(" ")
	clippunct(wordList)
	retSet = set(commentfilter(wordList)) #auto clips duplicates by def.
	return retSet

#Signature: Dict, Set, String, String -> NoneType
#Purpose: Write the acronyms of a comment body to the datatable.
def addrows(dataDict, acroSet, comment, subRedName):
	user = comment.author.name
	time = comment.created_utc
	id = comment.id
	for term in acroSet:
		dataDict[id] = [time,user,subRedName,term]
	return

#Signature: Dictionary String ListingGenerator -> NoneType
#Purpose: Main method to pull acronyms out of a subreddit.
#iterates through every commentbody and pulls acronyms
#this function exploits pythons pass by shared object and
#mutation effects to populate the dataDict!
def minesubredditcomments(dataDict,subRName,listGen):
	#commentLim = 1000 #500
	#repMoreLim = 32 #32

	for submission in listGen:
		submission.comments.replace_more(limit=commentLim, threshold=repMoreLim)
		for comm in submission.comments.list():
			if ((comm.body is not None) and (comm.author is not None)):
				acroSet = pullacronyms(comm.body)
				if len(acroSet) > 0:
					addrows(dataDict, acroSet, comm, subRName)
	return

#Signature: Dictionary, String -> NoneType
#Purpose: Write our megatable of acronyms to a file.
def writetofile(dataDict,path):
	outFP = open(path, "w")
	for entry in list(dataDict.keys()):
		row = str(entry)
		for elem in dataDict[entry]:
			row += ","
			row += str(elem)
		row += "\n"
		outFP.write(row)
	outFP.close()
	return

#Signature: Dictionary, String -> NoneType
#Purpose: Write our megatable of acronyms to a file.
def readsrfile(path):
	retList = []
	fp = open(path,"r")
	for line in fp:
		retList.append(line.replace('\n' , ''))
	fp.close()
	return retList



#Signature: Void -> Void.
#Purpose: Our main method that acts as the scope for all functions.
#Implemented this way to avoid heavy usage of global variables.
def main(credFile):
	rootPath="/home/user/Documents/Workspace/CodeProjects/Python3/RedditAnalytics"
	srFilePath = rootPath+"/data/subreddits.txt"
	subRedditList = readsrfile(srFilePath)
	#print(subRedditList)

	writePath = rootPath+"/data/"+tableName
	dataDict = {} #hexID -> subreddit,user,term,timestamp
	#fetchSubLimit = 1000

	theSession = startredditsession(credFile,True)

	for item in subRedditList:
		listGen = theSession.subreddit(item).new(limit=fetchSubLimit)
		minesubredditcomments(dataDict,item, listGen)
		print("Just finished subreddit:" + item)
	#print(dataDict)
	writetofile(dataDict,writePath)

if __name__ == "__main__":
	credFile =  "/home/user/Documents/Workspace/Me/Credentials/reddit.txt"
	main(credFile)

#References:
#[1]: http://praw.readthedocs.io/en/latest/getting_started/quick_start.html#submission-iteration
#[2]: Regex Replacement (terse):  http://stackoverflow.com/questions/3900054/python-strip-multiple-characters
