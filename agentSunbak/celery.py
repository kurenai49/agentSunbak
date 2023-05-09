from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# 'settings' 모듈을 Celery 프로그램의 기본 설정 소스로 설정합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agentSunbak.settings')

app = Celery('agentSunbak')

# Django의 설정에서 Celery 설정을 가져옵니다.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 등록된 Django 앱 설정에서 작업을 자동 찾습니다.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
