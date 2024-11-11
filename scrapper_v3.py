import aiohttp
import asyncio
import json
import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

async def fetch_page(session, url):
    """Fetch content from a URL asynchronously"""
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()

def extract_data(page_content, keywords, base_url):
    """Extract relevant data from the page based on keywords"""
    soup = BeautifulSoup(page_content, 'html.parser')
    text_content = soup.get_text().lower()
    
    matched_keywords = [kw for kw in keywords if kw.lower() in text_content]
    
    if matched_keywords:
        data = {
            'url': soup.find('link', rel='canonical')['href'] if soup.find('link', rel='canonical') else base_url,
            'title': soup.title.string if soup.title else 'No Title',
            'keywords_matched': matched_keywords,
            'content': text_content,
            'files': []  # Initialize list for downloadable files
        }
        
        # Check for downloadable files related to keywords
        for link in soup.find_all('a', href=True):
            file_url = urljoin(base_url, link['href'])  # Ensure full URL using urljoin
            if any(keyword.lower() in file_url.lower() for keyword in keywords):  # Check if any keyword is in the file URL
                if file_url.endswith(('.pdf', '.jpg', '.jpeg', '.png', '.docx', '.zip')):  # Example file extensions
                    data['files'].append(file_url)

        return data
    return None

async def download_file(session, file_url, save_path):
    """Download a file from a URL and save it to the specified path"""
    try:
        async with session.get(file_url) as response:
            response.raise_for_status()
            with open(save_path, 'wb') as file:
                file.write(await response.read())
            print(f"Downloaded {file_url} to {save_path}")
    except Exception as e:
        print(f"Error downloading {file_url}: {e}")

async def download_files(session, files, save_dir):
    """Download all files and save them in the specified directory"""
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    tasks = []
    for file_url in files:
        file_name = os.path.basename(urlparse(file_url).path)  # Get the file name from the URL
        save_path = os.path.join(save_dir, file_name)
        tasks.append(download_file(session, file_url, save_path))
    
    await asyncio.gather(*tasks)

async def scrape_url(session, url, keywords, data_type):
    """Scrape a single URL and return relevant data"""
    try:
        page_content = await fetch_page(session, url)
        data = extract_data(page_content, keywords, url)
        
        if data and data['files']:
            # Create a directory for saving files based on the type of content (e.g., 'articles', 'books')
            save_dir = os.path.join('scraped_data', 'v3', data_type, data['title'])
            await download_files(session, data['files'], save_dir)

        return data
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

async def scrape_urls(urls, keywords, data_type):
    """Scrape a list of URLs for relevant content asynchronously."""
    semaphore = asyncio.Semaphore(10)  # Limit concurrency to 10
    async with aiohttp.ClientSession() as session:
        tasks = [scrape_url(session, url, keywords, data_type) for url in urls]
        try:
            results = await asyncio.gather(*tasks)
            results = [result for result in results if result]  # Filter out None results
            save_results_to_file(results, data_type)
        except Exception as e:
            print(f"Error scraping URLs: {e}")
    return results

def save_results_to_file(results, data_type):
    """Save the results to a JSON file based on the type of content"""
    # Create the directory if it doesn't exist
    if not os.path.exists('scraped_data/v3'):
        os.makedirs('scraped_data/v3')
    
    # Define the file path for the data type (articles, books, etc.)
    file_path = os.path.join('scraped_data', 'v3', f'{data_type}.json')
    
    # If file exists, append results; otherwise, create a new file
    if os.path.exists(file_path):
        with open(file_path, 'r+', encoding='utf-8') as file:
            existing_data = json.load(file)
            existing_data.extend(results)
            file.seek(0)
            json.dump(existing_data, file, ensure_ascii=False, indent=4)
    else:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)
    
    print(f"Results saved to {file_path}")

def read_texts_from_file(file_path):
    """Read texts from a text file and return them as a list."""
    try:
        with open(file_path, 'r') as file:
            texts = [line.strip() for line in file.readlines() if line.strip()]
        return texts
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading texts from file {file_path}: {e}")
        return []


# Example usage
async def main():
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

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())
