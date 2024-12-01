import os
import pika
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.environ.get('RABBITMQ_PORT', 5672))
rabbitmq_user = os.environ.get('RABBITMQ_USER', 'guest')
rabbitmq_password = os.environ.get('RABBITMQ_PASSWORD', 'guest')
queue_name = 'links_queue'

def get_internal_links(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        domain = urlparse(url).netloc
        links = set()
        for link in soup.find_all('a', href=True):
            href = link['href']
            absolute_url = urljoin(url, href)
            if urlparse(absolute_url).netloc == domain:
                links.add(absolute_url)
        return links, soup.title.string if soup.title else "Untitled"
    except Exception as e:
        print(f"Error while processing {url}: {e}")
        return set(), None

def main():
    url = input("Enter a URL to process: ").strip()
    if not url.startswith("http"):
        url = f"http://{url}"

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=rabbitmq_host, port=rabbitmq_port, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    internal_links, page_title = get_internal_links(url)
    print(f"Processing page: {page_title} ({url})")

    for link in internal_links:
        print(f"Found link: {link}")
        channel.basic_publish(exchange='', routing_key=queue_name, body=link)

    connection.close()

if __name__ == '__main__':
    main()
