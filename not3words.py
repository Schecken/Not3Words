#!/usr/bin/env python3
"""
not3words: Human-readable addresses for every 3x3m square on the earth's surface.
Provides both a command-line interface and an API for import into other scripts.

Usage (command-line):
  To encode:
    python not3words.py encode -k <KEY> --words 3 "-33.867480754852295,151.20700120925903"
  To decode:
    python not3words.py decode -k <KEY> --words 3 "covary-britt-kydd"

Usage (import):
    >>> import not3words
    >>> sydney = "-33.867480754852295, 151.20700120925903"
    >>> print(not3words.three_words(sydney))
    covary-britt-kydd
    >>> print(not3words.decode("covary-britt-kydd"))
    (-33.867480754852295, 151.20700120925903)
"""

import argparse
import hashlib
import random
import geohash

# --- Custom ArgumentParser to treat coordinate strings as positional ---
class MyArgumentParser(argparse.ArgumentParser):
    def _parse_optional(self, arg_string):
        """
        Override _parse_optional so that if arg_string looks like coordinates
        (e.g. "-33.867480754852295,151.20700120925903" or
         "-33.867480754852295 151.20700120925903"),
        then it is not treated as an optional argument.
        """
        # Check for comma-separated coordinates
        if ',' in arg_string:
            tokens = arg_string.split(',')
            if len(tokens) == 2:
                try:
                    float(tokens[0].strip())
                    float(tokens[1].strip())
                    return None
                except ValueError:
                    pass
        # Check for space-separated coordinates
        if ' ' in arg_string:
            tokens = arg_string.split()
            if len(tokens) == 2:
                try:
                    float(tokens[0].strip())
                    float(tokens[1].strip())
                    return None
                except ValueError:
                    pass
        # Also, if the string is a single number (like "-33.867480754852295")
        try:
            float(arg_string)
            return None
        except ValueError:
            pass
        return super()._parse_optional(arg_string)

# --- Utility: Parse coordinate strings ---
def parse_coords(coords):
    """
    Parse coordinate input that can be in any of these formats:
      - "-33.867480754852295 151.20700120925903"
      - "-33.867480754852295,151.20700120925903"
      - "-33.867480754852295, 151.20700120925903"
    Returns a tuple (latitude, longitude) as floats.
    """
    if isinstance(coords, (tuple, list)):
        if len(coords) == 2:
            return (float(coords[0]), float(coords[1]))
        else:
            raise ValueError("Coordinates must contain exactly two values.")
    elif isinstance(coords, str):
        coords = coords.strip()
        if ',' in coords:
            parts = coords.split(',')
        else:
            parts = coords.split()
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) != 2:
            raise ValueError("Coordinate string must contain exactly two numbers.")
        return (float(parts[0]), float(parts[1]))
    else:
        raise ValueError("Coordinates must be a string or a tuple of two numbers.")

# --- Utility: Deterministic key-based shuffle ---
def key_shuffle(word_list, key):
    """
    Deterministically shuffle a list of words using a secret key.
    Each word is hashed with the key (using SHA256) and then sorted by that hash.
    """
    hashed = [(word, hashlib.sha256((key + word).encode('utf-8')).hexdigest())
              for word in word_list]
    sorted_words = [word for word, _ in sorted(hashed, key=lambda x: x[1])]
    return sorted_words

# --- Utility: Load word list from file ---
def get_words(fname):
    with open(fname, "r") as f:
        words = [line.strip() for line in f]
    random.seed(634634)
    random.shuffle(words)
    words = words[:2**15]
    assert len(words) == len(set(words))
    return words

# --- Word lists ---
GOOGLE_WORDLIST = get_words("words/google-ngram-list")
GOOGLE_4096WORDS = get_words("words/google-ngram-list-4096")
WORDNET_LEMMAS = get_words("words/wordnet-list")

