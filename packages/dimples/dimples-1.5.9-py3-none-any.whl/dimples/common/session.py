# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
#
#                                Written in 2021 by Moky <albert.moky@gmail.com>
#
# ==============================================================================
# MIT License
#
# Copyright (c) 2021 Albert Moky
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
from typing import Optional, Tuple

from startrek.types import SocketAddress

from dimsdk import DateTime
from dimsdk import ID
from dimsdk import Content
from dimsdk import InstantMessage, ReliableMessage

from .dbi import SessionDBI


class Transmitter(ABC):

    @abstractmethod
    async def send_content(self, content: Content, sender: Optional[ID], receiver: ID,
                           priority: int = 0) -> Tuple[InstantMessage, Optional[ReliableMessage]]:
        """
        Send content from sender to receiver with priority

        :param content:  message content
        :param sender:   from where
        :param receiver: to where
        :param priority: smaller is faster
        :return: (i_msg, None) on error
        """
        raise NotImplemented

    @abstractmethod
    async def send_instant_message(self, msg: InstantMessage, priority: int = 0) -> Optional[ReliableMessage]:
        """
        Send instant message with priority

        :param msg:      plain message
        :param priority: smaller is faster
        :return: None on error
        """
        raise NotImplemented

    @abstractmethod
    async def send_reliable_message(self, msg: ReliableMessage, priority: int = 0) -> bool:
        """
        Send reliable message with priority

        :param msg:      encrypted & signed message
        :param priority: smaller is faster
        :return: False on error
        """
        raise NotImplemented


class Session(Transmitter, ABC):

    @property
    def database(self) -> SessionDBI:
        """ Session Database """
        raise NotImplemented

    @property
    def remote_address(self) -> SocketAddress:
        """ Remote (host, port) """
        raise NotImplemented

    @property
    def session_key(self) -> Optional[str]:
        """ Session Key """
        raise NotImplemented

    @property
    def identifier(self) -> Optional[ID]:
        """ Login User ID """
        raise NotImplemented

    def set_identifier(self, identifier: ID) -> bool:
        """ Update ID and return True on changed """
        raise NotImplemented

    @property
    def active(self) -> bool:
        """ Session active """
        raise NotImplemented

    @abstractmethod
    def set_active(self, active: bool, when: DateTime = None) -> bool:
        """ Update active flag and return True on changed """
        raise NotImplemented

    # Override
    def __str__(self) -> str:
        clazz = self.__class__.__name__
        session_key = self.session_key
        remote = self.remote_address
        return '<%s:%s %s|%s active=%s />' % (clazz, session_key, remote, self.identifier, self.active)

    # Override
    def __repr__(self) -> str:
        clazz = self.__class__.__name__
        session_key = self.session_key
        remote = self.remote_address
        return '<%s:%s %s|%s active=%s />' % (clazz, session_key, remote, self.identifier, self.active)

    async def queue_message_package(self, msg: ReliableMessage, data: bytes, priority: int = 0) -> bool:
        """
        Pack message into a waiting queue

        :param msg:      network message
        :param data:     serialized message
        :param priority: smaller is faster
        :return: False on error
        """
        raise NotImplemented
