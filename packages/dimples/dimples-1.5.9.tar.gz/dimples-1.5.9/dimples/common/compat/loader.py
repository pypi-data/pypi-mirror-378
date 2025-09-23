# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2024 Albert Moky
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

from typing import Optional, Any

from dimsdk import Converter, BaseConverter
from dimsdk import DateTime
from dimsdk import ID, Address, Meta
from dimsdk import ContentType
from dimsdk import MetaType
from dimsdk import AppCustomizedContent
from dimplugins import ExtensionLoader
from dimplugins import PluginLoader

from ...utils.digest import MD5, MD5Digester
from ...utils.digest import SHA1, SHA1Digester

from ..protocol import HandshakeCommand, BaseHandshakeCommand
from ..protocol import LoginCommand
from ..protocol import ReportCommand
from ..protocol import AnsCommand
from ..protocol import MuteCommand, BlockCommand
from ..protocol import QueryCommand, QueryGroupCommand

from ..ans import AddressNameServer, ANSFactory
from ..facebook import CommonFacebook

from .entity import EntityIDFactory
from .address import CompatibleAddressFactory
from .meta import CompatibleMetaFactory


class LibraryLoader:

    def __init__(self, extensions: ExtensionLoader = None, plugins: PluginLoader = None):
        super().__init__()
        self.__extensions = CommonExtensionLoader() if extensions is None else extensions
        self.__plugins = CommonPluginLoader() if plugins is None else plugins
        self.__loaded = False

    def run(self):
        if self.__loaded:
            # no need to load it again
            return
        else:
            # mark it to loaded
            self.__loaded = True
        # try to load all plugins
        self.load()

    def load(self):
        self.__extensions.load()
        self.__plugins.load()


class CommonExtensionLoader(ExtensionLoader):
    """ Extensions Loader """

    # Override
    def _register_customized_factories(self):
        self._set_content_factory(ContentType.APPLICATION, alias='application', content_class=AppCustomizedContent)
        self._set_content_factory(ContentType.CUSTOMIZED, alias='customized', content_class=AppCustomizedContent)

    # Override
    def _register_command_factories(self):
        super()._register_command_factories()
        # Handshake
        self._set_command_factory(cmd=HandshakeCommand.HANDSHAKE, command_class=BaseHandshakeCommand)
        # Login
        self._set_command_factory(cmd=LoginCommand.LOGIN, command_class=LoginCommand)
        # Report
        self._set_command_factory(cmd=ReportCommand.REPORT, command_class=ReportCommand)
        # ANS
        self._set_command_factory(cmd=AnsCommand.ANS, command_class=AnsCommand)
        # Mute
        self._set_command_factory(cmd=MuteCommand.MUTE, command_class=MuteCommand)
        # Block
        self._set_command_factory(cmd=BlockCommand.BLOCK, command_class=BlockCommand)
        # Group command (deprecated)
        self._set_command_factory(cmd=QueryCommand.QUERY, command_class=QueryGroupCommand)


# noinspection PyMethodMayBeStatic
class CommonPluginLoader(PluginLoader):
    """ Plugin Loader """

    # Override
    def load(self):
        Converter.converter = _SafeConverter()
        super().load()

    # Override
    def _register_digesters(self):
        super()._register_digesters()
        self._register_md5_digesters()
        self._register_sha1_digesters()

    def _register_md5_digesters(self):
        MD5.digester = MD5Digester()

    def _register_sha1_digesters(self):
        SHA1.digester = SHA1Digester()

    # Override
    def _register_id_factory(self):
        ans = AddressNameServer()
        factory = EntityIDFactory()
        ID.set_factory(factory=ANSFactory(factory=factory, ans=ans))
        CommonFacebook.ans = ans

    # Override
    def _register_address_factory(self):
        Address.set_factory(factory=CompatibleAddressFactory())

    # Override
    def _register_meta_factories(self):
        mkm = CompatibleMetaFactory(version=MetaType.MKM)
        btc = CompatibleMetaFactory(version=MetaType.BTC)
        eth = CompatibleMetaFactory(version=MetaType.ETH)
        Meta.set_factory(version='1', factory=mkm)
        Meta.set_factory(version='2', factory=btc)
        Meta.set_factory(version='4', factory=eth)
        Meta.set_factory(version='mkm', factory=mkm)
        Meta.set_factory(version='btc', factory=btc)
        Meta.set_factory(version='eth', factory=eth)
        Meta.set_factory(version='MKM', factory=mkm)
        Meta.set_factory(version='BTC', factory=btc)
        Meta.set_factory(version='ETH', factory=eth)

    # TODO: RSA keys with created time


class _SafeConverter(BaseConverter):

    # Override
    def get_bool(self, value: Any, default: Optional[bool]) -> Optional[bool]:
        try:
            return super().get_bool(value=value, default=default)
        except ValueError:
            return default

    # Override
    def get_int(self, value: Any, default: Optional[int]) -> Optional[int]:
        try:
            return super().get_int(value=value, default=default)
        except ValueError:
            return default

    # Override
    def get_float(self, value: Any, default: Optional[float]) -> Optional[float]:
        try:
            return super().get_float(value=value, default=default)
        except ValueError:
            return default

    # Override
    def get_datetime(self, value: Any, default: Optional[DateTime]) -> Optional[DateTime]:
        try:
            return super().get_datetime(value=value, default=default)
        except ValueError:
            return default
