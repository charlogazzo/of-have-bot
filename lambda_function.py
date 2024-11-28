import praw
import boto3
from praw.models import MoreComments
from praw.exceptions import RedditAPIException
import cred
import re

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
f = open("comments-replied-to.txt", "a+")

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

    f_read = open("comments-replied-to.txt", "r+")
    # create a function to read ids from S3
    # IDs = f_read.readlines()
    
    corrected_snippets = of_have_replacer(comment)

    # this will be used as the reply string for the first deployment of the bot
    reply_paragraph_v1 = '👋 Hi there! I couldn’t help but notice you wrote "should of," "would of," or "could of." While it’s a common mistake, the correct phrase is actually "should have," "would have," or "could have." 😊... Think of it like this: "should’ve," "would’ve," and "could’ve" sound similar to "should of," "would of," and "could of," but the grammar police (and your English teacher) would prefer the former. 🚓✍️...Carry on with your excellent commenting! 🚀'
    
    

    if corrected_snippets is not None:
        if str(comment.id) + "\n" not in IDs:
            comment.reply(reply_paragraph_v1 + '\n\n\n' + '"' + corrected_snippets.strip() + '"')
            # create a function to write new ids to s3
            # first append the new ids to the 'IDs' variable
            # then write all to s3
            f.write(comment.id + "\n")
            IDs.append(comment.id)
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
        comment_string = comment.body
        if "should of " in comment_string or "could of " in comment_string or "would of " in comment_string:
            try:
                reply_to_comment(comment)
            except RedditAPIException:
                continue
    
    # update list of comments replied to in s3
    write_new_ids_to_s3(IDs)

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

# This is to run the program locally.
# On AWS Lambda, this call is not required
lambda_handler()