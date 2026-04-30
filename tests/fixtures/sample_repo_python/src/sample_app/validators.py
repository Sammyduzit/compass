def require_name(name: str) -> None:
    if not name:
        raise ValueError('name is required')
