import scrapy
import json
import mysql.connector


class BettingSpider(scrapy.Spider):
    name = "events"
    allowed_domains = ["sports.msw.ph"]
    start_urls = [
        "https://sports.msw.ph/xapi/rest/events?bettable=true&marketStatus=OPEN&periodType=PRE_MATCH&includeMarkets=true&includeHiddenOutcomes=true&includeHiddenMarkets=false&maxMarketPerEvent=100&lightWeightResponse=true&sportGroups=REGULAR&allBettableEvents=true&marketFilter=GAME&eventType=GAME&excludeMarketByOpponent=true&marketTypeIds=1257%2C3061%2C15%2C3060%2C3056&periodIds=1195%2C1196&includeAdditional=false&additionalMarketTypeIds=&additionalPeriodIds=%2C&sortMarketsByPriceDifference=true&includeLiveEvents=true&sportCodes=FOOT%2CTENN%2CBASK%2CBASE%2CVOLL%2CBADM%2CICEH%2CAMFB%2CRUGL%2CRUGU%2CTABL%2CSNOO%2CDART%2CCRIC%2CHAND%2CEFOT%2CEBSK%2CVICR%2CFUTS%2CBEVO&liveMarketStatus=OPEN%2CSUSPENDED&liveAboutToStart=true&liveExcludeLongTermSuspended=true&eventPathIds=227&maxMarketsPerMarketType=1&sortByEventpath=true&sortByEventpathIds=227%2C239%2C1200%2C226%2C240%2C1%2C2100%2C1900%2C238%2C5000%2C1100%2C1250%2C22877%2C215%2C237%2C22884%2C1600%2C22881%2C1300%2C22886%2C3700%2C2700%2C1400%2C2900%2C22878%2C1500&page=1&eventsPerPage=20&l=en"
    ]

    def __init__(self):
        # ✅ Connect to MySQL database
        self.conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Changepa$$06",  # 🔹 Replace with your MySQL password
            database="betting_db"
        )
        self.cursor = self.conn.cursor()

        # ✅ Create table if it doesn't exist
        self.create_table()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS events (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bookie VARCHAR(50) DEFAULT 'MegaSportsWorld',
            eventID INT UNIQUE
        );
        """
        self.cursor.execute(create_table_query)
        self.conn.commit()
        self.log("✅ Table 'events' is ready.")

    def parse(self, response):
        try:
            data = json.loads(response.text)

            # ✅ Extract event IDs
            event_ids = [event["id"] for event in data]
            bookie_name = "MegaSportsWorld"

            self.log(f"📌 Scraped Event IDs: {event_ids}")

            # ✅ Insert into MySQL
            for event_id in event_ids:
                insert_query = """
                INSERT IGNORE INTO events (eventID, bookie) VALUES (%s, %s);
                """
                self.cursor.execute(insert_query, (event_id, bookie_name))

            self.conn.commit()  # ✅ Save changes

            yield {"event_ids": event_ids, "bookie": bookie_name}

        except json.JSONDecodeError:
            self.log("❌ Failed to decode JSON. The response might be HTML.")

    def closed(self, reason):
        self.cursor.close()
        self.conn.close()
        self.log("✅ Database connection closed.")
