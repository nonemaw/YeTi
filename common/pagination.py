from math import ceil
from common.meta import Meta



# http://flask.pocoo.org/snippets/44/
class Pagination:
    """
    the base Pagination class
    """

    def __init__(self, current_page: int, per_page: int = 5,
                 total_count: int = 0):
        self.current_page = current_page
        self.per_page = per_page
        self.total_count = total_count
        self.next_num = self.current_page + 1  # next page arrow
        self.prev_num = self.current_page - 1  # prev page arrow

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.current_page > 1

    @property
    def has_next(self):
        return self.current_page < self.pages

    def iter_pages(self, left_edge: int = 2, left_current: int = 2,
                   right_current: int = 5, right_edge: int = 2):
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
                    (num > self.current_page - left_current - 1 and
                             num < self.current_page + right_current) or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


# class PaginationSnippet(Pagination):
#     def __init__(self, current_page, show_followed_posts_cookie=0, per_page=5):
#         super(PaginationSnippet, self).__init__(current_page, per_page=per_page)
#         if not show_followed_posts_cookie:  # all posts
#             self.posts = db.Post.find({}).sort([('timestamp', -1)])
#         else:  # posts from followers
#             following = db.User.\
#                 find_one({'_id': ObjectId(current_user.id)}).get('following')
#             following_ids = [id for id,timestamp in following.items()]
#             self.posts = db.Post.\
#                 find({'author_id': {'$in': following_ids}}).sort([('timestamp', -1)])
#         self.total_count = self.posts.count()
#         self.current_num = self.total_count - (self.per_page *
#                                                        (self.current_page - 1))
#         if self.current_num > self.per_page:
#             self.current_num = self.per_page
#         self.items = [self.posts[self.prev_num * self.per_page + i] \
#                       for i in range(self.current_num)]


class PaginationSnippet(Pagination):
    def __init__(self, current_page: int, per_page: int = 15):
        super(PaginationSnippet, self).__init__(current_page,
                                                per_page=per_page)
        self.snippets = Meta.db_default.SnippetScenario.find({}).sort([('name', 1)])
        self.total_count = self.snippets.count()
        self.current_num = self.total_count - (
        self.per_page * (self.current_page - 1))
        if self.current_num > self.per_page:
            self.current_num = self.per_page
        self.items = [self.snippets[self.prev_num * self.per_page + i] for i in
                      range(self.current_num)]
