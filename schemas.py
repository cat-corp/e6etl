_posts = """
id               INT PRIMARY KEY,
uploader_id      INT,
created_at       TIMESTAMP,
md5              TEXT,
source           TEXT,
rating           TEXT,
image_width      INT,
image_height     INT,
tag_string       TEXT,
locked_tags      TEXT,
fav_count        INT,
file_ext         TEXT,
parent_id        INT,
change_seq       INT,
approver_id      INT,
file_size        INT,
comment_count    INT,
description      TEXT,
duration         INTERVAL,
updated_at       TIMESTAMP,
is_deleted       BOOLEAN,
is_pending       BOOLEAN,
is_flagged       BOOLEAN,
score            INT,
up_score         INT,
down_score       INT,
is_rating_locked BOOLEAN,
is_status_locked BOOLEAN,
is_note_locked   BOOLEAN
"""

_pools = """
id INT PRIMARY KEY,
name TEXT, created_at TIMESTAMP,
updated_at TIMESTAMP,
creator_id INT,
description TEXT,
is_active BOOLEAN,
category TEXT,
post_ids INT[]
"""

_tag_aliases = """
id               INT PRIMARY KEY,
antecedent_name  TEXT,
consequent_name  TEXT,
created_at       TIMESTAMP,
status           TEXT
"""

_tag_implications = """
id               INT PRIMARY KEY,
antecedent_name  TEXT,
consequent_name  TEXT,
created_at       TIMESTAMP,
status           TEXT
"""

_tags = """
id               INT PRIMARY KEY,
name             TEXT,
category         TEXT,
post_count       INT
"""

tables = {
    "posts": _posts,
    "pools": _pools,
    "tag_aliases": _tag_aliases,
    "tag_implications": _tag_implications,
    "tags": _tags
}