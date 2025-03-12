from django.core.management.base import BaseCommand
from scraper import save_to_database, scrape_courses_from_term

class Command(BaseCommand):
    help = "Scrapes course data and updates the database"

    def add_arguments(self, parser):
        parser.add_argument("term", type=str, help="The term to scrape (e.g., 'spring2024')")


    def handle(self, *args, **options):
        term = options["term"]

        # Call scraper for the given term
        courses, season, year = scrape_courses_from_term(term)
        if courses:
            save_to_database(courses, season, year)
            self.stdout.write(self.style.SUCCESS(f"Scraping complete for {term}. Data saved to database."))
        else:
            self.stdout.write(self.style.WARNING(f"No courses found for {term}."))

        self.stdout.write(self.style.SUCCESS("Scraper ran successfully!"))