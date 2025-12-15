import pytest
from unittest.mock import patch, MagicMock
import logging
from requests.exceptions import HTTPError, ConnectionError

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from src.connectors.base_connector import BaseConnector

# Import lớp cần test
# (Thay thế 'base_connector' bằng tên file của bạn nếu khác)

# --- CÁC HẰNG SỐ VÀ SETUP CHUNG ---
BASE_URL = "http://api.test.com"
ENDPOINT = "users"
MOCK_TOKEN = "test_token_123"
SUCCESS_DATA = {"id": 1, "name": "Test User"}


# --- LỚP GIẢ LẬP RESPONSE ---
# Lớp này mô phỏng một đối tượng requests.Response
class MockResponse:
    """Giả lập đối tượng Response của requests."""

    def __init__(self, status_code, json_data=None, url=None):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.url = url or BASE_URL
        self.text = str(self._json_data)  # cần cho raise_for_status

    def json(self):
        """Trả về dữ liệu JSON giả lập."""
        return self._json_data

    def raise_for_status(self):
        """Mô phỏng raise_for_status() của requests."""
        if not 200 <= self.status_code < 300:
            # Raise HTTPError cho tất cả các mã lỗi không thành công khác 429/5xx
            raise HTTPError(f"Mock HTTP Error: {self.status_code} for URL: {self.url}")


# --- FIXTURES (CÀI ĐẶT MOCK TỰ ĐỘNG) ---

@pytest.fixture(autouse=True)
def mock_time_sleep():
    """Tự động giả lập time.sleep để tăng tốc độ kiểm thử."""
    # Chúng ta sử dụng 'time.sleep' để patch hàm gốc
    with patch('time.sleep', return_value=None) as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_logging():
    """Tự động giả lập logging để kiểm tra thông báo."""
    # Chúng ta patch cả warning và error
    with patch('logging.warning') as mock_warn, \
            patch('logging.error') as mock_error:
        yield mock_warn, mock_error


# --- KIỂM THỬ KHỞI TẠO (__init__) ---

def test_init_no_token():
    """Kiểm tra khởi tạo không có token."""
    connector = BaseConnector(BASE_URL)
    assert connector.base_url == BASE_URL  # Không có '/' ở cuối
    assert connector.token is None
    assert connector.headers == {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }


def test_init_with_token():
    """Kiểm tra khởi tạo có token và chuẩn hóa URL."""
    # Thử truyền URL có dấu '/' ở cuối
    connector = BaseConnector(BASE_URL + '/', token=MOCK_TOKEN)
    assert connector.base_url == BASE_URL
    assert connector.token == MOCK_TOKEN
    assert connector.headers['Authorization'] == f'Bearer {MOCK_TOKEN}'


# --- KIỂM THỬ THÀNH CÔNG ---

@patch('requests.request')
def test_success_on_first_attempt(mock_request):
    """Kiểm tra: Trả về thành công (200) ngay lần đầu tiên."""
    connector = BaseConnector(BASE_URL, token=MOCK_TOKEN)

    # Thiết lập mock_request để trả về thành công
    mock_request.return_value = MockResponse(200, json_data=SUCCESS_DATA)

    result = connector._make_request('GET', ENDPOINT, params={'limit': 10})

    # 1. Kiểm tra kết quả
    assert result == SUCCESS_DATA

    # 2. Kiểm tra lệnh gọi request
    mock_request.assert_called_once_with(
        'GET',
        f'{BASE_URL}/{ENDPOINT}',
        headers=connector.headers,
        params={'limit': 10},
        json=None,
        verify=False
    )


# --- KIỂM THỬ CƠ CHẾ THỬ LẠI (RETRY & BACKOFF) ---

@patch('requests.request')
def test_retry_on_rate_limit_then_success(mock_request, mock_time_sleep, mock_logging):
    """Kiểm tra: Lỗi 429 lần đầu, thành công ở lần thứ hai."""
    connector = BaseConnector(BASE_URL)

    # Thiết lập phản hồi cho từng lần gọi: 429 -> 200
    mock_request.side_effect = [
        MockResponse(429),  # Lần gọi 1: Rate Limit
        MockResponse(200, json_data={"status": "ok"})  # Lần gọi 2: Thành công
    ]

    result = connector._make_request('POST', ENDPOINT)

    # 1. Kiểm tra kết quả trả về
    assert result == {"status": "ok"}

    # 2. Kiểm tra số lần requests.request được gọi
    assert mock_request.call_count == 2

    # 3. Kiểm tra time.sleep được gọi (Exponential Backoff: 2**0 = 1s)
    mock_time_sleep.assert_called_once_with(1)

    # 4. Kiểm tra logging.warning được gọi cho lỗi 429
    mock_logging[0].assert_called_once()
    assert "Gặp lỗi 429" in mock_logging[0].call_args[0][0]


