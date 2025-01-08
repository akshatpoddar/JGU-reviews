import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

BASE_URL = "https://www.jgu.edu.in/academics"


seasons = ['spring', 'fall']
years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
terms = [f"{s}{y}" for s in seasons for y in years]

# print(terms)



def extract_courses(soup):
    # Find the table containing the course information
    table = soup.find('table')

    # Initialize a list to store course details
    courses = []

    # Iterate over each row in the table body
    for row in table.tbody.find_all('tr'):
        # Find all columns in the row
        cols = row.find_all('td')
        if len(cols) >= 2:
            course_name = cols[0].get_text(strip=True)
            instructor = cols[1].get_text(strip=True)
            courses.append((course_name, instructor))

    # Display the extracted courses and instructors
    # for course, instructor in courses:
    #     print(f"Course: {course}, Instructor: {instructor}")
    return courses


def goto_next_page(soup):
    try:
        li_next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/scriptasync/div[2]/div/div/div[3]/div[2]/div/ul/li[9]"))
        )
        if "disabled" in li_next_button.get_attribute("class"):
            return False
        link_next_button = li_next_button.find_element(By.TAG_NAME, "a")
        link_next_button.click()
        time.sleep(2)  # Allow time for the next page to load
        return True
    except NoSuchElementException:
        return False


def scrape_courses(soup, driver):
    all_courses = []

    while goto_next_page(driver):
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        if soup:
            courses = extract_courses(soup)
            all_courses.extend(courses)
        else:
            break

    return all_courses


def initSelenium(url):
    driver = webdriver.Chrome()
    driver.get(url)
    return driver

def initSoup(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html5lib')
    return soup

URL = f"{BASE_URL}/spring2018/elective.php"
soup = initSoup(URL)
driver = initSelenium(URL)

print(scrape_courses(soup, driver))