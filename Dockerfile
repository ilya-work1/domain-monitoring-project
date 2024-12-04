
FROM python

# Set working directory
WORKDIR /app

# Copy application files
COPY . /app

# Install dependencies
RUN pip install -r requirements.txt

# Start the application
CMD ["python", "app.py"]
