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

from typing import Optional, List, Tuple

from dimsdk import GroupCommand, ResetCommand
from dimsdk import PrivateKey, DecryptKey, SignKey
from dimsdk import ID, Meta, Document, Bulletin
from dimsdk import ReliableMessage
from dimsdk import MetaUtils

from ..utils import Config
from ..common import AccountDBI

from .t_private import PrivateKeyTable
from .t_meta import MetaTable
from .t_document import DocumentTable
from .t_user import UserTable
from .t_group import GroupTable
from .t_group_history import GroupHistoryTable


class AccountDatabase(AccountDBI):
    """
        Database for MingKeMing
        ~~~~~~~~~~~~~~~~~~~~~~~
    """

    def __init__(self, config: Config):
        super().__init__()
        self._private_table = PrivateKeyTable(config=config)
        self._meta_table = MetaTable(config=config)
        self._doc_table = DocumentTable(config=config)
        self._user_table = UserTable(config=config)
        self._group_table = GroupTable(config=config)
        self._history_table = GroupHistoryTable(config=config)

    def show_info(self):
        self._private_table.show_info()
        self._meta_table.show_info()
        self._doc_table.show_info()
        self._user_table.show_info()
        self._group_table.show_info()
        self._history_table.show_info()

    #
    #   PrivateKey DBI
    #

    # Override
    async def save_private_key(self, key: PrivateKey, user: ID, key_type: str = 'M') -> bool:
        return await self._private_table.save_private_key(key=key, user=user, key_type=key_type)

    # Override
    async def private_keys_for_decryption(self, user: ID) -> List[DecryptKey]:
        return await self._private_table.private_keys_for_decryption(user=user)

    # Override
    async def private_key_for_signature(self, user: ID) -> Optional[SignKey]:
        return await self._private_table.private_key_for_signature(user=user)

    # Override
    async def private_key_for_visa_signature(self, user: ID) -> Optional[SignKey]:
        return await self._private_table.private_key_for_visa_signature(user=user)

    #
    #   Meta DBI
    #

    # Override
    async def save_meta(self, meta: Meta, identifier: ID) -> bool:
        # check meta with ID
        if not MetaUtils.match_identifier(identifier=identifier, meta=meta):
            raise ValueError('meta not match: %s => %s' % (identifier, meta))
        return await self._meta_table.save_meta(meta=meta, identifier=identifier)

    # Override
    async def get_meta(self, identifier: ID) -> Optional[Meta]:
        return await self._meta_table.get_meta(identifier=identifier)

    #
    #   Document DBI
    #

    # Override
    async def save_document(self, document: Document) -> bool:
        # check meta first
        meta = await self._meta_table.get_meta(identifier=document.identifier)
        if meta is None:
            raise LookupError('meta not exists: %s' % document.identifier)
        # check document valid before saving it
        if not (document.valid or document.verify(public_key=meta.public_key)):
            raise ValueError('document error: %s' % document.identifier)
        # check founder in group document
        if isinstance(document, Bulletin):
            founder = document.founder
            if founder is not None:
                f_meta = await self._meta_table.get_meta(identifier=founder)
                if f_meta is None or meta.public_key != meta.public_key:
                    raise ValueError('founder error: %s, group: %s' % (founder, document.identifier))
        # document ok, try to save it
        return await self._doc_table.save_document(document=document)

    # Override
    async def get_documents(self, identifier: ID) -> List[Document]:
        return await self._doc_table.get_documents(identifier=identifier)

    #
    #   User DBI
    #

    # Override
    async def get_local_users(self) -> List[ID]:
        return await self._user_table.get_local_users()

    # Override
    async def save_local_users(self, users: List[ID]) -> bool:
        return await self._user_table.save_local_users(users=users)

    # Override
    async def get_contacts(self, user: ID) -> List[ID]:
        return await self._user_table.get_contacts(user=user)

    # Override
    async def save_contacts(self, contacts: List[ID], user: ID) -> bool:
        return await self._user_table.save_contacts(contacts=contacts, user=user)

    #
    #   Group DBI
    #

    # Override
    async def get_founder(self, group: ID) -> Optional[ID]:
        return await self._group_table.get_founder(group=group)

    # Override
    async def get_owner(self, group: ID) -> Optional[ID]:
        return await self._group_table.get_owner(group=group)

    # Override
    async def get_members(self, group: ID) -> List[ID]:
        return await self._group_table.get_members(group=group)

    # Override
    async def save_members(self, members: List[ID], group: ID) -> bool:
        return await self._group_table.save_members(members=members, group=group)

    # Override
    async def get_assistants(self, group: ID) -> List[ID]:
        return await self._group_table.get_assistants(group=group)

    # Override
    async def save_assistants(self, assistants: List[ID], group: ID) -> bool:
        return await self._group_table.save_assistants(assistants=assistants, group=group)

    # Override
    async def get_administrators(self, group: ID) -> List[ID]:
        return await self._group_table.get_administrators(group=group)

    # Override
    async def save_administrators(self, administrators: List[ID], group: ID) -> bool:
        return await self._group_table.save_administrators(administrators=administrators, group=group)

    #
    #   Group History DBI
    #

    # Override
    async def save_group_history(self, group: ID, content: GroupCommand, message: ReliableMessage) -> bool:
        return await self._history_table.save_group_history(group=group, content=content, message=message)

    # Override
    async def get_group_histories(self, group: ID) -> List[Tuple[GroupCommand, ReliableMessage]]:
        return await self._history_table.get_group_histories(group=group)

    # Override
    async def get_reset_command_message(self, group: ID) -> Tuple[Optional[ResetCommand], Optional[ReliableMessage]]:
        return await self._history_table.get_reset_command_message(group=group)

    # Override
    async def clear_group_member_histories(self, group: ID) -> bool:
        return await self._history_table.clear_group_member_histories(group=group)

    # Override
    async def clear_group_admin_histories(self, group: ID) -> bool:
        return await self._history_table.clear_group_admin_histories(group=group)
