import os
import pika
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# Получаем параметры подключения к RabbitMQ
rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.environ.get('RABBITMQ_PORT', 5672))
rabbitmq_user = os.environ.get('RABBITMQ_USER', 'guest')
rabbitmq_password = os.environ.get('RABBITMQ_PASSWORD', 'guest')
queue_name = 'links_queue'
timeout = int(os.environ.get('QUEUE_TIMEOUT', 10))

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

def callback(ch, method, properties, body):
    url = body.decode()
    print(f"Processing message: {url}")
    internal_links, page_title = get_internal_links(url)
    print(f"Page: {page_title} ({url})")

    for link in internal_links:
        print(f"Found link: {link}")
        ch.basic_publish(exchange='', routing_key=queue_name, body=link)

def main():
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=rabbitmq_host, port=rabbitmq_port, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=queue_name)

    def consume():
        try:
            for method_frame, properties, body in channel.consume(queue=queue_name, inactivity_timeout=timeout):
                if body is None:
                    print(f"Queue is empty. Exiting after {timeout} seconds of inactivity.")
                    break
                callback(channel, method_frame, properties, body)
                channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        except Exception as e:
            print(f"Error: {e}")

    consume()
    connection.close()

if __name__ == '__main__':
    main()
