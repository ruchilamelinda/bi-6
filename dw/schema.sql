-- Tabel dimensi
CREATE TABLE dim_app (
    app_id SERIAL PRIMARY KEY,
    app_name TEXT,
    category TEXT,
    genres TEXT,
    current_ver TEXT
);

CREATE TABLE dim_price (
    price_id SERIAL PRIMARY KEY,
    price_value FLOAT,
    price_type TEXT
);

CREATE TABLE dim_contentRating (
    contentRating_id SERIAL PRIMARY KEY,
    content_rating TEXT
);

CREATE TABLE dim_device (
    device_id SERIAL PRIMARY KEY,
    android_version TEXT,
    size_mb FLOAT
);

CREATE TABLE dim_date (
    date_id SERIAL PRIMARY KEY,
    release_date DATE,
    release_month TEXT,
    release_year INT
);

-- Tabel fakta
CREATE TABLE fact_app_reviews (
    fact_id SERIAL PRIMARY KEY,
    app_id INT REFERENCES dim_app(app_id),
    device_id INT REFERENCES dim_device(device_id),
    date_id INT REFERENCES dim_date(date_id),
    price_id INT REFERENCES dim_price(price_id),
    contentRating_id INT REFERENCES dim_contentRating(contentRating_id),
    rating FLOAT,
    total_reviews INT,
    total_installs INT
);
