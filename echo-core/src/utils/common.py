def to_string(obj, *keys) -> str:
    def _warp(v):
        return "'" + v + "'" if isinstance(v, str) else v

    return ", ".join([f"{k}={_warp(getattr(obj, k))}" for k in keys])
