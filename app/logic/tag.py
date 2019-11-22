from app.db.models import TagDb
from app.exceptions import IntegrityError


def get(tag_type: str, value: str) -> TagDb:
    """Get tag from database

    ## Arguments:
    - `tag_type`: `str`:
        - The tag type ("genre", "custom", etc)
    - `value`: `str`:
        - The value of the tag

    ## Returns:
    - `TagDb`:
        - The found tag. Returns `None` when no tag is found
    """
    return TagDb.get(tag_type=tag_type, value=value)


def exists(tag_type: str, value: str) -> bool:
    """Check if the tag already exists in the database

    ## Arguments:
    - `tag_type`: `str`:
        - The tag type ("genre", "custom", etc)
    - `value`: `str`:
        - The value of the tag

    ## Returns:
    - `bool`:
        - `True` when tag exists, `False` when it doesn't
    """
    tag = get(tag_type=tag_type, value=value)
    return True if tag is not None else False


def add(tag_type: str, value: str, return_existing: bool = False) -> TagDb:
    """Add tag to the database

    ## Arguments:
    - `tag_type`: `str`:
        - The tag type ("genre", "custom", etc)
    - `value`: `str`:
        - The value of the tag
    - `return_existing`: `bool`, optional:
        - Return existing database object when found or not. Defaults to `False`

    ## Raises:
    - `IntegrityError`:
        - If the tag already exists and `return_existing` is `False`

    ## Returns:
    - `TagDb`:
        - The created tag, or existing tag when `return_existing` is `True`
        and it already exists
    """
    existing = get(tag_type=tag_type, value=value)
    if existing is not None:
        if not return_existing:
            raise IntegrityError("tag already exists")
        return existing
    return TagDb(tag_type=tag_type, value=value)
