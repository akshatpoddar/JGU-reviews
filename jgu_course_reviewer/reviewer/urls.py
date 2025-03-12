from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('courses/', views.courses_view, name='courses'),
    path('instructors/', views.instructors_view, name='instructors'),
    path('instructor/<int:id>/', views.instructor_info, name='instructor_info'),
    path('course/<int:id>/', views.course_info, name='course_info'),
    path('review/create/', views.create_review_view, name='create_review'),
    path('reviews/', views.review_list, name='review_list'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_confirm_view, name='logout'),
    path('run-scraper/', views.run_scraper_view, name='run_scraper'),
    path('user/me', views.profile_view_me, name='profile'),
    path('user/<int:id>', views.profile_view, name='profile'),
]