from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse
from django.utils import timezone
from django.views import View

from .crawler import crawl_ksupk, crawl_daehansunbak, crawl_joonggobae
from .models import sunbak_Crawl_DataModel, connectionTimeModel



class RunCrawlerView(View):
    def get(self, request, *arg, **kwargs):
        new_items = []
        for boardType in ('어선','낚시배','레저선박','기타선박'):
            data = crawl_ksupk(boardType)
            # 데이터 저장
            for item in data:
                print(item)
                obj, created = sunbak_Crawl_DataModel.objects.update_or_create(
                    siteName=item[5],
                    regNumber=item[8],
                    defaults={
                        'imgsrc': item[0],
                        'title': item[1],
                        'price': item[2],
                        'boardType': item[3],
                        'updated_at': item[4],
                        'price_int': item[6],
                        'detailURL': item[7],
                        'boardURL': item[9],
                    }
                )
                if created:
                    new_items.append(obj)

            try:
                obj = connectionTimeModel.objects.get(boardType=boardType)
                obj.action_time = timezone.now()
                obj.boardType = boardType
                obj.save()
            except ObjectDoesNotExist:
                connectionTimeModel.objects.get_or_create(
                    action_time=timezone.now(),
                    boardType=boardType,
                )
        for boardType in ('어선','낚시배','레저선박','기타선박'):
            data = crawl_daehansunbak(boardType)
            # 데이터 저장
            for item in data:
                obj, created = sunbak_Crawl_DataModel.objects.update_or_create(
                    siteName=item[5],
                    regNumber=item[8],
                    defaults={
                        'imgsrc': item[0],
                        'title': item[1],
                        'price': item[2],
                        'boardType': item[3],
                        'updated_at': item[4],
                        'price_int': item[6],
                        'detailURL': item[7],
                        'boardURL': item[9],
                    }
                )
                if created:
                    new_items.append(obj)

            try:
                obj = connectionTimeModel.objects.get(boardType=boardType)
                obj.action_time = timezone.now()
                obj.boardType = boardType
                obj.save()
            except ObjectDoesNotExist:
                connectionTimeModel.objects.get_or_create(
                    action_time=timezone.now(),
                    boardType=boardType,
                )
        for boardType in ('어선','낚시배','레저선박','기타선박'):
            data = crawl_joonggobae(boardType)
            # 데이터 저장
            for item in data:
                obj, created = sunbak_Crawl_DataModel.objects.update_or_create(
                    siteName=item[5],
                    regNumber=item[8],
                    defaults={
                        'imgsrc': item[0],
                        'title': item[1],
                        'price': item[2],
                        'boardType': item[3],
                        'updated_at': item[4],
                        'price_int': item[6],
                        'detailURL': item[7],
                        'boardURL': item[9],
                    }
                )
                if created:
                    new_items.append(obj)

            try:
                obj = connectionTimeModel.objects.get(boardType=boardType)
                obj.action_time = timezone.now()
                obj.boardType = boardType
                obj.save()
            except ObjectDoesNotExist:
                connectionTimeModel.objects.get_or_create(
                    action_time=timezone.now(),
                    boardType=boardType,
                )

        # items = sunbak_Crawl_DataModel.objects.all()
        context = {'new_items': new_items}
        return render(request, 'sunbak_crawler/crawlResult.html', context)
