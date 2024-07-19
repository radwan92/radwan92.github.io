# Downloads images for all books in _data/books.yml

import yaml
import requests
import os
from bs4 import BeautifulSoup

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
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Get the image meta tag
            image = soup.find('meta', property='og:image')

            # Download the image
            image_url = image['content']
            image_response = requests.get(image_url)

            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            with open(image_path, 'wb') as image_file:
                image_file.write(image_response.content)

            print(f'Downloaded {image_path}')


if __name__ == '__main__':
    fetch_book_covers()
    