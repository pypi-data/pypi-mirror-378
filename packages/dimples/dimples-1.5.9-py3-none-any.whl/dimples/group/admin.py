# -*- coding: utf-8 -*-
#
#   DIM-SDK : Decentralized Instant Messaging Software Development Kit
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

from typing import List

from dimsdk import ID, Document, Bulletin
from dimsdk import Station
from dimsdk import DocumentCommand

from .delegate import TripletsHelper


class AdminManager(TripletsHelper):

    async def update_administrators(self, administrators: List[ID], group: ID) -> bool:
        """
        Update 'administrators' in bulletin document
        (broadcast new document to all members and neighbor station)

        :param administrators: admin list
        :param group:          group ID
        :return: False on error
        """
        assert group.is_group, 'group ID error: %s' % group
        facebook = self.facebook
        delegate = self.delegate
        #
        #   0. get current user
        #
        user = await facebook.current_user
        if user is None:
            self.error(msg='failed to get current user')
            return False
        me = user.identifier
        sign_key = await facebook.private_key_for_visa_signature(identifier=me)
        assert sign_key is not None, 'failed to get sign key for current user: %s' % me
        #
        #   1. check permission
        #
        is_owner = await delegate.is_owner(user=me, group=group)
        if not is_owner:
            self.warning(msg='cannot update administrators for group: %s, %s' % (group, me))
            return False
        #
        #   2. update document
        #
        doc = await delegate.get_bulletin(group)
        if doc is None:
            # TODO: create new one?
            self.error(msg='failed to get group document: %s, owner: %s' % (group, me))
            return False
        else:
            # clone for modifying
            clone = Document.parse(document=doc.copy_dictionary())
            if isinstance(clone, Bulletin):
                doc = clone
            else:
                assert False, 'bulletin error: %s, %s' % (group, doc)
        # update new bulletin document
        doc.set_property(name='administrators', value=ID.revert(identifiers=administrators))
        signature = None if sign_key is None else doc.sign(private_key=sign_key)
        if signature is None:
            self.error(msg='failed to sign document for group: %s, owner: %s' % (group, me))
            return False
        elif not await delegate.save_document(document=doc):
            self.error(msg='failed to save document for group: %s' % group)
            return False
        else:
            self.info(msg='group document updated: %s' % group)
        #
        #   3. broadcast bulletin document
        #
        assert isinstance(doc, Bulletin), 'group document error: %s' % doc
        return await self.broadcast_document(document=doc)

    async def broadcast_document(self, document: Bulletin) -> bool:
        facebook = self.facebook
        messenger = self.messenger
        assert facebook is not None and messenger is not None,\
            'facebook messenger not ready: %s, %s' % (facebook, messenger)
        delegate = self.delegate
        #
        #   0. get current user
        #
        user = await facebook.current_user
        if user is None:
            self.error(msg='failed to get current user')
            return False
        me = user.identifier
        #
        #   1. create 'document' command, and send to current station
        #
        group = document.identifier
        meta = await facebook.get_meta(identifier=group)
        content = DocumentCommand.response(identifier=group, meta=meta, documents=[document])
        await messenger.send_content(sender=me, receiver=Station.ANY, content=content, priority=1)
        #
        #   2. check group bots
        #
        bots = await delegate.get_assistants(identifier=group)
        if len(bots) > 0:
            # group bots exist, let them to deliver to all other members
            for item in bots:
                if me == item:
                    self.info(msg='skip cycled message: %s' % item)
                    continue
                await messenger.send_content(sender=me, receiver=item, content=content, priority=1)
            return True
        #
        #   3. broadcast to all members
        #
        members = await delegate.get_members(identifier=group)
        if len(members) == 0:
            self.error(msg='failed to get group members: %s' % group)
            return False
        for item in members:
            if me == item:
                self.info(msg='skip cycled message: %s' % item)
                continue
            await messenger.send_content(sender=me, receiver=item, content=content, priority=1)
        return True
