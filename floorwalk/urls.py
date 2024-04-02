from django.urls import path
from . import views
from django.conf.urls import handler404
from floorwalk import views

urlpatterns = [
    path("", views.index, name="index"),
    path('search/', views.search_results, name='search_results'),
    path('store_info/', views.store_info, name='store_info'),
    path('get_data/<str:industry>/', views.get_data, name='get_data'),
    path('top/', views.top, name='top'),
    path('sitemap.xml', views.sitemap, name='sitemap'),
]
handler404 = views.custom_page_not_found_view
