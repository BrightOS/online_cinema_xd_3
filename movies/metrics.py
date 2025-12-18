from prometheus_client import Counter, Histogram

# User activity metrics
USER_SEARCH_TOTAL = Counter(
    "user_search_total",
    "Total number of searches performed by users",
    ["query_type"]
)

MOVIE_VIEW_DETAILS_TOTAL = Counter(
    "movie_view_details_total",
    "Total number of times movie details were viewed",
    ["movie_id"]
)

EPISODE_VIEW_TOTAL = Counter(
    "episode_view_total",
    "Total number of times an episode was viewed",
    ["episode_id"]
)

GENRE_VIEW_TOTAL = Counter(
    "genre_view_total",
    "Total number of times a genre was viewed",
    ["genre_id"]
)

PERSON_VIEW_TOTAL = Counter(
    "person_view_total",
    "Total number of times a person was viewed",
    ["person_id"]
)
