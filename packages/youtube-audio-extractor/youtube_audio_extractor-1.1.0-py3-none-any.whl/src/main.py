"""Main entry point for the YouTube Audio Extractor CLI."""

import os
import sys
import logging
from pathlib import Path
from typing import Optional

import click

from .config import config
from .extractor import YouTubeExtractor
from .converter import AudioConverter
from .metadata import extract_metadata, format_metadata_for_id3
from .history import DownloadHistory
from .utils import ExtractionOptions
from .progress import ProgressTracker
from .progress import RichProgressTracker
from .errors import ErrorHandler, URLValidationError, NetworkError, FileSystemError, ConversionError


def setup_logging(verbose: bool) -> None:
    """
    Configure logging based on verbosity level.
    
    Sets up the logging system with appropriate format and level based on the
    verbosity setting. In verbose mode, detailed debug information is shown.
    In normal mode, only essential information is displayed.
    
    Args:
        verbose (bool): If True, enable detailed logging output with DEBUG level.
                       If False, use INFO level with simplified format.
    
    Example:
        >>> setup_logging(True)   # Enable verbose logging
        >>> setup_logging(False)  # Use standard logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    format_string = config.LOG_FORMAT_VERBOSE if verbose else config.LOG_FORMAT_SIMPLE
    
    # Clear any existing handlers to avoid conflicts
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True  # Force reconfiguration
    )


def validate_quality(ctx, param, value):
    """
    Validate the audio quality parameter for Click CLI.
    
    Ensures the provided quality value is one of the supported options.
    Used as a Click callback function for parameter validation.
    
    Args:
        ctx: Click context (unused)
        param: Click parameter object (unused)
        value (str): The quality value to validate
        
    Returns:
        str: The validated quality value
        
    Raises:
        click.BadParameter: If the quality value is not supported
    """
    if not config.validate_quality(value):
        raise click.BadParameter(f'Quality must be one of: {", ".join(config.SUPPORTED_QUALITIES)}')
    return value


def validate_output_dir(ctx, param, value):
    """
    Validate and create the output directory if needed.
    
    Ensures the output directory exists and is writable. Creates the directory
    if it doesn't exist. Used as a Click callback function for parameter validation.
    
    Args:
        ctx: Click context (unused)
        param: Click parameter object (unused)
        value (str): The output directory path to validate
        
    Returns:
        str: The validated output directory path
        
    Raises:
        click.BadParameter: If the directory cannot be created or accessed
    """
    if value:
        try:
            Path(value).mkdir(parents=True, exist_ok=True)
            return value
        except (OSError, PermissionError) as e:
            raise click.BadParameter(f'Cannot create output directory "{value}": {e}')
    return value


def validate_dependencies() -> None:
    """
    Validate that all required dependencies are available.
    
    Checks for the presence of required Python packages and system dependencies
    like ffmpeg. This function should be called before attempting any audio
    extraction to ensure the system is properly configured.
    
    Raises:
        ConversionError: If ffmpeg is not available or not properly installed.
        ImportError: If required Python packages (yt-dlp, ffmpeg-python, 
                    mutagen, click) are missing.
    
    Example:
        >>> try:
        ...     validate_dependencies()
        ...     print("All dependencies are available")
        ... except (ConversionError, ImportError) as e:
        ...     print(f"Missing dependency: {e}")
    """
    logger = logging.getLogger(__name__)
    
    # Check Python dependencies
    required_modules = ['yt_dlp', 'ffmpeg', 'mutagen', 'click']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        raise ImportError(
            f"Missing required Python packages: {', '.join(missing_modules)}. "
            f"Please install them using: pip install {' '.join(missing_modules)}"
        )
    
    # Check ffmpeg availability (this will raise ConversionError if not found)
    try:
        converter = AudioConverter()
        logger.info("All dependencies validated successfully")
    except ConversionError:
        raise  # Re-raise as ConversionError for consistent error handling


@click.command()
@click.argument('url', required=True, metavar='URL')
@click.option('--search', is_flag=True, help='Interpret URL argument as a search query (ytsearch)')
@click.option('--search-limit', type=int, default=10, help='Number of results to fetch when using --search')
@click.option('--urls-file', type=click.Path(exists=True), help='Path to a file containing URLs (one per line)')
@click.option('--min-duration', type=int, default=None, help='Minimum duration in seconds to include')
@click.option('--max-duration', type=int, default=None, help='Maximum duration in seconds to include')
@click.option('--include', type=str, default=None, help='Comma-separated keywords to include (title)')
@click.option('--exclude', type=str, default=None, help='Comma-separated keywords to exclude (title)')
@click.option('--stats', is_flag=True, help='Show download statistics and exit')
@click.option('--resume', is_flag=True, help='Skip items already downloaded (based on history)')
@click.option('--health', is_flag=True, help='Run health checks and exit')
@click.option(
    '--quality', '-q',
    default=config.DEFAULT_QUALITY,
    callback=validate_quality,
    help=f'Audio quality in kbps. Choices: {", ".join(config.SUPPORTED_QUALITIES)} (default: {config.DEFAULT_QUALITY})'
)
@click.option(
    '--format', '-f',
    type=click.Choice(config.SUPPORTED_FORMATS, case_sensitive=False),
    default=config.DEFAULT_OUTPUT_FORMAT,
    help=f'Output audio format. Choices: {", ".join(config.SUPPORTED_FORMATS)} (default: {config.DEFAULT_OUTPUT_FORMAT})'
)
@click.option(
    '--output', '-o',
    default=config.DEFAULT_OUTPUT_DIR,
    callback=validate_output_dir,
    help=f'Output directory for downloaded files (default: {config.DEFAULT_OUTPUT_DIR})'
)
@click.option(
    '--playlist-folder/--no-playlist-folder',
    default=config.DEFAULT_CREATE_PLAYLIST_FOLDERS,
    help='Create separate folders for playlists (default: enabled)'
)
@click.option(
    '--metadata/--no-metadata',
    default=config.DEFAULT_EMBED_METADATA,
    help='Embed metadata in MP3 files (default: enabled)'
)
@click.option(
    '--verbose', '-v',
    is_flag=True,
    help='Enable verbose logging output'
)
@click.option(
    '--fast-validation',
    is_flag=True,
    help='Use fast URL validation (recommended for large playlists)'
)
@click.option(
    '--batch-size',
    default=5,
    type=int,
    help='Number of videos to process in parallel (1-10, default: 5)'
)
@click.option(
    '--cookie-path',
    type=str,
    default=None,
    help='Path to cookies.txt (Netscape format) to pass to yt-dlp for authenticated requests'
)
@click.help_option('--help', '-h')
@click.version_option(version=config.APP_VERSION, prog_name=config.APP_NAME)
def main(url: str, quality: str, output: str, playlist_folder: bool, 
         metadata: bool, verbose: bool, fast_validation: bool, batch_size: int,
         cookie_path: Optional[str], format: str, search: bool, urls_file: Optional[str],
         min_duration: Optional[int], max_duration: Optional[int], include: Optional[str],
         exclude: Optional[str], stats: bool, health: bool, search_limit: int, resume: bool) -> None:
    """
    Extract audio from YouTube videos and playlists.
    
    This tool downloads audio from YouTube videos or entire playlists,
    converts them to high-quality MP3 format, and embeds proper metadata
    for use on devices like iPods.
    
    URL: YouTube video or playlist URL to extract audio from
    
    Examples:
    
    \b
    # Extract single video with default settings
    youtube-audio-extractor "https://www.youtube.com/watch?v=VIDEO_ID"
    
    \b
    # Extract playlist with custom quality and output directory
    youtube-audio-extractor -q 192 -o ~/Music "https://www.youtube.com/playlist?list=PLAYLIST_ID"
    
    \b
    # Extract with verbose logging
    youtube-audio-extractor -v "https://www.youtube.com/watch?v=VIDEO_ID"
    
    \b
    # Fast processing for large playlists
    youtube-audio-extractor --fast-validation --batch-size 3 "PLAYLIST_URL"
    """
    # Setup logging
    setup_logging(verbose)
    logger = logging.getLogger(__name__)
    
    # Apply user config overrides (non-intrusive)
    defaults = config.get_default_options()
    overrides = config.load_user_overrides()
    effective = config.merge_with_overrides(defaults, overrides)
    # CLI args take precedence over config file
    effective.update({
        'quality': quality or effective['quality'],
        'output_dir': output or effective['output_dir'],
        'embed_metadata': metadata if metadata is not None else effective['embed_metadata'],
        'output_format': (format or effective.get('output_format') or config.DEFAULT_OUTPUT_FORMAT).lower(),
    })

    # Display startup information
    app_info = config.get_app_info()
    click.echo(f"{app_info['name']} v{app_info['version']}")
    click.echo(f"Quality: {effective['quality']}kbps | Output: {effective['output_dir']}")
    if verbose:
        logger.info(f"Verbose logging enabled")
        logger.info(f"Playlist folders: {'enabled' if playlist_folder else 'disabled'}")
        logger.info(f"Metadata embedding: {'enabled' if metadata else 'disabled'}")
        if cookie_path:
            logger.info(f"Using cookies from: {cookie_path}")
    
    try:
        # Early commands
        if stats:
            from .analytics import generate_report
            rep = generate_report()
            click.echo(f"Total downloads: {rep['total_downloads']}")
            if rep['last_download_utc']:
                click.echo(f"Last download (UTC): {rep['last_download_utc']}")
            click.echo(f"Recent tracked: {rep['recent_count']}")
            if rep['top_titles']:
                click.echo("Top titles:")
                for title, cnt in rep['top_titles']:
                    click.echo(f"  - {title} x{cnt}")
            if rep['formats']:
                click.echo("Formats in recent:")
                for ext, cnt in rep['formats'].most_common():
                    click.echo(f"  - {ext}: {cnt}")
            return

        if health:
            # Simple health: deps and writable output
            try:
                validate_dependencies()
                Path(effective['output_dir']).mkdir(parents=True, exist_ok=True)
                click.echo("Health OK: dependencies and output directory validated")
            except Exception as e:
                click.echo(click.style(f"Health check failed: {e}", fg='red'), err=True)
                sys.exit(1)
            return
        # Initialize error handler
        error_handler = ErrorHandler()
        
        # Validate all dependencies
        try:
            validate_dependencies()
            converter = AudioConverter()
            logger.info("All dependencies validated successfully")
        except (ConversionError, ImportError) as e:
            click.echo(click.style(f"Error: {e}", fg='red'), err=True)
            if hasattr(e, 'suggestions'):
                for suggestion in e.suggestions:
                    click.echo(f"  • {suggestion}", err=True)
            sys.exit(1)
        
        # Create progress tracker
        # Use rich progress if available and not disabled
        progress_tracker = RichProgressTracker(verbose=verbose)
        if not hasattr(progress_tracker, 'create_yt_dlp_hook'):
            progress_tracker = ProgressTracker(verbose=verbose)
        
        # Create extraction options
        options = ExtractionOptions(
            quality=effective['quality'],
            output_dir=effective['output_dir'],
            embed_metadata=effective['embed_metadata'],
            cookie_path=cookie_path,
            output_format=effective['output_format']
        )
        
        # Initialize extractor with progress tracker
        extractor = YouTubeExtractor(options, progress_tracker)

        # Support search queries
        if search:
            n = max(1, min(search_limit or 10, 50))
            url = f"ytsearch{n}:{url}"

        # Support batch URLs file
        if urls_file:
            with open(urls_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            for line_url in urls:
                # Minimal per-URL processing (no playlist in batch for brevity)
                try:
                    error_handler.validate_url(line_url)
                except (URLValidationError, NetworkError) as e:
                    progress_tracker.show_error_with_suggestions(str(e), e.suggestions)
                    continue
                if extractor.is_playlist_url(line_url):
                    click.echo(click.style("Detected playlist URL", fg='blue'))
                    process_playlist(extractor, converter, line_url, options, playlist_folder, verbose, progress_tracker)
                else:
                    click.echo(click.style("Detected video URL", fg='blue'))
                    process_video(extractor, converter, line_url, options, verbose, progress_tracker)
            return
        
        # Validate URL (fast or thorough)
        # Force fast validation for search queries (ytsearch: URLs are not http(s))
        if fast_validation or search:
            progress_tracker.show_stage_message("Fast URL validation")
            if not extractor.validate_url_lazy(url):
                progress_tracker.show_error_with_suggestions(
                    "Invalid URL format",
                    ["Check URL format", "Ensure it's a YouTube URL"]
                )
                sys.exit(1)
        else:
            progress_tracker.show_stage_message("Validating URL")
            try:
                error_handler.validate_url(url)
            except (URLValidationError, NetworkError) as e:
                progress_tracker.show_error_with_suggestions(str(e), e.suggestions)
                sys.exit(1)
        
        # Check if URL is a playlist
        if extractor.is_playlist_url(url):
            click.echo(click.style("Detected playlist URL", fg='blue'))
            # Optional filtering
            filtered_videos = None
            if any([min_duration, max_duration, include, exclude]):
                info = extractor.get_playlist_info(url)
                if info:
                    inc_keywords = set([k.strip().lower() for k in (include or '').split(',') if k.strip()])
                    exc_keywords = set([k.strip().lower() for k in (exclude or '').split(',') if k.strip()])
                    selected = []
                    for v in info.videos:
                        if min_duration is not None and v.duration and v.duration < min_duration:
                            continue
                        if max_duration is not None and v.duration and v.duration > max_duration:
                            continue
                        title_l = (v.title or '').lower()
                        if inc_keywords and not any(k in title_l for k in inc_keywords):
                            continue
                        if exc_keywords and any(k in title_l for k in exc_keywords):
                            continue
                        selected.append(v)
                    filtered_videos = selected
            if resume:
                # Filter out already-downloaded items based on history
                from .history import DownloadHistory
                h = DownloadHistory()
                base_list = filtered_videos if filtered_videos is not None else (info.videos if info else [])
                base_list = [v for v in base_list if not h.is_already_downloaded(v.id)]
                filtered_videos = base_list

            process_playlist(extractor, converter, url, options, playlist_folder, verbose, progress_tracker if not filtered_videos else progress_tracker)
            # Re-run with filtered list through concurrent API if filters applied
            if filtered_videos is not None:
                import asyncio
                asyncio.run(extractor.extract_playlist_audio_concurrent(url))
        else:
            click.echo(click.style("Detected video URL", fg='blue'))
            if resume:
                from .history import DownloadHistory
                h = DownloadHistory()
                vi = extractor.get_video_info(url)
                if vi and h.is_already_downloaded(vi.id):
                    click.echo(click.style("Already downloaded. Skipping (--resume).", fg='yellow'))
                    return
            process_video(extractor, converter, url, options, verbose, progress_tracker)
            
    except (ConversionError, FileSystemError, URLValidationError, NetworkError) as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
        for suggestion in e.suggestions:
            click.echo(f"  • {suggestion}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo(click.style("\nOperation cancelled by user", fg='yellow'))
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        click.echo(click.style(f"Unexpected error: {e}", fg='red'), err=True)
        sys.exit(1)


def process_video(extractor: YouTubeExtractor, converter: AudioConverter, 
                 url: str, options: ExtractionOptions, verbose: bool, progress_tracker: ProgressTracker) -> None:
    """
    Process a single video URL for audio extraction.
    
    Handles the complete workflow for extracting audio from a single YouTube video,
    including download, conversion, and metadata embedding. Provides user feedback
    through the progress tracker and handles errors gracefully.
    
    Args:
        extractor (YouTubeExtractor): Configured extractor instance for downloading
        converter (AudioConverter): Audio converter for format conversion and metadata
        url (str): YouTube video URL to process
        options (ExtractionOptions): Configuration options for extraction
        verbose (bool): Whether verbose logging is enabled
        progress_tracker (ProgressTracker): Progress tracker for user feedback
        
    Raises:
        SystemExit: If extraction fails or encounters unrecoverable errors
        
    Example:
        >>> extractor = YouTubeExtractor(options, progress_tracker)
        >>> converter = AudioConverter()
        >>> process_video(extractor, converter, "https://youtube.com/watch?v=...", 
        ...               options, False, progress_tracker)
    """
    logger = logging.getLogger(__name__)
    
    # Extract audio (this will handle all progress tracking internally)
    output_path = extractor.extract_video_audio(url)
    
    if not output_path:
        progress_tracker.show_error_with_suggestions(
            "Failed to extract audio",
            [
                "Check internet connection",
                "Verify the video is available and not private",
                "Try again later",
                "Check available disk space"
            ]
        )
        sys.exit(1)
    
    # Get video info for metadata
    video_info = extractor.get_video_info(url)
    
    # Embed metadata if enabled and file is MP3
    if options.embed_metadata and output_path.endswith('.mp3') and video_info:
        progress_tracker.show_stage_message("Embedding metadata")
        
        # Convert VideoInfo to dict format expected by extract_metadata
        video_dict = {
            'title': video_info.title,
            'uploader': video_info.uploader,
            'duration': video_info.duration,
            'upload_date': video_info.upload_date
        }
        metadata_obj = extract_metadata(video_dict)
        
        # Convert to format expected by converter
        converter_metadata = {
            'title': metadata_obj.title,
            'artist': metadata_obj.artist,
            'album': metadata_obj.album,
            'date': metadata_obj.date,
            'duration': metadata_obj.duration
        }
        
        try:
            if converter.embed_metadata(output_path, converter_metadata):
                logger.info("Metadata embedded successfully")
        except ConversionError as e:
            click.echo(click.style(f"Warning: Failed to embed metadata: {e}", fg='yellow'))
            if verbose:
                for suggestion in e.suggestions:
                    click.echo(f"  • {suggestion}")
    
    # Show completion summary
    results = {
        'title': video_info.title if video_info else 'Unknown',
        'output_path': output_path
    }
    progress_tracker.show_processing_summary(results)

    # Record download history
    try:
        if video_info:
            history = DownloadHistory()
            history.add_download(video_info.id, video_info.title, output_path)
    except Exception:
        # History should not affect main flow; ignore errors silently
        pass


def process_playlist(extractor: YouTubeExtractor, converter: AudioConverter,
                    url: str, options: ExtractionOptions, playlist_folder: bool, verbose: bool, progress_tracker: ProgressTracker) -> None:
    """
    Process a playlist URL for audio extraction.
    
    Handles the complete workflow for extracting audio from all videos in a YouTube
    playlist. Creates organized folder structure, processes videos sequentially with
    error recovery, and embeds metadata for all successful downloads.
    
    Args:
        extractor (YouTubeExtractor): Configured extractor instance for downloading
        converter (AudioConverter): Audio converter for format conversion and metadata
        url (str): YouTube playlist URL to process
        options (ExtractionOptions): Configuration options for extraction
        playlist_folder (bool): Whether to create separate folders for playlists
        verbose (bool): Whether verbose logging is enabled
        progress_tracker (ProgressTracker): Progress tracker for user feedback
        
    Raises:
        SystemExit: If playlist extraction fails or encounters unrecoverable errors
        
    Example:
        >>> extractor = YouTubeExtractor(options, progress_tracker)
        >>> converter = AudioConverter()
        >>> process_playlist(extractor, converter, "https://youtube.com/playlist?list=...", 
        ...                  options, True, False, progress_tracker)
    """
    logger = logging.getLogger(__name__)
    
    # Extract playlist audio (this will handle all progress tracking internally)
    results = extractor.extract_playlist_audio(url)
    
    if not results['success']:
        error_msg = results.get('error', 'Unknown error')
        if error_msg == 'Operation cancelled by user':
            click.echo("Operation cancelled.")
            return
        
        progress_tracker.show_error_with_suggestions(
            error_msg,
            [
                "Check if the playlist URL is valid",
                "Verify the playlist is public",
                "Check internet connection",
                "Try again later"
            ]
        )
        sys.exit(1)
    
    # Get playlist info for metadata processing and history recording
    playlist_info = extractor.get_playlist_info(url)
    
    # Process metadata for successful downloads if enabled
    if options.embed_metadata and playlist_info:
        progress_tracker.show_stage_message("Embedding metadata for downloaded files")
        
        for download in results['successful_downloads']:
            if download['output_path'].endswith('.mp3'):
                # Find corresponding video info
                video_info = None
                for video in playlist_info.videos:
                    if video.url == download['url']:
                        video_info = video
                        break
                
                if video_info:
                    # Convert VideoInfo to dict format expected by extract_metadata
                    video_dict = {
                        'title': video_info.title,
                        'uploader': video_info.uploader,
                        'duration': video_info.duration,
                        'upload_date': video_info.upload_date
                    }
                    playlist_dict = {'title': playlist_info.title}
                    metadata_obj = extract_metadata(video_dict, playlist_dict)
                    
                    # Convert to format expected by converter
                    converter_metadata = {
                        'title': metadata_obj.title,
                        'artist': metadata_obj.artist,
                        'album': metadata_obj.album,
                        'date': metadata_obj.date,
                        'duration': metadata_obj.duration
                    }
                    
                    try:
                        converter.embed_metadata(download['output_path'], converter_metadata)
                    except ConversionError as e:
                        logger.warning(f"Failed to embed metadata for {download['title']}: {e}")
    
    # Record download history for all successful downloads
    if playlist_info:
        try:
            history = DownloadHistory()
            # Build url -> VideoInfo map
            url_to_info = {v.url: v for v in playlist_info.videos}
            for download in results['successful_downloads']:
                v = url_to_info.get(download['url'])
                if v:
                    history.add_download(v.id, v.title, download['output_path'])
        except Exception:
            pass

    # Show completion summary
    progress_tracker.show_processing_summary(results)


if __name__ == "__main__":
    main()