HUMAN_WORDLIST = (
    'ack', 'alabama', 'alanine', 'alaska', 'alpha', 'angel', 'apart', 'april',
    'arizona', 'arkansas', 'artist', 'asparagus', 'aspen', 'august', 'autumn',
    'avocado', 'bacon', 'bakerloo', 'batman', 'beer', 'berlin', 'beryllium',
    'black', 'blossom', 'blue', 'bluebird', 'bravo', 'bulldog', 'burger',
    'butter', 'california', 'carbon', 'cardinal', 'carolina', 'carpet', 'cat',
    'ceiling', 'charlie', 'chicken', 'coffee', 'cola', 'cold', 'colorado',
    'comet', 'connecticut', 'crazy', 'cup', 'dakota', 'december', 'delaware',
    'delta', 'diet', 'don', 'double', 'early', 'earth', 'east', 'echo',
    'edward', 'eight', 'eighteen', 'eleven', 'emma', 'enemy', 'equal',
    'failed', 'fanta', 'fifteen', 'fillet', 'finch', 'fish', 'five', 'fix',
    'floor', 'florida', 'football', 'four', 'fourteen', 'foxtrot', 'freddie',
    'friend', 'fruit', 'gee', 'georgia', 'glucose', 'golf', 'green', 'grey',
    'hamper', 'happy', 'harry', 'hawaii', 'helium', 'high', 'hot', 'hotel',
    'hydrogen', 'idaho', 'illinois', 'india', 'indigo', 'ink', 'iowa',
    'island', 'item', 'jersey', 'jig', 'johnny', 'juliet', 'july', 'jupiter',
    'kansas', 'kentucky', 'kilo', 'king', 'kitten', 'lactose', 'lake', 'lamp',
    'lemon', 'leopard', 'lima', 'lion', 'lithium', 'london', 'louisiana',
    'low', 'magazine', 'magnesium', 'maine', 'mango', 'march', 'mars',
    'maryland', 'massachusetts', 'may', 'mexico', 'michigan', 'mike',
    'minnesota', 'mirror', 'mississippi', 'missouri', 'mobile', 'mockingbird',
    'monkey', 'montana', 'moon', 'mountain', 'muppet', 'music', 'nebraska',
    'neptune', 'network', 'nevada', 'nine', 'nineteen', 'nitrogen', 'north',
    'november', 'nuts', 'october', 'ohio', 'oklahoma', 'one', 'orange',
    'oranges', 'oregon', 'oscar', 'oven', 'oxygen', 'papa', 'paris', 'pasta',
    'pennsylvania', 'pip', 'pizza', 'pluto', 'potato', 'princess', 'purple',
    'quebec', 'queen', 'quiet', 'red', 'river', 'robert', 'robin', 'romeo',
    'rugby', 'sad', 'salami', 'saturn', 'september', 'seven', 'seventeen',
    'shade', 'sierra', 'single', 'sink', 'six', 'sixteen', 'skylark', 'snake',
    'social', 'sodium', 'solar', 'south', 'spaghetti', 'speaker', 'spring',
    'stairway', 'steak', 'stream', 'summer', 'sweet', 'table', 'tango', 'ten',
    'tennessee', 'tennis', 'texas', 'thirteen', 'three', 'timing', 'triple',
    'twelve', 'twenty', 'two', 'uncle', 'undress', 'uniform', 'uranus', 'utah',
    'vegan', 'venus', 'vermont', 'victor', 'video', 'violet', 'virginia',
    'washington', 'west', 'whiskey', 'white', 'william', 'winner', 'winter',
    'wisconsin', 'wolfram', 'wyoming', 'xray', 'yankee', 'yellow', 'zebra',
    'zulu'
)

