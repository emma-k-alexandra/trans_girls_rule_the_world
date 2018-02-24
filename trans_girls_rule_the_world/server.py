"""Simple server for queueing selfies to reblog"""
import collections

import flask

import trans_girls_rule_the_world.rule

APP = flask.Flask(__name__)

POST_QUEUE = collections.deque()

@APP.route('/post_selfie')
def post_selfie():
    """Endpoint to queue and reblog selfies"""
    # fetch posts
    post_determiner = trans_girls_rule_the_world.rule.TransGirls()
    posts = post_determiner.fetch_posts()

    posts_to_reblog = []

    # determine what posts to reblog
    for post in posts:
        if post_determiner.should_reblog_post(post):
            posts_to_reblog.append(post)

    # don't add any duplicate posts to the post queue
    for post in posts_to_reblog:
        should_add_to_queue = True
        for post_in_queue in POST_QUEUE:
            if post_determiner.post_id(post) == post_determiner.post_id(post_in_queue):
                should_add_to_queue = False

        if should_add_to_queue:
            POST_QUEUE.append(post)

    # if we have a post to reblog, reblog it and remove from queue
    if POST_QUEUE:
        post_determiner.reblog_post(POST_QUEUE.popleft())

    # we did it!
    return 'Success'

APP.run()
