from django.contrib import admin
from .models import Course, Instructor, Term, CourseInstructorTerm, Review
# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'course_name')  # Display fields in the list view
    search_fields = ('name',)     # Add a search bar

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('id', 'instructor_name')
    search_fields = ('name',)

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('id', 'term_name')
    search_fields = ('name',)

@admin.register(CourseInstructorTerm)
class CourseInstructorTermAdmin(admin.ModelAdmin):
    list_display = ('course', 'instructor', 'term')
    list_filter = ('term',)  # Add a filter by term in the list view

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('course_instructor_term', 'reviewer_name', 'rating', 'created_at')
    list_filter = ('rating', 'course_instructor_term__term')
