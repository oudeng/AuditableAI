"""Seven-field scientific claim record with a content fingerprint.

A fingerprint detects content changes; it does not authenticate a claim.
"""
from dataclasses import asdict, dataclass
import hashlib
import json


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


@dataclass
class ClaimRecord:
    clm: str
    scp: dict
    art: dict
    ref: dict
    pro: dict
    evd: dict
    bnd: str

    def to_dict(self):
        value = asdict(self)
        return {**value, 'record_sha256': fingerprint(value)}

