from prometheus_client import Counter

# Video streaming metrics
VIDEO_STREAMING_REQUESTS_TOTAL = Counter(
    "video_streaming_requests_total",
    "Total number of video streaming requests",
    ["type", "movie_id"]
)

VIDEO_PLAYBACK_ERRORS_TOTAL = Counter(
    "video_playback_errors_total",
    "Total number of video playback errors",
    ["error_type", "movie_id"]
)
