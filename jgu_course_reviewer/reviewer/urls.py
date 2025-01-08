from django.urls import path, include
from .views import home_view, courses_view, instructors_view, create_review_view, instructor_info, course_info

urlpatterns = [
    path('', home_view, name='home'),
    path('courses', courses_view, name='courses'),
    path('instructors', instructors_view, name='instructors'),
    path('create-review', create_review_view, name='create-reviews'),
    path('instructors/<int:id>', instructor_info, name='instructor-info'),
    path('courses/<int:id>', course_info, name='course-info'),
]