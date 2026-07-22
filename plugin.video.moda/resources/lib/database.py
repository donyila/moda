import os
import glob
import uuid
import sqlite3
import json

import xbmcvfs


class KodiDatabase:

    MOVIE_SCRAPER = (
        "metadata.movies.thetvdb.com.v4.python"
    )

    TVSHOW_SCRAPER = (
        "metadata.tvshows.thetvdb.com.v4.python"
    )

    def __init__(self):

        self.database = xbmcvfs.translatePath(
            "special://profile/Database/"
        )

        self.uuid = self.get_uuid()

    def get_database(self):

        files = glob.glob(
            os.path.join(
                self.database,
                "MyVideos*.db"
            )
        )

        if not files:
            return None

        files.sort()

        return files[-1]

    def connect(self):

        db = self.get_database()

        if not db:
            return None

        return sqlite3.connect(
            db,
            timeout=30,
            check_same_thread=False
        )


    def get_uuid(self):

        profile = xbmcvfs.translatePath(
            "special://profile/addon_data/plugin.video.moda/"
        )

        os.makedirs(profile, exist_ok=True)

        filename = os.path.join(
            profile,
            "settings.json"
        )

        if os.path.exists(filename):

            with open(
                filename,
                "r",
                encoding="utf-8"
            ) as f:

                data = json.load(f)

            if "uuid" in data:
                return data["uuid"]

        value = str(uuid.uuid4())

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                {
                    "uuid": value
                },
                f,
                indent=4,
                ensure_ascii=False
            )

        return value

    def _settings_xml(self):

        return f"""<settings version="2">
<setting id="language" default="true">English</setting>
<setting id="rating_country" default="true">USA</setting>
<setting id="get_tags" default="true">true</setting>
<setting id="gender" default="true">Other</setting>
<setting id="year" default="true">1900</setting>
<setting id="pin" default="true" />
<setting id="uuid">{self.uuid}</setting>
</settings>"""

    def ensure_content(
        self,
        path,
        content,
        scraper
    ):

        conn = self.connect()

        if conn is None:
            return

        cur = conn.cursor()

        cur.execute(
            """
            SELECT idPath
            FROM path
            WHERE strPath=?
            """,
            (path,)
        )

        row = cur.fetchone()

        settings = self._settings_xml()

        if row:

            cur.execute(
                """
                UPDATE path
                SET
                    strContent=?,
                    strScraper=?,
                    scanRecursive=?,
                    useFolderNames=?,
                    strSettings=?,
                    noUpdate=0,
                    exclude=0,
                    allAudio=0
                WHERE idPath=?
                """,
                (
                    content,
                    scraper,
                    2147483647,
                    0,
                    settings,
                    row[0]
                )
            )

        else:

            cur.execute(
                """
                INSERT INTO path
                (
                    strPath,
                    strContent,
                    strScraper,
                    strHash,
                    scanRecursive,
                    useFolderNames,
                    strSettings,
                    noUpdate,
                    exclude,
                    allAudio,
                    dateAdded,
                    idParentPath
                )
                VALUES
                (
                    ?, ?, ?, '',
                    ?, ?, ?,
                    0,0,0,
                    '',
                    NULL
                )
                """,
                (
                    path,
                    content,
                    scraper,
                    2147483647,
                    0,
                    settings
                )
            )

        conn.commit()

        conn.close()

    def ensure_movies_content(
        self,
        path
    ):

        self.ensure_content(
            path,
            "movies",
            self.MOVIE_SCRAPER
        )

    def ensure_tvshows_content(
        self,
        path
    ):

        self.ensure_content(
            path,
            "tvshows",
            self.TVSHOW_SCRAPER
        )
