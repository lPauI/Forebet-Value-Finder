from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from time import sleep
from colorama import init, Fore
from pandas import DataFrame, ExcelWriter
from win32com.client import Dispatch
from os import getcwd
from datetime import date, datetime, timedelta

init(autoreset=True)


class Predictor:
    def __init__(self, url, predict_type, finished):
        self.TYPE = predict_type
        self.FINISHED = finished

        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--window-size=1920x1080')

        # Setting user-agent to avoid bot detection
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                             "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0")

        driver = webdriver.Chrome(options=options)

        driver.get(url)

        # Accepting cookies consent
        driver.find_element(By.CLASS_NAME, "fc-button-label").click()  # Consent

        try:
            load_more = driver.find_element(
                By.XPATH,
                value="//div[@id='mrows']/span[text()='More']"
            )

        except NoSuchElementException:
            pass

        else:
            driver.execute_script("arguments[0].scrollIntoView(true);", load_more)
            driver.execute_script("arguments[0].click();", load_more)

            sleep(1)

        self.soup = BeautifulSoup(driver.page_source, "html.parser")

        self.predictions = {}

    def scraper(self):
        index = 0

        # Find all divs containing match information
        first_divs = self.soup.find_all("div", class_="rcnt tr_0")
        second_divs = self.soup.find_all("div", class_="rcnt tr_1")

        # Combine divs from both classes
        all_divs = first_divs[:-2] + second_divs

        for div in all_divs:
            home_team = div.find("span", class_="homeTeam")
            away_team = div.find("span", class_="awayTeam")

            odds = div.find("span", class_="lscrsp")

            odd = odds.text

            dates_span = div.find("time", itemprop="startDate")

            dates = dates_span.find("span", class_="date_bah").text

            score = div.find("b", class_="l_scr")

            # Store match information in predictions dictionary
            self.predictions[index] = {
                "HOME": home_team.text,
                "AWAY": away_team.text,
                "Date": dates,
                "Odd": float(odds.text) if odd != " - " else "-",
                "Score": score.text if score else "-"
            }

            fprc_divs = div.find("div", class_="fprc")

            percentages = fprc_divs.find_all("span")

            # Store prediction percentages based on type
            if self.TYPE == "1x2":
                home = int(percentages[0].text)
                tie = int(percentages[1].text)
                away = int(percentages[2].text)

                self.predictions[index].update({
                    "1": home,
                    "X": tie,
                    "2": away
                })

            elif self.TYPE == "goals":
                under = int(percentages[0].text)
                over = int(percentages[1].text)

                self.predictions[index].update({
                    "U": under,
                    "O": over
                })

            index += 1

    def final_predictions(self):
        matches = []

        for prediction in self.predictions:
            current_match = self.predictions[prediction]

            minimum_percentage = 0
            maximum_percentage = 0

            tip = ""

            # Determine the tip and value based on prediction type
            if self.TYPE == "1x2":
                minimum_percentage = 65
                maximum_percentage = max(current_match["1"], current_match["X"], current_match["2"])

                if maximum_percentage == current_match["1"]:
                    tip = "HOME"

                elif maximum_percentage == current_match["X"]:
                    tip = "TIE"

                else:
                    tip = "AWAY"

            elif self.TYPE == "goals":
                minimum_percentage = 85
                maximum_percentage = max(current_match["U"], current_match["O"])

                if maximum_percentage == current_match["U"]:
                    tip = "UNDER"

                else:
                    tip = "OVER"

            if 100 > maximum_percentage >= minimum_percentage:
                real_odds = 100 / maximum_percentage
                bookies_odds = current_match["Odd"]

                if bookies_odds == "-":
                    value = "-"

                else:
                    value = (bookies_odds / real_odds - 1) * 100

                if (value == "-") or (value != "-" and value > 0):
                    current_match.update({
                        "Tip": tip,
                        "Value": str(round(value, 2)) + "%" if value != "-" else "-"
                    })

                    try:
                        dt_timestamp = datetime.strptime(current_match["Date"], "%d/%m/%Y %H:%M").timestamp()

                    except ValueError:
                        dt_timestamp = datetime.strptime(current_match["Date"], "%d/%m/%Y").timestamp()

                    if not self.FINISHED:
                        if dt_timestamp > datetime.now().timestamp():
                            matches.append(current_match)

                    else:
                        if dt_timestamp < datetime.now().timestamp():
                            match_score = current_match["Score"].replace(" ", "").split("-")

                            if match_score[0] != "":
                                match_score[0] = int(match_score[0])
                                match_score[1] = int(match_score[1])

                                results = []

                                if match_score[0] > match_score[1]:
                                    results.append("HOME")

                                elif match_score[0] == match_score[1]:
                                    results.append("TIE")

                                else:
                                    results.append("AWAY")

                                if match_score[0] + match_score[1] > 2:
                                    results.append("OVER")

                                else:
                                    results.append("UNDER")

                                if tip in results:
                                    prediction_result = True

                                else:
                                    prediction_result = False

                                current_match.update({
                                    "Prediction Result": prediction_result
                                })

                                matches.append(current_match)

        return matches


