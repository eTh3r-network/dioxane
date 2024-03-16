#
# This file is part of the eTh3r project, written, hosted and distributed under MIT License
#  - eTh3r network, 2023-2024
#

import gnupg

from identity_provider.identity_provider import IdentityProvider
from models.identity import Identity

gpg = gnupg.GPG()

# UNTESTED
class GPGKeyProvider(IdentityProvider):
    @staticmethod
    def getIdentity(identity: str) -> Identity:
        # TODO : This is only the backbone of GPG Key Provider
        # It hasn't been verified and may not even work
        key = gpg.export_keys(identity, False, armor=False)
        key_id = int(f"0x1312") # Todo : use gpg to get key_id
        return Identity(name=identity,
                        key_length=len(hex(key))-2,
                        key=hex(key),
                        key_id_length=len(hex(key_id))-2,
                        key_id=hex(key_id))
