from django.urls import path

from .views import terms_list, terms_create, terms_delete, terms_update, download_template, terms_import

app_name = 'terms'

urlpatterns = [
    path('terms/', terms_list, name='terms_list'),
    path('terms/add/', terms_create, name='terms_create'),
    path('terms/<int:pk>/change/', terms_update, name='terms_update'),
    path('terms/<int:pk>/delete/', terms_delete, name='terms_delete'),

    path('terms/download_template/', download_template, name='download_template'),
    path('terms/import/', terms_import, name='terms_import'),
]