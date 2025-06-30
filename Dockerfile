# Use a stable Python version
FROM python:3.10

# Set the working directory inside the container
WORKDIR /app

# Copy your code into the container
COPY . .

# Install Python packages
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expose the port your app will run on
EXPOSE 10000

# Start your Flask app using Gunicorn
CMD ["gunicorn", "Edubot:app", "--bind", "0.0.0.0:10000"]
