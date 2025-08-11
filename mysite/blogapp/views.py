from typing import Sequence

from django.views.generic import ListView

from blogapp.models import Article


class BasedView(ListView):
    queryset = (
        Article.objects.
        select_related().
        prefetch_related()
    )
    titles: Sequence[Article] = Article.objects.defer("content")