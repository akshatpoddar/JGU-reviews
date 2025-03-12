from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
import django
import sys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

# Set up Django environment
import sys
import os
import django

# Set up Django environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Adjust path
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jgu_course_reviewer.settings")
django.setup()

# Import Django models
from reviewer.models import Course, Instructor, Term, CourseInstructorTerm

BASE_URL = "https://www.jgu.edu.in/academics"

# Define seasons and years
seasons = ['spring', 'fall']
years = [2019, 2020, 2021, 2022, 2023, 2024]
terms = [f"{s}{y}" for s in seasons for y in years]

def extract_courses(soup):
    """Extract course and instructor information from the soup object."""
    # Find the table containing the course information
    table = soup.find('table')
    
    if not table or not hasattr(table, 'tbody'):
        print("No table found or table has no tbody")
        return []

    # Initialize a list to store course details
    courses = []

    # Iterate over each row in the table body
    for row in table.tbody.find_all('tr'):
        # Find all columns in the row
        cols = row.find_all('td')
        if len(cols) >= 2:
            course_name = cols[0].get_text(strip=True)
            instructor = cols[1].get_text(strip=True)
            
            # Skip empty values and headers
            if not course_name or not instructor or course_name == 'Course Title' or instructor == 'Instructor':
                continue
                
            courses.append((course_name, instructor))

    return courses

def goto_next_page(driver):
    """Navigate to the next page if available."""
    try:
        # Wait for the next button to be clickable
        li_next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/scriptasync/div[2]/div/div/div[3]/div[2]/div/ul/li[9]"))
        )
        
        # Check if the button is disabled (no more pages)
        if "disabled" in li_next_button.get_attribute("class"):
            return False
            
        # Find and click the link inside the button
        link_next_button = li_next_button.find_element(By.TAG_NAME, "a")
        link_next_button.click()
        time.sleep(2)  # Allow time for the next page to load
        return True
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
        print(f"Error navigating to next page: {e}")
        return False

def scrape_courses_from_term(term):
    """Scrape all courses for a specific term."""
    course_types = ['core', 'elective']
    course_url = {'core': 'corecourse', 'elective': 'elective'}
    all_courses = []

    for course_type in course_types:

        url = f"{BASE_URL}/{term}/{course_url[course_type]}.php"
        print(f"Scraping {course_type} courses for {term}...")
        
        try:
            options = Options()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--headless")  # Run in headless mode (important for servers)
            options.add_argument("--user-data-dir=/tmp/selenium_user_data")
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Get initial page content
            page_count = 1
            soup = BeautifulSoup(driver.page_source, 'html5lib')
            print(f"Processing page {page_count} for {term}")
            extracted_courses = extract_courses(soup)

            for course_name, instructor_name in extracted_courses:
                all_courses.append((course_name, instructor_name, course_type))
            
            # Navigate through pagination
            while goto_next_page(driver):
                page_count += 1
                print(f"Processing page {page_count} for {term}")
                soup = BeautifulSoup(driver.page_source, 'html5lib')
                extracted_courses = extract_courses(soup)

                for course_name, instructor_name in extracted_courses:
                    all_courses.append((course_name, instructor_name, course_type))

            print(f"Scraped {len(all_courses)} {course_type} courses from {term}")

        except Exception as e:
            print(f"Error scraping {term}: {e}")
            try:
                driver.quit()
            except:
                pass
            return [], term
        
    print(f"Scraped {len(all_courses)} courses from {term}")
    driver.quit()
    return all_courses, term

def save_to_database(courses_data, term):
    """Save scraped data to Django database."""
    # Use database transaction for better performance and consistency
    from django.db import transaction
    
    # Convert season to proper case for the model
    for (i,c) in enumerate(term):
        if c.isDigit():
            break
    season = term[:i]
    year = term[i:]
    season_proper = season.capitalize()
    
    # Counter for statistics
    courses_created = 0
    instructors_created = 0
    relationships_created = 0
    
    try:
        with transaction.atomic():
            # Get or create the Term
            term, created = Term.objects.get_or_create(
                term_season=season_proper,
                term_year=int(year)
            )
            if created:
                print(f"Created new term: {term}")
            
            # Process each course-instructor pair
            for course_name, instructor_name, course_type in courses_data:
                # Create or get Course
                course, course_created = Course.objects.get_or_create(
                    course_name=course_name,
                    defaults={'course_type': course_type}  # Set course type when creating
                )

                # If course exists but doesn't have a type, update it
                if not course.course_type:
                    course.course_type = course_type
                    course.save()
                
                if course_created:
                    courses_created += 1
                    
                # Create or get Instructor
                instructor, instructor_created = Instructor.objects.get_or_create(instructor_name=instructor_name)
                if instructor_created:
                    instructors_created += 1
                
                # Create the relationship if it doesn't exist
                cit, cit_created = CourseInstructorTerm.objects.get_or_create(
                    course=course,
                    instructor=instructor,
                    term=term
                )
                if cit_created:
                    relationships_created += 1
    
        print(f"Statistics for {season} {year}:")
        print(f"- Courses created: {courses_created}")
        print(f"- Instructors created: {instructors_created}")
        print(f"- Course-Instructor-Term relationships created: {relationships_created}")
        print(f"- Total course-instructor pairs processed: {len(courses_data)}\n")
        
        return courses_created, instructors_created, relationships_created
        
    except Exception as e:
        print(f"Error saving data for {season} {year}: {e}")
        return 0, 0, 0


def main():
    """Main function to scrape all terms and save data."""
    print("Starting JGU course scraper...")
    
    total_courses = 0
    total_instructors = 0
    total_terms = 0
    total_relationships = 0
    
    # Initial counts for comparison
    initial_course_count = Course.objects.count()
    initial_instructor_count = Instructor.objects.count()
    initial_term_count = Term.objects.count()
    initial_cit_count = CourseInstructorTerm.objects.count()
    
    # Process each term
    for term in terms:
        courses, term = scrape_courses_from_term(term)
        if courses:
            save_to_database(courses, term)
    
    # Final counts for comparison
    final_course_count = Course.objects.count()
    final_instructor_count = Instructor.objects.count()
    final_term_count = Term.objects.count()
    final_cit_count = CourseInstructorTerm.objects.count()
    
    # Calculate totals
    total_courses = final_course_count - initial_course_count
    total_instructors = final_instructor_count - initial_instructor_count
    total_terms = final_term_count - initial_term_count
    total_relationships = final_cit_count - initial_cit_count
    
    print("\nScraping and database population complete!")
    print("Summary:")
    print(f"- Added {total_courses} new courses")
    print(f"- Added {total_instructors} new instructors")
    print(f"- Added {total_terms} new terms")
    print(f"- Created {total_relationships} new course-instructor-term relationships")

if __name__ == "__main__":
    main()