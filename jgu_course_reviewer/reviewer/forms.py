from django import forms
from .models import Review, Term, Course, Instructor, CourseInstructorTerm
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django_select2.forms import ModelSelect2Widget


class CourseInstructorTermWidget(ModelSelect2Widget):
    model = CourseInstructorTerm
    search_fields = [
        'course__course_name__icontains',
        'instructor__instructor_name__icontains',
        'term__term_name__icontains',
    ]

class CourseWidget(ModelSelect2Widget):
    model = Course
    search_fields = [
        'course_name__icontains',
    ]
    def build_attrs(self, base_attrs, extra_attrs=None):
        """Override attributes to set minimum input length to 0."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-minimum-input-length'] = 0  # Allow search with 0 characters typed
        return attrs
    
class TermWidget(ModelSelect2Widget):
    model = Term
    search_fields = [
        'term_name__icontains',
    ]

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Override attributes to set minimum input length to 0."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-minimum-input-length'] = 0  # Allow search with 0 characters typed
        return attrs
    
class InstructorWidget(ModelSelect2Widget):
    model = Instructor
    search_fields = [
        'instructor_name__icontains',
    ]
    
    def build_attrs(self, base_attrs, extra_attrs=None):
        """Override attributes to set minimum input length to 0."""
        attrs = super().build_attrs(base_attrs, extra_attrs)
        attrs['data-minimum-input-length'] = 0  # Allow search with 0 characters typed
        return attrs

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("username", "email")

class ReviewForm(forms.ModelForm):

    course = forms.ModelChoiceField(
        queryset=Course.objects.all(),
        widget=CourseWidget,
        required=True,
    )
    term = forms.ModelChoiceField(
        queryset=Term.objects.all(),
        widget=TermWidget,
        required=True,
    )
    instructor = forms.ModelChoiceField(
        queryset=Instructor.objects.all(),
        widget=InstructorWidget,
        required=True,
    )


    class Meta:
        model = Review
        fields = ['course', 'term', 'instructor', 'description', 'rating']

    def __init__(self, *args, **kwargs):
        # Pop the user out of the kwargs (or set to None if not provided)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not (1 <= rating <= 5):
            raise forms.ValidationError("Rating must be between 1 and 5.")
        return rating
    
    def clean(self):
        cleaned_data = super().clean()
        course = cleaned_data.get('course')
        term = cleaned_data.get('term')
        instructor = cleaned_data.get('instructor')
        
        if course and term and instructor:
            try:
                # Look up the corresponding CourseInstructorTerm
                cit = CourseInstructorTerm.objects.get(course=course, term=term, instructor=instructor)
                cleaned_data['course_instructor_term'] = cit
            except CourseInstructorTerm.DoesNotExist:
                raise forms.ValidationError(
                    "The selected combination of course, term, and instructor does not exist. "
                    "Please verify your selections."
                )
            
        # Check if a review already exists for this user and combination.

        if Review.objects.filter(author=self.user, course_instructor_term=cit).exists():
            raise forms.ValidationError("You have already posted a review for this course, term, and instructor.")

        return cleaned_data

    def save(self, commit=True):
        # Create a Review instance and assign the found course_instructor_term.
        review = super().save(commit=False)
        review.course_instructor_term = self.cleaned_data.get('course_instructor_term')
        if commit:
            review.save()
        return review

    

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