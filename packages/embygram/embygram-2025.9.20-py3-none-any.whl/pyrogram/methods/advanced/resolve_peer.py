#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

import logging
import re
from typing import Optional, Union

import pyrogram
from pyrogram import raw, utils
from pyrogram.errors import PeerIdInvalid

log = logging.getLogger(__name__)


class ResolvePeer:
    async def resolve_peer(
        self: "pyrogram.Client",
        peer_id: Union[int, str]
    ) -> Optional["raw.base.InputPeer"]:
        """Get the InputPeer of a known peer id. Useful whenever an InputPeer type is required.

        .. note::

            This is a utility method intended to be used **only** when working with raw
            :obj:`functions <pyrogram.api.functions>` (i.e: a Telegram API method you wish to use which is not
            available yet in the Client class as an easy-to-use method).

        .. include:: /_includes/usable-by/users-bots.rst

        Parameters:
            peer_id (``int`` | ``str``):
                The peer id you want to extract the InputPeer from.
                Can be a direct id (int), a username (str), a link (str) or a phone number (str).

        Returns:
            :obj:`~pyrogram.raw.base.InputPeer`: On success, the resolved peer id is returned in form of an InputPeer object.

        Raises:
            KeyError: In case the peer doesn't exist in the internal database.
        """
        if not self.is_connected:
            raise ConnectionError("Client has not been started yet")

        if peer_id is None:
            return None

        if peer_id in ("self", "me"):
            return raw.types.InputPeerSelf()

        if peer_id == "empty":
            return raw.types.InputPeerEmpty()

        try:
            return await self.storage.get_peer_by_id(peer_id)
        except KeyError:
            if isinstance(peer_id, str):
                match = re.match(r"^(?:https?://)?(?:www\.)?(?:t(?:elegram)?\.(?:org|me|dog)/(?:c/)?)([\w]+)(?:.+)?$", peer_id.lower())

                if match:
                    try:
                        peer_id = utils.get_channel_id(int(match.group(1)))
                    except ValueError:
                        peer_id = match.group(1)
                else:
                    peer_id = re.sub(r"[@+\s]", "", peer_id.lower())

                try:
                    int(peer_id)
                except ValueError:
                    try:
                        return await self.storage.get_peer_by_username(peer_id)
                    except KeyError:
                        r = await self.invoke(
                            raw.functions.contacts.ResolveUsername(
                                username=peer_id
                            )
                        )

                        try:
                            return await self.storage.get_peer_by_id(utils.get_peer_id(r.peer))
                        except KeyError:
                            return await self.storage.get_peer_by_username(peer_id)
                else:
                    try:
                        return await self.storage.get_peer_by_phone_number(peer_id)
                    except KeyError as e:
                        raise PeerIdInvalid from e

            peer_type = utils.get_peer_type(peer_id)

            if peer_type == "user":
                await self.fetch_peers(
                    await self.invoke(
                        raw.functions.users.GetUsers(
                            id=[
                                raw.types.InputUser(
                                    user_id=utils.get_raw_peer_id(peer_id),
                                    access_hash=0
                                )
                            ]
                        )
                    )
                )
            elif peer_type == "chat":
                await self.invoke(
                    raw.functions.messages.GetChats(
                        id=[utils.get_raw_peer_id(peer_id)]
                    )
                )
            else:
                await self.invoke(
                    raw.functions.channels.GetChannels(
                        id=[
                            raw.types.InputChannel(
                                channel_id=utils.get_raw_peer_id(peer_id),
                                access_hash=0
                            )
                        ]
                    )
                )

            try:
                return await self.storage.get_peer_by_id(peer_id)
            except KeyError as e:
                raise PeerIdInvalid from e
