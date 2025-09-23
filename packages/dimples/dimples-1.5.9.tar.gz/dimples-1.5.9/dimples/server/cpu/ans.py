# -*- coding: utf-8 -*-
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

"""
    Command Processor for 'ans'
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    ANS protocol
"""

from typing import Optional, List

from dimsdk import ID
from dimsdk import ReliableMessage
from dimsdk import Content

from dimsdk.cpu import BaseCommandProcessor

from ...utils import Log
from ...common import AnsCommand


class AnsCommandProcessor(BaseCommandProcessor):

    # Override
    async def process_content(self, content: Content, r_msg: ReliableMessage) -> List[Content]:
        assert isinstance(content, AnsCommand), 'report command error: %s' % content
        names = content.names
        if len(names) == 0:
            text = 'ANS command error.'
            return self._respond_receipt(text=text, envelope=r_msg.envelope, content=content, extra={})
        records = {}
        missed = []
        for item in names:
            # get record from ANS factory
            identifier = self.ans_id(name=item)
            if identifier is None:
                missed.append(item)
            else:
                records[item] = str(identifier)
        res = AnsCommand.response(names=names, records=records)
        if len(missed) > 0:
            res['missed'] = missed
        return [res]

    @classmethod
    def ans_id(cls, name: str) -> Optional[ID]:
        try:
            return ID.parse(identifier=name)
        except ValueError as e:
            Log.warning(msg='ANS record not exists: %s, %s' % (name, e))
