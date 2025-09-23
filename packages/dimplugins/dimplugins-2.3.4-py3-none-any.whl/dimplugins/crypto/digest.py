# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2020 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

"""
    Message Digest
    ~~~~~~~~~~~~~~

    SHA-256, Keccak256, RipeMD-160, ...
"""

import hashlib

from Crypto.Hash import keccak

from dimp import MessageDigester


class SHA256Digester(MessageDigester):

    # Override
    def digest(self, data: bytes) -> bytes:
        """ SHA-256 """
        hash_obj = hashlib.sha256(data)
        return hash_obj.digest()


class KECCAK256Digester(MessageDigester):

    # Override
    def digest(self, data: bytes) -> bytes:
        """ Keccak256 digest """
        hash_obj = keccak.new(digest_bits=256)
        hash_obj.update(data)
        return hash_obj.digest()


class RIPEMD160Digester(MessageDigester):

    # Override
    def digest(self, data: bytes) -> bytes:
        """ RipeMD-160 """
        hash_obj = hashlib.new('ripemd160')
        hash_obj.update(data)
        return hash_obj.digest()
