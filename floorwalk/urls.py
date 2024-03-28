from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path("", views.index, name="index"),
    path('search/', views.search_results, name='search_results'),
    path('store_info/', views.store_info, name='store_info'),
    path('get_data/<str:industry>/', views.get_data, name='get_data'),
    path('top/', views.top, name='top'),
    path('sitemap.xml', views.sitemap, name='sitemap'),
]
