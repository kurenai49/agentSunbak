from sunbak_crawler.models import sunbak_Crawl_DataModel


def save_data_to_model(table_data):
    for row in table_data:
        # 각 행의 열 데이터를 사용하여 모델 객체를 생성합니다.
        model_instance, created = sunbak_Crawl_DataModel.objects.get_or_create(column1=row[0], column2=row[1], column3=row[2], column4=row[3])

        # 새로 생성된 객체인 경우 저장합니다. #중복은 걸러냅니다
        if created:
            model_instance.save()
