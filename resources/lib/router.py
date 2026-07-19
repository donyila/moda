import sys
from urllib.parse import parse_qsl

import xbmcplugin
import xbmcgui

from resources.lib.scraper import Scraper


class Router:

    def __init__(self):

        self.handle = int(sys.argv[1])

        if len(sys.argv) > 2:
            self.params = dict(parse_qsl(sys.argv[2][1:]))
        else:
            self.params = {}

        self.scraper = Scraper()

    def run(self):

        action = self.params.get("action")

        if action is None:
            self.root()

        elif action == "years":
            self.show_years()

        elif action == "movies":
            self.show_movies()

        elif action == "videos":
            self.show_videos()

        elif action == "play":
            self.play()

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
                + "?action=videos"
                + "&url="
                + movie["url"]
            )

            xbmcplugin.addDirectoryItem(
                self.handle,
                url,
                li,
                True
            )

        xbmcplugin.endOfDirectory(self.handle)

    def show_videos(self):

        movie_url = self.params["url"]

        videos = self.scraper.get_video_files(movie_url)

        for video in videos:

            li = xbmcgui.ListItem(video["label"])

            li.setProperty("IsPlayable", "true")

            url = (
                sys.argv[0]
                + "?action=play"
                + "&url="
                + video["url"]
            )

            xbmcplugin.addDirectoryItem(
                self.handle,
                url,
                li,
                False
            )

        xbmcplugin.endOfDirectory(self.handle)

    def play(self):

        url = self.params["url"]

        li = xbmcgui.ListItem(path=url)

        xbmcplugin.setResolvedUrl(
            self.handle,
            True,
            li
        )