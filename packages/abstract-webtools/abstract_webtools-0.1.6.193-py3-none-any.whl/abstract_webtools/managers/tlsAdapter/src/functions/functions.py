from ..imports import *
def normalize_ciphers(ciphers: Optional[Union[str, Sequence[str]]]) -> Optional[str]:
    if ciphers is None:
        return None
    if isinstance(ciphers, str):
        # collapse whitespace, dedupe accidental commas
        parts = [p.strip() for p in ciphers.split(",") if p.strip()]
        return ",".join(parts) if parts else ""
    # it's a sequence
    return ",".join(s.strip() for s in ciphers if s and s.strip())
