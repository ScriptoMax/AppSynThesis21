from django.urls import path

from . import views

urlpatterns = [
    path('login/', views.manage_user_login, name='manage_user_login'),
    path('logout/', views.manage_user_logout, name='manage_user_logout'),
    path('init/', views.init_session, name='init_session'),
    path('cancel/', views.cancel_session, name='cancel_session'),
    path('<int:user_id>/reports', views.get_user_reports, name='get_user_reports'),
    path('report/<int:report_id>', views.get_report_details, name='get_report_details'),
    path('options/baseCategories', views.get_base_category_options, name='get_base_category_options'),
    path('options/subcategories', views.get_subcategory_options, name='get_subcategory_options'),
    path('options/serviceCategories', views.get_service_categories, name='get_service_categories')
]