from src.prawscrape import prawpull as pwp
import os.path

#is our datatable present?
def test_datapresent():
    assert os.path.isfile("./data/datatable.csv")


#Crude check to see if the subreddit listing file has
#valid subreddits.
def test_subredditfile():
    try:
        credFile = "/home/user/Documents/Workspace/Me/Credentials/reddit.txt"
        pwp.fetchSubLimit=1
        pwp.commentLim=1
        pwp.repMoreLim=1
        pwp.tableName="test.csv"
        pwp.main(credFile)
        os.remove("./data/" + pwp.tableName)
        assert (1==1)
    except Exception as e:
        assert (1==0)
