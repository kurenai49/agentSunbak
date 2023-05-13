'''
http://www.ksupk.or.kr/file/index.php   # 한국선박중개소
https://daehansunbak.com/
http://www.xn--299ak40atvj.com/
http://www.goldenship.co.kr/
'''
import os
import re
import shutil
import uuid
from time import sleep
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
# Create your views here.
from django.utils import timezone

from .models import sunbak_Crawl_DataModel, connectionTimeModel


# Create your views here.


def download_and_save_image(model_instance, url):
    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()  # 에러 발생 시 예외를 발생시킵니다.

        # UUID를 사용하여 임의의 파일 이름을 생성합니다.
        # 이미지 URL의 확장자를 유지하기 위해 os.path.splitext를 사용합니다.
        ext = urlparse(url).path.split('.')[-1]
        filename = '{}.{}'.format(uuid.uuid4(), ext)

        model_instance.thumb_image.save(filename, ContentFile(response.content), save=False)
        return True
    except:
        return False

# URL + params = GET URL
def create_get_url(base_url, params):
    from urllib.parse import urlencode
    query_string = urlencode(params)
    full_url = f"{base_url}?{query_string}"
    return full_url

# 어선 # 낚시배 # 선외기 # 레저선박
def extract_price_and_convert_to_int(price_str):
    # 정규식을 사용하여 금액 정보를 추출합니다.
    extracted_price = re.findall(r'((?:\d*[일이삼사오육칠팔구]?[억만천백십]+)+)', price_str)

    # 숫자만 있는 경우 처리
    if price_str.isdigit():
        return int(price_str)

    # 첫 번째 금액 정보만 변환하여 반환합니다.
    if extracted_price:
        return convert_price_to_int(extracted_price[0])
    else:
        return None

def convert_price_to_int(price_str):
    try:
        # 한글 숫자를 일반 숫자로 변환합니다.
        korean_to_number = {'일': '1', '이': '2', '삼': '3', '사': '4', '오': '5', '육': '6', '칠': '7', '팔': '8', '구': '9'}
        for kor, num in korean_to_number.items():
            price_str = price_str.replace(kor, num)

        # 정규식을 사용하여 숫자와 한글 문자를 추출합니다.
        price_parts = re.findall(r'(\d+|[억만천백십원])', price_str)

        price_int = 0
        current_value = ''
        current_man_unit = 0

        for part in price_parts:
            if part.isdigit():
                current_value += str(part)
            elif part == '천':
                current_multiplier = 1000
                current_man_unit += int(current_value) * current_multiplier
                current_value = ''
            elif part == '백':
                current_multiplier = 100
                current_man_unit += int(current_value) * current_multiplier
                current_value = ''
            elif part == '십':
                current_multiplier = 10
                current_man_unit += int(current_value) * current_multiplier
                current_value = ''
            elif part == '원':
                if current_man_unit == 0:
                    price_int += int(current_value)
                break
            elif part == '억':
                price_int += current_man_unit * 100000000 if current_man_unit != 0 else int(current_value) * 100000000
                current_value = ''
                current_man_unit = 0
            elif part == '만':
                price_int += current_man_unit * 10000 if current_man_unit != 0 else int(current_value) * 10000
                current_value = ''
                current_man_unit = 0
        if current_man_unit != 0:
            price_int += current_man_unit

        return price_int
    except:
        return price_str


