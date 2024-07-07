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
subreddit = r.subreddit("funny")

# get details of submissions from a subreddit
for submission in subreddit.hot(limit=5):
    print("Title:", submission.title)
    print("Text:", submission.selftext)
    print("Score:", submission.score)

    for comment in submission.comments:
        if isinstance(comment, MoreComments):
            continue
        elif "should of" in comment.body:
            print(comment.body)
            # comment.reply("Well hello there! I see you wrote 'should of' but I'm guessing you meant 'should have'")

    print("-------------------------------\n")