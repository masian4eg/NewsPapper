import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.core.mail import send_mail
from .models import Category, Post
from django.utils import timezone
from collections import defaultdict


logger = logging.getLogger(__name__)


def send_posts_to_email_weekly():
    last_week_posts_qs = Post.objects.filter(time_post__gte=time_post.now(tz=timezone.utc) - timedelta(days=7))

    # собираем в словарь список пользователей и список постов, которые им надо разослать
    posts_for_user = defaultdict(set)  # user -> posts

    for post in last_week_posts_qs:
        for category in post.categories.all():
            for user in category.subscribed_users.all():
                posts_for_user[user].add(post)

    send_mail(
        subject=f'{Category.name}',
        message=f'Привет, статьи за неделю {posts_for_user}',
        from_email='masian4eg@yandex.ru',
        recipient_list=['maxi4eg@mail.ru']
    )


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            send_posts_to_email_weekly,
            trigger=CronTrigger(day_of_week='mon', hour=10, minute=00),
            # То же, что и интервал, но задача триггера таким образом более понятна django
            id="send_posts_to_email_weekly",  # уникальный id
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'send_posts_to_email_weekly'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shutdown successfully!")
