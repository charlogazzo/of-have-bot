import os

# praw
client_id=os.environ['PRAW_CLIENT_ID']
client_secret=os.environ['PRAW_CLIENT_SECRET']
password=os.environ['PRAW_PASSWORD']
username=os.environ['PRAW_USERNAME']
user_agent=os.environ['PRAW_USER_AGENT']

# aws
bucket_name=os.environ['OF_HAVE_BOT_S3_BUCKET_NAME']
file_name=os.environ['OF_HAVE_BOT_S3_FILENAME']
