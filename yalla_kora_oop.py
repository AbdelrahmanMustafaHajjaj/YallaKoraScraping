import requests
import sys
import lxml
import os
import csv
import argparse
from datetime import datetime
from dateutil import parser
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

class YallakoraExtractor:
    def __init__(self, date, output_file="yallakora_matches.csv"):
        self.date = date
        self.output_file = output_file
        self.match_details = []

    def get_match_info(self, match_card):
        """Extract match details from a single match card element."""
        try:
            champion_title = match_card.contents[1].find("h2").text.strip()
            all_matches = match_card.find_all("div", class_="liItem")

            for match in all_matches:
                team_a = match.find("div", class_="teamA").text.strip()
                team_b = match.find("div", class_="teamB").text.strip()
                match_time = match.find("span", class_="time").text.strip()
                score = match.find_all("span", class_="score")
                match_score = f"{score[0].text.strip()} - {score[1].text.strip()}"

                return {
                    "champion_Name": champion_title,
                    "TeamA": team_a,
                    "TeamB": team_b,
                    "matchStart": match_time,
                    "MatchScore": match_score
                }
        except (AttributeError, IndexError) as e:
            logging.error(f"Error extracting match details: {e}")
            return None

    def fetch_matches(self):
        """Fetch match data from Yallakora website for the specified date."""
        try:
            date = parser.parse(self.date).strftime("%m/%d/%Y")
        except ValueError:
            logging.error("Invalid date format. Please use the format MM/DD/YYYY.")
            sys.exit(1)

        url = f"https://www.yallakora.com/match-center/%D9%85%D8%B1%D9%83%D8%B2-%D8%A7%D9%84%D9%85%D8%A8%D8%A7%D8%B1%D9%8A%D8%A7%D8%AA?date={date}"
        logging.info(f"Fetching matches for date: {date}")

        try:
            page = requests.get(url)
            page.raise_for_status()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching page: {e}")
            sys.exit(1)

        soup = BeautifulSoup(page.content, "lxml")
        match_cards = soup.find_all("div", class_="matchCard")

        for card in match_cards:
            match_info = self.get_match_info(card)
            if match_info:
                self.match_details.append(match_info)

    def save_to_csv(self):
        """Save the match details to a CSV file."""
        output_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), self.output_file)
        logging.info(f"Writing match details to: {output_file}")

        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as file:
                dict_writer = csv.DictWriter(file, fieldnames=self.match_details[0].keys())
                dict_writer.writeheader()
                dict_writer.writerows(self.match_details)
        except IOError as e:
            logging.error(f"Error writing to file: {e}")
            sys.exit(1)

        logging.info("Done!")

def main():
    parser = argparse.ArgumentParser(description="Yallakora match data extractor")
    parser.add_argument("date", help="Date of matches in the format MM/DD/YYYY")
    parser.add_argument("--output-file", "-o", default="yallakora_matches.csv", help="Output CSV file name")
    args = parser.parse_args()

    extractor = YallakoraExtractor(args.date, args.output_file)
    extractor.fetch_matches()
    extractor.save_to_csv()

if __name__ == "__main__":
    main()