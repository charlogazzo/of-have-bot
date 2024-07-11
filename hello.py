import praw
from praw.models import MoreComments
import cred

# initialize the reddit agent
r = praw.Reddit(
    client_id=cred.client_id,
    client_secret=cred.client_secret,
    username=cred.username,
    password=cred.password,
    user_agent=cred.user_agent
)

# specify the subreddit
subreddit = r.subreddit("Boxing_Clips")

def of_have_replacer(comment):
    comment_string = comment
    if "should of" in comment_string:
        print("found 'should of'\n")
        comment_string = comment_string.replace("should of", "***should have***")
    if "could of" in comment_string:
        comment_string = comment_string.replace("could of", "***could have***")
    if "would of" in comment_string:
        comment_string = comment_string.replace("would of", "***would have***")
    
    return comment_string
    

# get details of submissions from a subreddit
for submission in subreddit.hot(limit=5):
    print("Title:", submission.title)
    print("Text:", submission.selftext)
    print("Score:", submission.score)

    for comment in submission.comments:
        comment_string = comment.body
        if isinstance(comment, MoreComments):
            extra_comments = comment.comments
            print('These are MoreComments')
            for extra_comment in extra_comments:
                print(of_have_replacer(extra_comment))
        if "should of" in comment_string or "could of" in comment_string or "would of" in comment_string:
            reply_string = "Hi, I believe you meant to type " + of_have_replacer(comment_string)
            comment.reply(reply_string)

    print("-------------------------------\n")