# Improved Scraper Logic

# This logic will target specific news entry containers rather than crawling all links.

def scrape_news_entries(response):
    from bs4 import BeautifulSoup
    
    # Parse the response content
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all news entry containers
    news_entries = soup.find_all('div', class_='news-entry')  # Update this selector to target your needs
    
    # Extract data from each news entry
    for entry in news_entries:
        title = entry.find('h2').get_text() if entry.find('h2') else 'No Title'
        link = entry.find('a')['href'] if entry.find('a') else 'No Link'
        print(f'Title: {title}\nLink: {link}')

# Add your specific logic of how you will handle the links, save to DB, etc.