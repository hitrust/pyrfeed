INSERT INTO
    _tmpItem
(
    google_id,
    original_id,
    link,
    content,
    title,
    author,
    published,
    updated,
    crawled
)
VALUES
(
    %(google_id)r,
    %(original_id)r,
    %(link)r,
    %(content)r,
    %(title)r,
    %(author)r,
    %(published)d,
    %(updated)d,
    %(crawled)d
)
;
