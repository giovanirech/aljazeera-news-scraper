from robocorp.tasks import task
from robocorp import workitems
from robocorp.tasks import get_output_dir
from libs.NewsScraper import NewsScraper


OUTPUT_DIR = get_output_dir()
TARGET_WEBSITE = "https://www.aljazeera.com/"

@task
def make_aljazeera_news_report():
    
    scraper = NewsScraper()

    try:
        scraper.set_output_dir(OUTPUT_DIR / "aljazeera_news")
        scraper.prepare_environment(browser="Chrome")
        scraper.access_home_page(TARGET_WEBSITE)

        for item in workitems.inputs:
            search_phrase = item.payload.get("search_phrase", "Science")
            number_of_months = item.payload.get("number_of_months", 1)
            scraper.collect_articles(search_phrase, number_of_months=number_of_months)

        scraper.create_report()
        scraper.archive_collection()

    finally:
        scraper.driver_quit()

