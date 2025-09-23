# YouTube Audio Extractor

A command-line tool that extracts audio from YouTube videos and playlists, converting them to high-quality MP3 format for use on devices like iPods and other audio players.

## Features

- Extract audio from individual YouTube videos
- Process entire YouTube playlists
- Convert to MP3 with selectable quality (128kbps, 192kbps, 320kbps)
- Embed proper metadata (title, artist, album, date)
- Organize playlist downloads in folders
- Progress tracking and error recovery
- Cross-platform compatibility

## Installation

### Install from PyPI

```bash
pip install youtube-audio-extractor
```

**That's it!** The package will automatically install all dependencies.

### Prerequisites

**Python 3.8 or higher** is required. Check your version:
```bash
python --version
```

**ffmpeg** is required for audio conversion:

- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `choco install ffmpeg`

Verify ffmpeg installation:
```bash
ffmpeg -version
```

## Quick Start

1. **Install the package:**
   ```bash
   pip install youtube-audio-extractor
   ```

2. **Extract audio from a video:**
   ```bash
   youtube-audio-extractor "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
   ```

3. **Extract a playlist:**
   ```bash
   youtube-audio-extractor "https://www.youtube.com/playlist?list=PLAYLIST_ID"
   ```

That's it! Your MP3 files will be saved in the `downloads` folder.

## Web UI (no GUI install required)

Run the embedded web interface:

```bash
youtube-audio-extractor-web             # defaults to http://127.0.0.1:5000
# or choose a port
YAE_PORT=5051 youtube-audio-extractor-web
```

Features available in the Web UI:

- Start downloads from URL or search query (non-URL input auto-treated as search)
- Quality/format/output directory
- Filters: min/max duration, include/exclude keywords
- Resume (skip already downloaded)
- Cookies upload (Netscape cookies.txt)
- Batch upload (.txt file), per-line options (e.g. `| q=192 | f=m4a | min=120 | include=remix`)
- Health check, Stats (pretty last time and format mix), History with direct download links
- Stop running jobs (best-effort)

## What’s New in 1.1.0

- Multiple output formats via `-f/--format` (mp3, m4a, opus, flac)
- Playlist filtering: `--min-duration`, `--max-duration`, `--include`, `--exclude`
- Batch processing from file: `--urls-file urls.txt`
- YouTube search integration: `--search` with `--search-limit`
- Resume downloads: `--resume` to skip already-downloaded items
- Analytics report: `--stats`
- Health checks: `--health`
- Optional user config at `~/.youtube-extractor/config.yaml`

## Legal & Educational Notice

This tool is provided for educational and personal use only. Ensure your use complies with all applicable laws and YouTube's Terms of Service. Only download content you own, have permission to download, or that is in the public domain. The authors assume no liability for misuse.

