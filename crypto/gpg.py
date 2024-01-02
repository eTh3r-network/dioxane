#
# This file is part of the eTh3r project, written, hosted and distributed under MIT License
#  - eTh3r network, 2023-2024
#

import gnupg

gpg = gnupg.GPG()

def getKey(key_id):
    return gpg.export_keys(key_id, False, armor=False)
