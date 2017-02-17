"""Tumblr bot to reblog trans girl's selfies"""
import sys
import time
import random

import emoji
import pytumblr

import trans_girls_rule_the_world.settings

reload(sys)
sys.setdefaultencoding('utf-8')

class TransGirls(object):
    """Tumblr bot to reblog selfies"""

    def __init__(self):
        """Initialize tumblr and mongo client"""
        self.__tumblr = pytumblr.TumblrRestClient(*trans_girls_rule_the_world.settings.TUMBLR)
        self.__emojis = trans_girls_rule_the_world.settings.SAFE_EMOJIS
        self.__reblogged_posts = self.__get_reblogged_posts()

        self.posts = []


    def __get_reblogged_posts(self):
        """Fetches previously reblogged posts from tumblr api

        Returns:
            list - tumblr post dicts
        """
        return sorted(
            self.__tumblr.posts(trans_girls_rule_the_world.settings.BLOG_URL)['posts'],
            key=lambda p: p['timestamp'],
            reverse=True
        )


    def generate_emoji_string(self, length):
        """Generates a string of safe emojis of the given length

        Args:
            length (int): desired length of emoji string

        Returns:
            str: emoji string of given length
        """
        emoji_string = ''

        for _ in xrange(0, random.randint(0, length + 1)):
            emoji_string += self.__emojis[random.randint(0, len(self.__emojis) - 1)]

        return emoji.emojize(emoji_string, use_aliases=True)


    def fetch_posts(self):
        """Gets posts from tumblr

        Returns:
            list: post dicts from tumblr api
        """
        posts = []

        for tag in trans_girls_rule_the_world.settings.TAGS:
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


    def already_reblogged(self, post):
        """Determines if a post has already been reblogged recently

        Args:
            post (dict): a tumblr post

        Returns:
            bool - if this post has already been reblogged
        """
        one_hour_ago_in_seconds = time.time() - 3600 # seconds in an hour
        if post['timestamp'] < one_hour_ago_in_seconds:
            return True

        # canonical url for the first photo in this post
        original_photo = post['photos'][0]['original_size']['url']

        # canonical url for first photo of all posts we've already reblogged
        reblogged_posts_photo = [
            reblogged_post['photos'][0]['original_size']['url']
            for reblogged_post in self.__reblogged_posts if
            reblogged_post.get('photos')
        ]

        # if post is in list of posts that we've already reblogged, we already reblogged it
        return original_photo in reblogged_posts_photo


    def user_posting_a_lot(self, post):
        """Determines if the author of the given post is posting a lot

        Args:
            post (dict): a tumblr post

        Returns:
            bool - if the author of this post is posting a lot
        """
        # if we've already reblogged 2 of someone's posts recently
        # that user is posting a lot
        return len([
            True \
            for reblogged_post in self.__reblogged_posts \
            if post['blog_name'] == reblogged_post['post_author']
        ]) > 2


    def should_reblog_post(self, post):
        """Determines if a post should be reblogged

        Args:
            post (dict): post from tumblr api

        Returns:
            bool: if the given post should be reblogged
        """
        # if posts is not a photo, ignore this post
        if post['type'] != 'photo':
            return False

        for blocked_word in trans_girls_rule_the_world.settings.BLACKLIST:

            # if username contains any text in the blacklist, ignore it
            if blocked_word in post['blog_name']:
                return False

        case_insenstive_tags = set(tag.lower() for tag in post['tags'])

        # if posts contains any tags in the blacklist, ignore it
        tags_are_naughty = len(
            case_insenstive_tags & trans_girls_rule_the_world.settings.BLACKLIST
        )

        # if text of post contains any text in the blacklist, ignore it
        text_in_blacklist = len(
            set(post['summary'].lower().split()) & trans_girls_rule_the_world.settings.BLACKLIST
        )


        # if we've already reblogged this post, ignore this post
        # if the author of this post is posting a lot, ignore them
        should_ignore_post = any((
            tags_are_naughty,
            text_in_blacklist,
            self.already_reblogged(post),
            self.user_posting_a_lot(post)
        ))

        if should_ignore_post:
            return False

        # if we meet our critia to reblog, we should reblog!
        return True


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
        self.__tumblr.reblog(trans_girls_rule_the_world.settings.BLOG_URL, **post_args)


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