Built by [KetchaLegend](https://github.com/ketchalegend).

## Usage

### Basic Usage

**Extract a single video:**

```bash
youtube-audio-extractor "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Extract a playlist:**

```bash
youtube-audio-extractor "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

### Command Options

```bash
youtube-audio-extractor [OPTIONS] URL
```

**Options:**

- `-q, --quality`: Audio quality in kbps (128, 192, 320) - default: 320
- `-f, --format`: Output format (mp3, m4a, opus, flac) - default: mp3
- `-o, --output`: Output directory - default: downloads
- `--playlist-folder/--no-playlist-folder`: Create folders for playlists - default: enabled
- `--metadata/--no-metadata`: Embed metadata in MP3 files - default: enabled
- `--cookie-path`: Path to cookies.txt (Netscape format) to pass to yt-dlp
- `--search`: Treat argument as search query (uses ytsearch)
- `--search-limit`: Number of results to fetch with --search (default 10, max 50)
- `--urls-file`: Process multiple URLs from a text file (one per line)
- `--min-duration/--max-duration`: Filter playlist items by duration (seconds)
- `--include/--exclude`: Comma-separated title keywords to include/exclude
- `--resume`: Skip items already downloaded (based on local history)
- `--stats`: Show download statistics and exit
- `--health`: Run a health check (deps, output dir) and exit
- `-v, --verbose`: Enable detailed logging
- `-h, --help`: Show help message

### Examples

**High-quality single video:**

```bash
youtube-audio-extractor -q 320 "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

**Playlist to custom directory:**

```bash
youtube-audio-extractor -o ~/Music/Playlists "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMt9xaJGA6H_VjlXEL"
**Search and download top 5 results:**

```bash
youtube-audio-extractor --search --search-limit 5 "rick astley"
```

**Batch process URLs from a file:**

```bash
youtube-audio-extractor --urls-file urls.txt -q 192 -f m4a
```

**Filter playlist (2-10 minutes, exclude live):**

```bash
youtube-audio-extractor --min-duration 120 --max-duration 600 --exclude live "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

**Resume mode (skip already-downloaded):**

```bash
youtube-audio-extractor --resume "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

```

**Lower quality for faster downloads:**

```bash
youtube-audio-extractor -q 128 -v "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Without metadata embedding:**

```bash
youtube-audio-extractor --no-metadata "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Custom output directory:**

```bash
youtube-audio-extractor -q 320 -o ~/Music "https://www.youtube.com/watch?v=VIDEO_ID"
```

**Use cookies to avoid throttling/restrictions:**

```bash
youtube-audio-extractor --cookie-path /path/to/cookies.txt "https://www.youtube.com/watch?v=VIDEO_ID"
```

Export cookies from your browser in Netscape format (e.g., using a cookies.txt exporter extension) and pass the file via `--cookie-path`.

## Output Structure

### Single Video

```
downloads/
└── Video_Title.mp3
```

### Playlist

```
downloads/
└── Playlist_Name/
    ├── Video_1_Title.mp3
    ├── Video_2_Title.mp3
    └── Video_3_Title.mp3
```

## Metadata

The tool automatically embeds the following metadata in MP3 files:

- **Title**: Video title
- **Artist**: Channel/uploader name
- **Album**: Playlist name (for playlist items)
- **Date**: Upload year
- **Duration**: Track length

## Troubleshooting

### Common Issues

**1. "ffmpeg not found" error**

```
Error: ffmpeg is not installed or not found in PATH
```

**Solutions:**

- Install ffmpeg using your system's package manager
- Ensure ffmpeg is added to your system PATH
- Restart your terminal after installation
- Test with: `ffmpeg -version`

**2. "Permission denied" error**

```
Error: Permission denied when creating output directory
```

**Solutions:**

- Check write permissions for the output directory
- Try a different output directory: `-o ~/Downloads`
- Run with appropriate permissions (avoid sudo if possible)
- Ensure the directory path exists and is accessible

**3. "Video unavailable" error**

```
Error: Video is unavailable or private
```

**Solutions:**

- Verify the URL is correct and accessible in a browser
- Check if the video is private, unlisted, or region-restricted
- Try a different video to test the tool
- Ensure stable internet connection

**4. "Playlist not found" error**

```
Error: Could not retrieve playlist information
```

**Solutions:**

- Verify the playlist URL is correct
- Check if the playlist is public (not private)
- Ensure the playlist contains videos
- Try accessing the playlist in a browser first

**5. "Network timeout" error**

```
Error: Network timeout during download
```

**Solutions:**

- Check your internet connection
- Try again later (YouTube may be temporarily unavailable)
- Use verbose mode (`-v`) to see detailed error information
- Consider using lower quality (`-q 128`) for faster downloads

**6. "Disk space" error**

```
Error: Insufficient disk space
```

**Solutions:**

- Free up disk space on your system
- Choose a different output directory with more space
- Use lower quality settings to reduce file sizes

**7. "Invalid URL" error**

```
Error: The provided URL is not a valid YouTube URL
```

**Solutions:**

- Ensure the URL starts with `https://www.youtube.com/`
- Copy the URL directly from your browser
- Remove any extra parameters or tracking information
- Test with a simple video URL first

### Getting Help

**Enable verbose logging for detailed error information:**

```bash
youtube-audio-extractor -v "YOUR_URL"
```

**Check system requirements:**

```bash
python --version    # Should be 3.8+
ffmpeg -version     # Should show ffmpeg information
pip show youtube-audio-extractor  # Check if package is installed
```

**Test with a known working video:**

```bash
youtube-audio-extractor "https://www.youtube.com/watch?v=jNQXAC9IVRw"
```

## Performance Tips

1. **Use appropriate quality settings:**

   - 320kbps: Best quality, larger files, slower downloads
   - 192kbps: Good balance of quality and size
   - 128kbps: Smaller files, faster downloads

2. **For large playlists:**

   - Use verbose mode (`-v`) to monitor progress
   - Ensure stable internet connection
   - Have sufficient disk space available
   - Consider processing in smaller batches

3. **Network optimization:**
   - Close other bandwidth-intensive applications
   - Use wired connection when possible
   - Avoid peak usage hours for better speeds

## Technical Details

### Dependencies

- **yt-dlp**: YouTube content downloading (actively maintained youtube-dl fork)
- **ffmpeg-python**: Audio conversion and processing
- **mutagen**: MP3 metadata manipulation
- **click**: Command-line interface framework

### Supported Formats

- **Input**: Any format supported by yt-dlp (YouTube videos/playlists)
- **Output**: MP3 with ID3v2 metadata tags

### Quality Settings

- **128kbps**: ~1MB per minute of audio
- **192kbps**: ~1.4MB per minute of audio
- **320kbps**: ~2.4MB per minute of audio

## Performance Optimizations

### Fast Validation for Large Playlists
For playlists with many videos (50+), use fast validation to skip thorough checking:
```bash
youtube-audio-extractor --fast-validation "LARGE_PLAYLIST_URL"
```

### Batch Processing
Process multiple videos with improved performance:
```bash
youtube-audio-extractor --batch-size 3 --urls-file urls.txt
```

### Combined Optimizations
For maximum speed on large playlists:
```bash
youtube-audio-extractor --fast-validation --batch-size 5 -q 192 "LARGE_PLAYLIST_URL"
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Want to contribute or install from source? Check out the [GitHub repository](https://github.com/ketchalegend/youtube-extractor).

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## User Configuration

Optional config file at `~/.youtube-extractor/config.yaml`:

```yaml
quality: "192"           # default quality
output_dir: "~/Music"    # default output folder
output_format: "m4a"     # mp3|m4a|opus|flac
embed_metadata: true
```

## Credits

**Created by:** [KetchaLegend](https://github.com/ketchalegend)

## Legal Disclaimer

**IMPORTANT COPYRIGHT NOTICE:**

This tool is provided for educational and personal use only. Users are solely responsible for ensuring their use complies with applicable laws and YouTube's Terms of Service.

### Copyright Responsibility
- **User Responsibility:** Users are entirely responsible for respecting copyright laws and intellectual property rights
- **No Liability:** The developers assume no responsibility for any copyright infringement or illegal use of this tool
- **Content Ownership:** Only download content you own, have permission to download, or that is in the public domain
- **Terms of Service:** Users must comply with YouTube's Terms of Service and any applicable platform policies

### Prohibited Uses
- Downloading copyrighted content without permission
- Commercial use of downloaded content without proper licensing
- Violating YouTube's Terms of Service
- Any illegal distribution or use of downloaded content

### Legal Compliance
By using this tool, you acknowledge that:
1. You are solely responsible for your actions and any legal consequences
2. You will only download content you have the right to download
3. You understand and accept all copyright and legal risks
4. The developers are not liable for any misuse of this software

**USE AT YOUR OWN RISK. RESPECT COPYRIGHT LAWS.**