# boardType'어선'
def crawl_ksupk(boardType):
    data = []
    siteName = '한국선박중개소'
    def crawling():
        page = 0
        for _ in range(30): # 최대 30페이지까지 확인, 그전에 페이지가 끝나면 break
            page += 1
            if page == 1:
                response = requests.get(
                    req_url,
                    params=params,
                    headers=headers,
                    verify=False,
                )
            else:
                postdata = {
                    'cs_mkey': '1',
                    'cs_ancestor': '1',
                    'kw': '',
                    'tkind': '',
                    'page': page,
                }
                response = requests.post(
                    req_url_add,
                    headers=headers,
                    data=postdata,
                    verify=False,
                )
            sleep(1)

            # 응답 헤더에서 인코딩 확인
            encoding = response.encoding

            # 인코딩이 정의되지 않은 경우, 일반적으로 사용되는 utf-8로 설정
            if encoding != 'euc-kr':
                encoding = 'euc-kr'
            try:
                soup = BeautifulSoup(response.content.decode(encoding), 'html.parser')
            except:
                soup = BeautifulSoup(response.content.decode('cp949'), 'html.parser')
            items = soup.select('#ship_list_area')

            for item in items:
                imgsrc = item.select_one('img')['src']
                if imgsrc.startswith('./'):
                    imgsrc = 'http://www.ksupk.or.kr/file' + imgsrc[1:]

                try:
                    regNumber = int(item.select_one('#ship_list_area2').text.strip())
                except:
                    continue
                title = item.select_one('#ship_list_area4 span').text.strip()

                uploaded_date = item.select_one('#ship_list_area9').contents[0]
                uploaded_date = parse(uploaded_date).strftime('%Y-%m-%d')
                price = item.select_one('#ship_list_area8').text.strip()
                price_int = extract_price_and_convert_to_int(price)

                try:
                    detailURL = item.select_one('span[style="cursor: pointer;"]')['onclick']
                except:
                    detailURL = ''
                try:
                    price_int = int(price_int)
                except:
                    price_int = 0

                if price_int < 10000:
                    price_int = price_int * 10000

                if price == '협의원':
                    price = '협의'
                boardURL = create_get_url(req_url, params)
                try:
                    image_file = requests.get(imgsrc).content
                except:
                    pass
                data.append((imgsrc, title, price, boardType, uploaded_date, siteName, price_int, detailURL, regNumber, boardURL, image_file))

            nextPage = soup.select('span.choi_button3')[-1]['value']
            if int(page) >= int(nextPage):
                break
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-CN;q=0.6,zh;q=0.5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'http://www.ksupk.or.kr/file/ship_sale_list2.php?cs_ancestor=1&cs_mkey=1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }
    if boardType == '어선':
        params = {
            'cs_ancestor': '1',
            'cs_mkey': '1',
        }
        req_url = 'http://www.ksupk.or.kr/file/ship_sale_list2.php'
        req_url_add = 'http://www.ksupk.or.kr/file/ship_sale_list_add2.php'

        crawling()
    elif boardType == '낚시배':
        params = {
            'cs_ancestor': '2',
            'cs_mkey': '2',
        }
        req_url = 'http://www.ksupk.or.kr/file/ship_sale_list1.php'
        req_url_add = 'http://www.ksupk.or.kr/file/ship_sale_list_add1.php'
        crawling()
    elif boardType == '레저선박':
        params = {
            'cs_ancestor': '9',
            'cs_mkey': '9',
        }
        req_url = 'http://www.ksupk.or.kr/file/ship_sale_list6.php'
        req_url_add = 'http://www.ksupk.or.kr/file/ship_sale_list_add6.php'
        crawling()
    elif boardType == '기타선박':
        params = {
            'cs_ancestor': '9',
            'cs_mkey': '9',
        }

        req_url = 'http://www.ksupk.or.kr/file/ship_sale_list3.php' # 기타선박
        req_url_add = 'http://www.ksupk.or.kr/file/ship_sale_list_add3.php'
        crawling()

        params = {
            'cs_ancestor': '3',
            'cs_mkey': '3',
        }
        req_url = 'http://www.ksupk.or.kr/file/ship_sale_list5.php' # 선외기
        req_url_add = 'http://www.ksupk.or.kr/file/ship_sale_list_add5.php'
        crawling()
    return data

# 대한선박중개
def crawl_daehansunbak(boardType):
    siteName = '대한선박중개'
    data = []
    def crawling():
        page = 0
        for _ in range(30):
            page += 1
            req_url = 'https://daehansunbak.com/index.html'
            if page == 1:
                response = requests.get(req_url, params=params, headers=headers, verify=False)
            else:
                params['page'] = page
                response = requests.get(req_url, params=params, headers=headers, verify=False)
            sleep(1)
            soup = BeautifulSoup(response.text, 'html.parser')

            trs = soup.select_one('tr[align="center"]').parent.select('tr')[1:]
            if not trs:
                break
            for tr in trs:
                location = tr.select('td')[3].text.strip()
                tons = tr.select('td')[4].text.strip()
                modelYear = tr.select('td')[5].text.strip().split('/')[0]
                permission = tr.select('td')[6].text.strip()

                try:
                    regNumber = int(tr.select('td')[0].text.strip())
                except:
                    continue
                title = f"{location}/{tons}/{modelYear}연식/{permission}"
                imgsrc = tr.select('td')[2].img['src']
                price = tr.select('td')[8].text.strip().replace('계약가능','')
                uploaded_date = tr.select('td')[9].text.strip()
                uploaded_date = parse(uploaded_date).strftime('%Y-%m-%d')
                try:
                    detailURL = tr.select('td')[3].a['onclick'].split("'")[1]
                except:
                    detailURL = ''
                price_int = extract_price_and_convert_to_int(price)
                try:
                    price_int = int(price_int)
                except:
                    price_int = 0
                boardURL = create_get_url(req_url, params)
                data.append((imgsrc, title, price, boardType, uploaded_date, siteName, price_int, detailURL, regNumber, boardURL))
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-CN;q=0.6,zh;q=0.5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'https://daehansunbak.com/index.html?p_no=5',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    if boardType == '어선':
        params = {
            'p_no': '5', # 근해어선
        }
        crawling()
        params = {
            'p_no': '1', # 어선
        }
        crawling()
    elif boardType == '낚시선':
        params = {
            'p_no': '2', # 낚시선
        }
        crawling()
    elif boardType == '레저선박':
        params = {
            'p_no': '3', # 레저선
        }
        crawling()
    elif boardType == '기타선박':
        params = {
            'p_no': '4', # 기타선박
        }
        crawling()
    return data

