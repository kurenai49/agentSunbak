from django.views.generic import ListView
from sunbak_crawler.models import sunbak_Crawl_DataModel
from django.db.models import Q
from datetime import datetime
# Create your views here.

class ArticleView(ListView):
    model = sunbak_Crawl_DataModel
    context_object_name = 'articles'
    template_name = 'articleapp/article_list.html'
    paginate_by = 21

    def get_queryset(self):
        boardType = self.kwargs['boardType']

        query = self.request.GET.get('query', '')
        # site_name = self.request.GET.get('site_name', '')  # 이름 변경
        order = self.request.GET.get('order', 'update_desc')  # 'desc' 또는 'asc'

        min_price = self.request.GET.get('min_price', 0)
        max_price = self.request.GET.get('max_price', None)
        min_tons = self.request.GET.get('min_tons', 0)  # Minimum tons filter
        max_tons = self.request.GET.get('max_tons', None)  # Maximum tons filter

        if min_price == '':
            min_price = 0
        if max_price == '':
            max_price = 100
        if min_tons == '':
            min_tons = 0
        if max_tons == '':
            max_tons = 1000


        filter_conditions = Q(boardType=boardType)

        if query:
            filter_conditions &= Q(title__icontains=query)

        # if site_name:
        #     filter_conditions &= Q(siteName=site_name)

        # Price filters
        if min_price is not None:
            filter_conditions &= Q(price_int__gte=int(min_price)*100000000)

        if max_price is not None:
            filter_conditions &= Q(price_int__lte=int(max_price)*100000000)

        # Tons filters
        if min_tons is not None:
            filter_conditions &= Q(tons__gte=min_tons)

        if max_tons is not None:
            filter_conditions &= Q(tons__lte=max_tons)

        # 지역 필터링 로직
        region = self.request.GET.get('region', '')

        filter_conditions = Q(boardType=boardType)

        # 지역 필터 추가
        if region:
            filter_conditions &= Q(salesLocation=region)

        min_modelYear = self.request.GET.get('min_modelYear', None)
        max_modelYear = self.request.GET.get('max_modelYear', None)

        if min_modelYear:
            filter_conditions &= Q(modelYear__gte=min_modelYear)

        if max_modelYear:
            filter_conditions &= Q(modelYear__lte=max_modelYear)

        articles = sunbak_Crawl_DataModel.objects.filter(filter_conditions)

        if order == 'update_desc':
            articles = articles.order_by('-updated_at')
        elif order == 'update_asc':
            articles = articles.order_by('updated_at')
        elif order == 'price_desc':
            articles = articles.order_by('-price_int')
        elif order == 'price_asc':
            articles = articles.order_by('price_int')

        return articles

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_names'] = sunbak_Crawl_DataModel.objects.values_list('siteName', flat=True).distinct()
        context['order'] = self.request.GET.get('order', '')
        context['selected_site_name'] = self.request.GET.get('site_name', '')
        context['selected_region'] = self.request.GET.get('region', '')  # 선택된 지역 추가
        context['regions'] = sunbak_Crawl_DataModel.objects.values_list('salesLocation', flat=True).distinct().exclude(salesLocation='')

        context['modelYears'] = range(1980, datetime.now().year + 1)
        context['selected_min_modelYear'] = self.request.GET.get('min_modelYear', '')
        context['selected_max_modelYear'] = self.request.GET.get('max_modelYear', '')


        # 쿼리 파라미터를 포함한 페이지네이션 링크를 생성하기 위해 현재의 쿼리 파라미터를 context에 추가
        context['query_params'] = self.request.GET.urlencode()

        return context
