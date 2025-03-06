from django.db import IntegrityError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Review, Course, Instructor
from .forms import ReviewForm, ReviewFilterForm, CustomUserCreationForm

# Home view displaying reviews with filtering
def home_view(request):
    reviews = Review.objects.select_related(
        'course_instructor_term__course', 
        'course_instructor_term__instructor', 
        'course_instructor_term__term'
    )
    form = ReviewFilterForm(request.GET or None)
    return render(request, 'home.html', {'reviews': reviews, 'form': form})

# View to list all courses
def courses_view(request):
    sort = request.GET.get('sort', 'name')
    courses = Course.objects.all()
    
    if sort == 'name':
        courses = courses.order_by('course_name')
    elif sort == 'rating_high':
        courses = courses.order_by('-avg_rating', 'course_name')
    elif sort == 'rating_low':
        courses = courses.order_by('avg_rating', 'course_name')
    
    return render(request, 'courses.html', {'courses': courses, 'current_sort': sort})

# View to list all instructors
def instructors_view(request):
    sort = request.GET.get('sort', 'name')
    instructors = Instructor.objects.all()
    
    if sort == 'name':
        instructors = instructors.order_by('instructor_name')
    elif sort == 'rating_high':
        instructors = instructors.order_by('-avg_rating', 'instructor_name')
    elif sort == 'rating_low':
        instructors = instructors.order_by('avg_rating', 'instructor_name')
    
    return render(request, 'instructors.html', {'instructors': instructors, 'current_sort': sort})

# Detail view for a specific instructor and its reviews
def instructor_info(request, id):
    instructor = get_object_or_404(Instructor, id=id)
    reviews = Review.objects.filter(course_instructor_term__instructor=instructor)
    return render(request, 'instructor_info.html', {'instructor': instructor, 'reviews': reviews})

# Detail view for a specific course and its reviews
def course_info(request, id):
    course = get_object_or_404(Course, id=id)
    reviews = Review.objects.filter(course_instructor_term__course=course)
    return render(request, 'course_info.html', {'course': course, 'reviews': reviews})

# Register view using the custom user creation form
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in immediately after registration
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Login view using Django's built-in AuthenticationForm
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Logout view
def logout_confirm_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')
    return render(request, 'logout_confirm.html')

# Create review view; only accessible for logged in users

def create_review_view(request):
    """
    Only a logged-in user can create a review. This view uses the ReviewForm,
    sets the review’s author to the logged-in user, and then saves the review.
    """
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to post a review.")
        return redirect('login')  # Make sure 'login' is defined in your urls
    if request.method == "POST":
        form = ReviewForm(request.POST, user=request.user)
        if form.is_valid():
            review = form.save(commit=False)
            review.author = request.user
            try:
                review.save()
                return redirect('home')
            except IntegrityError:
                form.add_error(None, "You have already posted a review for this course, term, and instructor.")
    else:
        form = ReviewForm(user=request.user)
    return render(request, 'create_review.html', {'form': form})

# View to list reviews with filtering applied via GET parameters
def review_list(request):
    # Initialize the filter form with GET data
    form = ReviewFilterForm(request.GET or None)
    
    # Start with all reviews
    reviews = Review.objects.all()
    
    # Apply filters if the form is valid
    if form.is_valid():
        if form.cleaned_data.get('term'):
            reviews = reviews.filter(course_instructor_term__term=form.cleaned_data['term'])
        if form.cleaned_data.get('course'):
            reviews = reviews.filter(course_instructor_term__course=form.cleaned_data['course'])
        if form.cleaned_data.get('instructor'):
            reviews = reviews.filter(course_instructor_term__instructor=form.cleaned_data['instructor'])

    return render(request, 'review_list.html', {'reviews': reviews, 'form': form})