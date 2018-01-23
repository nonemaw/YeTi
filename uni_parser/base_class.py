class ScannerBase:
    def __init__(self, source_file, comment_tag):
        self.source_file = source_file
        self.comment_tag = comment_tag

    def accept(self):
        pass

    def look_ahead(self, nth: int):
        pass

    def move_ahead(self, nth: int):
        pass

    def get_token_type(self):
        pass

    def make_escape(self, char: str):
        pass

    def skip_space_comments(self):
        pass

    def get_token(self):
        pass

    def build_token(self):
        pass
