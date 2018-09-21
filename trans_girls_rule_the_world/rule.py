"""Tumblr bot to reblog trans girl's selfies"""
import sys
import json
import time
import random

import emoji
import pytumblr

import scrape_tumblr

import trans_girls_rule_the_world.settings

class TransGirls(object):
    """Tumblr bot to reblog selfies"""

    def __init__(self):
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
            self.__tumblr.posts(
                trans_girls_rule_the_world.settings.BLOG_URL,
                limit=100
            )['posts'],
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

        for _ in range(0, random.randint(0, length + 1)):
            emoji_string += self.__emojis[random.randint(0, len(self.__emojis) - 1)]

        return emoji.emojize(emoji_string, use_aliases=True)


    def fetch_posts(self):
        """Gets posts from tumblr

        Returns:
            list: post dicts from tumblr api
        """
        posts = []

        for tag in trans_girls_rule_the_world.settings.TAGS:
            posts += scrape_tumblr.scape(tag)

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
            return post['photos'][0]['original_size']['url']

        post_id_list = [trail['post']['id'] for trail in post['trail'] if trail.get('is_root_item')]
        return int(post_id_list[0])


    def already_reblogged(self, post):
        """Determines if a post has already been reblogged recently

        Args:
            post (dict): a tumblr post

        Returns:
            bool - if this post has already been reblogged
        """
        # If this post is older than an hour, ignore it
        one_hour_ago_in_seconds = time.time() - 3600 # seconds in an hour
        if post['timestamp'] < one_hour_ago_in_seconds:
            return True
        
        current_id = self.post_id(post)
        reblogged_ids = [self.post_id(reblogged_post) for reblogged_post in self.__reblogged_posts]

        return current_id in reblogged_ids


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
            if post['blog_name'] == reblogged_post['blog_name']
        ]) > 2


    def save_post(self, post, positive):
        filename = '{}/{}.json'.format(
            'positive' if positive else 'negative', 
            self.post_id(post)
        ) 
        with open(filename, 'w+') as json_file:
            print('saving {}'.format(filename))
            json.dump(post, json_file)


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

        case_insenstive_tags = set(tag.lower() for tag in post['tags'])

        if post['type'] != 'photo':
            return False

        for blocked_word in trans_girls_rule_the_world.settings.BLACKLIST:

            # if username contains any text in the blacklist, ignore it
            if blocked_word in post['blog_name']:
                return False

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
            self.user_posting_a_lot(post)
        ))

        if should_ignore_post:
            self.save_post(post, positive=False)
            return False

        # if we meet our critia to reblog, we should reblog!
        self.save_post(post, positive=True)
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
