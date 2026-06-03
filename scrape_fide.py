"""
FIDE Directory Web Scraper
Scrapes contact information from FIDE member federations directory
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FIDEScraper:
    """Scraper for FIDE directory contact information"""

    BASE_URL = "https://directory.fide.com"
    FEDS_API = f"{BASE_URL}/a_fedslist.php"
    CONTACTS_API = f"{BASE_URL}/a_index.php"

    def __init__(self, delay: float = 1.5):
        """
        Initialize the scraper

        Args:
            delay: Delay in seconds between requests (default 1.5)
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': f'{self.BASE_URL}/list/member_federations/main',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        })

    def get_federations(self) -> List[Dict]:
        """
        Fetch list of all member federations

        Returns:
            List of federation dictionaries
        """
        try:
            logger.info("Fetching federation list...")
            response = self.session.get(self.FEDS_API, timeout=10)
            response.raise_for_status()

            # Handle UTF-8 BOM by decoding with utf-8-sig
            response.encoding = 'utf-8-sig'
            federations = response.json()

            logger.info(f"Successfully fetched {len(federations)} federations")
            return federations
        except Exception as e:
            logger.error(f"Error fetching federations: {e}")
            return []

    def get_federation_contacts(self, fed_code: str, fed_name: str) -> List[Dict]:
        """
        Fetch contact details for a specific federation

        Args:
            fed_code: Federation details_code from API
            fed_name: Federation name for logging

        Returns:
            List of contact dictionaries
        """
        contacts = []

        try:
            params = {
                'category': '1',
                'b': '2',
                'c': fed_code
            }

            logger.info(f"Fetching contacts for {fed_name} ({fed_code})...")
            response = self.session.get(self.CONTACTS_API, params=params, timeout=10)
            response.raise_for_status()

            # Parse HTML response
            soup = BeautifulSoup(response.text, 'lxml')

            # Extract contact information
            contacts = self._parse_contacts(soup, fed_name)

            if contacts:
                logger.info(f"Found {len(contacts)} contact(s) for {fed_name}")
            else:
                logger.warning(f"No contacts found for {fed_name}")

        except Exception as e:
            logger.error(f"Error fetching contacts for {fed_name}: {e}")

        return contacts

    def _parse_contacts(self, soup: BeautifulSoup, country: str) -> List[Dict]:
        """
        Parse contact information from HTML

        Args:
            soup: BeautifulSoup object of the page
            country: Country name

        Returns:
            List of contact dictionaries
        """
        contacts = []

        # Find all directory-card divs (each contains one person's info)
        card_divs = soup.find_all('div', class_='directory-card')

        for card in card_divs:
            contact = {
                'country': country,
                'name': '',
                'position': '',
                'email': ''
            }

            # Find h4 for name
            h4 = card.find('h4')
            if h4:
                name_link = h4.find('a')
                if name_link:
                    contact['name'] = name_link.get_text(strip=True)
                else:
                    contact['name'] = h4.get_text(strip=True)

            # Find p tags for position (first p tag that doesn't contain @)
            for p in card.find_all('p'):
                text = p.get_text(strip=True)
                if text and '@' not in text and not contact['position']:
                    contact['position'] = text
                    break

            # Find h6 for email (email is in h6 tag)
            h6 = card.find('h6')
            if h6:
                email_text = h6.get_text(strip=True)
                # Email might contain multiple addresses separated by comma
                if '@' in email_text:
                    # Take first email if multiple
                    emails = [e.strip() for e in email_text.split(',')]
                    contact['email'] = emails[0] if emails else email_text

            # Only add if we have at least a name
            if contact['name']:
                contacts.append(contact)

        return contacts

    def scrape_all(self, test_mode: bool = False, test_limit: int = 5) -> pd.DataFrame:
        """
        Scrape all federations and their contacts

        Args:
            test_mode: If True, only scrape first few federations
            test_limit: Number of federations to scrape in test mode

        Returns:
            DataFrame with all contact information
        """
        all_contacts = []

        # Get list of federations
        federations = self.get_federations()

        if not federations:
            logger.error("No federations found. Aborting.")
            return pd.DataFrame()

        # Limit for testing
        if test_mode:
            federations = federations[:test_limit]
            logger.info(f"TEST MODE: Scraping only {test_limit} federations")

        # Scrape each federation
        total = len(federations)
        for idx, fed in enumerate(federations, 1):
            # Use details_code for API call (not fed_short_name)
            fed_code = fed.get('details_code', fed.get('fed_short_name', ''))
            fed_name = fed.get('fed_long_name', fed_code)

            logger.info(f"Progress: {idx}/{total} - {fed_name}")

            contacts = self.get_federation_contacts(fed_code, fed_name)
            all_contacts.extend(contacts)

            # Rate limiting
            if idx < total:
                time.sleep(self.delay)

        # Create DataFrame
        df = pd.DataFrame(all_contacts)

        if not df.empty:
            # Reorder columns
            columns = ['country', 'name', 'position', 'email']
            df = df[columns]
            logger.info(f"Successfully scraped {len(df)} total contacts from {total} federations")
        else:
            logger.warning("No contacts were scraped!")

        return df

    def save_to_csv(self, df: pd.DataFrame, filename: str = 'fide_contacts.csv'):
        """
        Save DataFrame to CSV file

        Args:
            df: DataFrame to save
            filename: Output filename
        """
        try:
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")


def main():
    """Main execution function"""

    print("=" * 60)
    print("FIDE Directory Web Scraper")
    print("=" * 60)
    print()

    # Create scraper instance
    scraper = FIDEScraper(delay=1.5)

    # Ask user if they want to run in test mode
    print("Options:")
    print("1. Test mode (scrape first 5 countries)")
    print("2. Full scrape (all 191+ countries)")
    print()

    choice = input("Enter your choice (1 or 2, default=1): ").strip() or "1"

    test_mode = choice == "1"

    print()
    print("Starting scrape...")
    print()

    # Scrape data
    df = scraper.scrape_all(test_mode=test_mode, test_limit=5)

    # Save to CSV
    if not df.empty:
        filename = 'fide_contacts_test.csv' if test_mode else 'fide_contacts.csv'
        scraper.save_to_csv(df, filename)

        print()
        print("=" * 60)
        print("SCRAPING COMPLETE!")
        print("=" * 60)
        print(f"Total contacts scraped: {len(df)}")
        print(f"Output file: {filename}")
        print()
        print("Sample data:")
        print(df.head(10).to_string())
    else:
        print()
        print("No data was scraped. Please check the logs for errors.")


if __name__ == "__main__":
    main()
