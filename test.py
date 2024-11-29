import unittest
import boto3
import praw
import cred
import time

class TestIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # initialize reddit client
        cls.r = praw.Reddit(
            client_id=cred.client_id,
            client_secret=cred.client_secret,
            username=cred.username,
            password=cred.password,
            user_agent=cred.user_agent
        )

        # initialize s3 client
        cls.s3 = boto3.client('s3')
        cls.bucket_name = 'of-have-bot'
        cls.file_name = 'comments-replied-to.txt'
    
    def test_persisting_ids_to_s3(self):
        Ids = ['id1', 'id2', 'id3']
        Ids_to_s3 = '\n'.join(Ids)

        # upload initial Ids to s3
        self.s3.put_object(Bucket=self.bucket_name, Key=self.file_name, Body=Ids_to_s3)

        # get list of Ids from s3 and verify
        response = self.s3.get_object(Bucket=self.bucket_name, Key=self.file_name)
        existing_list = response['Body'].read().decode('utf-8').split('\n')
        self.assertEqual(Ids, existing_list)

        # append new Ids
        updated_list_before_persist = existing_list + ['id4', 'id5']
        new_list_of_ids = '\n'.join(updated_list_before_persist)
        self.s3.put_object(Bucket=self.bucket_name, Key=self.file_name, Body=new_list_of_ids)

        # verify updated list in s3
        response = self.s3.get_object(Bucket=self.bucket_name, Key=self.file_name)
        updated_list_of_ids_from_s3 = response['Body'].read().decode('utf-8').split('\n')
        self.assertEqual(updated_list_before_persist, updated_list_of_ids_from_s3)
    

    def test_read_comments_from_reddit(self):
        sub = 'Boxing_Clips'   # subreddit was created specifically to test this bot
        subreddit = self.r.subreddit(sub)

        # load the test data
        with open('./test_resources/submission_text.txt') as f:
            text_for_submission = f.read()
        
        with open('./test_resources/comments.txt') as f_comments:
            comment_list = f_comments.readlines()
            
        # clear the subreddit
        for submission in subreddit.hot():
            submission.delete()

        # create a new post
        new_post = subreddit.submit(title='Test Post', selftext=text_for_submission)

        # add comments to the post
        for comment in comment_list:
            new_post.reply(comment)

        # read comments from posts in subreddit
        # sleep thread to ensure comments are sent
        # time.sleep(3)
        # for some reason, using list comprehension causes this test to fail so I went with an old fashioned double for-loop
        # comment_list_from_reddit = [comment.body for post in subreddit.hot() for comment in post.comments]

        time.sleep(3)

        comment_list_from_reddit = []

        for post in subreddit.hot():
            post_comments = post.comments
            for comment in post_comments:
                comment_list_from_reddit.append(comment.body)

        # verify comments match
        self.assertEqual(len(comment_list), len(comment_list_from_reddit))
        self.assertListEqual(
            sorted(comment.strip() for comment in comment_list),
            sorted(comment.strip() for comment in comment_list_from_reddit)
        )

if __name__ == '__main__':
    unittest.main()
