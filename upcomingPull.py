#v0.4
#Author: Sean al-Baroudi
#sean.al.baroudi@gmail.com
#Next, I will write an outer loop function that skims a list of subreddits, and pumps out a file for each of them.
#The files can be read in R, and put into tally tables to look at trends.

import praw
import re
import hashlib

#Our target subreddit and appropriate limit


#Next, lets try to get comment forests for one submission, and get a flattened list of them.
#The output is piped to a shell script file container (instead of being handled in python).
def startredditsession():
	#As I am posting this code in GitHub, I need to store the credentials outside the Git Folder. Its not included
	#in the project at all.
	credList = []
	credFP =  open(credRedditFile, "r")
	for line in credFP:
		hold = line.split("::")
		credList.append(hold[1])
	r = praw.Reddit(client_id=credList[0],
	client_secret=credList[1], username=credList[2],  \
	password=credList[3], user_agent=credList[4])
	print(r.user.me())
	return r

def addtodict(extractList):
	for noun in extractList:
		if noun in pNounStats:
			pNounStats[noun] = pNounStats[noun] + 1
		else:
			pNounStats[noun] = 1

def grabsubmissions(sR):
	for aSub in sR.new(limit=fetchLimit):
		aSub.comments.replace_more(limit=comRepLimit)
		for comment in ((aSub.comments.list())): #[1] We don't care about CommentTrees structure; just pull nouns.
			extractList = pullwords(comment.body)
			extractList = pullnouns(extractList)
			addtodict(extractList)
	return

#The sorting and statistics are done in R; this just pumped to a file via commandline.

def printtofile(name,orderedTuples):
	fo = open(writeDirectory + name + ".txt", "w+")
	for tup in orderedTuples:
		fo.write(str(tup[1]) + ":" + str(tup[2]) + "\n")
	fo.close()
	return

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

def commentfilter(dataDict,sub):
	for comm in sub.comments:
		if ((comm.body is not None) and (comm.author is not None)):
			print(comm.body)
	return

#Login Stuff
#Here we do modular filtering


def clippunct(wordList):
	exceptionString = ' \.,;\[\]\(\)'
	for index in range(0, len(wordList)): #apply some functional programming?
		wordList[index] = re.sub(exceptionString, '', wordList[index])
	return wordList

def pullacronyms(commentBody):
	#In this simple case, we just get acronyms by finding capitals
	wordList = commentBody.split(" ");
	wordList = clippunct(wordList)
	retList = []
	pattern = re.compile("[A-Z]{3,7}")
	for word in extractList:
		hold = re.findall(pattern, word)
		#if (len(hold) != 0):
		for anItem in hold:
			if len(anItem) <= 5:
				retList.append(anItem)
	return retList

def filtercomment(submission):

#signature: Dictionary -> NoneType
#Purpose:
def minesubmission(dataDict,submission):
	commentLim = 5 #500
	rmThresh = 1 #32
	submission.comments.replace_more(limit=commentLim, threshold=rmThresh)
	for comment in submission.comments.list():
		retList = filtersubmission(submission)
	print(retList)
	return


#Signature: Void -> Void.
#Purpose: Our main method that acts as the scope for all functions.
#Implemented this way to avoid heavy usage of global variables.
def main(credFile):
	subredditList = ["MachineLearning"]
	writeDirectory = "./data/"
	fetchLimit = 2
	dataDict = {}

	theSession = startredditsession(credFile,True)
	#theSession.read_only = True #To avoid throttling.
		#Get a SubReddit Object from our list.

	for item in subredditList:
		for submission in theSession.subreddit(item).hot(limit=fetchLimit):
			print(submission.title)
			minecsubmission(dataDict,submission)
		print("Just finished subreddit:" + item)

if __name__ == "__main__":
	credFile =  "/home/user/Documents/Workspace/Me/Credentials/reddit.txt"
	main(credFile)


#References:
#[1]: http://praw.readthedocs.io/en/latest/getting_started/quick_start.html#submission-iteration
#[2]: Regex Replacement (terse):  http://stackoverflow.com/questions/3900054/python-strip-multiple-characters
