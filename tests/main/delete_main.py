import woocommerce
import json
import logging
import time

# --- CẤU HÌNH API WOOCOMMERCE ---
WOO_URL = "http://localhost:8000"
WOO_KEY = "ck_f69bcf35f88017f32a096029a21964f363280112"
WOO_SECRET = "cs_cfa9bdad76571d91354c6e6249ad81ef297904ef"
# ---------------------------------

# Cấu hình Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def initialize_wcapi():
    """Khởi tạo đối tượng WC API."""
    try:
        wcapi = woocommerce.API(
            url=WOO_URL,
            consumer_key=WOO_KEY,
            consumer_secret=WOO_SECRET,
            wp_api=True,  # Bắt buộc nếu URL là Wordpress Root
            version="wc/v3",
            timeout=30  # Tăng timeout để tránh lỗi khi xử lý số lượng lớn
        )
        return wcapi
    except Exception as e:
        logging.error(f"Lỗi khởi tạo WC API: {e}")
        return None


def get_all_product_ids(wcapi):
    """Lấy tất cả ID sản phẩm (bao gồm cả draft/private)"""
    product_ids = []
    page = 1
    # WooCommerce API giới hạn 100 sản phẩm/trang.
    per_page = 100

    logging.info("Bắt đầu lấy danh sách ID sản phẩm...")

    while True:
        try:
            # Lấy 100 sản phẩm mỗi lần, bao gồm cả các trạng thái khác 'publish'
            response = wcapi.get("products", params={'per_page': per_page, 'page': page, 'status': 'any'})

            if response.status_code != 200:
                logging.error(f"Lỗi khi lấy dữ liệu (trang {page}): {response.status_code} - {response.text}")
                break

            products = response.json()

            if not products:
                # Dừng khi không còn sản phẩm nào nữa
                break

            # Trích xuất ID
            ids = [product['id'] for product in products]
            product_ids.extend(ids)

            logging.info(f"Đã lấy ID của {len(product_ids)} sản phẩm (trang {page}).")
            page += 1
            # Tạm dừng ngắn để tránh quá tải server (Rate Limit)
            time.sleep(0.5)

        except Exception as e:
            logging.error(f"Lỗi trong quá trình lấy ID sản phẩm: {e}")
            break

    logging.info(f"Tổng cộng đã lấy được {len(product_ids)} ID sản phẩm.")
    return product_ids


def get_all_category_ids(wcapi):
    """Lấy tất cả ID danh mục sản phẩm"""
    category_ids = []
    page = 1
    # Thiết lập số lượng danh mục tối đa trên mỗi trang (Max là 100)
    per_page = 100

    # Định nghĩa endpoint
    endpoint = "products/categories"

    logging.info(f"Bắt đầu lấy danh sách ID danh mục từ endpoint: {endpoint}...")

    try:
        while True:
            # Tham số để lấy dữ liệu
            params = {
                "per_page": per_page,
                "page": page
            }

            logging.info(f"-> Đang lấy danh mục (trang {page}, số lượng {per_page})...")

            # Thực hiện lời gọi API, truyền cả per_page và page
            response = wcapi.get(endpoint, params=params)

            if response.status_code != 200:
                logging.error(f"Lỗi khi lấy dữ liệu (trang {page}): {response.status_code} - {response.text}")
                # Thoát vòng lặp nếu có lỗi API
                break

            categories = response.json()

            # Kiểm tra xem có dữ liệu trả về không
            if not categories:
                logging.info(f"Không còn danh mục nào ở trang {page}. Dừng lấy dữ liệu.")
                break  # Dừng vòng lặp khi không còn danh mục

            # Trích xuất ID
            ids = [category['id'] for category in categories]
            category_ids.extend(ids)

            logging.info(f"Đã lấy thêm {len(ids)} ID danh mục. Tổng cộng: {len(category_ids)} ID.")

            # Tăng số trang để lấy dữ liệu tiếp theo
            page += 1

            # Tạm dừng ngắn để tránh quá tải server (Rate Limit)
            time.sleep(0.5)

    except Exception as e:
        logging.error(f"Lỗi trong quá trình lấy ID danh mục: {e}")

    logging.info(f"Tổng cộng đã lấy được {len(category_ids)} ID danh mục.")
    return category_ids


