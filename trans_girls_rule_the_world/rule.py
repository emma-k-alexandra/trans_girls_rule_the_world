"""Tumblr bot to reblog trans girl's selfies"""
import time
import random

from sklearn.externals import joblib

import pytumblr
import emoji

import settings

GOOD_POST = 1
BAD_POST = 0

class TransGirls(object):
    """Tumblr bot to reblog selfies"""

    def __init__(self):
        self.__tumblr = pytumblr.TumblrRestClient(*settings.TUMBLR)
        self.__emojis = settings.SAFE_EMOJIS
        self.__reblogged_posts = self.__get_reblogged_posts()
        self.__vectorizer = joblib.load('count_vectorizer.joblib')
        self.__classifier = joblib.load('mlp_post_classifier.joblib')

        self.posts = []


    def __get_reblogged_posts(self):
        """Fetches previously reblogged posts from tumblr api

        Returns:
            list - tumblr post dicts
        """
        offset = 0
        posts = []
        while offset < 100:
            posts += self.__tumblr.posts(
                settings.BLOG_URL,
                offset=offset
            )['posts']
            offset += 20

        posts.sort(key=lambda p: p['timestamp'], reverse=True)

        return posts


    def generate_emoji_string(self, length):
        """Generates a string of safe emojis of the given length

        Args:
            length (int): desired length of emoji string

        Returns:
            str: emoji string of given length
        """
        emoji_string = ''

        for _ in range(0, random.randint(0, length + 1)):
            emoji_string += self.__emojis[random.randint(0, len(self.__emojis) - 1)]

        return emoji.emojize(emoji_string, use_aliases=True)


    def fetch_posts(self):
        """Gets posts from tumblr

        Returns:
            list: post dicts from tumblr api
        """
        posts = []

        for tag in settings.TAGS:
            posts += self.__tumblr.tagged(tag)

        # sort posts reverse chronologically
        posts.sort(
            key=lambda p: p['timestamp'],
            reverse=True
        )

        return posts


    def __all_posts_by_user(self, user):
        """Post IDs of all recent posts by given user

        Args:
            user (str): username to find other posts for

        Returns:
            list: Post IDs of all recent posts by given user
        """
        return [post['id'] for post in self.posts if post['blog_name'] == user]


    def post_id(self, post):
        """Determines the root post id of the given post

        Args:
            post (dict): A tumblr post

        Returns:
            int - The given post's root id
        """
        if not post['trail']:
            return post['id']

        post_id_list = [trail['post']['id'] for trail in post['trail'] if trail.get('is_root_item')]
        return int(post_id_list[0])


    def already_reblogged(self, post):
        """Determines if a post has already been reblogged recently

        Args:
            post (dict): a tumblr post

        Returns:
            bool - if this post has already been reblogged
        """
        # If this post is older than 1 day, ignore it
        one_day_ago_in_seconds = time.time() - 86400 # seconds in a day
        if post['timestamp'] < one_day_ago_in_seconds:
            return True

        current_id = self.post_id(post)
        reblogged_ids = [self.post_id(reblogged_post) for reblogged_post in self.__reblogged_posts]

        return current_id in reblogged_ids


    def should_reblog_post(self, post):
        """Determines if a post should be reblogged

        Args:
            post (dict): post from tumblr api

        Returns:
            bool: if the given post should be reblogged
        """
        # if posts is not a photo, ignore this post
        if self.already_reblogged(post):
            return False

        tags = ' '.join(post['tags'])
        body = post['summary']

        text_of_post = ' '.join([tags, body])

        vector_of_post = self.__vectorizer.transform([text_of_post])

        predicton = self.__classifier.predict(vector_of_post)[0]

        return predicton == GOOD_POST


    def reblog_post(self, post):
        """Reblogs a post

        Args:
            post (dict): post from tumblr api
        """
        # we want to reblog this post, start building our reblog arguments
        post_args = {
            'id': post['id'],
            'reblog_key': post['reblog_key'],
        }

        # like this post bc we're having fun here
        self.__tumblr.like(**post_args)

        # generate some emoji tags
        post_args['tags'] = [
            self.generate_emoji_string(length=5),
            self.generate_emoji_string(length=5)
        ]

        # reblog
        self.__tumblr.reblog(settings.BLOG_URL, **post_args)


    def attempt_post(self):
        """Fetches posts from tumblr, determines if they're worthy, posts 'em"""
        self.posts = self.fetch_posts()

        # iterate over potential posts
        for post in self.posts:
            if self.should_reblog_post(post):
                self.reblog_post(post)

                # we only want to reblog one post within a five minute period, maximum
                return


def main():
    """Attempts to post to blog"""
    TransGirls().attempt_post()


if __name__ == '__main__':
    main()
