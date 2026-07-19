from html.parser import HTMLParser


class DirectoryParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self.items = []

        self._href = None
        self._text = ""

        self._inside_a = False
        self._inside_code = False

    def handle_starttag(self, tag, attrs):

        if tag == "a":

            self._inside_a = True
            self._href = None
            self._text = ""

            for k, v in attrs:
                if k == "href":
                    self._href = v

        elif tag == "code":
            self._inside_code = True

    def handle_endtag(self, tag):

        if tag == "code":
            self._inside_code = False

        elif tag == "a":

            if self._href:

                self.items.append({
                    "href": self._href.strip(),
                    "text": self._text.strip()
                })

            self._inside_a = False
            self._href = None
            self._text = ""

    def handle_data(self, data):

        if self._inside_a and self._inside_code:

            self._text += data