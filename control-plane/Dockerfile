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
RUN a2enmod rewrite

# Create the folder where the GCS bucket will be mounted
# We'll put it in 'storage/database'
RUN mkdir -p /var/www/html/storage/database && \
    chown -R www-data:www-data /var/www/html/storage

WORKDIR /var/www/html
COPY . .

COPY --from=composer:latest /usr/bin/composer /usr/bin/composer
RUN composer install --no-dev --optimize-autoloader

# Final permission check
RUN chown -R www-data:www-data /var/www/html/storage /var/www/html/bootstrap/cache

EXPOSE 8080
CMD ["sh", "-c", "php artisan migrate --force && apache2-foreground"]
