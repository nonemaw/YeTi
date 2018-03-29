import enum


class FLAGS(enum.Enum):
    """
    status of crawler
    """
    RUNNING = "tasks_running"     # flag of tasks_running
    FETCH = "url_fetch"           # flag of url_fetched
    PARSE = "html_parse"          # flag of html_parsed
    SAVE = "item_save"            # flag of item_saved
    NOT_FETCH = "url_not_fetch"   # flag of url_not_fetch
    NOT_PARSE = "html_not_parse"  # flag of html_not_parse
    NOT_SAVE = "item_not_save"    # flag of item_not_save
