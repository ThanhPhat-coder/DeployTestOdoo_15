FROM python:3.8

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    libpq-dev \
    build-essential \
    wget \
    curl \
    python3-dev \
    python3-venv \
    postgresql-client \
    libldap2-dev \
    libsasl2-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /odoo

# Copy Odoo source
COPY ./odoo /odoo
COPY ./addons /mnt/extra-addons
COPY ./odoo.conf /etc/odoo/odoo.conf
COPY ./requirements.txt /odoo/requirements.txt
COPY ./entrypoint.sh /entrypoint.sh
COPY ./recruitment_db.dump /recruitment_db.dump

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r /odoo/requirements.txt

# Set entrypoint
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
