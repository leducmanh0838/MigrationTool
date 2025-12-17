import pathlib
from anytree import Node, RenderTree


def build_project_tree(path_obj, parent_node, excludes):
    """
    Hàm đệ quy để duyệt thư mục và xây dựng Node AnyTree.

    Args:
        path_obj (pathlib.Path): Đối tượng Path hiện tại.
        parent_node (anytree.Node): Node cha trong cây AnyTree.
        excludes (set): Tập hợp các tên file/thư mục cần loại trừ.
    """

    # Duyệt qua các mục con trong thư mục hiện tại
    for entry in sorted(path_obj.iterdir()):

        # 1. Loại trừ các file/thư mục không mong muốn
        if entry.name in excludes or entry.name.startswith('.'):
            continue

        # 2. Xử lý Thư mục con
        if entry.is_dir():
            # Tạo node mới cho thư mục (thêm / vào tên)
            current_node = Node(entry.name + '/', parent=parent_node)

            # Gọi đệ quy để xử lý thư mục con
            build_project_tree(entry, current_node, excludes)

        # 3. Xử lý File
        else:
            # Tạo node cho file
            Node(entry.name, parent=parent_node)


def print_project_tree(start_path, excludes=None):
    """
    Hàm chính để bắt đầu quá trình xây dựng và in cây.
    """
    if excludes is None:
        excludes = {'.venv', '__pycache__', '.git', '.idea', 'requirements.txt'}

    root_path = pathlib.Path(start_path)
    if not root_path.exists():
        print(f"Lỗi: Không tìm thấy thư mục gốc tại {start_path}")
        return None

    # Khởi tạo node gốc
    root = Node(root_path.name)

    # Bắt đầu quá trình xây dựng cây đệ quy
    build_project_tree(root_path, root, set(excludes))

    # In cấu trúc
    for pre, fill, node in RenderTree(root):
        print(f"{pre}{node.name}")

    return root


# --- THỰC THI (Giữ nguyên phần này) ---
START_DIR = '.'
CUSTOM_EXCLUDES = {
    '.venv',
    '__pycache__',
    '.git',
    '.idea',
    'requirements.txt',
    # Các thư mục riêng của bạn (tôi tạm loại trừ tests và .idea để sơ đồ ngắn hơn)
    'tests',
    'main.py',
}

# Thay thế project_root = build_project_tree(...) bằng print_project_tree(...)
# vì hàm này giờ đã đảm nhận cả việc in ra
print_project_tree(START_DIR, excludes=CUSTOM_EXCLUDES)