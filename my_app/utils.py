import asyncio
import aiohttp
import cloudinary.uploader
import math
import os
import praw

from api.settings import reddit
from django.db.utils import IntegrityError
from hashlib import sha256
from my_app.models import Submissions
from praw.models import MoreComments
from requests import get
from wordcloud import WordCloud

PUSHSHIFT_SUBMISSION_API = 'https://api.pushshift.io/reddit/submission/comment_ids/'
PUSHSHIFT_COMMENT_API = 'https://api.pushshift.io/reddit/comment/search?ids='
DELAY = 1.0

def fetch(submission_id):
    reddit_submission = reddit.submission(id=submission_id)
    params = {}
    all_comments_info = get_all_comments_info(submission_id)
    all_comments_body = all_comments_info['all_comments_body']
    params['commenter_count'] = all_comments_info['commenter_count']
    params['submission_id'] = submission_id
    params['title'] = reddit_submission.title
    params['poster'] = reddit_submission.author.name
    params['subreddit'] = reddit_submission.subreddit.display_name
    params['num_comments'] = reddit_submission.num_comments
    params['sha256'] = sha256(all_comments_body.encode('utf-8')).hexdigest()
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
        wordcloud_config['max_words'] = 100
        wordcloud_config['collocations'] = False
        wordcloud = WordCloud(**wordcloud_config).generate_from_text(all_comments_body)
        image_name = '{}.jpg'.format(params['sha256'])
        wordcloud.to_file(image_name)
        wordcloud_url = cloudinary.uploader.upload(image_name, crop="limit",width=2000,height=1000)['secure_url']
        submission.wordcloud_url = wordcloud_url
        submission.save()
        os.remove(image_name)

    return {'sha256': params['sha256']}

def get_all_comments_info(submission_id):
    def append_comment(comments_body, comment_block):
        resp = get(PUSHSHIFT_COMMENT_API + comment_ids_str)
        comments_data = resp.json()['data']
        body = ' '.join(list(map(lambda x: x['body'], comments_data)))
        comments_body.append(body)

    # fetch all comment ids of a submission
    all_comment_ids = get(PUSHSHIFT_SUBMISSION_API + submission_id).json()['data']
    # list that contains url for fetching comments
    fetch_urls = []

    # divide comment ids into blocks of 1000
    i = 0
    while i < math.ceil(len(all_comment_ids) / 1000):
        start = i * 1000
        end = start + 1000
        sl = slice(start, end, 1)
        comment_ids_str = ','.join(all_comment_ids[sl])
        fetch_urls.append(f'{PUSHSHIFT_COMMENT_API}{comment_ids_str}')
        i += 1

    comments_body = []
    comments_store = {}
    commenter_count = {}
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(fetch_all(fetch_urls, comments_store, commenter_count, loop))
    loop.run_forever()

    count = 0
    for j in range(i):
        count += comments_store[f'count{j}']
        comments_body.append(comments_store[j])

    print('comments: ' + str(count))

    return {'all_comments_body': ' '.join(comments_body), 'commenter_count': commenter_count}

async def fetch_comments(session, url, comments_store, commenter_count, index):
    async with session.get(url) as response:
        json = await response.json()
        data = json['data']
        comments = ' '.join(list(map(lambda c: c['body'].replace('\n', ' '), data)))
        comments_store[index] = comments
        comments_store[f'count{index}'] = len(data)
        for comment in data:
            author = comment['author']
            if commenter_count.get(author) is None:
                commenter_count[author] = 1
            else:
                commenter_count[author] += 1

async def fetch_all(fetch_urls, comments_store, commenter_count, loop):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(len(fetch_urls)):
            url = fetch_urls[i]
            tasks.append(asyncio.ensure_future(fetch_comments(session, url, comments_store, commenter_count, i)))
            await asyncio.sleep(DELAY)
        await asyncio.gather(*tasks)
        loop.stop()
