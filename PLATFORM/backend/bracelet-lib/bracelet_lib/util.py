import collections
import itertools
import unicodedata


def r_replace(string: str, old: str, new: str, max_count: int):
    return new.join( string.rsplit(old, max_count) )


def remove_accents(input_str) -> bytes :
    nfkd_form  = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')

    return only_ascii


def consume(iterator, n=None):
    """Advance the iterator n-steps ahead. If n is None, consume entirely."""
    # Use functions that consume iterators at C speed.
    if n is None:
        # feed the entire iterator into a zero-length deque
        collections.deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(itertools.islice(iterator, n, n), None)