def get_all_entity_ids(wcapi, endpoint):
    """Lấy tất cả ID danh mục sản phẩm"""
    ids = []
    page = 1
    # Thiết lập số lượng danh mục tối đa trên mỗi trang (Max là 100)
    per_page = 100

    logging.info(f"Bắt đầu lấy danh sách ID danh mục từ endpoint: {endpoint}...")

    try:
        while True:
            # Tham số để lấy dữ liệu
            params = {
                "per_page": per_page,
                "page": page
            }

            logging.info(f"-> Đang lấy danh mục (trang {page}, số lượng {per_page})...")

            # Thực hiện lời gọi API, truyền cả per_page và page
            response = wcapi.get(endpoint, params=params)

            if response.status_code != 200:
                logging.error(f"Lỗi khi lấy dữ liệu (trang {page}): {response.status_code} - {response.text}")
                # Thoát vòng lặp nếu có lỗi API
                break

            items = response.json()

            # Kiểm tra xem có dữ liệu trả về không
            if not items:
                logging.info(f"Không còn danh mục nào ở trang {page}. Dừng lấy dữ liệu.")
                break  # Dừng vòng lặp khi không còn danh mục

            # Trích xuất ID
            ids = [item['id'] for item in items]
            ids.extend(ids)

            logging.info(f"Đã lấy thêm {len(ids)} ID danh mục. Tổng cộng: {len(ids)} ID.")

            # Tăng số trang để lấy dữ liệu tiếp theo
            page += 1

            # Tạm dừng ngắn để tránh quá tải server (Rate Limit)
            time.sleep(0.5)

    except Exception as e:
        logging.error(f"Lỗi trong quá trình lấy ID danh mục: {e}")

    logging.info(f"Tổng cộng đã lấy được {len(ids)} ID danh mục.")
    return ids


def delete_items_in_batches(wcapi, endpoint, ids):
    """Xóa các sản phẩm theo lô (batch)."""
    if not ids:
        logging.info("Không có thể loại nào để xóa.")
        return

    # API hỗ trợ xóa tối đa 100 mục trong một yêu cầu DELETE batch.
    batch_size = 50
    deleted_count = 0
    total_to_delete = len(ids)

    logging.warning(f"BẮT ĐẦU XÓA TỔNG SỐ {total_to_delete} SẢN PHẨM VĨNH VIỄN (FORCE=TRUE)!")

    for i in range(0, total_to_delete, batch_size):
        batch = ids[i:i + batch_size]

        # Cấu trúc dữ liệu cho yêu cầu xóa hàng loạt (batch delete)
        data = {
            "delete": batch
        }

        try:
            # Gửi yêu cầu DELETE batch
            # force=true: xóa vĩnh viễn, không vào thùng rác
            response = wcapi.post(f"{endpoint}/batch?force=true", data)

            if response.status_code == 200:
                result = response.json()
                successful_deletes = len(result.get('delete', []))
                deleted_count += successful_deletes

                logging.info(
                    f"Đã xóa thành công lô #{i // batch_size + 1} ({successful_deletes}/{len(batch)} sản phẩm).")

                # Kiểm tra các lỗi riêng lẻ trong lô
                if result.get('errors'):
                    logging.warning(f"Có {len(result['errors'])} lỗi trong lô này. Chi tiết: {result['errors']}")

            else:
                logging.error(f"Lỗi khi gửi yêu cầu xóa lô: {response.status_code} - {response.text}")

            # Tạm dừng giữa các lô để đảm bảo ổn định
            time.sleep(1)

        except Exception as e:
            logging.error(f"Lỗi nghiêm trọng trong quá trình xóa lô: {e}")
            break

    logging.info(f"--- HOÀN TẤT QUÁ TRÌNH XÓA ---")
    logging.info(f"Tổng cộng đã xóa thành công {deleted_count} thể loại.")


