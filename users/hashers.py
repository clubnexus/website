from django.contrib.auth.hashers import PBKDF2PasswordHasher

import hashlib

class PBKDF2SHA512PasswordHasher(PBKDF2PasswordHasher):
    algorithm = "pbkdf2_sha512"
    iterations = 60000
    digest = hashlib.sha512