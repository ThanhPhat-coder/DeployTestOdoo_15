# Sử dụng Python 3.8
FROM python:3.8

# Cài đặt các gói hệ thống cần thiết
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

# Thiết lập thư mục làm việc
WORKDIR /odoo

# Sao chép toàn bộ mã nguồn Odoo vào container
COPY . /odoo

# Sao chép các addons tùy chỉnh (nếu có)
COPY ./addons /mnt/extra-addons

# Sao chép file cấu hình, yêu cầu, script, và dump database
COPY ./odoo.conf /etc/odoo/odoo.conf
COPY ./requirements.txt /odoo/requirements.txt
COPY ./entrypoint.sh /entrypoint.sh
COPY ./recruitment_db.dump /recruitment_db.dump

# Cài đặt các thư viện Python
RUN pip install --upgrade pip && pip install -r /odoo/requirements.txt

# Cấp quyền thực thi cho script
RUN chmod +x /entrypoint.sh

# Entrypoint khi container khởi động
ENTRYPOINT ["/entrypoint.sh"]
