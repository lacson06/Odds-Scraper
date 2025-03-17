import scrapy
import json
import mysql.connector
import re

class SportsPlusSpider(scrapy.Spider):
    name = "sp"

    def __init__(self):
        """✅ Initialize MySQL connection and fetch event IDs."""
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Changepa$$06",
                database="betting_db"
            )
            self.cursor = self.conn.cursor()

            # ✅ Fetch event IDs from events table
            self.cursor.execute("SELECT eventID FROM events WHERE bookie = 'Sports Plus';")
            self.event_ids = [row[0] for row in self.cursor.fetchall()]  # Convert to list

        except mysql.connector.Error as e:
            self.log(f"❌ MySQL Connection Error: {e}")

    def clean_game_name(self, game_name):
        game_name = re.sub(r'\W+', '_', game_name.lower()).strip("_")  # Replace non-alphanumeric with _
        table_name = f"SP_{game_name}"  # Add MSW_ prefix
        return table_name[:64]  # ✅ Limit to 64 characters (MySQL table name limit)

    def create_table(self, table_name):
        """✅ Create table dynamically if it does not exist."""
        self.cursor.execute(f"""
               CREATE TABLE IF NOT EXISTS {table_name} (
                   id INT AUTO_INCREMENT PRIMARY KEY,
                   bet_name VARCHAR(255),
                   team1 VARCHAR(100),
                   sp_odds1 DECIMAL(10,2), 
                   team2 VARCHAR(100),
                   sp_odds2 DECIMAL(10,2), 
                   team3 VARCHAR(100) NULL,
                   sp_odds3 DECIMAL(10,2) NULL 
               );
           """)
        self.conn.commit()

    def start_requests(self):
        cookies = {
            "default_culture": "en-us",
            "brand": "Sp",
            "culture": "en-us",
            "_ga": "GA1.1.506116744.1738161703",
            "_pid": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNZW1iZXJSb2xlIjoiMSIsIk1lbWJlcklkIjoiMzRkMDdiNjIxZWFmNDBlNThkNjkzYmY4MWZmNmZiZTMiLCJDdWx0dXJlIjoiZW4tcGgiLCJDb3VudHJ5Q29kZSI6IlBIIiwiZXhwIjoxNzQxNTgyMjIxLCJhdWQiOiJsb2NhbGhvc3QifQ.7xbi07FKlmCRQ9KZmwOYysP5lNtXB8qylrTfvCgNHq4; _ga_LTSKQQZXD8=GS1.1.1741499273.14.1.1741499423.0.0.0"
        }

        for event_id in self.event_ids:
            url = f"https://www.sportsplus.ph/sbk/api/v1/single/match/{event_id}?fl=false"
            yield scrapy.Request(url, callback=self.parse, cookies=cookies, meta={"event_id": event_id})


    def parse(self, response):
        """✅ Parse JSON response and insert into MySQL."""
        try:
            data = response.json()
            market_lines = data["d"].get("marketLines", [])
            selections = data["d"].get("selections", [])

            one_team = data["d"]["match"]["competitor1Name"]["long"]
            two_team = data["d"]["match"]["competitor2Name"]["long"]
            game_name = f"{one_team} vs {two_team}"
            table_name = self.clean_game_name(game_name)

            # ✅ Create table if not exists
            self.create_table(table_name)

            for market in market_lines:
                market_id = market["marketLineId"]
                market_name = market["marketLineName"]["long"]

                team_1, odds_1, handicap_1 = None, None, None
                team_2, odds_2, handicap_2 = None, None, None
                team_3, odds_3 = None, None  # ✅ Support for third odd

                for selection in selections:
                    if selection["marketLineId"] == market_id:
                        option_id = selection["optionId"]
                        team_name = selection["selectionName"]["long"]
                        odds = selection.get("odds")
                        handicap = selection.get("handicap")

                        if option_id == 1:
                            team_1, odds_1, handicap_1 = team_name, odds, handicap
                        elif option_id == 2:
                            team_2, odds_2, handicap_2 = team_name, odds, handicap
                        elif option_id == 3:  # ✅ Handle odd 3 if available
                            team_3, odds_3 = team_name, odds

                # ✅ Merge handicap with team names (only if available)
                final_team_1 = f"{team_1} {handicap_1}" if handicap_1 else team_1
                final_team_2 = f"{team_2} {handicap_2}" if handicap_2 else team_2

                # ✅ Ensure all required data is available before inserting
                if team_1 and team_2 and odds_1 and odds_2:
                    sql = f"""
                        INSERT INTO {table_name} (bet_name, team1, sp_odds1, team2, sp_odds2, team3, sp_odds3)
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """
                    values = (market_name, final_team_1, odds_1, final_team_2, odds_2, team_3, odds_3)
                    self.cursor.execute(sql, values)
                    self.conn.commit()

                else:
                    self.log(f"⚠️ Missing data for market {market_id} - Skipping...")

        except json.JSONDecodeError:
            self.log(f"❌ Failed to decode JSON for event {response.meta.get('event_id', 'Unknown')}.")

    def close(self, reason):
        """✅ Close MySQL connection when spider finishes."""
        self.cursor.close()
        self.conn.close()