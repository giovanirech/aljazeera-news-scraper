from libs.CustomSelenium import CustomSelenium
from RPA.Robocorp.WorkItems import WorkItems
import logging
from pathlib import Path

class NewsScraper(CustomSelenium):
    def __init__(self):
        # Initialize logging
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def prepare_crawler(self, browser="Chrome"):

        # Prepare the output folder
        if not self.output_dir.exists():
            self.output_dir.mkdir()
            self.logger.info(f"Created dump folder: {self.dump_folder}")

        # Set the webdriver
        self.driver.set_webdriver(browser)

        # Set the page size
        self.driver.set_page_size(1920, 1080)



    def get_input_parameters(self):
        work_items = WorkItems()
        work_items.get_input_work_item()
        variables = work_items.get_work_item_variables()
        
        self.search_phrase = variables.get("search_phrase", "")
        self.news_category = variables.get("news_category", "")
        self.number_of_months = int(variables.get("number_of_months", "1"))
        
        self.logger.info(f"Input parameters received: search_phrase='{self.search_phrase}', news_category='{self.news_category}', number_of_months={self.number_of_months}")

    def initialize_browser(self):
        self.browser = CustomSelenium()
        self.browser.prepare_crawler(browser="Chrome")
        self.logger.info("Browser initialized.")

    def close_browser(self):
        if self.browser:
            self.browser.driver_quit()
            self.logger.info("Browser closed.")


    def close_driver(self):
        if self.driver:
            self.driver.quit()
            self.logger.info("Driver closed")
        else:
            self.logger.warning("Driver not set")
