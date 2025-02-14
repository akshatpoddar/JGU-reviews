from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Course, Instructor, Term, CourseInstructorTerm, Review
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "username",]

admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_name')  # Display fields in the list view
    search_fields = ('course_name',)     # Add a search bar

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('id', 'instructor_name')
    search_fields = ('instructor_name',)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('id', 'term_name')
    search_fields = ('term_name',)

@admin.register(CourseInstructorTerm)
class CourseInstructorTermAdmin(admin.ModelAdmin):
    list_display = ('course', 'instructor', 'term')
    list_filter = ('course', 'instructor', 'term') 

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('course_instructor_term', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'course_instructor_term__term')
    search_fields = (
        'author__username',  # Search by author username                        
        'course_instructor_term__course__course_name',      # Search by course name
        'course_instructor_term__instructor__instructor_name',  # Search by instructor name
        'course_instructor_term__term__term_name'  # Search by term name
    )