# --- WordHasher class ---
class WordHasher(object):
    def __init__(self, key=None):
        """
        Convert latitude and longitudes into human-readable word addresses.
        If a key is provided, the word lists are deterministically shuffled
        based on that key.
        """
        self._symbols = "0123456789bcdefghjkmnpqrstuvwxyz"
        self._decode_symbols = {ch: i for i, ch in enumerate(self._symbols)}
        self._encode_symbols = {i: ch for i, ch in enumerate(self._symbols)}
        self.six_wordlist = HUMAN_WORDLIST
        self.four_wordlist = GOOGLE_4096WORDS
        self.three_wordlist = GOOGLE_WORDLIST

        if key:
            self.three_wordlist = key_shuffle(self.three_wordlist, key)
            self.four_wordlist = key_shuffle(self.four_wordlist, key)
            self.six_wordlist = key_shuffle(self.six_wordlist, key)

    def three_words(self, lat_long):
        """Convert coordinates to a three-word address."""
        lat, lon = parse_coords(lat_long) if isinstance(lat_long, str) else lat_long
        gh = geohash.encode(lat, lon, 9)
        indices = self.to_rugbits(self.geo_to_int(gh))
        words = "-".join(self.three_wordlist[p] for p in indices)
        return words

    def four_words(self, lat_long):
        """Convert coordinates to a four-word address."""
        lat, lon = parse_coords(lat_long) if isinstance(lat_long, str) else lat_long
        gh = geohash.encode(lat, lon, 9)
        indices = self.to_quads(self.pad(gh))
        words = "-".join(self.four_wordlist[p] for p in indices)
        return words

    def six_words(self, lat_long):
        """Convert coordinates to a six-word address."""
        lat, lon = parse_coords(lat_long) if isinstance(lat_long, str) else lat_long
        gh = geohash.encode(lat, lon, 9)
        indices = self.to_bytes(self.pad(gh))
        words = "-".join(self.six_wordlist[p] for p in indices)
        return words

    def decode(self, words):
        """
        Decode a word address (with '-' or '.' as separator) to coordinates.
        The same key (if any) used during encoding must be used.
        """
        words = words.replace('.', '-').split("-")
        if len(words) == 3:
            i = self.rugbits_to_int([self.three_wordlist.index(w) for w in words])
        elif len(words) == 4:
            i = self.quads_to_int([self.four_wordlist.index(w) for w in words])
            i = self.unpad(i)
        elif len(words) == 6:
            i = self.bytes_to_int([self.six_wordlist.index(w) for w in words])
            i = self.unpad(i)
        else:
            raise RuntimeError("Cannot decode a set of %i words." % len(words))
        geo_hash = self.int_to_geo(i)
        return geohash.decode(geo_hash)

    def geo_to_int(self, geo_hash):
        base = len(self._symbols)
        number = 0
        for symbol in geo_hash:
            number = number * base + self._decode_symbols[symbol]
        return number

    def int_to_geo(self, integer):
        base = len(self._symbols)
        symbols = []
        while integer > 0:
            remainder = integer % base
            integer //= base
            symbols.append(self._encode_symbols[remainder])
        return ''.join(reversed(symbols))

    def pad(self, geo_hash):
        assert len(geo_hash) == 9
        return self.geo_to_int(geo_hash) * 8

    def unpad(self, integer):
        return integer >> 3

    def to_bytes(self, integer):
        bytes_list = [integer & 0xFF]
        for n in range(1, 6):
            div = 2 ** (n * 8)
            bytes_list.append((integer // div) & 0xFF)
        bytes_list.reverse()
        return bytes_list

    def bytes_to_int(self, bytes_list):
        assert len(bytes_list) == 6
        N = 0
        bytes_list = list(reversed(bytes_list))
        for n, b in enumerate(bytes_list):
            N += b * (2 ** (8 * n))
        return N

    def to_quads(self, integer):
        quads = [integer & 0xFFF]
        for n in range(1, 4):
            div = 2 ** (n * 12)
            quads.append((integer // div) & 0xFFF)
        quads.reverse()
        return quads

    def quads_to_int(self, quads):
        assert len(quads) == 4
        N = 0
        quads = list(reversed(quads))
        for n, b in enumerate(quads):
            N += b * (2 ** (12 * n))
        return N

    def to_rugbits(self, integer):
        fifteen_bits = 0x7FFF
        rugbits = [
            (integer >> 30) & fifteen_bits,
            (integer >> 15) & fifteen_bits,
            integer & fifteen_bits
        ]
        return rugbits

    def rugbits_to_int(self, rugbits):
        assert len(rugbits) == 3
        return (rugbits[0] << 30) + (rugbits[1] << 15) + rugbits[2]

# --- Global default instance ---
_default_hasher = WordHasher()

def set_key(key):
    """
    Set the default secret key for encoding/decoding.
    Subsequent calls to the top-level functions will use this key.
    """
    global _default_hasher
    _default_hasher = WordHasher(key=key)

# --- Top-level API functions ---
def three_words(coords, key=None):
    """
    Convert coordinates (in any supported format) to a three-word address.
    """
    if key is not None:
        return WordHasher(key=key).three_words(coords)
    return _default_hasher.three_words(coords)

def four_words(coords, key=None):
    if key is not None:
        return WordHasher(key=key).four_words(coords)
    return _default_hasher.four_words(coords)

def six_words(coords, key=None):
    if key is not None:
        return WordHasher(key=key).six_words(coords)
    return _default_hasher.six_words(coords)

def decode(words, key=None):
    """
    Decode a word address back to (latitude, longitude).
    """
    if key is not None:
        return WordHasher(key=key).decode(words)
    return _default_hasher.decode(words)

# --- Command-line interface ---
def main():
    parser = MyArgumentParser(
        description="Encode or decode geographic coordinates using a key-based word rotation."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    encode_parser = subparsers.add_parser("encode", help="Encode coordinates to words.")
    encode_parser.add_argument("coords", nargs='+', 
                               help="Coordinates in any of these formats: \"lat lon\", \"lat,lon\", or \"lat, lon\"")
    encode_parser.add_argument("--key", "-k", type=str, help="Secret key for shuffling the word list")
    encode_parser.add_argument("--words", "-w", type=int, choices=[3, 4, 6], default=3,
                               help="Number of words to use (default: 3)")

    decode_parser = subparsers.add_parser("decode", help="Decode a word address to coordinates.")
    decode_parser.add_argument("address", type=str, help="Word address (use '-' or '.' as separator)")
    decode_parser.add_argument("--key", "-k", type=str, help="Secret key used for encoding")
    decode_parser.add_argument("--words", "-w", type=int, choices=[3, 4, 6], default=3,
                               help="Number of words in the address (default: 3)")

    args = parser.parse_args()

    if args.command == "encode":
        coord_str = " ".join(args.coords)
        latlon = parse_coords(coord_str)
        hasher = WordHasher(key=args.key) if args.key else _default_hasher
        if args.words == 3:
            result = hasher.three_words(latlon)
        elif args.words == 4:
            result = hasher.four_words(latlon)
        elif args.words == 6:
            result = hasher.six_words(latlon)
        print("Encoded address:", result)
    elif args.command == "decode":
        address = args.address.replace('.', '-')
        hasher = WordHasher(key=args.key) if args.key else _default_hasher
        result = hasher.decode(address)
        print("Decoded coordinates:", result)

if __name__ == '__main__':
    main()
