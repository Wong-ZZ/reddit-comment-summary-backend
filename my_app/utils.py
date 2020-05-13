import os
import praw

from api.settings import reddit
from django.db.utils import IntegrityError
from hashlib import sha256
from multiprocessing import Process, Manager
from my_app.models import Submissions

def fetch(submission_id):
    reddit_submission = reddit.submission(id=submission_id)
    params = {}
    all_comments = get_all_comments(reddit_submission)
    params['submission_id'] = submission_id
    params['title'] = reddit_submission.title
    params['poster'] = reddit_submission.author.name
    params['subreddit'] = reddit_submission.subreddit.display_name
    params['num_comments'] = reddit_submission.num_comments
    params['sha256'] = sha256(all_comments)
    submission = Submissions(**params)
    try:
        submission.save()
    except IntegrityError as e:
        print('duplicate key')
        return 'duplicate key'
    return {'sha256': params['sha256']}

def get_all_comments(submission):
    def append_comment(comment_list, comment):
            comment_list.append(comment.body)

    comment_list = Manager().list()
    processes = []
    comments = submission.comments.list()

    for c in comments:
        p = Process(target=append_comment, args=(comment_list,c))
        p.start()
        processes.append(p)

    for p in processes:
        p.join()

    return ''.join(comment_list)
