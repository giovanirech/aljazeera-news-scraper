import re
from pathlib import Path
import logging
from datetime import datetime
import urllib.request
from shutil import make_archive
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
from libs.CustomSelenium import CustomSelenium
from RPA.Robocorp.WorkItems import WorkItems
from libs.Article import Article


class NewsScraper(CustomSelenium):
    """
    A web scraper for extracting articles from news websites using Selenium.

    This class extends the CustomSelenium class, leveraging its web automation functionalities.
    It scrapes articles from Al Jazeera and other pre-defined sources based on a search term.

    Attributes
    ----------
    articles : list
        List of collected articles during the scraping session.

    Methods
    -------
    set_output_dir(output_dir: Path):
        Sets the directory where the scraped articles and other files will be saved.
    prepare_environment(browser: str = "Chrome"):
        Prepares the environment, initializes the WebDriver, and creates output folders.
    access_home_page(url: str = "https://www.aljazeera.com/", screenshot: str = None):
        Accesses the homepage of the news website and optionally takes a screenshot.
    accept_cookies():
        Accepts the cookie consent on the homepage.
    collect_articles(search_term: str, number_of_months: int = 1):
        Collects articles based on the search term and date range.
    perform_search(search_term: str):
        Executes a search for articles on the website using the provided search term.
    sort_by(by: str):
        Sorts the search results by the specified option (date or relevance).
    close_ad_in_search_results():
        Closes any advertisements that appear in the search results.
    load_more_articles():
        Loads additional articles by clicking the "Load more" button.
    explicitly_wait_for_show_more_button(timeout: int = 10):
        Waits for the "Show more" button to appear before proceeding.
    create_report():
        Generates a Excel report of the collected articles.
    archive_collection():
        Archives the output directory into a ZIP file.
    _get_web_element(locator: str, locator_type: str = "xpath", parent: WebElement = None, multiple: bool = False) -> WebElement | list[WebElement]:
        Retrieves a web element or a list of web elements based on the locator type and strategy.
    """
    def __init__(self):
        """
        Initializes the NewsScraper class and sets up logging for the scraping process.
        """
        super().__init__()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.articles = []


    def set_output_dir(self, output_dir: Path):
        """
        Sets the output directory for storing scraped articles and other files.

        Parameters
        ----------
        output_dir : Path
            Directory path where the output files will be saved.
        """
        self.output_dir = Path(output_dir)


    def prepare_environment(self, browser: str = "Chrome"):
        """
        Prepares the environment for scraping by setting up the WebDriver and creating necessary folders.

        Parameters
        ----------
        browser : str, optional
            The browser to use for scraping, default is 'Chrome'.
        """        
        if not self.output_dir.exists():
            self.output_dir.mkdir()
            self.logger.info(f"Created output folder: {self.output_dir}")

        self.set_webdriver(browser)
        self.set_page_size(1920, 1080)  # Set the window size to 1920x1080


    def access_home_page(self, url: str = "https://www.aljazeera.com/", screenshot: str = None):
        """
        Accesses the homepage of the given URL (default is Al Jazeera) and accepts cookies.

        Parameters
        ----------
        url : str, optional
            URL of the homepage, default is 'https://www.aljazeera.com/'.
        screenshot : str, optional
            Filename to save a screenshot of the homepage, default is None.

        Raises
        ------
        NotImplementedError
            If a website other than Al Jazeera is accessed.
        """
        if url != "https://www.aljazeera.com/":
            raise NotImplementedError("Only https://www.aljazeera.com/ is implemented for now.")

        self.open_url(url, screenshot)
        self.accept_cookies()


    def accept_cookies(self):
        """
        Accepts the cookie consent pop-up on the homepage of the news website.
        """
        accept_button = self._get_web_element("//button[@id='onetrust-accept-btn-handler']")
        if accept_button:
            accept_button.click()
            self.logger.info("Accepted cookies.")


    def collect_articles(self, search_term: str, number_of_months: int = 1):
        """
        Collects articles based on the provided search term and limits the results to the specified date range.
        Articles are stored in the 'articles' list attribute.

        Parameters
        ----------
        search_term : str
            The keyword to search for in the articles.
        number_of_months : int, optional
            The number of months back to limit the search results, default is 1 month.
        """

        limit_date = datetime.today() - pd.tseries.offsets.DateOffset(months=number_of_months)
        self.logger.info(f"Limit date: {limit_date}")

        self.perform_search(search_term)

        self.sort_by("date")

        # Sometimes an ad pops up. Let's close it
        self.close_ad_in_search_results()

        search_results_xpath = ".//div[@class='search-result__list']"
        search_results_element = self._get_web_element(search_results_xpath)

        list_of_articles_elements = self._get_web_element("//article", multiple=True, parent=search_results_element)

        while list_of_articles_elements:
            article_element = list_of_articles_elements.pop(0)
            # Make sure element is visible
            self.driver.execute_script("arguments[0].scrollIntoView();", article_element)
            current_article = Article(article_element, search_term, self.output_dir)

            if current_article.date and current_article.date < limit_date:
                break

            self.articles.append(current_article)
            current_article.download_image()
            self.logger.info(f"Collected article: {current_article.title}")

            if len(list_of_articles_elements) == 0:
                # We reached the end of the page. Let's load more articles
                success = self.load_more_articles()
                if not success:
                    # No more articles to load
                    break

                # Get the new list of articles
                list_of_articles_elements = self._get_web_element(
                    ".//article", multiple=True, parent=search_results_element
                )
                # Ignore articles that were already collected
                list_of_articles_elements = list_of_articles_elements[len(self.articles) :]


    def perform_search(self, search_term: str):
        """
        Performs a search for articles on the website using the specified search term.

        Parameters
        ----------
        search_term : str
            The term to search for in articles.
        """
        # Click on the search icon
        search_icon = self._get_web_element("//div[@class='site-header__search-trigger']")
        search_icon.click()

        # enter the search term
        search_bar = self._get_web_element(".//input[@class='search-bar__input']")
        search_bar.send_keys(search_term)

        # Simulate enter key press
        logging.info(f"Searching for '{search_term}'.")
        search_bar.send_keys(Keys.RETURN)


    def sort_by(self, by: str):
        """
        Sorts the search results by the specified criterion.

        Parameters
        ----------
        by : str
            Sorting criterion, either 'date' or 'relevance'.

        Raises
        ------
        ValueError
            If the sorting criterion is not 'date' or 'relevance'.
        """

        if by not in ["date", "relevance"]:
            raise ValueError(f"Sorting by '{by}' not supported.")

        sort_by_option = self._get_web_element(".//option[@value='date']")
        sort_by_option.click()

        logging.info(f"Sorted results by '{by}'.")


    def close_ad_in_search_results(self):
        """
        Closes a advertisement pop-up that appear in the bottom of search results
        and sometimes prevents interaction with the "Show more" button.
        """
        try:
            add_close_button = self._get_web_element("//button[@class='ads__close-button']")
            add_close_button.click()
            self.logger.info("Closed add in search results.")
        except (NoSuchElementException, ElementClickInterceptedException):
            self.logger.info("No add to close in search results.")


    def load_more_articles(self) -> bool:
        """
        Clicks the "Show more" button to load additional articles.

        Returns
        -------
        bool
            True if more articles were loaded, False otherwise.
        """
        load_more_button = self._get_web_element("//button[@class='show-more-button grid-full-width']")

        if not load_more_button:
            self.logger.info("No 'Show more' button found.")
            return False

        # Scroll to the button
        self.driver.execute_script("arguments[0].scrollIntoView();", load_more_button)

        # Click the button
        load_more_button.click()
        self.logger.info("Clicked 'Show more' button.")

        # Explicitly wait for the page to load
        self.explicitly_wait_for_show_more_button()

        return True

    def explicitly_wait_for_show_more_button(self, timeout: int = 10):
        """
        Waits for the "Show more" button to appear, indicating that more articles can be loaded.

        Parameters
        ----------
        timeout : int, optional
            Time to wait before timing out, default is 10 seconds.
        """
        try:
            _ = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, "//button[@class='show-more-button grid-full-width']"))
            )
        except TimeoutException:
            self.logger.error("Show more button not found.")


    def create_report(self):
        """
        Creates a CSV report of the collected articles.

        The report includes article titles, publication dates, descriptions, image file names,
        the number of matches for the search term, and whether money figure is present.
        """
        report_file = self.output_dir / "report.xlsx"
        report_df = pd.DataFrame([vars(article) for article in self.articles])
        report_df = report_df[["title", "date", "description", "image_file_name", "matches_count", "has_money"]]
        report_df.to_csv(self.output_dir / "report.csv", index=False)
        report_df.to_excel(report_file, index=False)


    def archive_collection(self):
        """
        Archives the output directory containing the collected articles and images into a ZIP file.
        """
        zip_path = make_archive(self.output_dir, "zip", self.output_dir)
        self.logger.info(f"Collection archived to {zip_path}.zip")

    def _get_web_element(
        self,
        locator: str,
        locator_type: str = "xpath",
        parent: WebElement = None,
        multiple: bool = False,
        explicit_wait: int = 0,
        wait_condition: str = None,
    ) -> WebElement | list[WebElement]:
        """
        Retrieves a web element or a list of web elements using the specified locator strategy and criteria.

        Parameters
        ----------
        locator : str
            The locator string used to identify the web element(s).
        locator_type : str, optional
            The type of locator to use ('xpath', 'id', 'name', 'class', or 'css'), default is 'xpath'.
        parent : WebElement, optional
            The parent element to search within, default is None.
        multiple : bool, optional
            If True, retrieves a list of elements, default is False.
        explicit_wait : int, optional
            The maximum time to wait for the element(s), default is 0 (no wait).
        wait_condition : str, optional
            The condition to wait for ('presence' or 'clickable'), default is 'presence'.

        Returns
        -------
        WebElement or list of WebElement or None
            The found web element(s), or None if not found.

        Raises
        ------
        ValueError
            If an unsupported locator type or wait condition is provided.
        """
        parent = parent or self.driver

        locator_types = {
            "id": By.ID,
            "xpath": By.XPATH,
            "name": By.NAME,
            "class": By.CLASS_NAME,
            "css": By.CSS_SELECTOR,
        }

        by = locator_types.get(locator_type)
        if by is None:
            raise ValueError(f"Unsupported locator type '{locator_type}'.")

        valid_wait_conditions = [None, "presence", "clickable"]
        if wait_condition not in valid_wait_conditions:
            raise ValueError(
                f"Invalid wait_condition '{wait_condition}'. Valid values are 'presence', 'clickable', or None."
            )

        wait_condition = wait_condition or "presence"

        try:
            if explicit_wait > 0:
                condition = self._get_wait_condition(by, locator, wait_condition, multiple)
                return WebDriverWait(parent, explicit_wait).until(condition)
            else:
                if multiple:
                    elements = parent.find_elements(by, locator)
                    if not elements:
                        raise NoSuchElementException
                    return elements
                else:
                    return parent.find_element(by, locator)
        except (TimeoutException, NoSuchElementException):
            self.logger.error(f"Element with locator '{locator}' not found.")
            return None



    def _get_wait_condition(self, by: By, locator: str, wait_condition: str, multiple: bool) -> EC:
        """
        Determines the appropriate expected condition for WebDriverWait based on the wait condition and multiplicity.

        Parameters
        ----------
        by : selenium.webdriver.common.by.By
            The strategy to locate elements, such as By.ID, By.XPATH.
        locator : str
            The locator string used to identify the web element(s).
        wait_condition : str
            The condition to wait for ('presence' or 'clickable').
        multiple : bool
            If True, expects multiple elements to be located.

        Returns
        -------
        selenium.webdriver.support.expected_conditions._Condition
            The expected condition to be used with WebDriverWait.

        Raises
        ------
        ValueError
            If an unsupported wait condition is provided.
        """
        if wait_condition == "clickable":
            return EC.element_to_be_clickable((by, locator))
        elif wait_condition == "presence" and multiple:
            return EC.presence_of_all_elements_located((by, locator))
        else:
            return EC.presence_of_element_located((by, locator))