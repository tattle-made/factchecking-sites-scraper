from lxml.html import fromstring
from lxml.html import HtmlElement

# Add site specific parsers
from parser_altnews import get_post_altnews
from parser_vishvasnews import get_post_vishvasnews
from parser_quint import get_post_quint


class ArticleParser:
    def __init__(self, domain: str):
        super().__init__()

        self.log_adapter = None

        self.parser = None

        if "altnews" in domain:
            self.parser = get_post_altnews
        elif "vishvasnews" in domain:
            self.parser = get_post_vishvasnews
        elif "thequint" in domain:
            self.parser = get_post_quint

    def get_tree(self, post_file_path: str) -> HtmlElement:
        """
        Get tree from html

        Args:
            post_file_path: str

        Returns: lxml.html.HtmlElement

        """

        with open(post_file_path, "r") as file:
            html = file.read()

        tree = fromstring(html)

        return tree