def predict(url, predict_type, finished):
    print(f"{Fore.BLUE}>> {Fore.WHITE}Initializing {predict_type} (finished={finished}) predictor..")
    predict_class = Predictor(url, predict_type, finished)

    print(f"{Fore.BLUE}>> {Fore.WHITE}Scraping..")

    # Scrape the data
    predict_class.scraper()

    print(f"{Fore.BLUE}>> {Fore.WHITE}Giving final predictions..")
    # Generate final predictions
    return predict_class.final_predictions()


def append_to_excel(fpath, dff, sheet_name):
    # Convert DataFrame to Excel
    with ExcelWriter(fpath, mode="a") as f:
        dff.to_excel(f, sheet_name=sheet_name)


# Predict upcoming matches
ft_predict = predict(
    url="https://www.forebet.com/en/football-tips-and-predictions-for-today/by-league",
    predict_type="1x2",
    finished=False
)

print("\n")

# Predict goals for upcoming matches
goals_predict = predict(
    url="https://www.forebet.com/en/football-tips-and-predictions-for-today/predictions-under-over-goals/by-league",
    predict_type="goals",
    finished=False
)

print("\n")

# Predict finished matches from yesterday
ft_finished_predict = predict(
    url=f"https://www.forebet.com/en/football-predictions/predictions-1x2/{date.today() - timedelta(1)}/by-league",
    predict_type="1x2",
    finished=True
)

print("\n")

# Predict goals for finished matches from yesterday
goals_finished_predict = predict(
    url=f"https://www.forebet.com/en/football-predictions/under-over-25-goals/{date.today() - timedelta(1)}/by-league",
    predict_type="goals",
    finished=True
)

print("\n")

print(f"{Fore.LIGHTRED_EX}>> {Fore.WHITE}Writing results to excel..")

FILE_NAME = f"predictions-{date.today()}.xlsx"

# Write upcoming predictions to Excel
df = DataFrame(data=ft_predict + goals_predict)

df.to_excel(FILE_NAME, sheet_name="Upcoming Today")

# Append finished predictions to Excel
df = DataFrame(data=ft_finished_predict + goals_finished_predict)

append_to_excel(FILE_NAME, df, sheet_name="Finished Yesterday")

print(f"{Fore.LIGHTRED_EX}>> {Fore.WHITE}AutoFit columns width..")

# AutoFit columns in Excel
excel = Dispatch("Excel.Application")

workbook = excel.Workbooks.Open(getcwd() + "\\" + FILE_NAME)

for sheet in workbook.Sheets:
    sheet.Activate()

    sheet.Columns.AutoFit()

workbook.Save()
workbook.Close()

excel.Quit()

print(f"{Fore.YELLOW}>> {Fore.WHITE}All done. Closing program..")
