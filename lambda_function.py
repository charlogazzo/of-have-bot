import praw
import boto3
from praw.models import MoreComments
from praw.models import Comment as PrawComment
from praw.exceptions import RedditAPIException
import praw.models
import cred
import re
<<<<<<< HEAD
from typing import List, Set, Optional
from collections import deque
=======

# initialize the reddit agent
r = praw.Reddit(
    client_id=cred.client_id,
    client_secret=cred.client_secret,
    username=cred.username,
    password=cred.password,
    user_agent=cred.user_agent
)

# s3 connection
bucket_name = cred.bucket_name
file_name = cred.file_name

# all the Comments
global_comment_list, corrected_comment_list = [], []
number_of_replies = 0

# initialize s3 client
s3 = boto3.client('s3')
IDs = []
try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        IDs = response['Body'].read().decode('utf-8').split('\n')
except Exception as e:
    print('An error occured', e)

def write_new_ids_to_s3(ids):
    ids_as_a_string = '\n'.join(ids)
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=ids_as_a_string)
    print("written new list of ids to s3")

# this method separates a moreComments instance into its individual comments
# I will test to see if it can be iterated only twice
def handleMoreComments(moreComment):
    for comment in moreComment.comments():
        if isinstance(comment, MoreComments):
            # continue for now till we can recursively work through all comments in the MoreComments object
            continue
        else:
            global_comment_list.append(comment)


# go through all comments, identify and replace matching comments
def of_have_replacer(comment):
    comment_string = comment.body

    # remove this check
    # it already happens before the reply_to_comment function is called
    if "should of " in comment_string or "could of " in comment_string or "would of " in comment_string:
        print("Found a matching comment\n")
        print(comment_string, '\n')

        # Replace the phrases with corrected versions
        corrected_comment = comment_string.replace("should of ", "***should have*** ")
        corrected_comment = corrected_comment.replace("could of ", "***could have*** ")
        corrected_comment = corrected_comment.replace("would of ", "***would have*** ")

        # Find all matches with up to 5 words before and after
        matches = re.finditer(r"((?:\S+\s+){0,5})((?:\*\*\*should have\*\*\*|\*\*\*could have\*\*\*|\*\*\*would have\*\*\*))((?:\s+\S+[.,]?\s*){0,5})", corrected_comment)

        # Collect all snippets
        snippets = []
        for match in matches:
            snippets.append(match.group(1) + match.group(2) + match.group(3))

        # Join the snippets into a single string if needed
        comment_string = " [...] ".join(snippets)  # Separate snippets with ellipses for readability
    else:
        comment_string = None    
    
    if comment_string != None:        
        return comment_string


# rewrite this method to read only from s3
def reply_to_comment(comment):
    global number_of_replies
>>>>>>> parent of dda8436 (fix bug in matching string. use regex for matching)
    
    def process_subreddits(self, subreddits: List[str], posts_limit: int = 10) -> None:
        """Process multiple subreddits efficiently"""
        for subreddit_name in subreddits:
            subreddit = self.reddit.subreddit(subreddit_name)

            for submission in subreddit.hot(limit=posts_limit):
                # process comments in batches
                comments = []
                # use limit of 5 to allow some moreComments instances to be resolved
                # if there isn't much increase in processing time, we can increase the limit
                submission.comments.replace_more(limit=5)

<<<<<<< HEAD
                for comment in submission.comments.list():
                    if isinstance(comment, MoreComments):
                        comments.extend(self.process_more_comments(comment))
                    elif comment.author.id != self.bot_id:
                        comments.append(comment)

                self.total_comments += len(comments)

                for comment in comments:
                    if any(phrase in comment.body.lower() for phrase in ('should of', 'would of', 'could of')):
                        self.handle_comment(comment)

    def handle_comment(self, comment: praw.models.Comment) -> None:
        """Handle individual comment processing and replying"""
        if comment.id in self.processed_ids:
            return
        
        corrected_snippets = self.correct_comment(comment.body)
        if corrected_snippets:
            try:
                comment.reply(f'{self.reply_template}\n\n\n"{corrected_snippets.strip()}"')
                self.replies_made += 1
                self.processed_ids.add(comment.id)
                print(f"Replied to comment: {comment.id}")
            except RedditAPIException as e:
                print(f'Failed to reply to comment {comment.id}')
=======
# subreddits will be read from a file as the number increases
list_of_subreddits = ["Boxing_Clips", "Advice", "AdviceForTeens", "relationship_advice", "dating_advice", "duolingo"]
other_subs = []

def lambda_handler():
    bot = OfHaveBot()
    subreddits = ["Advice", "AdviceForTeens", "relationship_advice", 
                  "dating_advice", "funny", "videos", "memes"]
    test_subreddit = ["Boxing_Clips"]

    bot.process_subreddits(test_subreddit)
    bot.save_processed_ids()

    # return statement used in AWS Lambda
    """return {
        "status_code": 200,
        "body": f"{bot.replies_made} comment(s) replied to"
    }"""

# Function is called directly to run locally
lambda_handler()
