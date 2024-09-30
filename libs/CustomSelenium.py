
import logging
from selenium import webdriver
from pathlib import Path
from RPA.core.webdriver import start


class CustomSelenium:
    """
    Custom Selenium wrapper class for controlling browsers and interacting with web elements.
    """
    def __init__(self):
        """
        Initializes the CustomSelenium class, setting up logging, the default output directory, 
        and browser user agent.
        """
        self.driver = None
        self.logger = logging.getLogger(__name__)
        self.clogger = logging.getLogger(str(self))
        self.output_dir = Path(__file__).parent
        self.implicit_wait = 10
        self.user_agent = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        )


    def set_implicit_wait(self, seconds: int):
        """
        Sets the implicit wait time for the web driver.

        Parameters
        ----------
        seconds : int
            Time in seconds to wait for elements.
        """
        self.implicit_wait = seconds
        self.logger.info(f"Implicit wait set to {seconds} seconds.")
        if self.driver:
            self.driver.implicitly_wait(seconds)
            self.logger.info(f"Implicit wait of browser updated to {seconds} seconds.")


    def _set_chrome_options(self) -> webdriver.ChromeOptions:
        """
        Sets Chrome options such as headless mode, user agent, etc.

        Returns
        -------
        webdriver.ChromeOptions
            Configured Chrome options object.
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--headless') # No UI
        options.add_argument("--no-sandbox")  # Bypass OS security model
        options.add_argument("--disable-extensions")  # Disable extensions
        options.add_argument("--disable-gpu")  # applicable to windows os only
        options.add_argument("--disable-web-security")  # Disable web security
        options.add_argument("--start-maximized")  # Start maximized
        options.add_argument("--remote-debugging-port=9222")  # Debugging port
        options.add_argument(f"--user-agent={self.user_agent}")  # Set user agent
        return options


    def set_webdriver(self, browser: str = "Chrome"):
        """
        Initializes the web driver based on the chosen browser.

        Parameters
        ----------
        browser : str, optional
            Name of the browser, default is 'Chrome'.
        
        Raises
        ------
        NotImplementedError
            If the browser is not supported.
        """
        if browser.casefold() == "chrome":
            options = self._set_chrome_options()
            browser = "Chrome"
        else:
            raise NotImplementedError(f"{browser} browser not implemented yet. Please use Chrome.")

        self.driver = start(browser, options=options)
        self.logger.info(f"Browser set to '{browser}' and initialized.")

        # Let's give 15 seconds for the pages to load so we can avoid spurious errors such as
        # NoSuchElementException, TimeoutException, ElementNotVisibleException, ElementNotSelectableException,
        # ElementClickInterceptedException, ElementNotInteractableException
        self.set_implicit_wait(self.implicit_wait)


    def set_page_size(self, width: int, height: int):
        """
        Sets the page size to the specified width and height.

        Parameters
        ----------
        width : int
            Width of the window.
        height : int
            Height of the window.
        """
        # Extract the current window size from the driver
        current_window_size = self.driver.get_window_size()

        # Extract the client window size from the html tag
        html = self.driver.find_element(By.TAG_NAME, "html")
        inner_width = int(html.get_attribute("clientWidth"))
        inner_height = int(html.get_attribute("clientHeight"))

        # "Internal width you want to set+Set "outer frame width" to window size
        target_width = width + (current_window_size["width"] - inner_width)
        target_height = height + (current_window_size["height"] - inner_height)
        self.driver.set_window_rect(width=target_width, height=target_height)


    def open_url(self, url: str, screenshot: str = None):
        """
        Opens a given URL and optionally takes a screenshot.

        Parameters
        ----------
        url : str
            URL to open in the browser.
        screenshot : str, optional
            File name to save the screenshot, by default None.
        """
        self.driver.get(url)
        if screenshot:
            self.driver.get_screenshot_as_file(self.output_dir / screenshot)


    def driver_quit(self):
        """
        Closes the web driver and quits the browser session.
        """
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed.")


    def full_page_screenshot(self, url:str):
        """
        Takes a full-page screenshot by adjusting the browser size to fit the entire page.

        Parameters
        ----------
        url : str
            URL to open and take the full-page screenshot of.
        """
        self.driver.get(url)
        page_width = self.driver.execute_script("return document.body.scrollWidth")
        page_height = self.driver.execute_script("return document.body.scrollHeight")
        self.driver.set_window_size(page_width, page_height)
        self.driver.save_screenshot("screenshot.png")
        self.driver.quit()


    def __str__(self):
        """
        Returns the name of the class as a string.

        Returns
        -------
        str
            Class name.
        """
        return self.__class__.__name__
