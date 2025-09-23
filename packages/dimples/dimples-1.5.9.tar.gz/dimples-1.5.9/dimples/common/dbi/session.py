# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2022 Albert Moky
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

from abc import ABC, abstractmethod
from typing import Optional, Any, Dict, List, Tuple
from typing import Iterable

from dimsdk import ID, Identifier, EVERYWHERE
from dimsdk import Station
from dimsdk import ReliableMessage

from ..protocol import LoginCommand


#
#   Service Provider
#


class ProviderInfo:

    # default service provider
    GSP = Identifier.new(name='gsp', address=EVERYWHERE)

    def __init__(self, identifier: ID, chosen: int):
        super().__init__()
        self.identifier = identifier
        self.chosen = chosen

    # Override
    def __str__(self) -> str:
        clazz = self.__class__.__name__
        return '<%s ID="%s" chosen=%d />' % (clazz, self.identifier, self.chosen)

    # Override
    def __repr__(self) -> str:
        clazz = self.__class__.__name__
        return '<%s ID="%s" chosen=%d />' % (clazz, self.identifier, self.chosen)

    @classmethod
    def convert(cls, array: Iterable[Dict[str, Any]]):  # -> List[ProviderInfo]:
        gf = ProviderFactoryManager.general_factory
        return gf.convert_providers(array=array)

    @classmethod
    def revert(cls, providers) -> List[Dict[str, Any]]:
        gf = ProviderFactoryManager.general_factory
        return gf.revert_providers(providers=providers)


class StationInfo:

    def __init__(self, identifier: Optional[ID], host: str, port: int, provider: ID, chosen: int):
        super().__init__()
        if identifier is None:
            identifier = Station.ANY  # 'station@anywhere'
        self.identifier = identifier
        self.host = host
        self.port = port
        self.provider = provider
        self.chosen = chosen

    # Override
    def __str__(self) -> str:
        clazz = self.__class__.__name__
        return '<%s host="%s" port=%d ID="%s" SP="%s" chosen=%d />' % (clazz, self.host, self.port, self.identifier,
                                                                       self.provider, self.chosen)

    # Override
    def __repr__(self) -> str:
        clazz = self.__class__.__name__
        return '<%s host="%s" port=%d ID="%s" SP="%s" chosen=%d />' % (clazz, self.host, self.port, self.identifier,
                                                                       self.provider, self.chosen)

    @classmethod
    def convert(cls, array: Iterable[Dict[str, Any]]):  # -> List[StationInfo]:
        gf = ProviderFactoryManager.general_factory
        return gf.convert_stations(array=array)

    @classmethod
    def revert(cls, stations) -> List[Dict[str, Any]]:
        gf = ProviderFactoryManager.general_factory
        return gf.revert_stations(stations=stations)


class ProviderGeneralFactory:

    def __init__(self):
        super().__init__()

    # noinspection PyMethodMayBeStatic
    def convert_providers(self, array: Iterable[Dict[str, Any]]) -> List[ProviderInfo]:
        providers = []
        for item in array:
            did = item.get('did')
            if did is None:
                did = item.get('ID')
            identifier = ID.parse(identifier=did)
            chosen = item.get('chosen')
            if identifier is None:
                # provider ID error
                continue
            info = ProviderInfo(identifier=identifier, chosen=chosen)
            providers.append(info)
        return providers

    # noinspection PyMethodMayBeStatic
    def revert_providers(self, providers: Iterable[ProviderInfo]) -> List[Dict[str, Any]]:
        array = []
        for item in providers:
            array.append({
                'ID': str(item.identifier),
                'did': str(item.identifier),
                'chosen': item.chosen,
            })
        return array

    # noinspection PyMethodMayBeStatic
    def convert_stations(self, array: Iterable[Dict[str, Any]]) -> List[StationInfo]:
        stations = []
        for item in array:
            did = item.get('did')
            if did is None:
                did = item.get('ID')
            identifier = ID.parse(identifier=did)
            host = item.get('host')
            port = item.get('port')
            provider = ID.parse(identifier=item.get('provider'))
            chosen = item.get('chosen')
            if host is None or port is None:  # or provider is None:
                # station socket error
                continue
            if chosen is None:
                chosen = 0
            info = StationInfo(identifier=identifier, host=host, port=port, provider=provider, chosen=chosen)
            stations.append(info)
        return stations

    # noinspection PyMethodMayBeStatic
    def revert_stations(self, stations: Iterable[StationInfo]) -> List[Dict[str, Any]]:
        array = []
        for item in stations:
            array.append({
                'ID': str(item.identifier),
                'did': str(item.identifier),
                'host': item.host,
                'port': item.port,
                'provider': str(item.provider),
                'chosen': item.chosen,
            })
        return array


class ProviderFactoryManager:

    general_factory = ProviderGeneralFactory()


class ProviderDBI(ABC):
    """ Provider Stations Table """

    @abstractmethod
    async def all_providers(self) -> List[ProviderInfo]:
        """ get list of (SP_ID, chosen) """
        raise NotImplemented

    @abstractmethod
    async def add_provider(self, identifier: ID, chosen: int = 0) -> bool:
        raise NotImplemented

    @abstractmethod
    async def update_provider(self, identifier: ID, chosen: int) -> bool:
        raise NotImplemented

    @abstractmethod
    async def remove_provider(self, identifier: ID) -> bool:
        raise NotImplemented


class StationDBI(ABC):

    @abstractmethod
    async def all_stations(self, provider: ID) -> List[StationInfo]:
        """ get list of (host, port, SP_ID, chosen) """
        raise NotImplemented

    @abstractmethod
    async def add_station(self, identifier: Optional[ID], host: str, port: int, provider: ID,
                          chosen: int = 0) -> bool:
        raise NotImplemented

    @abstractmethod
    async def update_station(self, identifier: Optional[ID], host: str, port: int, provider: ID,
                             chosen: int = None) -> bool:
        raise NotImplemented

    @abstractmethod
    async def remove_station(self, host: str, port: int, provider: ID) -> bool:
        raise NotImplemented

    @abstractmethod
    async def remove_stations(self, provider: ID) -> bool:
        raise NotImplemented


class LoginDBI(ABC):
    """ Login Command Table """

    #
    #   login command message
    #
    @abstractmethod
    async def get_login_command_message(self, user: ID) -> Tuple[Optional[LoginCommand], Optional[ReliableMessage]]:
        raise NotImplemented

    @abstractmethod
    async def save_login_command_message(self, user: ID, content: LoginCommand, msg: ReliableMessage) -> bool:
        raise NotImplemented


# noinspection PyAbstractClass
class SessionDBI(ProviderDBI, StationDBI, LoginDBI, ABC):
    """ Session Database """
    pass
