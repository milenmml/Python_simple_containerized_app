import os
import asyncio
import aiohttp
import logging
import time
from prometheus_client import Gauge, start_http_server, CollectorRegistry
from flask import Flask, Response

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("/tmp/app.log"),
        logging.StreamHandler()
    ]
)

# URLs to check
URLS = os.getenv('URLS', "https://httpstat.us/503,https://httpstat.us/200").split(',')
logging.info(f"URLs to check: {URLS}")

# Create a custom registry
custom_registry = CollectorRegistry()

# Prometheus metrics
url_up = Gauge('sample_external_url_up', 'URL Up Status', ['url'], registry=custom_registry)
url_response_ms = Gauge('sample_external_url_response_ms', 'URL Response Time', ['url'], registry=custom_registry)

async def fetch_status(session, url):
    start_time = time.time()
    try:
        async with session.get(url, timeout=3) as response:
            status = 1 if response.status == 200 else 0
            response_time = (time.time() - start_time) * 1000  # Calculate response time in milliseconds
            logging.info(f"Checked {url}: status {response.status}, response time {response_time} ms")
            return url, status, response_time
    except Exception as e:
        logging.error(f"Error checking {url}: {e}")
        return url, 0, 0

async def check_urls():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_status(session, url) for url in URLS]
        return await asyncio.gather(*tasks)

@app.route('/metrics')
async def metrics():
    logging.debug("Metrics endpoint called")
    try:
        results = await check_urls()
        metrics_output = []
        for url, status, response_time in results:
            url_up.labels(url=url).set(status)
            url_response_ms.labels(url=url).set(response_time)
            metrics_output.append(f'sample_external_url_up{{url="{url}"}} = {status}')
            metrics_output.append(f'sample_external_url_response_ms{{url="{url}"}} = {response_time}')
        return Response("\n".join(metrics_output), mimetype='text/plain')
    except Exception as e:
        logging.error(f"Error generating metrics: {e}")
        return Response("Internal Server Error", status=500)

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    # Start Prometheus HTTP server on port 8000
    start_http_server(8000, registry=custom_registry)
    logging.info("Prometheus HTTP server started on port 8000")
    # Start Flask app on port 9001
    app.run(host='0.0.0.0', port=9001)
    logging.info("Flask app started on port 9001")