@patch('requests.request')
def test_retry_on_server_error_then_success(mock_request, mock_time_sleep, mock_logging):
    """Kiểm tra: Lỗi 500 lần đầu, thành công ở lần thứ hai."""
    connector = BaseConnector(BASE_URL)

    # Thiết lập phản hồi cho từng lần gọi: 500 -> 200
    mock_request.side_effect = [
        MockResponse(500),  # Lần gọi 1: Server Error
        MockResponse(200, json_data={"status": "resolved"})  # Lần gọi 2: Thành công
    ]

    result = connector._make_request('GET', ENDPOINT)

    # 1. Kiểm tra kết quả trả về
    assert result == {"status": "resolved"}

    # 2. Kiểm tra time.sleep được gọi (2**0 = 1s)
    mock_time_sleep.assert_called_once_with(1)

    # 3. Kiểm tra logging.warning được gọi cho lỗi 500
    assert "Gặp lỗi 500" in mock_logging[0].call_args[0][0]


@patch('requests.request')
def test_max_retries_fail_with_429(mock_request, mock_time_sleep, mock_logging):
    """Kiểm tra: Thất bại sau khi vượt quá 3 lần thử Rate Limit."""
    connector = BaseConnector(BASE_URL)

    # Thiết lập phản hồi: Luôn là 429 cho 3 lần thử
    mock_request.side_effect = [MockResponse(429)] * 3

    result = connector._make_request('GET', ENDPOINT, retries=3)

    # 1. Kiểm tra kết quả trả về
    assert result is None

    # 2. Kiểm tra số lần requests.request được gọi
    assert mock_request.call_count == 3

    # 3. Kiểm tra time.sleep được gọi 2 lần (sau lần 1: 2**0=1s; sau lần 2: 2**1=2s)
    mock_time_sleep.assert_any_call(1)
    mock_time_sleep.assert_any_call(2)
    assert mock_time_sleep.call_count == 3

    # 4. Kiểm tra logging.error được gọi cho thất bại cuối cùng
    mock_logging[1].assert_called_once()
    assert "Thất bại sau 3 lần thử" in mock_logging[1].call_args[0][0]


# --- KIỂM THỬ XỬ LÝ LỖI KHÔNG THỬ LẠI (NON-RETRY ERRORS) ---

@patch('requests.request')
def test_non_retry_error_404(mock_request):
    """Kiểm tra: Lỗi HTTP 404 (Không thử lại, raise lỗi ngay lập tức)."""
    connector = BaseConnector(BASE_URL)

    # Thiết lập phản hồi: 404
    mock_request.return_value = MockResponse(404)

    # Kiểm tra ngoại lệ được raise
    with pytest.raises(HTTPError) as excinfo:
        connector._make_request('GET', ENDPOINT)

    # Kiểm tra lỗi là 404
    assert "404" in str(excinfo.value)

    # Kiểm tra chỉ gọi 1 lần
    assert mock_request.call_count == 1


@patch('requests.request')
def test_non_retry_error_401(mock_request):
    """Kiểm tra: Lỗi HTTP 401 (Không thử lại, raise lỗi ngay lập tức)."""
    connector = BaseConnector(BASE_URL)

    # Thiết lập phản hồi: 401 Unauthorized
    mock_request.return_value = MockResponse(401)

    # Kiểm tra ngoại lệ được raise
    with pytest.raises(HTTPError):
        connector._make_request('GET', ENDPOINT)

    assert mock_request.call_count == 1


# --- KIỂM THỬ NGOẠI LỆ KẾT NỐI (REQUESTS EXCEPTIONS) ---

@patch('requests.request')
def test_connection_error_retry_and_fail(mock_request, mock_time_sleep, mock_logging):
    """Kiểm tra: Lỗi kết nối (ConnectionError) được thử lại và cuối cùng thất bại."""
    connector = BaseConnector(BASE_URL)

    # Thiết lập: Luôn raise ConnectionError
    mock_request.side_effect = ConnectionError("Mock connection failed")

    result = connector._make_request('GET', ENDPOINT, retries=2)  # Đặt retries = 2

    # 1. Kiểm tra kết quả trả về
    assert result is None

    # 2. Kiểm tra số lần requests.request được gọi (2 lần)
    assert mock_request.call_count == 2

    # 3. Kiểm tra time.sleep được gọi (sau lần 1: 2**0=1s; sau lần 2 không gọi vì đã hết lần thử)
    mock_time_sleep.assert_called_once_with(1)

    # 4. Kiểm tra logging.error được gọi cho mỗi lần thất bại request
    assert mock_logging[1].call_count == 2
    assert "Request failed: Mock connection failed" in mock_logging[1].call_args_list[0][0][0]

    # 5. Kiểm tra logging.error cuối cùng được gọi (thông báo thất bại)
    assert "Thất bại sau 2 lần thử" in mock_logging[1].call_args[0][0]