"""Functions for generating hostnames."""

import random
from importlib.resources import files

PACKAGE = "hostdb.resources"
WORDLIST = "wordlist"


def _build_hostname_set() -> dict[str, str]:
    """Return the hostname set from the wordlist."""
    words: dict[str, str] = {}
    text = files(PACKAGE).joinpath(WORDLIST).read_text(encoding="utf-8")
    for line in text.split("\n"):
        if line.startswith("#"):
            continue
        for w in line.split(" "):
            w = w.strip()
            if not w:
                continue
            words[w] = ""
    return words


def allocate_hostnames(
    allocated: list[str], count: int, rand=random.Random()
) -> list[str]:
    """Produce the specified number of new hostnames that are not already allocated."""
    # Attempts to preserve order to facilitate testing with fixed random
    hostname_set = _build_hostname_set()
    for host in allocated:
        if host in hostname_set:
            del hostname_set[host]
    hostname_pool = list(hostname_set.keys())
    random.shuffle(hostname_pool)
    return hostname_pool[0:count]
