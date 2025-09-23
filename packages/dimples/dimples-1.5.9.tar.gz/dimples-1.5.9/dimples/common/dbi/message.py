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
from typing import Optional, Dict, List

from dimsdk import ID, ReliableMessage, CipherKeyDelegate


class ReliableMessageDBI(ABC):
    """ ReliableMessage Table """

    CACHE_LIMIT = 20480  # only cache last messages

    @abstractmethod
    async def get_reliable_messages(self, receiver: ID, limit: int = 1024) -> List[ReliableMessage]:
        """
        Get network messages

        :param receiver: actual receiver
        :param limit:    cache limit
        :return: last cached messages
        """
        raise NotImplemented

    @abstractmethod
    async def cache_reliable_message(self, msg: ReliableMessage, receiver: ID) -> bool:
        raise NotImplemented

    @abstractmethod
    async def remove_reliable_message(self, msg: ReliableMessage, receiver: ID) -> bool:
        raise NotImplemented


# noinspection PyAbstractClass
class CipherKeyDBI(CipherKeyDelegate, ABC):
    """ CipherKey Table """
    pass


class GroupKeysDBI(ABC):
    """ Group Keys Table """

    @abstractmethod
    async def get_group_keys(self, group: ID, sender: ID) -> Optional[Dict[str, str]]:
        raise NotImplemented

    @abstractmethod
    async def save_group_keys(self, group: ID, sender: ID, keys: Dict[str, str]) -> bool:
        raise NotImplemented


# noinspection PyAbstractClass
class MessageDBI(ReliableMessageDBI, CipherKeyDBI, GroupKeysDBI, ABC):
    """ Message Database """
    pass
