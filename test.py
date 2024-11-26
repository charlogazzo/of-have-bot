import logging
import boto3
import praw
from lambda_function import r #laziness lol

bucket_name = 'of-have-bot'
file_name = 'comments-replied-to.txt'

s3 = boto3.client('s3')

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
for logger_name in ("praw", "prawcore"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

# test that the ids of new comments are added to the list of IDs on AWS S3
def test_persisting_ids_to_s3():
    Ids = ['id1', 'id2', 'id3']

    Ids_to_s3 = '\n'.join(Ids)
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=Ids_to_s3)
    
    # get Ids of already replied-to comments from S3
    response = s3.get_object(Bucket=bucket_name, Key=file_name)
    existing_list = response['Body'].read().decode('utf-8').split('\n')
    assert Ids == existing_list

    # add new ids and persist to s3
    updated_list_before_persist = existing_list + ['id4', 'id5']
    new_list_of_ids = '\n'.join(updated_list_before_persist)
    s3.put_object(Bucket=bucket_name, Key=file_name, Body=new_list_of_ids)

    # get updated list from s3 and check if new
    response = s3.get_object(Bucket=bucket_name, Key=file_name)
    updated_list_of_ids_from_s3 = response['Body'].read().decode('utf-8').split('\n')
    assert updated_list_before_persist == updated_list_of_ids_from_s3

# create a new post with matching comments to test
def test_matching_comments_from_reddit():
    sub = 'Boxing_Clips'
    subreddit = r.subreddit(sub)

    # first clear subreddit
    for submission in subreddit.hot():
        submission.delete()

    # create a new post
    new_post = subreddit.submit(title='Test Post', selftext=)


test_persisting_ids_to_s3()