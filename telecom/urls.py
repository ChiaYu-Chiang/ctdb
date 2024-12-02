from django.urls import path

from .views import (isp_create, isp_delete, isp_list, isp_review, isp_update,
                    ispgroup_create, ispgroup_delete, ispgroup_list,
                    ispgroup_update, prefixlistupdatetask_clone,
                    prefixlistupdatetask_create, prefixlistupdatetask_delete,
                    prefixlistupdatetask_list, prefixlistupdatetask_update,
                    prefixlistupdatetask_previewmailcontent, prefixlistupdatetask_sendtaskmail,
                    archive_list, archive_create, archive_update, archive_delete)

app_name = 'telecom'

urlpatterns = [
    path('isps/', isp_list, name='isp_list'),
    path('isps/<int:pk>/review/', isp_review, name='isp_review'),
    path('isps/add/', isp_create, name='isp_create'),
    path('isps/<int:pk>/change/', isp_update, name='isp_update'),
    path('isps/<int:pk>/delete/', isp_delete, name='isp_delete'),
    path('ispgroups/', ispgroup_list, name='ispgroup_list'),
    path('ispgroups/add/', ispgroup_create, name='ispgroup_create'),
    path('ispgroups/<int:pk>/change/', ispgroup_update, name='ispgroup_update'),
    path('ispgroups/<int:pk>/delete/', ispgroup_delete, name='ispgroup_delete'),
    path('prefixlistupdatetasks/', prefixlistupdatetask_list, name='prefixlistupdatetask_list'),
    path('prefixlistupdatetasks/add/', prefixlistupdatetask_create, name='prefixlistupdatetask_create'),
    path('prefixlistupdatetasks/<int:pk>/change/', prefixlistupdatetask_update, name='prefixlistupdatetask_update'),
    path('prefixlistupdatetasks/<int:pk>/delete/', prefixlistupdatetask_delete, name='prefixlistupdatetask_delete'),
    path('prefixlistupdatetasks/<int:pk>/clone/', prefixlistupdatetask_clone, name='prefixlistupdatetask_clone'),
    path('prefixlistupdatetasks/<int:pk>/previewmailcontent/', prefixlistupdatetask_previewmailcontent, name='prefixlistupdatetask_previewmailcontent'),
    path('prefixlistupdatetasks/<int:pk>/sendtaskmail/', prefixlistupdatetask_sendtaskmail, name='prefixlistupdatetask_sendtaskmail'),
    path('telecom_archives/', archive_list, name='archive_list'),
    path('telecom_archives/add/', archive_create, name='archive_create'),
    path('telecom_archives/<int:pk>/change/', archive_update, name='archive_update'),
    path('telecom_archives/<int:pk>/delete/', archive_delete, name='archive_delete'),
]
