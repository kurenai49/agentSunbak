from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .views import RunCrawlerView

@shared_task
def run_crawler():
    RunCrawlerView().get(None)
