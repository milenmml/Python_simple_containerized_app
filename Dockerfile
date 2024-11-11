#Chainguard Images are regularly-updated, minimal images with low-to-zero CVEs.
FROM cgr.dev/chainguard/wolfi-base:latest

# Install Python and necessary packages
RUN apk add --no-cache python3 py3-pip

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py app.py

# Expose ports for Prometheus and Flask
EXPOSE 9001 8000

# Define environment variable
ENV URLS=https://httpstat.us/503,https://httpstat.us/200

# Install Gunicorn
RUN pip install gunicorn

# Create the /app directory and set permissions
RUN mkdir -p /app && chown -R nobody:nogroup /app

# Switch to a non-root user
USER nobody

# Use Gunicorn to run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:9001", "app:app"]