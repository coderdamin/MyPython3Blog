import re;

_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}');
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}');
