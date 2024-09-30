# 🤖 Al Jazeera News Scraper Automation

Welcome to the **Al Jazeera News Scraper Automation** project!

This project is an RPA (Robotic Process Automation) bot built using Python and Robocorp's automation tools. It automates the process of extracting news articles from the **Al Jazeera** website based on specific search terms and date ranges. The bot scrapes articles, generates a CSV report, and archives the collection for easy access.

## 📚 Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [How to Use](#how-to-use)
- [Project Structure](#project-structure)
- [Technologies Used](#technologies-used)
- [License](#license)
- [Contact](#contact)

---

## Project Overview

This RPA project is designed to automate the process of searching and collecting news articles from the Al Jazeera website. The bot:
- **Searches** for articles based on user-provided search terms.
- **Collects** articles within a specific date range.
- **Generates a Excel report** with article details (title, date, description, etc.).
- **Archives** all collected data, including images, in a ZIP file.

This project aims to demonstrate the implementation of web scraping and RPA as part of a technical portfolio. 📊

## Key Features

- 🌐 **Web Scraping**: Automatically scrapes news articles from the Al Jazeera website.
- 📝 **Customizable Searches**: Define search terms and date ranges for precise article collection.
- 📁 **Report Generation**: Outputs a detailed CSV report of collected articles.
- 🗄️ **Archiving**: Archives the scraped data (articles and images) into a ZIP file for easy sharing.
- 🖥️ **Headless Chrome Browser**: Uses Chrome in headless mode for faster and seamless scraping.
- ⌛ **Get elements with explicit waits**: Class method with the possibility of explicit waits, so you can wait for elements to fully load before interaction.

---

## Installation

To get started, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/giovanirech/aljazeera-news-scraper.git
   cd aljazeera-news-scraper
   ```

2. **Set Up the Environment**
   Ensure you have `rcc` (Robocorp CLI) installed, and run:
   ```bash
   rcc environment create --path .
   ```

   This command reads the `conda.yaml` file and sets up the environment with the required dependencies.

3. **Install Required Libraries**
   In addition to Robocorp dependencies, the bot uses `Selenium` for web automation:
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Use

The bot can be executed directly using Robocorp's `rcc` or by running the task script.

1. **Define Your Input**
   You can customize the bot's behavior by providing inputs through Robocorp work items. Each input can define:
   - `search_phrase`: The term you want to search for (e.g., "Technology").
   - `number_of_months`: The number of months back to limit the article search.

2. **Run the Bot**
   Run the task using `rcc`:
   ```bash
   rcc run
   ```

3. **Output**
   - The bot will generate a Excel report and save it in the `output` directory.
   - It will also archive the scraped data, including images, into a ZIP file.

---

## Project Structure

```
├── libs
│   ├── CustomSelenium.py      # Custom Selenium wrapper for browser control
│   ├── NewsScraper.py         # Scraper class to collect articles
│   ├── Article.py             # Article class to process articles
├── output                     # Directory where reports and archives are saved
├── tasks.py                   # Main task script
├── conda.yaml                 # Environment setup file for dependencies
├── robot.yaml                 # Robot configuration for Robocorp
├── README.md                  # Project documentation (this file)
```

- **`CustomSelenium.py`**: A custom wrapper around Selenium to handle browser automation.
- **`NewsScraper.py`**: Contains the logic for scraping articles, downloading images, and generating reports.
- **`Article.py`**: Class to represent a single news article collected by the scraper.
- **`tasks.py`**: The main entry point of the bot that orchestrates the scraping process.
- **`output/`**: The directory where the bot saves its CSV reports and archives.

---

## Technologies Used

- **Python**: The core language used to build the bot.
- **Robocorp**: Automation platform to run and orchestrate the bot.
- **Selenium**: Used for browser-based automation (Chrome).
- **Pandas**: For generating the Excel report.
- **Logging**: To capture runtime logs and errors.
- **Headless Chrome**: For faster, UI-less web scraping.

---

## License

This project is licensed under the Apache License - see the [LICENSE](LICENSE) file for details.

---

## Contact

Feel free to reach out for collaboration or if you have any questions! 🚀

- **Your Name**
- GitHub: [giovanirech](https://github.com/giovanirech)
- Email: gio.pi.rech@gmail.com

---

Thank you for checking out my page! 😊