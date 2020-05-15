import cloudinary.uploader
import os
import praw

from api.settings import reddit
from django.db.utils import IntegrityError
from hashlib import sha256
from multiprocessing import Process, Manager
from my_app.models import Submissions
from wordcloud import WordCloud

def fetch(submission_id):
    reddit_submission = reddit.submission(id=submission_id)
    params = {}
    all_comments = get_all_comments(reddit_submission)
    params['submission_id'] = submission_id
    params['title'] = reddit_submission.title
    params['poster'] = reddit_submission.author.name
    params['subreddit'] = reddit_submission.subreddit.display_name
    params['num_comments'] = reddit_submission.num_comments
    params['sha256'] = sha256(all_comments.encode('utf-8')).hexdigest()
    submission = Submissions(**params)

    try:
        submission.save()
    except IntegrityError as e:
        query = Submissions.objects.get(sha256=params['sha256'])
        return {'status': 'duplicate', 'query': query}

    if params['num_comments'] is not 0:
        wordcloud_config = {}
        wordcloud_config['width'] = 2000
        wordcloud_config['height'] = 1000
        wordcloud_config['max_words'] = 500
        wordcloud = WordCloud(**wordcloud_config).generate(all_comments)
        image_name = '{}.jpg'.format(params['sha256'])
        wordcloud.to_file(image_name)
        wordcloud_url = cloudinary.uploader.upload(image_name, crop="limit",width=2000,height=1000)['secure_url']
        submission.wordcloud_url = wordcloud_url
        submission.save()
        os.remove(image_name)

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
