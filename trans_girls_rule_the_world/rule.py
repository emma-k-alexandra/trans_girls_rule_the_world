"""
Tumblr bot to reblog trans girl's selfies
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import random
import emoji
import pymongo
import pytumblr
from trans_girls_rule_the_world import settings

class TransGirls(object):
    """
    Tumblr bot to reblog selfies
    """
    def __init__(self):
        """
        Initialize tumblr and mongo client
        """
        self.__mongo = pymongo.MongoClient()
        self.__tumblr = pytumblr.TumblrRestClient(*settings.TUMBLR)
        self.__emojis = settings.SAFE_EMOJIS


    def __random_emoji(self):
        """
        Determines a random emoji index from the safe emoji list
        """
        return int(
            random.random() * len(self.__emojis)
        )


    def generate_emoji_string(self, length):
        """
        Generates a string of safe emojis of the given length

        :param length:
            length of emoji string

        :returns:
            str - safe emoji string of given length
        """
        emoji_string = ''

        for _ in xrange(0, int(random.random() * length + 1)):
            emoji_string += self.__emojis[self.__random_emoji()]

        return emoji.emojize(emoji_string, use_aliases=True)


    def __in_database(self, post_id):
        """
        Checks if a post is in the database

        :param post_id:
            tumblr id for a post

        :returns:
            boolean - if the post is in the database
        """
        return bool(self.__mongo.tumblr.trans_girl.find_one({'_id': post_id}))


    def __save_post(self, post_id):
        """
        Saves a post id to the database

        :param post_id:
            tumblr id for a post
        """
        self.__mongo.tumblr.trans_girl.insert({'_id': post_id})


    def fetch_posts(self):
        """
        Gets posts from tumblr
        """
        posts = []

        for tag in settings.TAGS:
            posts += self.__tumblr.tagged(tag)

        # randomize posts from all the tags for funsies
        random.shuffle(posts)

        return posts


    def should_reblog_post(self, post):
        """
        Determines if a post should be reblogged

        :param post:
            dict of a tumblr post

        :returns:
            bool - if the post should be reblogged
        """
        # if posts is not a photo, give up
        if post['type'] != 'photo':
            return False

        # if we've already reblogged this post, ignore it
        if self.__in_database(post['id']):
            return False

        case_insenstive_tags = set([tag.lower() for tag in post['tags']])

        # If the poster is on an approved list, reblog (as long as it's not tagged don't reblog)
        if post['blog_name'] in settings.WHITELIST and \
            not len(case_insenstive_tags & set(["don't reblog", 'dont reblog'])):
            return True

        # if posts contains any tags in the blacklist, ignore it
        if len(case_insenstive_tags & settings.BLACKLIST):
            return False

        # if we meet our critia to reblog, we should reblog!
        return True


    def reblog_post(self, post):
        """
        Reblogs a post

        :param post:
            dict of a tumblr post
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
            self.generate_emoji_string(5),
            self.generate_emoji_string(5)
        ]

        # reblog
        self.__tumblr.reblog('transgirlsruletheworld.tumblr.com', **post_args)

        # record that we reblogged this post
        self.__save_post(post['id'])


    def attempt_post(self):
        """
        Fetches posts from tumblr, determines if they're worthy
        """
        # interate over potential posts
        for post in self.fetch_posts():

            if self.should_reblog_post(post):
                self.reblog_post(post)

                # we only want to reblog one post within a five minute period, maximum
                return


def main():
    """
    Attempts to post to blog
    """
    TransGirls().attempt_post()

if __name__ == '__main__':
    main()
