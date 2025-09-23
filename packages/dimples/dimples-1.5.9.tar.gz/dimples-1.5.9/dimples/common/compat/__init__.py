# -*- coding: utf-8 -*-
#
#   Ming-Ke-Ming : Decentralized User Identity Authentication
#
#                                Written in 2023 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2023 Albert Moky
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

from .network import NetworkType, network_to_type

from .entity import EntityIDFactory
from .entity import EntityID

from .address import CompatibleAddressFactory
from .address import UnknownAddress

from .meta import CompatibleMetaFactory

from .loader import CommonExtensionLoader
from .loader import CommonPluginLoader
from .loader import LibraryLoader

from .compressor import CompatibleCompressor  # , CompatibleShortener
from .compatible import Compatible, CompatibleIncoming, CompatibleOutgoing


__all__ = [

    'NetworkType', 'network_to_type',

    'EntityIDFactory',
    'EntityID',

    'CompatibleAddressFactory',
    'UnknownAddress',

    'CompatibleMetaFactory',

    'CommonExtensionLoader',
    'CommonPluginLoader',
    'LibraryLoader',

    'CompatibleCompressor',  # 'CompatibleShortener',
    'Compatible', 'CompatibleIncoming', 'CompatibleOutgoing',

]
