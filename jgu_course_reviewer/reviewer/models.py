from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass 

    def __str__(self):
        return self.username


class Course(models.Model):
    course_name = models.CharField(max_length=255, unique=True)
    avg_rating = models.FloatField(default=0.0)
    
    CORE = "core"
    ELEC = "elective"
    COURSE_CHOICES = (
        (CORE, "Core"),
        (ELEC, "Elective")
    )

    course_type = models.CharField(max_length=8, choices=COURSE_CHOICES)
    def __str__(self):
        return self.course_name

    def update_average_rating(self):
        """Update the course's average rating based on all associated reviews."""
        from django.db.models import Avg
        average = Review.objects.filter(course_instructor_term__course=self).aggregate(
            Avg('rating')
        )['rating__avg']
        self.avg_rating = round(average, 2) if average else 0.0
        self.save()

class Instructor(models.Model):
    instructor_name = models.CharField(max_length=255, unique=True)
    avg_rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.instructor_name
    
    def update_average_rating(self):
        """Update the instructor's average rating based on all associated reviews."""
        from django.db.models import Avg
        average = Review.objects.filter(course_instructor_term__instructor=self).aggregate(
            Avg('rating')
        )['rating__avg']
        self.avg_rating = round(average, 2) if average else 0.0
        self.save()


class Term(models.Model):
    SPRING = 'Spring'
    FALL = 'Fall'

    SEASON_CHOICES = [
        (SPRING, 'Spring'),
        (FALL, 'Fall'),
    ]
    
    term_season = models.CharField(
        max_length=6,
        choices=SEASON_CHOICES,  # Restrict input to "Spring" or "Fall"
        default=SPRING,  # Optional: Default value
    )
    term_year = models.PositiveIntegerField(default=2024)  
    term_name = models.CharField(max_length=20, unique=True, editable=False)

    class Meta:
        unique_together = ('term_season', 'term_year')  # Prevent duplicate terms like "Spring 2024"

    def __str__(self):
        return f"{self.term_season} {self.term_year}"

    def save(self, *args, **kwargs):
        # Generate the name field dynamically
        self.term_name = f"{self.term_season}{self.term_year}"
        super().save(*args, **kwargs)  # Call the parent class's save method


class CourseInstructorTerm(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE)
    term = models.ForeignKey(Term, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('course', 'instructor', 'term')  # Enforce uniqueness

    def __str__(self):
        return f"{self.course} - {self.instructor} - {self.term}"


class Review(models.Model):
    course_instructor_term = models.ForeignKey(CourseInstructorTerm, on_delete=models.CASCADE)
    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    description = models.TextField(blank=True, null=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # Rating between 1 and 5
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('author', 'course_instructor_term'),)
        
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.course_instructor_term.instructor.update_average_rating()
        self.course_instructor_term.course.update_average_rating()

    def delete(self, *args, **kwargs):
        instructor = self.course_instructor_term.instructor
        course = self.course_instructor_term.course
        super().delete(*args, **kwargs)
        instructor.update_average_rating()
        course.update_average_rating()    
    
    def __str__(self):
        return f"Review for {self.course_instructor_term} by {self.author.username}"
