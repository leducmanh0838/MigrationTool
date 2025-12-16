import requests
import cloudinary
import cloudinary.uploader
import base64

# --- Cấu hình Cloudinary ---
# Thay thế bằng thông tin API của bạn
CLOUDINARY_CLOUD_NAME="dedsaxk7j"
CLOUDINARY_API_KEY="475528271894445"
CLOUDINARY_API_SECRET="8OjLj8udRhzD494zkKSwCO3tZOo"

cloudinary.config(
  cloud_name = CLOUDINARY_CLOUD_NAME,
  api_key = CLOUDINARY_API_KEY,
  api_secret = CLOUDINARY_API_SECRET
)

# --- Cấu hình WooCommerce ---
# Thay thế bằng thông tin API WooCommerce của bạn
WOO_API_URL = "http://localhost:8000/wp-json/wc/v3/products"
CONSUMER_KEY = "YOUR_WOO_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_WOO_CONSUMER_SECRET"

# URL ảnh Magento (Phải là URL mà script Python của bạn truy cập được)
MAGENTO_IMAGE_URL = "https://magento.test/pub/media/catalog/product/w/s/wsh05-yellow_main_1.jpg"