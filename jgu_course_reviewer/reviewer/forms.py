from django import forms
from .models import Review, Term, Course, Instructor

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['reviewer_name', 'course_instructor_term', 'description', 'rating']

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not (1 <= rating <= 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating

class ReviewFilterForm(forms.Form):
    term = forms.ModelChoiceField(
        queryset=Term.objects.all(), 
        required=False, 
        empty_label="All Terms"
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.all(), 
        required=False, 
        empty_label="All Courses"
    )
    instructor = forms.ModelChoiceField(
        queryset=Instructor.objects.all(), 
        required=False, 
        empty_label="All Instructors"
    )