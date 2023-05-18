from django.views.generic import ListView
from sunbak_crawler.models import sunbak_Crawl_DataModel
from django.db.models import Q
# Create your views here.

class ArticleView(ListView):
    model = sunbak_Crawl_DataModel
    context_object_name = 'articles'
    template_name = 'articleapp/article_list.html'
    paginate_by = 21

    def get_queryset(self):
        boardType = self.kwargs['boardType']

        query = self.request.GET.get('query', '')
        site_name = self.request.GET.get('site_name', '')  # 이름 변경
        order = self.request.GET.get('order', 'update_desc')  # 'desc' 또는 'asc'
        tons_weight = self.request.GET.get('tons_weight', '')
        price = self.request.GET.get('price', '')


        filter_conditions = Q(boardType=boardType)

        if query:
            filter_conditions &= Q(title__icontains=query)

        if site_name:
            filter_conditions &= Q(siteName=site_name)

        if tons_weight:
            weight_from, weight_to = map(int, tons_weight.split(';'))
            filter_conditions &= Q(tons__gte=weight_from, tons__lte=weight_to)

        if price:
            price_from, price_to = map(int, price.split(';'))
            filter_conditions &= Q(price_int__gte=price_from, price_int__lte=price_to)

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

        # 쿼리 파라미터를 포함한 페이지네이션 링크를 생성하기 위해 현재의 쿼리 파라미터를 context에 추가
        context['query_params'] = self.request.GET.urlencode()

        return context
