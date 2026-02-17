FROM php:8.4-apache

# Install SQLite and other essentials
RUN apt-get update && apt-get install -y \
    libsqlite3-dev \
    libonig-dev \
    zip unzip git curl \
    && docker-php-ext-install pdo_mysql pdo_sqlite mbstring bcmath

# Configure Apache for Cloud Run ($PORT)
ENV PORT=8080
RUN sed -i 's/80/${PORT}/g' /etc/apache2/sites-available/000-default.conf /etc/apache2/ports.conf
RUN sed -i 's|/var/www/html|/var/www/html/public|g' /etc/apache2/sites-available/000-default.conf
RUN a2enmod rewrite

# Create the folder where the GCS bucket will be mounted
# We'll put it in 'storage/database'
RUN mkdir -p /var/www/html/storage/database && \
    mkdir -p /var/www/html/storage/app/livewire-tmp && \
    mkdir -p /var/www/html/storage/app/private && \
    mkdir -p /var/www/html/storage/framework/views && \
    mkdir -p /var/www/html/storage/framework/cache && \
    mkdir -p /var/www/html/storage/framework/sessions && \
    chown -R www-data:www-data /var/www/html/storage

# Increase PHP upload limits
RUN echo "upload_max_filesize=100M" > /usr/local/etc/php/conf.d/uploads.ini && \
    echo "post_max_size=100M" >> /usr/local/etc/php/conf.d/uploads.ini && \
    echo "memory_limit=256M" >> /usr/local/etc/php/conf.d/uploads.ini

WORKDIR /var/www/html
COPY . .

# Install composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer
RUN composer install --no-dev --optimize-autoloader

# Install Node.js and build assets
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    npm install && \
    npm run build

# Final permission check
RUN chown -R www-data:www-data /var/www/html/storage /var/www/html/bootstrap/cache

EXPOSE 8080
CMD ["sh", "-c", "php artisan migrate --force && apache2-foreground"]
