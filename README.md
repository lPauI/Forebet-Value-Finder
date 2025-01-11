# Forebet Value Finder

This project is a Python script that scrapes football match predictions from the Forebet website and calculates the value of these predictions. It uses Selenium for web scraping, BeautifulSoup for parsing HTML, and Pandas for handling data. The predictions are saved to an Excel file.

## Features

- Scrapes football match predictions for today and yesterday.
- Supports two types of predictions: `1x2` and `goals`.
- Calculates the value of predictions based on odds and percentages.
- Saves predictions to an Excel file.
- Auto-fits columns in the Excel file for better readability.
- Reads yesterday's predictions and indicates if they won or lost.
- Provides predictions for today's matches.

## Requirements

- Python 3.x
- Google Chrome
- Selenium 4.16.0
- BeautifulSoup4 4.12.3
- Colorama 0.4.6
- Pandas 2.2.0

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/lPauI/Forebet-Value-Finder
    cd forebet-value-finder
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Download and install [Google Chrome](https://www.google.com/chrome/).

## Usage

Run the script:
```sh
python3 predictions.py
```

The script will scrape predictions from the Forebet website, calculate their value, and save them to an Excel file named predictions-YYYY-MM-DD.xlsx in the current working directory. It will also read yesterday's predictions and indicate if they won or lost.

## Excel File Details

The Excel file contains the following columns:  
- HOME: The home teams.
- AWAY: The away teams.
- Date: The dates and times of the matches.
- Odd: The odds for the matches.
- Score: The final scores of the matches.
- 1: The percentage chances of home wins (for 1x2 predictions).
- X: The percentage chances of ties (for 1x2 predictions).
- 2: The percentage chances of away wins (for 1x2 predictions).
- U: The percentage chances of under 2.5 goals (for goals predictions).
- O: The percentage chances of over 2.5 goals (for goals predictions).
- Tip: The predicted outcomes (e.g., HOME, TIE, AWAY, UNDER, OVER).
- Value: The calculated values of the predictions.
- Prediction Result: Indicates if the predictions were correct (True/False).

## License
This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
