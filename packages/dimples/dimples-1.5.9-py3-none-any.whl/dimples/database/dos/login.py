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

from typing import Optional, Tuple

from dimsdk import ID
from dimsdk import ReliableMessage

from ...utils import template_replace
from ...common import LoginDBI, LoginCommand

from .base import Storage


class LoginStorage(Storage, LoginDBI):
    """
        Login Command Storage
        ~~~~~~~~~~~~~~~~~~~~~
        file path: '.dim/public/{ADDRESS}/login.js'
    """

    login_path = '{PUBLIC}/{ADDRESS}/login.js'

    def show_info(self):
        path = self.public_path(self.login_path)
        print('!!!      login cmd path: %s' % path)

    def __login_path(self, identifier: ID) -> str:
        path = self.public_path(self.login_path)
        return template_replace(path, key='ADDRESS', value=str(identifier.address))

    #
    #   Login DBI
    #

    # Override
    async def get_login_command_message(self, user: ID) -> Tuple[Optional[LoginCommand], Optional[ReliableMessage]]:
        """ load login command from file """
        path = self.__login_path(identifier=user)
        self.info(msg='Loading login command from: %s' % path)
        info = await self.read_json(path=path)
        if info is None:
            # command not found
            return None, None
        cmd = info.get('cmd')
        msg = info.get('msg')
        if cmd is not None:
            cmd = LoginCommand(content=cmd)
        return cmd, ReliableMessage.parse(msg=msg)

    # Override
    async def save_login_command_message(self, user: ID, content: LoginCommand, msg: ReliableMessage) -> bool:
        """ save login command into file """
        info = {
            'cmd': content.dictionary,
            'msg': msg.dictionary
        }
        path = self.__login_path(identifier=user)
        self.info(msg='Saving login command into: %s' % path)
        return await self.write_json(container=info, path=path)
