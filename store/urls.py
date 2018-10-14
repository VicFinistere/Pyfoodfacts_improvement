# store/urls.py
from django.urls import path
from django.views.generic import TemplateView
from store import views

app_name = 'store'

handler404 = 'views.page_not_found_view'
handler500 = 'views.server_error_view'


urlpatterns = [

    path('404/', views.page_not_found_view),
    path('500/', views.server_error_view),

    path('search/', views.search, name='search'),

    path('signup/', views.SignUp.as_view(),
         name='signup'),

    path('profile/', views.profile_page,
         name='profile_page'),

    path('update_profile/', views.update_profile,
         name='update_profile'),

    path('search/product_code=<int:product_code>', views.search,
         name='search'),

    path('search/product_code=<int:product_code>&nova=<slug:nova>', views.search,
         name='search'),

    path('product_page/<int:product_code>', views.product_page,
         name='product_page'),

    path('products/', views.products_page,
         name='products'),

    path('save/prod=<int:product_code>&sub=<int:substitute_code>', views.save_products_pair,
         name='save'),

    path('delete/product_id=<int:product_id>&substitute_id=<int:substitute_id>', views.delete_products_pair,
         name='delete'),

    path('legal/', TemplateView.as_view(template_name='store/legal.html'),
         name='legal'),

]

# https://wsvincent.com/django-user-authentication-tutorial-login-and-logout/
# path('', TemplateView.as_view(template_name='home.html'), name='home'),
