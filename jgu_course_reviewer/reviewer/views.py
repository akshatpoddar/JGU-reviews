from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from .models import Review, CourseInstructorTerm, Course, Instructor, Term
from .forms import ReviewForm, ReviewFilterForm

# Create your views here.
def home_view(request):
    reviews = Review.objects.select_related('course_instructor_term__course', 'course_instructor_term__instructor', 'course_instructor_term__term')
    form = ReviewFilterForm(request.GET or None)
    return render(request, 'home.html', {'reviews': reviews, 'form': form})

def instructor_info(request, id):
    instructor = get_object_or_404(Instructor, id=id)
    reviews = Review.objects.filter(course_instructor_term__instructor=instructor)
    return render(request, 'instructor_info.html', {'instructor': instructor, 'reviews': reviews})

def course_info(request, id):
    course = get_object_or_404(Course, id=id)
    reviews = Review.objects.filter(course_instructor_term__course=course)
    return render(request, 'course_info.html', {'course': course, 'reviews': reviews})


def create_review_view(request):
    if request.method == "POST":
        course_instructor_term_id = request.POST['course_instructor_term']
        name = request.POST['reviewer_name']
        descripton = request.POST['description']
        rating = int(request.POST['rating'])
        # Validate rating
        if not (1 <= rating <= 5):
            raise ValidationError("Rating must be between 1 and 5.")

        # Save the review
        course_instructor_term = CourseInstructorTerm.objects.get(id=course_instructor_term_id)
        Review.objects.create(
            course_instructor_term=course_instructor_term,
            reviewer_name=name,
            description=descripton,
            rating=rating,
        )
    
    review_form = ReviewForm()
    return render(request, 'create_review.html', {'form': review_form})

def review_list(request):
    # Initialize the form with GET data
    form = ReviewFilterForm(request.GET or None)
    
    # Start with all reviews
    reviews = Review.objects.all()
    
    # Apply filters if the form is valid
    if form.is_valid():
        if form.cleaned_data['term']:
            reviews = reviews.filter(course_instructor_term__term=form.cleaned_data['term'])
        if form.cleaned_data['course']:
            reviews = reviews.filter(course_instructor_term__course=form.cleaned_data['course'])
        if form.cleaned_data['instructor']:
            reviews = reviews.filter(course_instructor_term__instructor=form.cleaned_data['instructor'])

    return render(request, 'review_list.html', {'reviews': reviews, 'form': form})

def submit_review(request):
    if request.method == "POST":
        course_instructor_term_id = request.POST['course_instructor_term']
        name = request.POST['name']
        descripton = request.POST['description']
        rating = int(request.POST['rating'])
        print("POST")
        # Validate rating
        if not (1 <= rating <= 5):
            raise ValidationError("Rating must be between 1 and 5.")

        # Save the review
        course_instructor_term = CourseInstructorTerm.objects.get(id=course_instructor_term_id)
        Review.objects.create(
            course_instructor_term=course_instructor_term,
            name=name,
            description=descripton,
            rating=rating,
        )

def courses_view(request):
    courses = Course.objects.all()
    return render(request, 'courses.html',{'courses': courses})

def instructors_view(request):
    instructors = Instructor.objects.all()
    return render(request, 'instructors.html',{'instructors': instructors})