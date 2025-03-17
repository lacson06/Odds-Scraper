import scrapy
import json
import mysql.connector


class EventsSpider(scrapy.Spider):
    name = "events"
    allowed_domains = ["www.sportsplus.ph"]
    start_urls = ["https://www.sportsplus.ph/sbk/api/v1/popular/matches?sportId=2"]

    # ✅ Define cookies for authentication
    cookies = {
        "default_culture": "en-us",
        "brand": "Sp",
        "culture": "en-us",
        "_ga": "GA1.1.506116744.1738161703",
        "_pid": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNZW1iZXJSb2xlIjoiMSIsIk1lbWJlcklkIjoiMzRkMDdiNjIxZWFmNDBlNThkNjkzYmY4MWZmNmZiZTMiLCJDdWx0dXJlIjoiZW4tcGgiLCJDb3VudHJ5Q29kZSI6IlBIIiwiZXhwIjoxNzQxNTgyMjIxLCJhdWQiOiJsb2NhbGhvc3QifQ.7xbi07FKlmCRQ9KZmwOYysP5lNtXB8qylrTfvCgNHq4; _ga_LTSKQQZXD8=GS1.1.1741499273.14.1.1741499423.0.0.0"
    }

    def __init__(self):
        """✅ Initialize MySQL connection."""
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Changepa$$06",
                database="betting_db"
            )
            self.cursor = self.conn.cursor()
        except mysql.connector.Error as err:
            self.log(f"❌ MySQL Connection Error: {err}")
            self.conn, self.cursor = None, None  # Prevent crashes

    def start_requests(self):
        """✅ Send requests with authentication cookies."""
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, cookies=self.cookies)

    def parse(self, response):
        """✅ Process API response and store match IDs in the database."""
        if not self.cursor:
            self.log("❌ No database connection, skipping database insert.")
            return

        try:
            data = json.loads(response.text)  # ✅ Parse JSON safely
            match_ids = [match["matchId"] for match in data.get("d", [])]
            bookie_name = "Sports Plus"

            self.log(f"📌 Scraped Match IDs: {match_ids}")

            if match_ids:
                insert_query = "INSERT IGNORE INTO events (eventID, bookie) VALUES (%s, %s)"
                values = [(match_id, bookie_name) for match_id in match_ids]
                self.cursor.executemany(insert_query, values)  # ✅ Efficient batch insert
                self.conn.commit()

            yield {"event_ids": match_ids, "bookie": bookie_name}

        except json.JSONDecodeError:
            self.log("❌ JSON Decode Error: Invalid response format.")
        except Exception as e:
            self.log(f"❌ Unexpected Error: {e}")

    def closed(self, reason):
        """✅ Close MySQL connection when the spider stops."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.log("✅ Database connection closed.")
