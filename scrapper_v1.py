import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup
import os

async def fetch_page(session, url):
    """
    Fetch content from a URL asynchronously.

    Args:
        session (aiohttp.ClientSession): The session to use for the HTTP request.
        url (str): The URL to fetch the content from.

    Returns:
        str: The HTML content of the page.

    Raises:
        aiohttp.ClientError: If the request fails or the response status is not successful.
    """
    async with session.get(url) as response:
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        return await response.text()

def extract_data(page_content, keywords):
    """
    Extract relevant data from the page content based on provided keywords.

    Args:
        page_content (str): The HTML content of the page.
        keywords (list): A list of keywords to search for in the page content.

    Returns:
        dict or None: A dictionary containing the URL, title, matched keywords, and a snippet
                      of the page content if any keywords are matched; otherwise, None.
    """
    soup = BeautifulSoup(page_content, 'html.parser')  # Parse the page content with BeautifulSoup
    text_content = soup.get_text().lower()  # Extract and normalize the text content

    # Find keywords in the text content
    matched_keywords = [kw for kw in keywords if kw.lower() in text_content]

    if matched_keywords:
        # Extract relevant data if keywords are found
        data = {
            'url': soup.find('link', rel='canonical')['href'] if soup.find('link', rel='canonical') else None,
            'title': soup.title.string if soup.title else 'No Title',
            'keywords_matched': matched_keywords,
            'content': text_content,
        }
        return data
    return None  # Return None if no keywords are matched

async def scrape_url_with_limit(session, url, keywords, semaphore):
    """
    Scrape a single URL while enforcing a concurrency limit.

    Args:
        session (aiohttp.ClientSession): The session to use for the HTTP request.
        url (str): The URL to scrape.
        keywords (list): A list of keywords to search for.
        semaphore (asyncio.Semaphore): A semaphore to limit concurrency.

    Returns:
        dict or None: The extracted data if successful, None if an error occurs.
    """
    async with semaphore:
        return await scrape_url(session, url, keywords)

async def scrape_urls(urls, keywords, data_type):
    """
    Scrape a list of URLs for relevant content asynchronously, with concurrency control.

    Args:
        urls (list): A list of URLs to scrape.
        keywords (list): A list of keywords to search for in the content.
        data_type (str): A string indicating the type of data being scraped (e.g., 'articles', 'books').

    Returns:
        list: A list of dictionaries containing the extracted data for each URL.
    """
    semaphore = asyncio.Semaphore(10)  # Limit concurrency to 10 simultaneous requests
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_url_with_limit(session, url, keywords, semaphore) for url in urls]  # Create tasks for scraping each URL
        try:
            results = await asyncio.gather(*tasks)  # Run all scraping tasks asynchronously
            results = [result for result in results if result]  # Filter out None results
            save_results_to_file(results, data_type)  # Save the results to a file
        except Exception as e:
            print(f"Error scraping URLs: {e}")
    return results

async def scrape_url(session, url, keywords):
    """
    Scrape a single URL and return relevant data based on the keywords.

    Args:
        session (aiohttp.ClientSession): The session to use for the HTTP request.
        url (str): The URL to scrape.
        keywords (list): A list of keywords to search for in the content.

    Returns:
        dict or None: The extracted data if successful, None if an error occurs.
    """
    try:
        page_content = await fetch_page(session, url)  # Fetch the page content
        data = extract_data(page_content, keywords)  # Extract data from the page content
        return data
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def save_results_to_file(results, data_type):
    """
    Save the extracted results to a JSON file.

    Args:
        results (list): A list of dictionaries containing the scraped data.
        data_type (str): A string indicating the type of data being saved (e.g., 'articles', 'books').

    Returns:
        None
    """
    # Create the directory if it doesn't exist
    if not os.path.exists('scraped_data/v1'):
        os.makedirs('scraped_data/v1')
    
    # Define the file path based on the data type (e.g., 'articles.json', 'books.json')
    file_path = os.path.join('scraped_data', 'v1', f'{data_type}.json')

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
    """
    Read URLs or keywords from a text file and return them as a list.

    Args:
        file_path (str): The path to the text file containing URLs or keywords.

    Returns:
        list: A list of non-empty lines from the file (URLs or keywords).
    """
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
