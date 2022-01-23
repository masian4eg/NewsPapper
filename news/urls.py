from django.urls import path
from .views import NewsList, NewsDetail, FilterPostView, PostCreateView, PostDeleteView, PostUpdateView

urlpatterns = [
    path('', NewsList.as_view()),
    path('<int:pk>', NewsDetail.as_view(), name='new'),
    path('search/', FilterPostView.as_view()),
    path('create/', PostCreateView.as_view(), name='new_create'),  # Ссылка на создание новости
    path('create/<int:pk>', PostUpdateView.as_view(), name='new_update'),
    path('delete/<int:pk>', PostDeleteView.as_view(), name='new_delete'),
]
