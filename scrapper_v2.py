import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup
import os
import re  # To match file extensions in URLs

async def fetch_page(session, url):
    """Fetch content from a URL asynchronously."""
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()

def extract_data(page_content, keywords):
    """
    Extract relevant data from the page content based on provided keywords.
    Additionally, look for downloadable files related to the keywords.
    
    Args:
        page_content (str): The HTML content of the page.
        keywords (list): A list of keywords to search for in the page content.

    Returns:
        dict or None: A dictionary containing the URL, title, matched keywords, 
                      content snippet, and any relevant downloadable files if found.
    """
    soup = BeautifulSoup(page_content, 'html.parser')  # Parse the page content
    text_content = soup.get_text().lower()  # Extract and normalize the text content

    # Find keywords in the text content
    matched_keywords = [kw for kw in keywords if kw.lower() in text_content]

    # Initialize list to hold downloadable files
    downloadable_files = []

    # Look for links to downloadable files (e.g., PDFs, DOCX, images)
    for link in soup.find_all('a', href=True):
        file_url = link['href']
        # Check if the link ends with a common file extension
        if re.search(r'\.(pdf|docx|xlsx|pptx|jpg|jpeg|png|gif|zip|rar)$', file_url, re.IGNORECASE):
            # Check if the file URL contains any of the keywords
            if any(kw.lower() in file_url.lower() for kw in keywords):
                downloadable_files.append(file_url)

    if matched_keywords:
        # Extract relevant data if keywords are found
        data = {
            'url': soup.find('link', rel='canonical')['href'] if soup.find('link', rel='canonical') else None,
            'title': soup.title.string if soup.title else 'No Title',
            'keywords_matched': matched_keywords,
            'content': text_content,
            'downloadable_files': downloadable_files  # Include the list of relevant downloadable files
        }
        return data
    return None  # Return None if no keywords are matched

async def scrape_url_with_limit(session, url, keywords, semaphore):
    """Scrape a single URL while enforcing a concurrency limit."""
    async with semaphore:
        return await scrape_url(session, url, keywords)

async def scrape_urls(urls, keywords, data_type):
    """Scrape a list of URLs for relevant content asynchronously, with concurrency control."""
    semaphore = asyncio.Semaphore(10)  # Limit concurrency to 10 simultaneous requests
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_url_with_limit(session, url, keywords, semaphore) for url in urls]
        try:
            results = await asyncio.gather(*tasks)  # Run all scraping tasks asynchronously
            results = [result for result in results if result]  # Filter out None results
            save_results_to_file(results, data_type)  # Save the results to a file
        except Exception as e:
            print(f"Error scraping URLs: {e}")
    return results

async def scrape_url(session, url, keywords):
    """Scrape a single URL and return relevant data based on the keywords."""
    try:
        page_content = await fetch_page(session, url)  # Fetch the page content
        data = extract_data(page_content, keywords)  # Extract data from the page content
        return data
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def save_results_to_file(results, data_type):
    """Save the extracted results to a JSON file."""
    # Create the directory if it doesn't exist
    if not os.path.exists('scraped_data/v2'):
        os.makedirs('scraped_data/v2')
    
    # Define the file path based on the data type (e.g., 'articles.json', 'books.json')
    file_path = os.path.join('scraped_data', 'v2', f'{data_type}.json')

    # If the file exists, append the results to it; otherwise, create a new file
    if os.path.exists(file_path):
        with open(file_path, 'r+', encoding='utf-8') as file:
            existing_data = json.load(file)
            existing_data.extend(results)  # Add the new results to the existing data
            file.seek(0)  # Move the file pointer to the beginning
            json.dump(existing_data, file, ensure_ascii=False, indent=4)  # Write the updated data
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)  # Create a new file and write the data
    
    print(f"Results saved to {file_path}")

def read_texts_from_file(file_path):
    """Read URLs or keywords from a text file and return them as a list."""
    try:
        with open(file_path, 'r') as file:
            texts = [line.strip() for line in file.readlines() if line.strip()]  # Read non-empty lines
        return texts
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []  # Return an empty list if the file is not found
    except Exception as e:
        print(f"Error reading texts from file {file_path}: {e}")
        return []  # Return an empty list if an error occurs

# Example usage of the scraper
async def main():
    # Read the list of keywords and URLs from text files
    keywords = read_texts_from_file("./keywords.txt")
    articles = read_texts_from_file("./articles.txt")
    books = read_texts_from_file("./books.txt")
    news = read_texts_from_file("./news.txt")
    regular_texts = read_texts_from_file("./regular.txt")
    
    # Scrape articles
    await scrape_urls(articles, keywords, 'articles')
    
    # Scrape books
    await scrape_urls(books, keywords, 'books')
    
    # Scrape news
    await scrape_urls(news, keywords, 'news')
    
    # Scrape regular texts
    await scrape_urls(regular_texts, keywords, 'regular')

# Run the async main function when the script is executed
if __name__ == "__main__":
    asyncio.run(main())
