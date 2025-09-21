def abv(fg=1.010, og=None, method=None):
    """Calculate Alcohol By Volume from an original gravity and final gravity reading.
    The following methods are available; Berry is used by default.

    Berry: (og - fg) * 131.25
    Cutaia, Reid and Speers: [coming soon]
    """
    if og is None:
        raise ValueError("An original gravity reading is required")
    match method:
        case _:
            return (og - fg) * 131.25
