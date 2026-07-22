import os
import re
import sqlite3
import xbmcvfs


class LibraryMaintenance:

    def __init__(self):

        db_path = xbmcvfs.translatePath(
            "special://database/"
        )

        files = sorted(
            [
                f for f in os.listdir(db_path)
                if f.startswith("MyVideos")
                and f.endswith(".db")
            ],
            reverse=True
        )

        self.db = os.path.join(
            db_path,
            files[0]
        )

        self.profile = xbmcvfs.translatePath(
            "special://profile/addon_data/plugin.video.moda/"
        )

        self.flag = os.path.join(
            self.profile,
            "dateadded.fixed"
        )

    def fix_date_added(self):

        # فقط یک بار اجرا شود
        if os.path.exists(self.flag):
            return

        conn = sqlite3.connect(self.db)

        cur = conn.cursor()

        cur.execute("""
            SELECT
                idFile,
                strFilename
            FROM files
            WHERE strFilename LIKE '%.strm'
        """)

        rows = cur.fetchall()

        for id_file, filename in rows:

            m = re.search(
                r"\((19|20)\d{2}\)",
                filename
            )

            if not m:
                continue

            year = int(
                m.group(0)[1:-1]
            )

            date_added = (
                f"{year}-01-01 00:00:00"
            )

            cur.execute(
                """
                UPDATE files
                SET dateAdded=?
                WHERE idFile=?
                """,
                (
                    date_added,
                    id_file
                )
            )

        conn.commit()

        conn.close()

        with open(
            self.flag,
            "w",
            encoding="utf-8"
        ) as f:
            f.write("done")