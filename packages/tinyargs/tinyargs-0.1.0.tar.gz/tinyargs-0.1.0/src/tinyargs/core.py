import sys

class TinyArgsError(Exception):
    """Custom error for missing or invalid arguments."""


def _parse_argv():
    """Parse sys.argv into a dict of {flag: value}."""
    argv = sys.argv[1:]
    out = {}
    i = 0
    while i < len(argv):
        token = argv[i]
        if token.startswith("--"):
            if "=" in token:
                key, val = token.split("=", 1)
                out[key] = val
            elif i + 1 < len(argv) and not argv[i + 1].startswith("--"):
                out[token] = argv[i + 1]
                i += 1
            else:
                out[token] = True
        i += 1
    return out


def _cast(value, typ):
    if value is True and typ is bool:
        return True
    try:
        return typ(value)
    except Exception as e:
        raise TinyArgsError(f"Could not cast {value!r} to {typ}") from e


def get(key, type=str, default=None, required=False):
    data = _parse_argv()
    if key not in data:
        if required:
            raise TinyArgsError(f"Missing required argument: {key}")
        return default
    return _cast(data[key], type)


def flag(key):
    data = _parse_argv()
    return bool(data.get(key, False))


def args(*keys, types=None, defaults=None, required=None):
    data = _parse_argv()
    results = []
    types = types or {}
    defaults = defaults or {}
    required = required or []

    for k in keys:
        if k not in data:
            if k in required:
                raise TinyArgsError(f"Missing required argument: {k}")
            results.append(defaults.get(k))
        else:
            results.append(_cast(data[k], types.get(k, str)))
    return tuple(results)
