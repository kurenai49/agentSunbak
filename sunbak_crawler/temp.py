import re

def extract_price_and_convert_to_int(price_str):
    # 정규식을 사용하여 금액 정보를 추출합니다.
    extracted_price = re.findall(r'((?:\d*[일이삼사오육칠팔구]?[억만천백십]+)+)', price_str)

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
        current_value = 1
        current_man_unit = 0

        for part in price_parts:
            if part.isdigit():
                current_value = int(part)
            elif part == '천':
                current_multiplier = 1000
                current_man_unit += current_value * current_multiplier
            elif part == '백':
                current_multiplier = 100
                current_man_unit += current_value * current_multiplier
            elif part == '십':
                current_multiplier = 10
                current_man_unit += current_value * current_multiplier
            elif part == '원':
                break
            elif part == '억':
                price_int += current_man_unit * 100000000 if current_man_unit != 0 else current_value * 100000000
                current_man_unit = 0
            elif part == '만':
                price_int += current_man_unit * 10000 if current_man_unit != 0 else current_value * 10000
                current_man_unit = 0
        if current_man_unit != 0:
            price_int += current_man_unit

        return price_int
    except:
        return price_str

examples = [
    "9천육백만", "3억팔천구백", "7천삼백만", "육천만", "8천구백",
    "1억이천삼백", "4천오백만", "삼억육천칠백", "9천일백만", "팔천이백",
    "2억삼천사백", "일억오천육백", "7천팔백만", "구천백만", "오천삼백",
    "6억칠천팔백", "이천일백만", "4억오천육백", "삼천사백만", "일천오백",
    "3억팔천일백", "오억육천칠백", "5천구백만", "사천이백만", "6천칠백",
    "2억일천삼백", "삼억사천오백", "팔천육백만", "7천오백만", "9천사백",
    "1억오천구백", "6억이천삼백", "오천일백만", "삼천만", "칠천팔백",
    "3억칠천오백", "4억구천이백", "이천사백만", "일억천만", "오천칠백",
    "5억오천일백", "삼억이천사백", "팔천만", "칠억일백만", "육천오백",
    "7억삼천이백", "오억칠천오백", "사천칠백만", "8억오백만", "이천삼백",
    "1억칠천사백", "4억오천구백", "삼천팔백만", "이억삼천만", "일천칠백",
    "9억오천칠백", "팔억구천이백", "5천오백만", "사억천만", "칠천삼백",
    "3억이천오백", "이억팔천일백", "일천이백만", "팔억오천만", "9천일백",
    "7억사천삼백", "오억일천이백", "사천오백만", "육억칠천만", "이천사"]

for example in examples:
    price_int = extract_price_and_convert_to_int(example)
    print(f"{example} -> {price_int:,}")
