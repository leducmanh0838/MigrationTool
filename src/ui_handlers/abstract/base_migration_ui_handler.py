from abc import ABC


class BaseMigrationUIHandler:
    def info(self, message: str): pass

    def success(self, message: str): pass

    def warning(self, message: str): pass

    def error(self, message: str, error_detail: str = ""): pass

    def track_progress(self, name: str, total: int): pass  # Trả về context progress

    def finish_migration(self, summary_data: list): pass
