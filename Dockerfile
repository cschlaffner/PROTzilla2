# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DEFAULT_TIMEOUT=100

# Install git, build-essential, and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libbz2-dev \
    liblzma-dev \
    libssl-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libffi-dev \
    zlib1g-dev \
    gcc \
    make \
    libxml2-dev \
    libxslt-dev \
    curl \
    tk-dev \
    python3-tk \
    && apt-get clean

# Install Rust (needed for gseapy)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Set the work directory to the root of your project inside the container
WORKDIR /project_root

# Install dependencies
COPY requirements.txt /project_root/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# Run the Django development server
RUN adduser --disabled-password --gecos '' myuser
USER myuser
CMD ["python", "ui/manage.py", "runserver", "0.0.0.0:8000"]
