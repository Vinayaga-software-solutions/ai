FROM php:8.3-cli

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y \
    git unzip libsqlite3-dev curl \
    && docker-php-ext-install pdo pdo_sqlite

# Copy project
COPY . .

# Install composer properly
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

RUN composer install --no-dev --optimize-autoloader

EXPOSE 8080

CMD php artisan migrate --force && php artisan serve --host=0.0.0.0 --port=8080
