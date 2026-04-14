from django.urls import path

from .views import news_create, news_delete, news_list, news_update, dep_news_list, news_sign_in, news_read_report, news_export_csv


app_name = 'news'

urlpatterns = [
    path('news/', news_list, name='news_list'),
    path('dep-news/', dep_news_list, name='dep_news_list'),
    path('news/add/', news_create, name='news_create'),
    path('news/<int:pk>/change/', news_update, name='news_update'),
    path('news/<int:pk>/delete/', news_delete, name='news_delete'),
    path('news/<int:pk>/sign-in/', news_sign_in, name='news_sign_in'),
    path('news/<int:pk>/report/', news_read_report, name='news_read_report'),
    path('news/<int:pk>/report/export/', news_export_csv, name='news_export_csv')
]
