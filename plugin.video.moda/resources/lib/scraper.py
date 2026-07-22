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

    def get_movie_ids(self, year_url):

        items = self._parse(year_url)

        movies = []

        year = os.path.basename(
            year_url.rstrip("/")
        )

        for item in items:

            href = item["href"]

            if href == "../":
                continue

            folder = href.strip("/")

            if not folder.isdigit():
                continue

            movie_url = urljoin(
                year_url,
                href
            )

            movies.append({
                "id": folder,
                "year": year,
                "url": movie_url
            })

        return movies
    def get_movie_info(self, movie):

        title = self._guess_movie_title(
            movie["url"]
        )

        return {
            "id": movie["id"],
            "label": title,
            "year": movie["year"],
            "url": movie["url"]
        }

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

            movie = {
                "id": folder,
                "url": urljoin(year_url, href)
            }

            movies.append(
                self.get_movie_info(movie)
            )

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

        # حذف پسوند فایل
        name = os.path.splitext(filename)[0]

        # پیدا کردن اولین سال معتبر
        match = re.search(r"(19\d{2}|20\d{2})", name)

        if not match:

            name = re.sub(r"[._+\-]+", " ", name)

            return re.sub(r"\s+", " ", name).strip()

        year = match.group(1)

        # فقط قسمت قبل از سال
        title = name[:match.start()]

        # تبدیل جداکننده‌ها به فاصله
        title = re.sub(r"[._+\-]+", " ", title)

        # حذف فاصله‌های اضافی
        title = re.sub(r"\s+", " ", title).strip()

        return f"{title} ({year})"

    def get_video_files(self, movie_url):

        items = self._parse(movie_url)

        videos = []

        for item in items:

            name = item["text"]

            if not name.lower().endswith((".mkv", ".mp4", ".avi")):
                continue

            lower = name.lower()

            # کیفیت
            quality = ""

            for q in ("2160p", "1080p", "720p", "480p"):
                if q in lower:
                    quality = q.upper()
                    break

            # کدک
            codec = ""
            if "x265" in lower or "hevc" in lower:
                codec = " x265"

            # ریلیز
            release = ""

            if ".psa." in lower:
                release = "PSA"
            elif ".yify." in lower:
                release = "YIFY"
            elif ".pahe." in lower:
                release = "Pahe"

            label = quality + codec

            if release:
                label += " (" + release + ")"

            videos.append({
                "label": label,
                "url": urljoin(movie_url, item["href"])
            })

        return videos