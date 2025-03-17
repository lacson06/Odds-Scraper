import scrapy
import json
import mysql.connector
import re


class BettingSpider(scrapy.Spider):
    name = "msw"
    allowed_domains = ["sports.msw.ph"]

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
            self.cursor.execute("SELECT eventID FROM events")
            self.event_ids = [row[0] for row in self.cursor.fetchall()]
            self.start_urls = [
                f"https://sports.msw.ph/xapi/rest/events/{event_id}?bettable=true&marketStatus=OPEN&periodType=PRE_MATCH&includeMarkets=true&lightWeightResponse=true&includeLiveEvents=true&maxMarketPerEvent=1000&l=en"
                for event_id in self.event_ids
            ]
        except mysql.connector.Error as err:
            self.log(f"❌ MySQL Connection Error: {err}")
            self.conn, self.cursor, self.event_ids = None, None, []

    def clean_game_name(self, game_name):
        """Clean game name to make it valid for MySQL table name."""
        return f"MSW_{re.sub(r'\W+', '_', game_name.lower())[:64]}"

    def parse(self, response):
        """Parse event data and insert into MySQL."""
        if not self.conn or not self.cursor:
            return

        try:
            data = json.loads(response.text)
            game_name = data.get("description", "unknown_game")
            if not game_name:
                return

            table_name = self.clean_game_name(game_name)

            # Create table if it doesn't exist
            self.cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS `{table_name}` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    bet_name VARCHAR(255),
                    team1 VARCHAR(100),
                    msw_odds1 DECIMAL(10,2),
                    team2 VARCHAR(100),
                    msw_odds2 DECIMAL(10,2),
                    team3 VARCHAR(100) NULL,
                    msw_odds3 DECIMAL(10,2) NULL
                );
            """)
            self.conn.commit()

            for market in data.get("markets", []):
                bet_name = market.get("description", "Unknown Bet")
                # Loop through each market's periods to get the fullDescription
                full_description = market.get("period", {}).get("fullDescription", "No full description")
                outcomes = market.get("outcomes", [])

                teams = [o.get("description", "Unknown Team") for o in outcomes]
                odds = [o.get("consolidatedPrice", {}).get("currentPrice", {}).get("decimal", 0.00) for o in outcomes]

                if len(teams) >= 2:
                    insert_query = f"""
                        INSERT INTO `{table_name}` (bet_name, team1, msw_odds1, team2, msw_odds2, team3, msw_odds3) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """
                    self.cursor.execute(insert_query, (
                        f"{bet_name} - {full_description}",
                        teams[0], odds[0],
                        teams[1], odds[1],
                        teams[2] if len(teams) > 2 else None,
                        odds[2] if len(teams) > 2 else None
                    ))
                    self.conn.commit()

                    yield {
                        "game_name": game_name,
                        "bet_name": f"{bet_name} - {full_description}",
                        "team1": teams[0],
                        "msw_odds1": odds[0],
                        "team2": teams[1],
                        "msw_odds2": odds[1],
                        "team3": teams[2] if len(teams) > 2 else None,
                        "msw_odds3": odds[2] if len(teams) > 2 else None
                    }

        except json.JSONDecodeError:
            self.log("❌ JSON Decode Error: Invalid response format.")
        except Exception as e:
            self.log(f"❌ Unexpected Error: {e}")

    def closed(self, reason):
        """✅ Close MySQL connection when spider stops."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.log("✅ Database connection closed.")
