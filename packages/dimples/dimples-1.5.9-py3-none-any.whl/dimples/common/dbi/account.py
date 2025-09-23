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
from typing import Optional, Union, Dict, List, Tuple
from typing import Iterable

from dimsdk import PrivateKey, SignKey, DecryptKey
from dimsdk import ID, Meta, Document
from dimsdk import ReliableMessage
from dimsdk import GroupCommand, ResetCommand


class PrivateKeyDBI(ABC):
    """ PrivateKey Table """

    META = 'M'  # ID_KEY_TAG
    VISA = 'V'  # MSG_KEY_TAG

    @abstractmethod
    async def save_private_key(self, key: PrivateKey, user: ID, key_type: str = 'M') -> bool:
        raise NotImplemented

    @abstractmethod
    async def private_keys_for_decryption(self, user: ID) -> List[DecryptKey]:
        raise NotImplemented

    @abstractmethod
    async def private_key_for_signature(self, user: ID) -> Optional[SignKey]:
        raise NotImplemented

    @abstractmethod
    async def private_key_for_visa_signature(self, user: ID) -> Optional[SignKey]:
        raise NotImplemented

    #
    #  Conveniences
    #

    @classmethod
    def convert_decrypt_keys(cls, keys: Iterable[PrivateKey]) -> List[DecryptKey]:
        decrypt_keys = []
        for item in keys:
            if isinstance(item, DecryptKey):
                decrypt_keys.append(item)
        return decrypt_keys

    @classmethod
    def convert_private_keys(cls, keys: Iterable[DecryptKey]) -> List[PrivateKey]:
        private_keys = []
        for item in keys:
            if isinstance(item, PrivateKey):
                private_keys.append(item)
        return private_keys

    @classmethod
    def revert_private_keys(cls, keys: Iterable[PrivateKey]) -> List[Dict]:
        array = []
        for item in keys:
            array.append(item.dictionary)
        return array

    @classmethod
    def insert(cls, item: PrivateKey, array: List[PrivateKey]) -> Optional[List[PrivateKey]]:
        index = cls.find(item=item, array=array)
        if index == 0:
            # nothing changed
            return None
        elif index > 0:
            # move to the front
            array.pop(index)
        elif len(array) > 2:
            # keep only last three records
            array.pop()
        array.insert(0, item)
        return array

    @classmethod
    def find(cls, item: Union[DecryptKey, PrivateKey], array: List[PrivateKey]) -> int:
        index = 0
        data = item.get('data')
        for key in array:
            if key.get('data') == data:
                return index
            index += 1
        return -1


class MetaDBI(ABC):
    """ Meta Table """

    @abstractmethod
    async def save_meta(self, meta: Meta, identifier: ID) -> bool:
        raise NotImplemented

    @abstractmethod
    async def get_meta(self, identifier: ID) -> Optional[Meta]:
        raise NotImplemented


class DocumentDBI(ABC):
    """ Document Table """

    @abstractmethod
    async def save_document(self, document: Document) -> bool:
        raise NotImplemented

    @abstractmethod
    async def get_documents(self, identifier: ID) -> List[Document]:
        raise NotImplemented


class UserDBI(ABC):
    """ User Table """

    @abstractmethod
    async def get_local_users(self) -> List[ID]:
        """ local user ID list """
        raise NotImplemented

    @abstractmethod
    async def save_local_users(self, users: List[ID]) -> bool:
        raise NotImplemented


class ContactDBI(ABC):
    """ Contact Table """

    @abstractmethod
    async def get_contacts(self, user: ID) -> List[ID]:
        """ contacts for user """
        raise NotImplemented

    @abstractmethod
    async def save_contacts(self, contacts: List[ID], user: ID) -> bool:
        raise NotImplemented


class GroupDBI(ABC):
    """ Group/Member Table """

    @abstractmethod
    async def get_founder(self, group: ID) -> Optional[ID]:
        raise NotImplemented

    @abstractmethod
    async def get_owner(self, group: ID) -> Optional[ID]:
        raise NotImplemented

    @abstractmethod
    async def get_members(self, group: ID) -> List[ID]:
        """ group members """
        raise NotImplemented

    @abstractmethod
    async def save_members(self, members: List[ID], group: ID) -> bool:
        raise NotImplemented

    @abstractmethod
    async def get_assistants(self, group: ID) -> List[ID]:
        """ bots for group """
        raise NotImplemented

    @abstractmethod
    async def save_assistants(self, assistants: List[ID], group: ID) -> bool:
        raise NotImplemented

    @abstractmethod
    async def get_administrators(self, group: ID) -> List[ID]:
        """ group admins """
        raise NotImplemented

    @abstractmethod
    async def save_administrators(self, administrators: List[ID], group: ID) -> bool:
        raise NotImplemented


class GroupHistoryDBI(ABC):
    """ Group History Command Command Table """

    @abstractmethod
    async def save_group_history(self, group: ID, content: GroupCommand, message: ReliableMessage) -> bool:
        """ save group commands:
                invite
                expel (deprecated)
                join
                quit
                reset
                resign
        """
        raise NotImplemented

    @abstractmethod
    async def get_group_histories(self, group: ID) -> List[Tuple[GroupCommand, ReliableMessage]]:
        """ load group commands:
                invite
                expel (deprecated)
                join
                quit
                reset
                resign
        """
        raise NotImplemented

    @abstractmethod
    async def get_reset_command_message(self, group: ID) -> Tuple[Optional[ResetCommand], Optional[ReliableMessage]]:
        """ load last 'reset' group command """
        raise NotImplemented

    @abstractmethod
    async def clear_group_member_histories(self, group: ID) -> bool:
        """ clear group commands for members:
                invite
                expel (deprecated)
                join
                quit
                reset
        """
        raise NotImplemented

    @abstractmethod
    async def clear_group_admin_histories(self, group: ID) -> bool:
        """ clear group commands for administrators:
                resign
        """
        raise NotImplemented


# noinspection PyAbstractClass
class AccountDBI(PrivateKeyDBI, MetaDBI, DocumentDBI, UserDBI, ContactDBI, GroupDBI, GroupHistoryDBI, ABC):
    """ Account Database """
    pass
