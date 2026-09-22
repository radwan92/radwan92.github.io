# Downloads images for all books in _data/books.yml

import yaml
import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit


def localized_goodreads_url(url):
    """Use Goodreads' localized route, which still returns the page HTML."""
    parsed = urlsplit(url)
    if parsed.hostname in {'goodreads.com', 'www.goodreads.com'} and not parsed.path.startswith('/en/'):
        parsed = parsed._replace(path=f'/en{parsed.path}')
    return urlunsplit(parsed)

def fetch_book_covers():
    with open('_data/books.yml') as file:
        books = yaml.load(file, Loader=yaml.FullLoader)

        for book in books:
            url = book['url']
            name = book['name']

            # Check if image already exists
            image_path = f'assets/images/books/{book["slug"]}.jpg'
            if os.path.exists(image_path):
                print(f'Image for "{name}" already exists at {image_path}')
                continue

            print(f'Fetching image for {name} from {url}')
            
            # Fetch book page
            response = requests.get(
                localized_goodreads_url(url),
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=30,
            )
            if response.status_code != 200 or not response.content:
                raise RuntimeError(
                    f'Could not fetch Goodreads page for "{name}": '
                    f'HTTP {response.status_code}, {len(response.content)} bytes'
                )

            soup = BeautifulSoup(response.text, 'html.parser')

            # Get the image meta tag
            image = soup.find('meta', property='og:image')
            if image is None or not image.get('content'):
                raise RuntimeError(f'No cover image found on Goodreads page for "{name}"')

            # Download the image
            image_url = image['content']
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            with open(image_path, 'wb') as image_file:
                image_file.write(image_response.content)

            print(f'Downloaded {image_path}')


if __name__ == '__main__':
    fetch_book_covers()
    
