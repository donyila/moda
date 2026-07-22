import xbmc

from resources.lib.library import LibraryManager
from resources.lib.maintenance import LibraryMaintenance

monitor = xbmc.Monitor()


if __name__ == "__main__":

    # صبر کن تا Kodi کاملاً بالا بیاید
    if monitor.waitForAbort(30):
        raise SystemExit

    # اگر Kodi در حال بسته شدن است
    if monitor.abortRequested():
        raise SystemExit

    try:

        created = LibraryManager().sync_library()

        # اگر هنگام Sync، Kodi بسته شد
        if monitor.abortRequested():
            raise SystemExit

        # اگر sync_library مقداری برنگرداند
        if created is None:
            created = 0

        # فقط اگر فیلم جدید پیدا شد
        if created > 0:

            xbmc.executebuiltin(
                "UpdateLibrary(video)"
            )

            # فقط اولین بار dateAdded را اصلاح کن
            LibraryMaintenance().fix_date_added()


    except Exception as e:

        xbmc.log(
            "[MODA] Service Error: %s" % str(e),
            xbmc.LOGERROR
        )