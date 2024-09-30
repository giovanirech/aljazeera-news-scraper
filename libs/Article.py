import logging
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException


class Article:
    """
    Class to represent an individual news article and its relevant details.

    Attributes
    ----------
    element : WebElement
        The article web element extracted from the page.
    search_term : str
        The search term used to find the article.
    output_dir : Path
        The directory where article-related files are saved.
    title : str
        The title of the article.
    date : datetime
        The publication (or last edited) date of the article.
    description : str
        A brief description or excerpt of the article.
    image_url : str
        The URL of the article's image.
    image_file_name : str
        The file name to save the article's image.
    matches_count : int
        The number of times the search term appears in the article's title or description.
    has_money : bool
        Whether the article title and description contains money figures.

    Methods
    -------
    download_image():
        Downloads the article's image to the specified output directory.
    """

    def __init__(self, element: WebElement, search_term: str, output_dir: Path):
        """
        Initializes an Article object and extracts relevant information from the web element.

        Parameters
        ----------
        element : WebElement
            The web element representing the article.
        search_term : str
            The search term used to find the article.
        output_dir : Path
            The directory where the article's image will be saved.
        """

        self.element = element
        self.search_term = search_term
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        self.title = self._parse_title()
        self.date = self._parse_date()
        self.description = self._parse_description()
        self.image_url, self.image_file_name = self._parse_image_url()
        self.matches_count = self._count_matches()
        self.has_money = self._find_money_mentions()


    def _parse_date(self) -> datetime | None:
        """
        Extracts and parses the article's publication date from the web element.

        Returns
        -------
        datetime | None
            The parsed date of the article, or None if the date could not be found.
        """
        date_xpath = ".//footer/div/div[@class='gc__date gc__date--published']/div/div/span[@aria-hidden='true']"
        date_element = self._get_web_element(date_xpath, parent=self.element)
        date_text = date_element.text if date_element else None
        if date_text:
            date_text = date_text.replace("Last update", "").strip().rstrip()
            date = datetime.strptime(date_text, "%d %b %Y")
            return date


    def _parse_title(self) -> str | None:
        """
        Extracts the title of the article from the web element.

        Returns
        -------
        str | None
            The title of the article, or None if not found.
        """
        title_xpath = ".//h3[@class='gc__title']/a[@class='u-clickable-card__link']"
        title_element = self._get_web_element(title_xpath, self.element)
        title = title_element.text if title_element else None
        return title
    

    def _parse_description(self) -> str | None:
        """
        Extracts the description or excerpt of the article.

        Returns
        -------
        str | None
            The description of the article, or None if not found.
        """
        description_xpath = ".//div[@class='gc__excerpt']/p"
        description_element = self._get_web_element(description_xpath, self.element)
        description = description_element.text if description_element else None
        return description


    def _parse_image_url(self) -> tuple[str | None, str | None]:
        """
        Extracts the image URL and file name from the article.

        Returns
        -------
        tuple[str | None, str | None]
            A tuple containing the image URL and the image file name, or (None, None) if the image is not found.
        """
        image_xpath = ".//img"
        image_element = self._get_web_element(image_xpath, self.element)
        if not image_element:
            return None, None

        image_url = image_element.get_attribute("src")
        image_name = image_url.split("?q=tbn:")[1].split("&")[0]
        image_file_name = f"{image_name}.jpeg"
        return image_url, image_file_name


    def _count_matches(self) -> int:
        """
        Counts the occurrences of the search term in the title and description of the article.

        Returns
        -------
        int
            The number of times the search term appears in the title and description.
        """
        counter = 0
        if self.title:
            counter += self.title.lower().count(self.search_term.lower())
        if self.description:
            counter += self.description.lower().count(self.search_term.lower())
        return counter
    

    def _find_money_mentions(self) -> bool:
        """
        Checks if the article mentions any reference to money in the title or description.

        The method detects monetary values formatted as:
        - $11.1 or $111,111.11
        - 11 dollars
        - 11 USD

        Returns
        -------
        bool
            True if the article mentions money, False otherwise.
        """
        patterns = [
            r"\$\s?[\d,]+\.\d+",  # Matches $11.1 or $111,111.11
            r"\b\d+\s*dollars\b",  # Matches 11 dollars
            r"\b\d+\s*USD\b",  # Matches 11 USD
        ]

        for pattern in patterns:
            if self.title and re.search(pattern, self.title, re.IGNORECASE):
                return True
            if self.description and re.search(pattern, self.description, re.IGNORECASE):
                return True

        return False

    def _get_web_element(
        self, locator: str, parent: WebElement, locator_type: str = "xpath", multiple: bool = False
    ) -> WebElement | list[WebElement]:
        """
        Retrieves a web element or elements within the article element.

        Parameters
        ----------
        locator : str
            The locator string to identify the web element.
        parent : WebElement
            The parent web element (i.e., the article container).
        locator_type : str, optional
            The type of locator to use ('xpath', 'id', 'class', 'name', or 'css'), default is 'xpath'.
        multiple : bool, optional
            If True, returns a list of elements, default is False.

        Returns
        -------
        WebElement | list[WebElement]
            The web element(s) found, or None if not found.

        Raises
        ------
        ValueError
            If an unsupported locator type is provided.
        """

        if multiple:
            method_to_use = parent.find_elements
        else:
            method_to_use = parent.find_element

        try:
            if locator_type == "id":
                return method_to_use(By.ID, locator)
            elif locator_type == "xpath":
                return method_to_use(By.XPATH, locator)
            elif locator_type == "name":
                return method_to_use(By.NAME, locator)
            elif locator_type == "class":
                return method_to_use(By.CLASS_NAME, locator)
            elif locator_type == "css":
                return method_to_use(By.CSS_SELECTOR, locator)
            else:
                raise ValueError(f"Locator type '{locator_type}' not supported.")
        except NoSuchElementException:
            self.logger.error(f"Element with locator '{locator}' not found.")
            return None


    def __str__(self) -> str:
        """
        String representation of the article, including its title and date.

        Returns
        -------
        str
            A formatted string containing the title and publication date.
        """
        return f"{self.title} - {self.date}"


    def download_image(self):
        """
        Downloads the article's image to the output directory.

        If the image URL is found, it will be saved to the output directory with the generated file name.
        """
        if not self.image_url:
            return

        image_file = self.output_dir / self.image_file_name
        self.logger.info(f"Downloading image: {self.image_url}")
        urllib.request.urlretrieve(self.image_url, image_file)
