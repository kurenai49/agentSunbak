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
import logging
import os, shutil

loggerName = 'sunbakCrawler'
save_logfileName = "logging.log"
purefilename = save_logfileName.split('.')[0]

logger = logging.getLogger(loggerName)
logger.setLevel(logging.INFO)

formatter = logging.Formatter(fmt='[%(asctime)s] - %(name)s - %(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
# formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s: %(message)s')

stream_hander = logging.StreamHandler()
stream_hander.setFormatter(formatter)
logger.addHandler(stream_hander)

file_handler = logging.FileHandler(save_logfileName, encoding='utf-8')  # 사용환경별 코드
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

if os.path.getsize(f"{purefilename}.log") > 500000:
    try:
        shutil.copy(f"{purefilename}.log",f"{purefilename}1.log")
        shutil.copy(f"{purefilename}.log1",f"{purefilename}2.log")
        shutil.copy(f"{purefilename}.log2",f"{purefilename}3.log")
        shutil.copy(f"{purefilename}.log3",f"{purefilename}4.log")
        os.remove(f"{purefilename}.log")
    except:
        pass

# logger.info('')
# logger.warning('')
# logger.error('')
# logger.critical('')
# logger.fatal('')
def tons_from_title(string):
    match = re.findall(r"(\b\d+\.\d+|\b\d+(?=\s?(t|톤|ton)))", string)
    if match:
        return match[0][0]
    else:
        return 0

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
    logger.info(f'한국선박중개소 크롤링을 시작합니다 boardType={boardType}')
    data = []
    siteName = '한국선박중개소'
    def crawling(params, headers):
        page = 0
        for _ in range(30): # 최대 30페이지까지 확인, 그전에 페이지가 끝나면 break
            page += 1
            logger.info(f'한국선박중개소 - boardType={boardType}, {page}페이지 크롤링')
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

                # tons 수집을 위한 detailURL 확인
                params = {
                    'no': regNumber,
                }
                try:
                    headers = {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-CN;q=0.6,zh;q=0.5',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Pragma': 'no-cache',
                        'Referer': 'http://www.ksupk.or.kr/file/ship_sale_list2.php?cs_ancestor=1&cs_mkey=1',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
                    }
                    response = requests.get(
                        'http://www.ksupk.or.kr/file/ship_view_pop.php',
                        params=params,
                        headers=headers,
                        verify=False,
                    )
                    try:
                        soupArticle = BeautifulSoup(response.content.decode('euc-kr'), 'html.parser')
                    except:
                        soupArticle = BeautifulSoup(response.content.decode('cp949'), 'html.parser')
                    # tons
                    for elem in soupArticle.select('td'):
                        if '톤수' in elem.text:
                            tons = tons_from_title(elem.nextSibling.nextSibling.text)
                            if tons:
                                tons = float(tons)
                            break
                    else:
                        tons = 0
                    # 모델연식
                    for elem in soupArticle.select('td'):
                        if '진수년월일' in elem.text:
                            try:
                                modelYear = elem.nextSibling.nextSibling.text.split('년')[0].strip()
                                modelYear = int(modelYear)
                            except:
                                modelYear = None
                            break
                    else:
                        modelYear = None

                    # 판매소재지
                    for elem in soupArticle.select('td'):
                        if '판매정박지' in elem.text:
                            try:
                                salesLocation = elem.nextSibling.nextSibling.text.strip()
                            except:
                                salesLocation = ""
                            break
                    else:
                        salesLocation = ""

                except:
                    tons = 0
                    modelYear = None
                    salesLocation = ""
                data.append([imgsrc, title, price, boardType, uploaded_date, siteName, price_int, detailURL, regNumber, boardURL, tons, modelYear, salesLocation])

            try:
                nextPage = soup.select('span.choi_button3')[-1]['value']
            except:
                logger.warning(f'다음 페이지({nextPage}) 없음')
                break
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
        crawling(params, headers)
    elif boardType == '낚시배':
        params = {
            'cs_ancestor': '2',
            'cs_mkey': '2',
        }
        req_url = 'http://www.ksupk.or.kr/file/ship_sale_list1.php'
        req_url_add = 'http://www.ksupk.or.kr/file/ship_sale_list_add1.php'
        crawling(params, headers)
    elif boardType == '레저선박':
        params = {
            'cs_ancestor': '9',
            'cs_mkey': '9',
        }
        req_url = 'http://www.ksupk.or.kr/file/ship_sale_list6.php'
        req_url_add = 'http://www.ksupk.or.kr/file/ship_sale_list_add6.php'
        crawling(params, headers)
    elif boardType == '기타선박':
        params = {
            'cs_ancestor': '9',
            'cs_mkey': '9',
        }

        req_url = 'http://www.ksupk.or.kr/file/ship_sale_list3.php' # 기타선박
        req_url_add = 'http://www.ksupk.or.kr/file/ship_sale_list_add3.php'
        crawling(params, headers)

        params = {
            'cs_ancestor': '3',
            'cs_mkey': '3',
        }
        req_url = 'http://www.ksupk.or.kr/file/ship_sale_list5.php' # 선외기
        req_url_add = 'http://www.ksupk.or.kr/file/ship_sale_list_add5.php'
        crawling(params, headers)
    return data

# 대한선박중개
def crawl_daehansunbak(boardType):
    siteName = '대한선박중개'
    logger.info(f'{siteName} 크롤링을 시작합니다 boardType={boardType}')
    data = []
    def crawling(params, headers):
        page = 0
        for _ in range(30):
            page += 1
            logger.info(f'{siteName} - boardType={boardType}, {page}페이지 크롤링')
            req_url = 'https://daehansunbak.com/index.html'
            if page == 1:
                response = requests.get(req_url, params=params, headers=headers, verify=False)
            else:
                params['page'] = page
                response = requests.get(req_url, params=params, headers=headers, verify=False)
            sleep(1)
            soup = BeautifulSoup(response.text, 'html.parser')

            try:
                trs = soup.select_one('tr[align="center"]').parent.select('tr')[1:]
            except AttributeError:
                break
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

                params = {
                    't_db': 'f_sunbak_sale',
                    'no': regNumber,
                }
                try:
                    headers = {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                        'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-CN;q=0.6,zh;q=0.5',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Pragma': 'no-cache',
                        'Referer': 'https://daehansunbak.com/index.html',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'same-origin',
                        'Sec-Fetch-User': '?1',
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
                        'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                    }
                    response = requests.get(
                        'https://daehansunbak.com/fboard/f_sunbak_sale/f_open_content.html',
                        params=params,
                        headers=headers,
                        verify=False
                    )
                    soupArticle = BeautifulSoup(response.text, 'html.parser')
                    for elem in soupArticle.select('td.th2'):
                        if '톤' in elem.text:
                            tons = tons_from_title(elem.nextSibling.nextSibling.text)
                            if tons:
                                tons = float(tons)
                            break
                    else:
                        tons = 0
                    for elem in soupArticle.select('td.th2'):
                        if '소재지역' in elem.text:
                            salesLocation = elem.nextSibling.nextSibling.text.strip()
                            break
                    else:
                        salesLocation = ""
                except:
                    tons = 0
                    salesLocation = ""
                data.append([imgsrc, title, price, boardType, uploaded_date, siteName, price_int, detailURL, regNumber, boardURL, tons, modelYear, salesLocation])

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
        crawling(params, headers)
        params = {
            'p_no': '1', # 어선
        }
        crawling(params, headers)
    elif boardType == '낚시선':
        params = {
            'p_no': '2', # 낚시선
        }
        crawling(params, headers)
    elif boardType == '레저선박':
        params = {
            'p_no': '3', # 레저선
        }
        crawling(params, headers)
    elif boardType == '기타선박':
        params = {
            'p_no': '4', # 기타선박
        }
        crawling(params, headers)

    return data

#도시선박 (중고배.com)
def crawl_joonggobae(boardType):
    siteName = '도시선박'
    logger.info(f'{siteName} 크롤링을 시작합니다 boardType={boardType}')
    def crawling(params, headers):
        page = 0
        for _ in range(30):
            page += 1
            logger.info(f'{siteName} - boardType={boardType}, {page}페이지 크롤링')
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

                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'ko,en-US;q=0.9,en;q=0.8,ru;q=0.7,zh-CN;q=0.6,zh;q=0.5',
                    'Cache-Control': 'no-cache',
                    'Connection': 'keep-alive',
                    'Pragma': 'no-cache',
                    'Referer': 'http://www.xn--299ak40atvj.com/board_ship/sell_list.asp?search_txt=&search_key=&s_board_cate=A&s_board_area=&page=5&nowblock=0',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
                }
                try:
                    response = requests.get(
                        detailURL,
                        params=params,
                        headers=headers,
                        verify=False
                    )
                    try:
                        soupArticle = BeautifulSoup(response.content.decode('euc-kr'), 'html.parser')
                    except:
                        soupArticle = BeautifulSoup(response.content.decode('cp949'), 'html.parser')
                    for elem in soupArticle.select('th'):
                        if '톤' in elem.text:
                            tons = tons_from_title(elem.nextSibling.nextSibling.text)
                            if tons:
                                tons = float(tons)
                            break
                    for elem in soupArticle.select('th'):
                        if '진수년월일' in elem.text:
                            try:
                                modelYear = elem.nextSibling.nextSibling.text.split('년')[0].strip()
                                modelYear = int(modelYear)
                            except:
                                modelYear = None
                            break
                    else:
                        modelYear = None
                    for elem in soupArticle.select('th'):
                        if '소재지역' in elem.text:
                            try:
                                salesLocation = elem.nextSibling.nextSibling.text.strip()
                            except:
                                salesLocation = ""
                            break
                    else:
                        salesLocation = ""
                except:
                    tons = 0
                    modelYear = None
                    salesLocation = ""
                data.append([imgsrc, title, price, boardType, uploaded_date, siteName, price_int, detailURL, regNumber, boardURL, tons, modelYear, salesLocation])


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
        crawling(params, headers)
        params = {
            's_board_cate': 'B',
        }
        crawling(params, headers)
    elif boardType == '낚시배':
        params = {
            's_board_cate': 'C',
        }
        crawling(params, headers)
    elif boardType == '레저선박':
        params = {
            's_board_cate': 'D',
        }
        crawling(params, headers)
    elif boardType == '기타선박':
        params = {
            's_board_cate': 'E',
        }
        crawling(params, headers)

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
                    'tons': item[10],
                    'modelYear': item[11],
                    'salesLocation': item[12],
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
                    'tons': item[10],
                    'modelYear': item[11],
                    'salesLocation': item[12],
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
                    'tons': item[10],
                    'modelYear': item[11],
                    'salesLocation': item[12],
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

