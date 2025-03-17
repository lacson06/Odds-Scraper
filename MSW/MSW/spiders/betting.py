import json

import scrapy


class BettingSpider(scrapy.Spider):
    name = "betting"
    allowed_domains = ["sports.msw.ph"]
    start_urls = ["https://sports.msw.ph/xapi/rest/events/39448850?bettable=true&marketStatus=OPEN&periodType=PRE_MATCH&includeMarkets=true&lightWeightResponse=true&includeLiveEvents=true&maxMarketPerEvent=1000&l=en"]

    def parse(self, response):
        data = json.loads(response.body)

        event_name = data.get('description')
        markets = data.get('markets')

#HEAD TO HEAD - MATCH
        if markets:
            first_market = markets[0]
            market_description = first_market.get("description", "No description available")
            outcomes = first_market.get("outcomes", [])

            team_one = outcomes[0].get("description", "No description available") if len(
                outcomes) > 0 else "No description available"
            team_two = outcomes[1].get("description", "No description available") if len(
                outcomes) > 1 else "No description available"

            decimal_price_one = outcomes[0].get("consolidatedPrice", {}).get("currentPrice", {}).get("decimal",
                                                                                                     "No price available") if len(
                outcomes) > 0 else "No price available"
            decimal_price_two = outcomes[1].get("consolidatedPrice", {}).get("currentPrice", {}).get("decimal",
                                                                                                     "No price available") if len(
                outcomes) > 1 else "No price available"
        else:
            market_description = "No description available"
            team_one = team_two = "No description available"
            decimal_price_one = decimal_price_two = "No price available"

        # HEAD TO HEAD - REGULATION
        if len(markets) > 0:  # Check if the list is not empty
            market_description_two = markets[1].get("description", "No description available")
        else:
            market_description_two = "No description available"

        yield {
            "game_name": event_name,
            "bet_name": market_description,
            "team1": f"{team_one} - {decimal_price_one}",
            "team2": f"{team_two} - {decimal_price_two}",
        }