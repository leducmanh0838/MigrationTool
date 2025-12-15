import requests
import woocommerce
import os

# --- CẤU HÌNH API WOOCOMMERCE (Sử dụng cấu hình của bạn) ---
WOO_URL = "http://localhost:8000"
WOO_KEY = "leducmanh0838@gmail.com"
WOO_SECRET = "oVvY wL2n XrIs 27ke VJug HVhJ"

# --- THÔNG TIN CẦN THAY ĐỔI ---
PRODUCT_ID = 99  # Thay bằng ID sản phẩm thực tế của bạn
IMAGE_FILE_PATH = "./image.jpg"  # Thay bằng đường dẫn đến file ảnh cục bộ


# --- 1. Tải ảnh lên WordPress Media (Sử dụng requests) ---
def upload_image_to_media(file_path, base_url, consumer_key, consumer_secret):
    """Tải file ảnh lên thư viện media và trả về ID của ảnh."""

    # 1.1 Cấu hình cho WordPress Media API
    media_endpoint = f"{base_url}/wp-json/wp/v2/media"

    # Lấy tên file
    file_name = os.path.basename(file_path)

    # Định nghĩa headers (bắt buộc)
    # Basic Auth được xử lý bằng tham số auth trong requests, nên chỉ cần headers cho Content-Disposition
    headers = {
        # Đặt tên file để WordPress nhận dạng
        "Content-Disposition": f"attachment; filename={file_name}",
        # Chỉ định loại nội dung (cần chính xác loại file)
        "Content-Type": "image/jpeg" if file_name.lower().endswith(('.jpg', '.jpeg')) else "image/png"
    }

    # Đọc nội dung file ảnh dưới dạng nhị phân
    with open(file_path, 'rb') as f:
        image_data = f.read()

    print(f"-> Bắt đầu tải lên file: {file_name}")

    try:
        response = requests.post(
            media_endpoint,
            headers=headers,
            data=image_data,
            # Xác thực Cơ bản HTTP
            auth=(consumer_key, consumer_secret)
        )
        response.raise_for_status()  # Báo lỗi nếu mã trạng thái là 4xx hoặc 5xx

        media_info = response.json()
        image_id = media_info.get('id')

        print(f"-> Tải lên thành công! Image ID: {image_id}")
        return image_id

    except requests.exceptions.HTTPError as e:
        print(f"!!! Lỗi HTTP khi tải ảnh lên: {e}")
        print(f"Chi tiết lỗi từ phản hồi: {response.json().get('message')}")
        return None
    except Exception as e:
        print(f"!!! Lỗi không xác định khi tải ảnh lên: {e}")
        return None


# --- 2. Gán ảnh cho sản phẩm (Sử dụng python-woocommerce) ---
def assign_image_to_product(product_id, image_id, base_url, consumer_key, consumer_secret):
    """Gán ID ảnh đã tải lên làm ảnh đại diện cho sản phẩm."""

    if not image_id:
        print("Không có ID ảnh để gán. Bỏ qua bước cập nhật sản phẩm.")
        return

    # Khởi tạo đối tượng WC API
    wcapi = woocommerce.API(
        url=base_url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        wp_api=True,  # Bắt buộc phải là True cho các phiên bản mới của WC
        version="wc/v3"
    )

    # Dữ liệu cập nhật sản phẩm: Đặt ảnh mới vào vị trí đầu tiên (position: 0)
    data = {
        "images": [
            {
                "id": image_id,
                "position": 0  # Đặt làm ảnh đại diện
            }
        ]
    }

    print(f"-> Bắt đầu cập nhật sản phẩm {product_id} với Image ID {image_id}...")

    try:
        response = wcapi.put(f"products/{product_id}", data)
        # response là một dictionary

        print("-> Cập nhật sản phẩm thành công!")
        print(f"Xem sản phẩm đã cập nhật: {response.get('permalink')}")

    except Exception as e:
        print(f"!!! Lỗi khi cập nhật sản phẩm: {e}")


# --- THỰC THI CHÍNH ---
if __name__ == "__main__":

    # Kiểm tra sự tồn tại của file ảnh
    if not os.path.exists(IMAGE_FILE_PATH):
        print(f"!!! Lỗi: Không tìm thấy file ảnh tại đường dẫn: {IMAGE_FILE_PATH}")
    else:
        # Bước 1: Tải ảnh lên
        uploaded_id = upload_image_to_media(
            IMAGE_FILE_PATH,
            WOO_URL,
            WOO_KEY,
            WOO_SECRET
        )

        # Bước 2: Gán ảnh cho sản phẩm
        if uploaded_id:
            assign_image_to_product(
                PRODUCT_ID,
                uploaded_id,
                WOO_URL,
                WOO_KEY,
                WOO_SECRET
            )