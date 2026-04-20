# Odds Scraper

This is an automated scraping engine designed to aggregate odds from various sportsbooks for complex mathematical calculations. This large-scale, ongoing project leverages statistics to identify market inefficiencies and arbitrage opportunities.

### Project Structure
* **MSW/**: Contains scripts and resources dedicated to scraping [msw.ph](https://msw.ph).
* **SportsPlus/**: Contains scripts and resources dedicated to scraping [sportsplus.ph](https://sportsplus.ph).
* **Deleting.py**: A maintenance script that clears stale data every 5 minutes to ensure the model uses the most current market information.
* **Mapping/**: Handles data normalization and mapping to ensure consistent processing across different data sources.
