# FIDE Directory Web Scraper

A Python web scraper that extracts contact information from the FIDE (International Chess Federation) member federations directory.

## Features

- Scrapes contact data from 204+ chess federations worldwide
- Extracts: Name, Position, Email, Country
- Exports data to CSV format
- Built-in rate limiting to respect server resources
- Test mode for quick validation
- Comprehensive error handling and logging

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Run the scraper:
```bash
python scrape_fide.py
```

### Choose a mode:
- **Option 1**: Test mode (scrapes first 5 countries) - Recommended for testing
- **Option 2**: Full scrape (all 204+ countries) - Takes ~5-7 minutes

### Output:
- Test mode: `fide_contacts_test.csv`
- Full mode: `fide_contacts.csv`

## CSV Output Format

The generated CSV file contains the following columns:
- `country`: Federation/Country name
- `name`: Contact person's full name
- `position`: Official position/title
- `email`: Email address

## Example Output

```csv
country,name,position,email
Algeria,Brahim Djelloul Azzedine,President/Delegate,azdan_2005@yahoo.fr
Algeria,Mahmoudi Abdelkader,1st Vice-President,mahmo272000@gmail.com
Algeria,Rahmouni Madjid,2nd Vice-President,rahmounim459@gmail.com
```

## How It Works

1. **Fetch Federation List**: Retrieves all 204+ federations from FIDE's JSON API
2. **Iterate Through Federations**: For each federation, makes an AJAX request to get contact details
3. **Parse HTML**: Extracts contact information from the HTML response using BeautifulSoup
4. **Export to CSV**: Saves all collected data to a CSV file using pandas

## Technical Details

- Uses `requests` for HTTP communication
- Parses HTML with `BeautifulSoup4` and `lxml`
- Applies 1.5-second delay between requests (rate limiting)
- Handles UTF-8 BOM encoding in API responses
- Comprehensive logging for debugging

## Data Source

- Website: https://directory.fide.com/list/member_federations/main
- Federation List API: `https://directory.fide.com/a_fedslist.php`
- Contact Details API: `https://directory.fide.com/a_index.php`

## Notes

- Some federations may not have complete contact information
- The scraper respects the server by implementing rate limiting
- All scraping is done from publicly accessible pages
- Data is current as of the scrape date

## License

This tool is for educational and research purposes only.
