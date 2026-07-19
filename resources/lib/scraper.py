import os
import re
from urllib.parse import urljoin

from resources.lib.network import Network
from resources.lib.parser import DirectoryParser


class Scraper:

    BASE_URL = "https://berlin.saymyname.website/"

    def __init__(self):
        self.network = Network()

    def _parse(self, url):
        html = self.network.get(url)

        parser = DirectoryParser()
        parser.feed(html)

        return parser.items

    def get_years(self):

        url = urljoin(self.BASE_URL, "Movies/")

        items = self._parse(url)

        years = []

        for item in items:

            href = item["href"]

            if href in ("../", "/", ""):
                continue

            folder = href.strip("/")

            if folder.isdigit() and len(folder) == 4:

                years.append({
                    "label": folder,
                    "url": urljoin(url, href)
                })

        years.sort(
            key=lambda x: x["label"],
            reverse=True
        )

        return years

    def get_movie_folders(self, year_url):

        items = self._parse(year_url)

        movies = []

        for item in items:

            href = item["href"]

            if href == "../":
                continue

            folder = href.strip("/")

            if not folder.isdigit():
                continue

            movie_url = urljoin(year_url, href)

            title = self._guess_movie_title(movie_url)

            movies.append({
                "label": title,
                "url": movie_url
            })

        movies.sort(key=lambda x: x["label"])

        return movies

    def _guess_movie_title(self, movie_url):

        try:

            items = self._parse(movie_url)

            for item in items:

                name = item["text"]

                if not name.lower().endswith((".mkv", ".mp4", ".avi")):
                    continue

                return self._filename_to_title(name)

        except Exception:
            pass

        return os.path.basename(movie_url.rstrip("/"))

    def _filename_to_title(self, filename):

        filename = os.path.splitext(filename)[0]

        filename = re.sub(
            r'\.(480p|720p|1080p|2160p).*',
            '',
            filename,
            flags=re.IGNORECASE
        )

        filename = filename.replace(".", " ")

        return filename.strip()

    def get_video_files(self, movie_url):

        items = self._parse(movie_url)

        videos = []

        for item in items:

            name = item["text"]

            if not name.lower().endswith((".mkv", ".mp4", ".avi")):
                continue

            videos.append({
                "label": name,
                "url": urljoin(movie_url, item["href"])
            })

        return videos