# MODA

**MODA** is an open-source Kodi video add-on that streams movies and TV
shows directly from remote HTTP directory servers without downloading
media files.

Instead of manually creating `.strm` files, MODA automatically scans
your media server, builds your Kodi library, and keeps it synchronized
with new content.

> ⚠️ The project is currently under active development.

## Features

### Movies

-   Browse movies by year
-   Automatic movie title detection
-   Multiple quality selection (480p / 720p / 1080p / 2160p)
-   Direct streaming over HTTP
-   Export movies to Kodi Library
-   Automatic STRM generation
-   Automatic Library synchronization
-   Cache system to avoid duplicate processing

### TV Shows (Planned)

-   Browse TV Shows
-   Seasons & Episodes
-   Automatic episode detection
-   Library synchronization
-   Metadata support

## Project Structure

``` text
plugin.video.moda/
├── main.py
├── service.py
├── addon.xml
└── resources/lib/
    ├── router.py
    ├── scraper.py
    ├── parser.py
    ├── network.py
    └── library.py
```

## Roadmap

### Phase 1

-   [x] HTTP directory parser
-   [x] Movie browser
-   [x] Quality selection
-   [x] Streaming
-   [x] STRM generation
-   [x] Library synchronization

### Phase 2

-   [ ] TVDb metadata
-   [ ] NFO generation
-   [ ] Poster & Fanart download

### Phase 3

-   [ ] TV Shows support
-   [ ] Seasons & Episodes
-   [ ] Automatic synchronization

## Requirements

-   Kodi 21+
-   Python 3

## License

MIT License

## Author

**Ali (donyila)**

GitHub: https://github.com/donyila
