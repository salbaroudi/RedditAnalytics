#v0.4
#Author: Sean al-Baroudi
#sean.al.baroudi@gmail.com
#Next, I will write an outer loop function that skims a list of subreddits, and pumps out a file for each of them.
#The files can be read in R, and put into tally tables to look at trends.

import praw
import re
import hashlib

#Our target subreddit and appropriate limit

def printtuples(orderedTuples):
	for tup in orderedTuples:
		print( str(tup[1]) + ":" + str(tup[2]) + ":" + str(tup[3]) + ":" )


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

def clippunct(wordList):
	exceptionString = ' \.,;\[\]\(\)'
	for index in range(0, len(wordList)): #apply some functional programming?
		wordList[index] = re.sub(exceptionString, '', wordList[index])
	return wordList

def commentfilter(wordList):
	retList = []
	pattern = re.compile("[A-Z]{3,7}")
	for word in wordList:
		hold = re.findall(pattern, word)
		for anItem in hold:
			if len(anItem) <= 5:
				retList.append(anItem)
	return retList

def pullacronyms(commentBody):
	#In this simple case, we just get acronyms by finding capitals
	wordList = commentBody.split(" ")
	clippunct(wordList)
	retSet = set(commentfilter(wordList)) #auto clips duplicates by def.
	return retSet

def addrows(dataDict, acroSet, comment, subRedName):
	user = comment.author.name
	time = comment.created_utc
	id = comment.id
	for term in acroSet:
		dataDict[id] = [time,user,subRedName,term]
	return

#signature: Dictionary -> Dictionary
#Purpose:
def minesubredditcomments(dataDict,subRName,listGen):
	commentLim = 10 #500
	rmThresh = 1 #32

	for submission in listGen:
		submission.comments.replace_more(limit=commentLim, threshold=rmThresh)
		for comm in submission.comments.list():
			if ((comm.body is not None) and (comm.author is not None)):
				acroSet = pullacronyms(comm.body)
				if len(acroSet) > 0:
					addrows(dataDict, acroSet, comm, subRName)
	return

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


#Signature: Void -> Void.
#Purpose: Our main method that acts as the scope for all functions.
#Implemented this way to avoid heavy usage of global variables.
def main(credFile):
	subredditList = ["MachineLearning"]
	writePath = "./data/datatable.csv"
	dataDict = {} #hexID -> subreddit,user,term,timestamp
	fetchLimit = 5

	theSession = startredditsession(credFile,True)

	for item in subredditList:
		listGen = theSession.subreddit(item).hot(limit=fetchLimit)
		minesubredditcomments(dataDict,item, listGen)
		print("Just finished subreddit:" + item)
	print(dataDict)
	writetofile(dataDict,writePath)
	return

if __name__ == "__main__":
	credFile =  "/home/user/Documents/Workspace/Me/Credentials/reddit.txt"
	main(credFile)


#References:
#[1]: http://praw.readthedocs.io/en/latest/getting_started/quick_start.html#submission-iteration
#[2]: Regex Replacement (terse):  http://stackoverflow.com/questions/3900054/python-strip-multiple-characters
