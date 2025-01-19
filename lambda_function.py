import praw
import boto3
from praw.models import MoreComments
from praw.models import Comment as PrawComment
from praw.exceptions import RedditAPIException
import praw.models
import cred
import re
from typing import List, Set, Optional
from collections import deque


class OfHaveBot:
    def __init__(self):
        # initialize PRAW client
        self.reddit = praw.Reddit(
            client_id=cred.client_id,
            client_secret=cred.client_secret,
            username=cred.username,
            password=cred.password,
            user_agent=cred.user_agent
        )

        self.bot_id = '14sfn724vi'

        # S3 Configuration
        self.bucket_name = cred.bucket_name
        self.file_name = cred.file_name
        self.s3 = boto3.client('s3')

        # Regex pattern
        self.pattern = re.compile(r'\b(should|could|would) of(?! course)\b', re.IGNORECASE)

        self.processed_ids: Set[str] = self.load_processed_ids()

        # For return statement
        self.total_comments = 0
        self.replies_made = 0

        self.reply_template = ('👋 Hi there! I couldn\'t help but notice you wrote "should of," "would of," '
                             'or "could of." While it\'s a common mistake, the correct phrase is actually '
                             '"should have," "would have," or "could have." 😊... Think of it like this: '
                             '"should\'ve," "would\'ve," and "could\'ve" sound similar to "should of," '
                             '"would of," and "could of," but the grammar police (and your English teacher) '
                             'would prefer the former. 🚓✍️...Carry on with your excellent commenting! 🚀')
        
    def load_processed_ids(self) -> Set[str]:
        """Load previously processed comment IDs from S3"""
        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=self.file_name)
            return set(response['Body'].read().decode('utf-8').split('\n'))
        except Exception as e:
            print(f'Error loading processed IDs: {e}')
            return set()
        
    def save_processed_ids(self) -> None:
        """Save processed comment IDs to S3"""
        ids_string = '\n'.join(self.processed_ids)
        self.s3.put_object(Bucket=self.bucket_name, Key=self.file_name, Body=ids_string)
        print('Updated processed IDs in S3')

    def process_more_comments(self, more_comments: MoreComments) -> List[PrawComment]:
        """Process MoreComment objects"""
        comments = []
        queue = deque([more_comments])

        while queue:
            # pop a MoreComments instance
            current = queue.popleft()
            try:
                for comment in current.comments():
                    if isinstance(comment, MoreComments):
                        queue.append(comment)
                    else:
                        comments.append(comment)
            except Exception as e:
                print(f'Error processing MoreComments: {e}')
                continue

        return comments
    
    def correct_comment(self, comment_text: str) -> Optional[str]:
        """Process and correct comment text"""
        def replace_match(match):
            word = match.group(1)
            return f'***{word} have*** '
        
        corrected = self.pattern.sub(replace_match, comment_text)

        if corrected != comment_text:
            # Extract context around corrections
            context_pattern = r"((?:\S+\s+){0,5})((?:\*\*\*should have\*\*\*|\*\*\*could have\*\*\*|\*\*\*would have\*\*\*))((?:\s+\S+[.,]?\s*){0,5})"
            matches = re.finditer(context_pattern, corrected)
            snippets = [f"{m.group(1)}{m.group(2)}{m.group(3)}" for m in matches]
            
            return " [...] ".join(snippets) if snippets else None
        return None
    
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
