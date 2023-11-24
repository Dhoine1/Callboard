import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django_apscheduler import util
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.utils.timezone import now
from announce.models import Note
from django.contrib.auth.models import User
import datetime

logger = logging.getLogger(__name__)


def my_job():
    week = now() - datetime.timedelta(days=7)
    posts = Note.objects.filter(create_date__gte=week)
    emails = User.objects.all().values_list('email', flat=True)
    list_to_send_text = ''
    list_to_send = ''

    for item_list in posts:
        list_to_send_text += f'-- {item_list.header} : Ссылка {settings.SITE_URL}/announce/{item_list.pk} --'
        list_to_send += f'<a href={settings.SITE_URL}/announce/{item_list.pk}> {item_list.header}</a><br><br>'

    for email in emails:
        title = f'Новости за неделю:'
        msg = EmailMultiAlternatives(title, list_to_send_text, None, [email])
        msg.attach_alternative(list_to_send, "text/html")
        msg.send()



@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="mon", hour="10", minute="00"),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")