#도시선박 (중고배.com)
def crawl_joonggobae(boardType):
    def crawling():
        page = 0
        for _ in range(30):
            page += 1
            req_url = 'http://www.xn--299ak40atvj.com/board_ship/sell_list.asp'
            if page != 1:
                params['page']=page
            response = requests.get(
                req_url,
                params=params,
                headers=headers,
                verify=False,
            )
            sleep(1)

            encoding = response.encoding

            # 인코딩이 정의되지 않은 경우, 일반적으로 사용되는 utf-8로 설정
            if encoding != 'euc-kr':
                encoding = 'euc-kr'
            try:
                soup = BeautifulSoup(response.content.decode(encoding), 'html.parser')
            except:
                soup = BeautifulSoup(response.content.decode('cp949'), 'html.parser')

            try:
                trs = soup.select_one('div.tableBox tr[style="cursor:pointer;"]').parent.select('tr')[1:]
            except:
                break

            for tr in trs:
                try:
                    regNumber = int(tr.select('td')[0].text.strip())
                except:
                    continue
                tons = tr.select('td')[3].text.strip()
                permission = tr.select('td')[4].text.strip()
                price = tr.select('td')[5].text.strip().split('/')[0]
                sellType = tr.select('td')[6].text.strip()

                title = f"{tons}/{permission}/{sellType}"
                imgsrc = tr.select('td')[1].select_one('div.photo')['style'].replace("background-image:url('", '').replace("'); ", '')
                if 'http://www.xn--299ak40atvj.com' not in imgsrc:
                    imgsrc = 'http://www.xn--299ak40atvj.com' + imgsrc
                uploaded_date = tr.select('td')[8].text.strip()
                uploaded_date = parse(uploaded_date).strftime('%Y-%m-%d')
                try:
                    detailURL = tr['onclick'].replace("location.href='", '').replace("';", '')
                    if 'http://www.xn--299ak40atvj.com/board_ship/' not in detailURL:
                        detailURL = 'http://www.xn--299ak40atvj.com/board_ship/' + detailURL
                except:
                    detailURL = ''
                price_int = extract_price_and_convert_to_int(price)
                try:
                    price_int = int(price_int)
                except:
                    price_int = 0
                boardURL = create_get_url(req_url, params)
                data.append((imgsrc, title, price, boardType, uploaded_date, siteName, price_int, detailURL, regNumber, boardURL))

    siteName = '도시선박'
    data = []
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-CN;q=0.6,zh;q=0.5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Referer': 'http://www.xn--299ak40atvj.com/',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    }

    if boardType == '어선':
        params = {
            's_board_cate': 'A',
        }
        crawling()
        params = {
            's_board_cate': 'B',
        }
        crawling()
    elif boardType == '낚시배':
        params = {
            's_board_cate': 'C',
        }
        crawling()
    elif boardType == '레저선박':
        params = {
            's_board_cate': 'D',
        }
        crawling()
    elif boardType == '기타선박':
        params = {
            's_board_cate': 'E',
        }
        crawling()
    return data



def run_crawler():
    # 크롤링할때마다 모든 데이터 삭제
    sunbak_Crawl_DataModel.objects.all().delete()
    media_dir = os.path.join(settings.MEDIA_ROOT, 'thumbs')
    if os.path.exists(media_dir):
        shutil.rmtree(media_dir)
    os.makedirs(media_dir, exist_ok=True)
    new_items = []
    for boardType in ('어선', '낚시배', '레저선박', '기타선박'):
        data = crawl_ksupk(boardType)
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
                if download_and_save_image(obj, item[0]):  # 이미지 다운로드 및 저장
                    obj.save()  # 이미지가 성공적으로 저장되면 변경 사항을 커밋합니다.
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
    for boardType in ('어선', '낚시배', '레저선박', '기타선박'):
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
                if download_and_save_image(obj, item[0]):  # 이미지 다운로드 및 저장
                    obj.save()  # 이미지가 성공적으로 저장되면 변경 사항을 커밋합니다.
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
    for boardType in ('어선', '낚시배', '레저선박', '기타선박'):
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
                if download_and_save_image(obj, item[0]):  # 이미지 다운로드 및 저장
                    obj.save()  # 이미지가 성공적으로 저장되면 변경 사항을 커밋합니다.
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
