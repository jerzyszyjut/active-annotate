from typing import get_origin, get_args, Annotated


def unwrap_annotated(tp):
    if get_origin(tp) is Annotated:
        return get_args(tp)[0]
    return tp