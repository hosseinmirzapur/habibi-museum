# Habibi Digital Bookstore

This project is designed to scrape web pages asynchronously, extract relevant data based on provided keywords, and save the results into a JSON file. It also includes a feature to identify downloadable files related to the keywords and include them in the scraped data.

## Features
- **Asynchronous Web Scraping**: Uses `aiohttp` and `asyncio` for efficient asynchronous scraping of multiple URLs.
- **Keyword-based Data Extraction**: Extracts text content from the page and matches it with a list of provided keywords.
- **Downloadable Files Detection**: Identifies and includes downloadable files (PDFs, images, etc.) related to the keywords in the scraped data.
- **Concurrency Limit**: Limits the number of concurrent requests to 10 using `asyncio.Semaphore` to avoid overloading the server.
- **Results Saving**: Saves the scraped results in a `scraped_data` directory, where each data type (e.g., articles, books, etc.) has its own JSON file.

## Requirements
- Python 3.6+
- `aiohttp`
- `beautifulsoup4`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/web-scraping-project.git
   cd web-scraping-project
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## How It Works

### Step 1: Prepare the Text Files
The script expects several text files that contain lists of URLs or keywords. These files should be formatted as one URL or keyword per line:
- `keywords.txt`: A list of keywords that will be used to match content on the scraped web pages.
- `articles.txt`, `books.txt`, `news.txt`, `regular.txt`: Lists of URLs for scraping.

### Step 2: Running the Script
To run the scraper, execute the following command:

```bash
python scraper.py
```

This will:
- Load the keywords and URLs from the specified text files.
- Scrape the URLs asynchronously for matching content.
- Save the results in a JSON file under the `scraped_data` directory.

### Step 3: Downloading Files
If a URL contains downloadable files (e.g., PDFs, images, etc.) related to the keywords, those files will be identified and included in the scraped data.

For each URL, the script will check for the presence of downloadable files (PDFs, images, etc.) and include the URL of the downloadable file in the result if the file name or content matches the keywords.

### Step 4: Results
After the script completes, the results will be saved in the `scraped_data` directory:
- Each type of data (articles, books, etc.) will have a corresponding JSON file, e.g., `articles.json`, `books.json`.

The structure of each JSON file will look like this:

```json
[
  {
    "url": "https://example.com/page1",
    "title": "Example Page Title",
    "keywords_matched": ["keyword1", "keyword2"],
    "content": "This is the extracted content from the page...",
    "files": [
      "https://example.com/file1.pdf",
      "https://example.com/file2.jpg"
    ]
  },
  {
    "url": "https://example.com/page2",
    "title": "Another Page Title",
    "keywords_matched": ["keyword3"],
    "content": "This is the extracted content from another page...",
    "files": []
  }
]
```

## Functionality Breakdown

1. **`fetch_page`**: 
   - Fetches the HTML content of a page asynchronously using `aiohttp`.
   
2. **`extract_data`**:
   - Extracts the text content of a page and matches it with the provided keywords.
   - If keywords are found, it returns a dictionary with the URL, title, matched keywords, and the first 500 characters of the content.
   
3. **`scrape_url_with_limit`**:
   - A helper function that enforces a concurrency limit when scraping a single URL.
   
4. **`scrape_urls`**:
   - Scrapes a list of URLs for content and saves the results into a JSON file.
   
5. **`scrape_url`**:
   - Scrapes a single URL and extracts relevant data.

6. **`save_results_to_file`**:
   - Saves the extracted data into a JSON file. If the file already exists, new results are appended to it.

7. **`read_texts_from_file`**:
   - Reads a list of texts (URLs or keywords) from a file.

## Versioning

* v1:
  - Only texts are scraped once the code is executed
* v2:
   - Scraping downloadable files and including them in the final results
* v3:
  - Scraping and downloading the files included in the json file


## Contributing
If you'd like to contribute to this project, feel free to fork the repository, make changes, and submit a pull request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.