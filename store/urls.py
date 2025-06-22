
from django.urls import path
from . import views


urlpatterns = [
    path('', views.store, name="store"),
    path('category/<slug:category_slug>/', views.store, name='product_by_category'),
    # path('category/<slug:category_slug>/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('set-currency/<str:currency>/', views.set_currency, name='set_currency'),
    path('price_search/',views.price_search, name='price_search'),
    path('price_search/<slug:category_slug>/', views.price_search, name='search_by_category'),

    path('subcategory/<slug:subcategory_slug>/', views.store_by_subcategory, name='store_by_subcategory'),
    path('subcategory/<slug:subcategory_slug>/<slug:product_slug>', views.product_detail, name='product_detail'),

    

    

] 
