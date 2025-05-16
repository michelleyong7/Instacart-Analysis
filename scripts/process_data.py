import pandas as pd
import os

# === Set File Paths ===
RAW_PATH = 'data/raw/'
PROCESSED_PATH = 'data/processed/'

# Create processed folder if it doesn't exist
os.makedirs(PROCESSED_PATH, exist_ok=True)

# === Load Raw CSVs ===
orders = pd.read_csv(os.path.join(RAW_PATH, 'orders.csv'))
order_products_prior = pd.read_csv(os.path.join(RAW_PATH, 'order_products__prior.csv'))
products = pd.read_csv(os.path.join(RAW_PATH, 'products.csv'))

# === 1. Cleaned Orders ===
orders_cleaned = orders.copy()
orders_cleaned['days_since_prior_order'] = orders_cleaned['days_since_prior_order'].fillna(0)
orders_cleaned.to_csv(os.path.join(PROCESSED_PATH, 'orders_cleaned.csv'), index=False)

# === 2. Merged Order-Product Dataset ===
order_products = order_products_prior.merge(products, on='product_id', how='left')
order_products_joined = order_products.merge(orders, on='order_id', how='left')
order_products_joined.to_csv(os.path.join(PROCESSED_PATH, 'joined_order_products.csv'), index=False)

# === 3. User-Level RFM Metrics ===
# Frequency
user_orders = orders.groupby('user_id')['order_number'].max().rename('frequency')

# Recency
user_recency = orders.groupby('user_id')['days_since_prior_order'].mean().rename('avg_days_between_orders')

# Basket Size
basket_sizes = order_products_prior.groupby('order_id').size().reset_index(name='basket_size')
orders_with_basket = orders.merge(basket_sizes, on='order_id')
user_basket = orders_with_basket.groupby('user_id')['basket_size'].mean().rename('avg_basket_size')

# Combine RFM
user_rfm = pd.concat([user_orders, user_recency, user_basket], axis=1).dropna()
user_rfm.to_csv(os.path.join(PROCESSED_PATH, 'user_rfm_metrics.csv'), index=True)

print(" Processed datasets saved to 'data/processed/'")
