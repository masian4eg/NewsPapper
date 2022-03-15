from django.contrib.auth.models import User
from news.models import *

def todo():
    # очищаем все объекты
    User.objects.all().delete()
    Category.objects.all().delete()

    # создание пользователей
    johny_user = User.objects.create_user(username='johny', email='johny@mail.ru', password='johny_password')
    tommy_user = User.objects.create_user(username='tommy', email='tommy@mail.ru', password='tommy_password')

    # создание объектов авторов
    johny = Author.objects.create(user=johny_user)
    tommy = Author.objects.create(user=tommy_user)

    # создание категорий
    cat_sport = Category.objects.create(name="Спорт")
    cat_music = Category.objects.create(name="Музыка")
    cat_cinema = Category.objects.create(name="Кино")
    cat_IT = Category.objects.create(name="IT")

    # создание текстов статей/новостей
    text_article_sport_cinema = """статья_спорт_кино_Джонни__статья_спорт_кино_Джонни__статья_спорт_кино_Джонни_
                                       _статья_спорт_кино_Джонни__статья_спорт_кино_Джонни__"""

    text_article_music = """статья_музыка_Томми__статья_музыка_Томми__статья_музыка_Томми_
                                _статья_музыка_Томми__статья_музыка_Томми__"""

    text_news_IT = """новость_IT_Томми__новость_IT_Томми__новость_IT_Томми__новость_IT_Томми__
                        новость_IT_Томми__новость_IT_Томми__новость_IT_Томми__новость_IT_Томми__"""

    # создание двух статей и новости
    article_johny = Post.objects.create(author=johny, post_type=Post.article, name_news="статья_спорт_кино_Джонни",
                                        text_news=text_article_sport_cinema)
    article_tommy = Post.objects.create(author=tommy, post_type=Post.article, name_news="статья_музыка_Томми",
                                        text_news=text_article_music)
    news_tommy = Post.objects.create(author=tommy, post_type=Post.news, name_news="новость_IT_Томми", text_news=text_news_IT)

    # присваивание категорий этим объектам
    PostCategory.objects.create(post=article_johny, category=cat_sport)
    PostCategory.objects.create(post=article_johny, category=cat_cinema)
    PostCategory.objects.create(post=article_tommy, category=cat_music)
    PostCategory.objects.create(post=news_tommy, category=cat_IT)

    # создание комментариев
    comment1 = Comment.objects.create(post = article_johny, user = tommy.user, comment = "коммент Томми №1 к статье Джонни")
    comment2 = Comment.objects.create(post=article_tommy, user=johny.user, comment="коммент Джонни №2 к статье Томми")
    comment3 = Comment.objects.create(post=news_tommy, user=tommy.user, comment="коммент Томми №3 к новости Томми")
    comment4 = Comment.objects.create(post = news_tommy, user = johny.user, comment = "коммент Джонни №4 к новости Томми")

    # ставим лайки / дизлайки
    article_johny.like()
    article_johny.like()
    article_johny.like()
    article_tommy.dislike()
    article_tommy.dislike()
    news_tommy.dislike()
    news_tommy.dislike()
    news_tommy.like()
    news_tommy.like()
    comment1.like()
    comment2.dislike()
    comment3.like()
    comment3.like()
    comment3.like()
    comment3.dislike()
    comment4.like()

    # обновляем рейтинги
    johny.update_rating()
    tommy.update_rating()

    # лучший автор
    best_author = Author.objects.order_by('-rating').values('user__username', 'rating').first()
    print("username:", best_author.user.username)
    print("Рейтинг:", best_author.rating)

    # лучшая статья
    best_article = Post.objects.filter(post_type='article').order_by('-rating').first()
    print("Дата:", best_article.created)
    print(best_article.author.user.username)
    print("Рейтинг:", best_article.rating)
    print("Заголовок:", best_article.title)
    print("Превью:", best_article.preview())

    # Вывести все комментарии (дата, пользователь, рейтинг, текст) к этой статье
    for comment in best_article.comments.all(): print(comment.time_comment, comment.rating, comment.comment, sep=', ')