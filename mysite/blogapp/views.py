from django.contrib.syndication.views import Feed
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy

from blogapp.models import Article


class ArticleListView(ListView):
    queryset = (
        Article.objects
        .filter(pub_date__isnull=False)
        .order_by("-pub_date")
    )


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'blogapp/article_list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related('author', 'category')
            .prefetch_related('tags')
            .defer('content')
            .order_by('-pub_date')
        )


class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("blogapp:articles")

    def items(self):
        return (
            Article.objects
            .filter(pub_date__isnull=False)
            .order_by("-pub_date")[:5]
    )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]
