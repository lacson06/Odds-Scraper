import scrapy

class SportsPlusSpider(scrapy.Spider):
    name = "api"
    start_urls = [
        "https://www.sportsplus.ph/sbk/api/v1/single/match/3286277?fl=false"
    ]

    def start_requests(self):
        cookies = {
            "default_culture": "en-us",
            "brand": "Sp",
            "culture": "en-us",
            "_ga": "GA1.1.506116744.1738161703",
            "_pid": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNZW1iZXJSb2xlIjoiMSIsIk1lbWJlcklkIjoiODliZmEzOTYyNzljNDY1NmJjZjJlYTFiMTA2NzI4YTIiLCJDdWx0dXJlIjoiZW4tcGgiLCJDb3VudHJ5Q29kZSI6IlBIIiwiZXhwIjoxNzQxMzU0NDg3LCJhdWQiOiJsb2NhbGhvc3QifQ.sbxwhjEAV7ZwUvL9Vq--dLLHNJpPoAruJ0s40yRe84w; _ga_LTSKQQZXD8=GS1.1.1741270835.12.1.1741271688.0.0.0"
        }

        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse,  cookies=cookies)

    def parse(self, response):
        data = response.json()

        team_one = data["d"]["match"]["competitor1Name"]["long"]
        team_two = data["d"]["match"]["competitor2Name"]["long"]
        # odd_one = data["d"]["match"]["market"]['selections']['odds'][0]

        for market in data["d"].get("marketLines", []):
            yield {
                "game_name": f"{team_one} vs {team_two}",
                "bet_name": market["marketLineName"]["long"],
                "team_1": team_one,
                # "odd_1": odd_one,
                "team_2": team_two,
            }