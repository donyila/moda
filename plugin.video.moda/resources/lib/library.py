import os
import json

import xbmc
import xbmcgui
import xbmcvfs
import xml.etree.ElementTree as ET
from resources.lib.database import KodiDatabase
from resources.lib.scraper import Scraper


class LibraryManager:

    def __init__(self):

        self.scraper = Scraper()

        self.profile = xbmcvfs.translatePath(
            "special://profile/addon_data/plugin.video.moda/"
        )

        self.library = xbmcvfs.translatePath(
            "special://profile/MODA Library/Movies/"
        )

        # ایجاد پوشه‌ها در صورت عدم وجود
        xbmcvfs.mkdirs(self.profile)
        xbmcvfs.mkdirs(self.library)

        self.cache = os.path.join(
            self.profile,
            "cache.json"
        )

        self.sources = xbmcvfs.translatePath(
            "special://profile/sources.xml"
        )

        # ایجاد فایل cache.json در اولین اجرا
        if not xbmcvfs.exists(self.cache):
            with open(self.cache, "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4)

    def load_cache(self):

        with open(self.cache, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_cache(self, cache):

        with open(self.cache, "w", encoding="utf-8") as f:
            json.dump(
                cache,
                f,
                indent=4,
                ensure_ascii=False
            )

    def build_plugin_url(self, movie):

        return (
            f"plugin://plugin.video.moda/"
            f"?action=quality"
            f"&id={movie['id']}"
            f"&url={movie['url']}"
        )

    def create_strm(self, movie):

        title = movie["label"]

        filename = os.path.join(
            self.library,
            title + ".strm"
        )

        with open(filename, "w", encoding="utf-8") as f:
            f.write(
                self.build_plugin_url(movie)
            )

    def remove_strm(self, movie):

        filename = os.path.join(
            self.library,
            movie["label"] + ".strm"
        )

        if os.path.exists(filename):
            os.remove(filename)

    def sync_library(self):

        self.ensure_sources_file()

        added = self.ensure_moda_source()

        KodiDatabase().ensure_movies_content(
            self.library
        )

        if added:

            xbmcgui.Dialog().notification(
                "MODA",
                "Library source added.\nRestart Kodi once.",
                xbmcgui.NOTIFICATION_INFO,
                6000
            )

        progress = xbmcgui.DialogProgressBG()

        progress.create(
            "MODA",
            "Updating Library..."
        )

        created = 0

        cache = self.load_cache()

        years = self.scraper.get_years()

        if not years:

            progress.close()

            xbmcgui.Dialog().notification(
                "MODA",
                "No years found.",
                xbmcgui.NOTIFICATION_ERROR,
                4000
            )

            return 0


        all_movies = []

        for year in years:

            all_movies.extend(
                self.scraper.get_movie_ids(
                    year["url"]
                )
            )


        total_movies = len(all_movies)


        if total_movies == 0:

            progress.close()

            xbmcgui.Dialog().notification(
                "MODA",
                "No movies found.",
                xbmcgui.NOTIFICATION_ERROR,
                4000
            )

            return 0


        for index, movie in enumerate(all_movies):

            percent = int(
                ((index + 1) / total_movies) * 100
            )


            # اگر قبلاً ساخته شده، رد شو
            if movie["id"] in cache:

                progress.update(
                    percent,
                    "Updating Library...",
                    f"Processed: {index + 1}/{total_movies}    New: {created}"
                )

                continue

            try:

                info = self.scraper.get_movie_info(movie)

                self.create_strm(info)

                created += 1

                cache[movie["id"]] = {
                    "title": info["label"]
                }

            except Exception as e:

                xbmc.log(
                    f"[MODA] {movie['id']} : {e}",
                    xbmc.LOGERROR
                )

                continue

            progress.update(
                percent,
                "Updating Library...",
                f"Processed: {index + 1}/{total_movies}    New: {created}"
            )

        if created > 0:

            self.save_cache(cache)

        progress.close()


        xbmcgui.Dialog().notification(
            "MODA",
            f"{created} new movies added.",
            xbmcgui.NOTIFICATION_INFO,
            4000
        )


        return created

    def ensure_sources_file(self):

        if os.path.exists(self.sources):
            return

        root = ET.Element("sources")

        ET.SubElement(root, "programs")
        ET.SubElement(root, "video")
        ET.SubElement(root, "music")
        ET.SubElement(root, "pictures")
        ET.SubElement(root, "files")

        tree = ET.ElementTree(root)

        tree.write(
            self.sources,
            encoding="utf-8",
            xml_declaration=True
        )

    def ensure_moda_source(self):

        self.ensure_sources_file()

        tree = ET.parse(self.sources)

        root = tree.getroot()

        video = root.find("video")

        if video is None:
            video = ET.SubElement(root, "video")

        # آیا قبلاً اضافه شده؟
        for source in video.findall("source"):

            name = source.find("name")

            if (
                name is not None and
                name.text == "MODA Library"
            ):
                return False

        source = ET.SubElement(video, "source")

        ET.SubElement(
            source,
            "name"
        ).text = "MODA Library"

        ET.SubElement(
            source,
            "path",
            pathversion="1"
        ).text = self.library

        ET.SubElement(
            source,
            "allowsharing"
        ).text = "true"

        tree.write(
            self.sources,
            encoding="utf-8",
            xml_declaration=True
        )

        return True