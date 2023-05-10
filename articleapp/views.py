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


        filter_conditions = Q(boardType=boardType)

        if query:
            filter_conditions &= Q(title__icontains=query)

        if site_name:
            filter_conditions &= Q(siteName=site_name)

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
        context['order'] = self.request.GET.get('order', '')  # 이 줄을 추가하세요
        context['selected_site_name'] = self.request.GET.get('site_name', '')  # 이 줄을 수정하세요
        return context