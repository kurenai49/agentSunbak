from django.views.generic import ListView, TemplateView
from sunbak_crawler.models import sunbak_Crawl_DataModel
from django.db.models import Q
from datetime import datetime
# Create your views here.


class RegionSelectView(TemplateView):
    template_name = 'articleapp/region_select.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regions'] = sunbak_Crawl_DataModel.objects.values_list('salesLocation', flat=True).distinct().exclude(salesLocation='')
        return context

class ArticleView(ListView):
    model = sunbak_Crawl_DataModel
    context_object_name = 'articles'
    template_name = 'articleapp/article_list.html'
    paginate_by = 21

    def get_queryset(self):
        filter_conditions = Q()

        region = self.request.GET.get('region')
        boardType = self.request.GET.get('boardType',None)
        query = self.request.GET.get('query', '')
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

        if query:
            filter_conditions &= Q(title__icontains=query)
        if region:
            filter_conditions &= Q(salesLocation=region)
        if boardType:
            filter_conditions &= Q(boardType=boardType)

        # Price filters
        price_range = self.request.GET.get('price_range')
        if price_range == 'below_100':
            filter_conditions &= Q(price_int__lt=100000000)
        elif price_range == '100_to_300':
            filter_conditions &= Q(price_int__gte=100000000, price_int__lte=300000000)
        elif price_range == '300_to_1000':
            filter_conditions &= Q(price_int__gte=300000000, price_int__lte=1000000000)
        elif price_range == 'above_1000':
            filter_conditions &= Q(price_int__gte=1000000000)

        # Tons filters
        tons_range = self.request.GET.get('tons_range')
        if tons_range == 'below_3t':
            filter_conditions &= Q(tons__lt=3)
        elif tons_range == '3t_to_5t':
            filter_conditions &= Q(tons__gte=3, tons__lte=5)
        elif tons_range == '5t_to_8t':
            filter_conditions &= Q(tons__gte=5, tons__lte=8)
        elif tons_range == '8t_to_10t':
            filter_conditions &= Q(tons__gte=8, tons__lte=10)
        elif tons_range == '10t':
            filter_conditions &= Q(tons__gte=10)

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
        context['order'] = self.request.GET.get('order', '')
        context['selected_region'] = self.request.GET.get('region', '')  # 선택된 지역 추가
        context['selected_price'] = self.request.GET.get('price_range', '')
        context['selected_tons'] = self.request.GET.get('tons_range', '')

        # 쿼리 파라미터를 포함한 페이지네이션 링크를 생성하기 위해 현재의 쿼리 파라미터를 context에 추가
        context['query_params'] = self.request.GET.urlencode()

        return context
