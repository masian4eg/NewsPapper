from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        # суммарный рейтинг каждой статьи автора * 3
        post_rating = Post.objects.filter(author=self).values('rating')  # получим список объектов со словарями
        # пройдёмся по списку, вытащим каждый словарь и у него - по ключу обратимся к значению
        post_rating = sum(rate['rating'] for rate in post_rating) * 3

        # суммарный рейтинг всех комментариев автора
        comments_rating = Comment.objects.filter(user=self.user).values('rating')  # получим список объектов со словарями
        comments_rating = sum(rate['rating'] for rate in comments_rating)

        # суммарный рейтинг всех комментариев к статьям автора
        news_comments_rating = Post.objects.filter(author=self).values('comments__rating')
        news_comments_rating = sum(rate['comments__rating'] for rate in news_comments_rating)

        self.rating = sum([post_rating, comments_rating, news_comments_rating])
        self.save()


class Category(models.Model):
    name = models.CharField(unique=True, max_length=150)


class Post(models.Model):
    article = 'a'
    news = 'n'

    POST_TYPE = [
        (article, "Статья"),
        (news, "Новость")
    ]

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=1, choices=POST_TYPE, default=article)
    time_post = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    name_news = models.CharField(max_length=256)
    text_news = models.TextField()
    rating = models.IntegerField(default=0)

    def get_categories(self):
        result = []
        for category in self.category.all():
            result.append(category)
        return result

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        size = 124 if len(self.text_news) > 124 else len(self.text_news)
        return self.text_news[:size] + '...'

    def get_absolute_url(self):
        return f'/news/{self.id}'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    time_comment = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0.0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()
