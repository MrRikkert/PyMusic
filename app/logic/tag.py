from app.db.models import TagDb
from app.exceptions import IntegrityError


def get(tag_type: str, value: str) -> TagDb:
    """Returns tag if it exists, else returns None"""
    return TagDb.get(tag_type=tag_type, value=value)


def exists(tag_type: str, value: str) -> bool:
    tag = get(tag_type=tag_type, value=value)
    return True if tag is not None else False


def add(tag_type: str, value: str, return_existing: bool = False) -> TagDb:
    existing = get(tag_type=tag_type, value=value)
    if existing is not None:
        if not return_existing:
            raise IntegrityError("tag already exists")
        return existing
    return TagDb(tag_type=tag_type, value=value)