def delete_products_in_batches(wcapi, product_ids):
    """Xóa các sản phẩm theo lô (batch)."""
    if not product_ids:
        logging.info("Không có sản phẩm nào để xóa.")
        return

    # API hỗ trợ xóa tối đa 100 mục trong một yêu cầu DELETE batch.
    batch_size = 50
    deleted_count = 0
    total_to_delete = len(product_ids)

    logging.warning(f"BẮT ĐẦU XÓA TỔNG SỐ {total_to_delete} SẢN PHẨM VĨNH VIỄN (FORCE=TRUE)!")

    for i in range(0, total_to_delete, batch_size):
        batch = product_ids[i:i + batch_size]

        # Cấu trúc dữ liệu cho yêu cầu xóa hàng loạt (batch delete)
        data = {
            "delete": batch
        }

        try:
            # Gửi yêu cầu DELETE batch
            # force=true: xóa vĩnh viễn, không vào thùng rác
            response = wcapi.post("products/batch?force=true", data)

            if response.status_code == 200:
                result = response.json()
                successful_deletes = len(result.get('delete', []))
                deleted_count += successful_deletes

                logging.info(
                    f"Đã xóa thành công lô #{i // batch_size + 1} ({successful_deletes}/{len(batch)} sản phẩm).")

                # Kiểm tra các lỗi riêng lẻ trong lô
                if result.get('errors'):
                    logging.warning(f"Có {len(result['errors'])} lỗi trong lô này. Chi tiết: {result['errors']}")

            else:
                logging.error(f"Lỗi khi gửi yêu cầu xóa lô: {response.status_code} - {response.text}")

            # Tạm dừng giữa các lô để đảm bảo ổn định
            time.sleep(1)

        except Exception as e:
            logging.error(f"Lỗi nghiêm trọng trong quá trình xóa lô: {e}")
            break

    logging.info(f"--- HOÀN TẤT QUÁ TRÌNH XÓA ---")
    logging.info(f"Tổng cộng đã xóa thành công {deleted_count} sản phẩm.")


def delete_categories_in_batches(wcapi, categories_ids):
    """Xóa các sản phẩm theo lô (batch)."""
    if not categories_ids:
        logging.info("Không có thể loại nào để xóa.")
        return

    # API hỗ trợ xóa tối đa 100 mục trong một yêu cầu DELETE batch.
    batch_size = 50
    deleted_count = 0
    total_to_delete = len(categories_ids)

    logging.warning(f"BẮT ĐẦU XÓA TỔNG SỐ {total_to_delete} SẢN PHẨM VĨNH VIỄN (FORCE=TRUE)!")

    for i in range(0, total_to_delete, batch_size):
        batch = categories_ids[i:i + batch_size]

        # Cấu trúc dữ liệu cho yêu cầu xóa hàng loạt (batch delete)
        data = {
            "delete": batch
        }

        try:
            # Gửi yêu cầu DELETE batch
            # force=true: xóa vĩnh viễn, không vào thùng rác
            response = wcapi.post("products/categories/batch?force=true", data)

            if response.status_code == 200:
                result = response.json()
                successful_deletes = len(result.get('delete', []))
                deleted_count += successful_deletes

                logging.info(
                    f"Đã xóa thành công lô #{i // batch_size + 1} ({successful_deletes}/{len(batch)} sản phẩm).")

                # Kiểm tra các lỗi riêng lẻ trong lô
                if result.get('errors'):
                    logging.warning(f"Có {len(result['errors'])} lỗi trong lô này. Chi tiết: {result['errors']}")

            else:
                logging.error(f"Lỗi khi gửi yêu cầu xóa lô: {response.status_code} - {response.text}")

            # Tạm dừng giữa các lô để đảm bảo ổn định
            time.sleep(1)

        except Exception as e:
            logging.error(f"Lỗi nghiêm trọng trong quá trình xóa lô: {e}")
            break

    logging.info(f"--- HOÀN TẤT QUÁ TRÌNH XÓA ---")
    logging.info(f"Tổng cộng đã xóa thành công {deleted_count} thể loại.")


def main():
    """Hàm chính thực thi quy trình xóa sản phẩm."""
    wcapi = initialize_wcapi()
    if not wcapi:
        return

    # 1. Lấy tất cả ID sản phẩm
    product_ids = get_all_product_ids(wcapi)

    if not product_ids:
        logging.info("Không có sản phẩm nào được tìm thấy. Kết thúc.")
        return

    # Bỏ comment 2 dòng dưới nếu bạn muốn xác nhận trước khi xóa
    # user_input = input(f"Bạn có chắc chắn muốn xóa vĩnh viễn {len(product_ids)} sản phẩm không? (gõ YES để tiếp tục): ")
    # if user_input.upper() != 'YES':
    #     logging.info("Người dùng hủy bỏ. Kết thúc.")
    #     return

    # 2. Xóa sản phẩm theo lô
    delete_products_in_batches(wcapi, product_ids)


if __name__ == "__main__":
    wcapi = initialize_wcapi()
    endpoints = ["products", "products/categories", "customers", "order"]
    # endpoints = ["orders"]
    for endpoint in endpoints:
        ids = get_all_entity_ids(wcapi, endpoint)
        delete_items_in_batches(wcapi, endpoint, ids)
    # ids = get_all_category_ids(wcapi)
    # # print(ids)
    # delete_categories_in_batches(wcapi, ids)
    # main()