import os
import xbmcvfs
import sys
from urllib.parse import parse_qsl
from urllib.parse import quote_plus

import xbmcplugin
import xbmcgui
import xbmc

from resources.lib.scraper import Scraper
from resources.lib.library import LibraryManager


class Router:

    def __init__(self):

        self.handle = int(sys.argv[1])

        if len(sys.argv) > 2:
            self.params = dict(parse_qsl(sys.argv[2][1:]))
        else:
            self.params = {}

        self.scraper = Scraper()
        self.library = LibraryManager()
        self.profile = xbmcvfs.translatePath(
        "special://profile/addon_data/plugin.video.moda/"
        )

        os.makedirs(self.profile, exist_ok=True)

    def run(self):

        action = self.params.get("action")

        try:

            if action is None:
                self.root()

            elif action == "years":
                self.show_years()

            elif action == "movies":
                self.show_movies()

            elif action == "quality":
                self.show_quality()

            elif action == "play":
                self.play()

            elif action == "sync":
                self.sync_library()

        except RuntimeError as e:

            message = str(e)

            xbmc.log(
                f"[MODA] {message}",
                xbmc.LOGERROR
            )

            xbmcgui.Dialog().notification(
                "MODA",
                message,
                xbmcgui.NOTIFICATION_ERROR,
                5000
            )

        except Exception as e:

            xbmc.log(
                f"[MODA] Unexpected Error: {e}",
                xbmc.LOGERROR
            )

            xbmcgui.Dialog().notification(
                "MODA",
                "Unexpected error.",
                xbmcgui.NOTIFICATION_ERROR,
                5000
            )

    def root(self):

        li = xbmcgui.ListItem("Movies")

        url = (
            sys.argv[0]
            + "?action=years"
        )

        xbmcplugin.addDirectoryItem(
            self.handle,
            url,
            li,
            True
        )

        li = xbmcgui.ListItem("Update Library")

        url = (
            sys.argv[0]
            + "?action=sync"
        )

        xbmcplugin.addDirectoryItem(
            self.handle,
            url,
            li,
            False
        )

        xbmcplugin.endOfDirectory(self.handle)

    def show_years(self):

        years = self.scraper.get_years()

        for year in years:

            li = xbmcgui.ListItem(year["label"])

            url = (
                sys.argv[0]
                + "?action=movies"
                + "&url="
                + year["url"]
            )

            xbmcplugin.addDirectoryItem(
                self.handle,
                url,
                li,
                True
            )

        xbmcplugin.endOfDirectory(self.handle)

    def show_movies(self):

        year_url = self.params["url"]

        movies = self.scraper.get_movie_folders(year_url)

        for movie in movies:

            li = xbmcgui.ListItem(movie["label"])

            url = (
                sys.argv[0]
                + "?action=quality"
                + "&id=" + quote_plus(movie["id"])
                + "&url=" + quote_plus(movie["url"])
            )

            xbmcplugin.addDirectoryItem(
                self.handle,
                url,
                li,
                True
            )

        xbmcplugin.endOfDirectory(self.handle)

    def show_quality(self):

        movie_url = self.params["url"]

        videos = self.scraper.get_video_files(movie_url)

        if not videos:
            xbmcgui.Dialog().notification(
                "MODA",
                "No video found.",
                xbmcgui.NOTIFICATION_ERROR
            )
            return

        labels = [video["label"] for video in videos]

        index = xbmcgui.Dialog().select(
            "Choose Quality",
            labels
        )

        if index == -1:
            return

        selected = videos[index]["url"]

        xbmc.Player().play(selected)

        xbmcplugin.endOfDirectory(self.handle)

    def play(self):

        url = self.params["url"]

        li = xbmcgui.ListItem(path=url)

        xbmcplugin.setResolvedUrl(
            self.handle,
            True,
            li
        )
    def sync_library(self):

        created = self.library.sync_library()

        if created > 0:

            xbmc.executebuiltin(
                "UpdateLibrary(video)"
            )