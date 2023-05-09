from django.urls import path

from sunbak_crawler.views import RunCrawlerView

app_name = 'crawler'
urlpatterns = [
    path('run_crawler/', RunCrawlerView.as_view(), name='run-crawler'),
]