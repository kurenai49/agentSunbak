import os
import sys

from django.core.wsgi import get_wsgi_application


# 프로젝트 디렉토리 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Django 환경 설정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agentSunbak.settings")
application = get_wsgi_application()

from sunbak_crawler.crawler import run_crawler

# 크롤러 실행
run_crawler()
