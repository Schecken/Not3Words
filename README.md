![WordGeo](https://github.com/user-attachments/assets/9dd14b0b-870c-436a-ba47-5d9504a72820)

# WordGeo

Based on the work found here https://github.com/Placeware/ThisPlace

What 3 Words (W3W) is a good way to convert coordinates into readable words so they can be memorised or passed to someone else discreetly. Now that W3W is well known, the privacy of those locations is poor and can be easily converted to find the location being passed.

I decided to have a crack at making it a little more private by applying a key that rotates the words and can be recovered by someone else that knows the key. I know this implementation is already different than W3W as I'm using a different wordlist but it was a worthwhile project either way. You could probably write a wrapper for W3W but I couldn't be bothered with setting up an API key - and the fact that you're requesting an encode/decode from their server is in itself not private anyway.

WordGeo supports 3, 4, or 6 word encode/decode and the following coordinate input formats:
```bash
-33.867480754852295 151.20700120925903
-33.867480754852295,151.20700120925903
-33.867480754852295, 151.20700120925903
```

## Use Cases
- You have a tag or beacon that is spitting out lat/longs and you don't want to transmit those in that format
- You don't want to use W3W because it can be easily reversed
- You want to have multiple tags or beacons, all with different keys

## Install
```bash
pip install -r requirements.txt
```
OR
```bash
pip install bottle
pip install python-geohash
```

## Usage
### Command Line
```bash
# Encode
python wordgeo.py encode -k <KEY> --words 3 "-33.867480754852295,151.20700120925903"

# Decode
python wordgeo.py decode -k <KEY> --words 3 "covary-britt-kydd"
```

### Import
You can import this into your scripts (make sure the files are in the same folder as your script) so you can do conversions on the fly.

> [!IMPORTANT]
> If you include this in your scripts as an import, consider using `argv` to set the key. This is better OPSEC as it won't be hard coded and will only show up in the process list while running (remember to send `.bash_history` to `/dev/null`

```python
>>> import wordgeo
# Set coordinates and convert
>>> sydney = (-33.867480754852295, 151.20700120925903)
>>> print(wordgeo.three_words(sydney))
covary-britt-kydd
# Check that it decodes properly
>>> sydney2 = "covary-britt-kydd"
>>> print(wordgeo.decode(sydney2))
(-33.867480754852295, 151.20700120925903)
# Set the key and show that it decodes differently
>>> wordgeo.set_key("SecretKey")
>>> print(wordgeo.decode(sydney2))
(16.94566011428833, -159.50283765792847)
# Encode the original coordinates again with the key
>>> print(wordgeo.three_words(sydney))
slept-schild-lydda
# Decode to discover correct original coordinates using the key
>>> sydney2 = "slept-schild-lydda"
>>> print(wordgeo.decode(sydney2))
(-33.867480754852295, 151.20700120925903)
```
