from django.urls import path

from articleapp.views import ArticleView

app_name = 'articleapp'

urlpatterns = [
    path('fishing_vessel/', ArticleView.as_view(), {'boardType':'어선'}, name='fishing_vessel'),
    path('fishing_boat/', ArticleView.as_view(), {'boardType':'낚시배'}, name='fishing_boat'),
    path('leisure_boat/', ArticleView.as_view(), {'boardType':'레저선박'}, name='leisure_boat'),
    path('etc/', ArticleView.as_view(), {'boardType':'기타선박'}, name='etc'),
]
