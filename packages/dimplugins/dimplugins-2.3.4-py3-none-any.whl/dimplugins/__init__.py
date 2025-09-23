# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2019 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2019 Albert Moky
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
    Decentralized Instant Messaging (Python Plugins)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from dimp.ext import *

from .crypto import *
from .format import *

from .mkm import *
from .dkd import *
from .ext import *

from .ext_loader import ContentParser, CommandParser
from .ext_loader import ExtensionLoader
from .plugin_loader import PluginLoader


__all__ = [

    'SymmetricKeyHelper', 'PublicKeyHelper', 'PrivateKeyHelper',
    # 'CryptoExtensions',
    'GeneralCryptoHelper', 'SharedCryptoExtensions',

    'TransportableDataHelper', 'PortableNetworkFileHelper',
    # 'FormatExtensions',
    'GeneralFormatHelper', 'SharedFormatExtensions',

    'AddressHelper', 'IdentifierHelper',
    'MetaHelper', 'DocumentHelper',
    # 'AccountExtensions',
    'GeneralAccountHelper', 'SharedAccountExtensions',

    'ContentHelper', 'EnvelopeHelper',
    'InstantMessageHelper', 'SecureMessageHelper', 'ReliableMessageHelper',
    # 'MessageExtensions',
    'GeneralMessageHelper', 'SharedMessageExtensions',

    'CommandHelper',
    # 'CommandExtensions',
    'GeneralCommandHelper', 'SharedCommandExtensions',

    #
    #   Crypto
    #

    'PlainKey', 'PlainKeyFactory',
    'AESKey', 'AESKeyFactory',

    'RSAPublicKey', 'RSAPublicKeyFactory',
    'RSAPrivateKey', 'RSAPrivateKeyFactory',

    'ECCPublicKey', 'ECCPublicKeyFactory',
    'ECCPrivateKey', 'ECCPrivateKeyFactory',

    #
    #   Message Digest
    #

    'SHA256Digester', 'KECCAK256Digester', 'RIPEMD160Digester',

    #
    #   Format
    #

    'Base64Coder', 'Base58Coder', 'HexCoder',
    'JSONCoder', 'UTF8Coder',

    'Base64Data', 'Base64DataFactory',
    'BaseNetworkFile', 'BaseNetworkFileFactory',

    #
    #   MingKeMing
    #

    'BTCAddress', 'ETHAddress',
    'BaseAddressFactory',

    'GeneralIdentifierFactory',

    'DefaultMeta', 'BTCMeta', 'ETHMeta',
    'BaseMetaFactory',

    'GeneralDocumentFactory',

    #
    #   DaoKeDao
    #

    'GeneralCommandFactory',
    'HistoryCommandFactory',
    'GroupCommandFactory',

    'MessageFactory',

    #
    #   Core Extensions
    #

    'CryptographyKeyGeneralFactory', 'FormatGeneralFactory',
    'AccountGeneralFactory',
    'MessageGeneralFactory', 'CommandGeneralFactory',

    #
    #   Loaders
    #

    'ContentParser', 'CommandParser',
    'ExtensionLoader',
    'PluginLoader',

]
