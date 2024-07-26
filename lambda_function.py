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

# all the Comments
global_comment_list, corrected_comment_list = [], []
f = open("comments-replied-to.txt", "a+")


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

    if "should of " in comment_string or "could of " in comment_string or "would of " in comment_string:
        print("found a matching comment\n")
        comment_string = comment_string.replace("should of ", "***should have*** ")
        comment_string = comment_string.replace("could of ", "***could have*** ")
        comment_string = comment_string.replace("would of ", "***would have*** ")
    else:
        comment_string = None    
    
    if comment_string != None:        
        return comment_string


# reply to the comment with the corrected comment
def reply_to_comment(comment):

    f_read = open("comments-replied-to.txt", "r+")
    IDs = f_read.readlines()
    
    reply_string = of_have_replacer(comment)
    if reply_string is not None:
        if str(comment.id) + "\n" not in IDs:
            comment.reply(reply_string)
            f.write(comment.id + "\n")
            print("replied to comment: ", comment.id)
        


list_of_subreddits = ["Boxing_Clips"]
other_subs = ["Advice", "AdviceForTeens", "relationship_advice", "dating_advice", "duolingo"]

def lambda_handler():
    for sub in list_of_subreddits:
        # specify the subreddit
        subreddit = r.subreddit(sub)
        print("Name of subreddit: ", sub)
        print("\n")

        # get details of submissions from a subreddit
        for submission in subreddit.hot(limit=10):

            for comment in submission.comments:
                if isinstance(comment, MoreComments):
                    handleMoreComments(comment)
                else:
                    global_comment_list.append(comment)


    print("number of comments: ", len(global_comment_list))

    for comment in global_comment_list:
        reply_to_comment(comment)

    number = 1
    for corrected_comment in corrected_comment_list:
        print(str(number) + " -------------\n", corrected_comment)
        number += 1
    
    # This return statement is used in the version deployed to AWS Lambda
    """ return_statement = ""
    for corrected_comment in corrected_comment_list:
        return_statement = return_statement + str(number) + " -------------\n" + corrected_comment
        number += 1

    return {
        "status_code": 200,
        "body": return_statement
    } """

lambda_handler()