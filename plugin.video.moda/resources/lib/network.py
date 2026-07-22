import socket
import ssl
import urllib.error
import urllib.request


class Network:

    def __init__(self):

        self.context = ssl.create_default_context()
        self.context.check_hostname = False
        self.context.verify_mode = ssl.CERT_NONE

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/138.0 Safari/537.36"
            )
        }

    def get(self, url):

        request = urllib.request.Request(
            url,
            headers=self.headers
        )

        try:

            response = urllib.request.urlopen(
                request,
                timeout=30,
                context=self.context
            )

            return response.read().decode(
                "utf-8",
                "ignore"
            )

        except urllib.error.HTTPError as e:

            raise RuntimeError(
                f"HTTP Error {e.code}"
            )

        except urllib.error.URLError as e:

            reason = e.reason

            if isinstance(reason, socket.timeout):

                raise RuntimeError(
                    "Connection timeout."
                )

            if isinstance(reason, socket.gaierror):

                raise RuntimeError(
                    "Cannot resolve server address."
                )

            raise RuntimeError(
                "Cannot connect to server."
            )

        except socket.timeout:

            raise RuntimeError(
                "Connection timeout."
            )

        except Exception as e:

            raise RuntimeError(
                str(e)
            )