#
# Copyright (c) 2022-present
#   Joachim Fenkes <git@dojoe.net>
#   Bryce Wilson Zunawe
#   Didier Malenfant <didier@malenfant.net>
#
# This file is part of TraktorBuddy.
#
# TraktorBuddy is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TraktorBuddy is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with TraktorBuddy. If not,
# see <https://www.gnu.org/licenses/>.
#

# This file implements the modified MD5 hash used by Traktor to compute the names of
# Stripe, Transient and extracted Stems files (and maybe others too)
import base64

from pathlib import Path

# md5Step() converted from @Zunawe's implementation on GitHub - thanks!

A = 0x67452301
B = 0xefcdab89
C = 0x98badcfe
D = 0x10325476

S = [
    7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22, 7, 12, 17, 22,
    5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20, 5,  9, 14, 20,  # noqa: E241
    4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23, 4, 11, 16, 23,
    6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21, 6, 10, 15, 21,
]

K = [
    0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
    0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
    0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
    0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
    0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
    0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
    0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
    0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
    0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
    0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
    0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
    0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
    0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
    0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
    0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
    0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391,
]


#
# Rotates a 32-bit word left by n bits
#
def rotate_left(x: int, n: int) -> int:
    x &= 0xFFFFFFFF
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def md5_step(ctx: list[int], data: bytes) -> None:
    input_value = [int.from_bytes(data[i * 4:i * 4 + 4], 'little') for i in range(16)]

    aa = ctx[0]
    bb = ctx[1]
    cc = ctx[2]
    dd = ctx[3]

    for i in range(64):
        if i < 16:
            e = ((bb & cc) | (~bb & dd))
            j = i
        elif i < 32:
            e = ((bb & dd) | (cc & ~dd))
            j = ((i * 5) + 1) % 16
        elif i < 48:
            e = (bb ^ cc ^ dd)
            j = ((i * 3) + 5) % 16
        else:
            e = (cc ^ (bb | ~dd))
            j = (i * 7) % 16

        temp = dd
        dd = cc
        cc = bb
        bb = bb + rotate_left(aa + e + K[i] + input_value[j], S[i])
        aa = temp

    ctx[0] = (ctx[0] + aa) & 0xFFFFFFFF
    ctx[1] = (ctx[1] + bb) & 0xFFFFFFFF
    ctx[2] = (ctx[2] + cc) & 0xFFFFFFFF
    ctx[3] = (ctx[3] + dd) & 0xFFFFFFFF


class TraktorHash:
    """
    Encapsulates the routines needed to generate a hashed file name from an Audio ID.
    Typical usage:
      path = TraktorHash(audio_id).fullpath(base_dir)
    """

    ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ012345'

    def __init__(self, audio_id: str):
        audio_id_bytes = base64.b64decode(audio_id)
        hash_value = self.hash(audio_id_bytes)
        self.dir_num, self.filename = self.hash2filename(hash_value)

    @property
    def fullname(self) -> Path:
        """
        The full name for a track, consisting of numbered directory and hashed file name.
        """
        return Path('%03d' % self.dir_num) / self.filename

    @staticmethod
    def hash(audio_id_bytes: bytes) -> list[int]:
        """
        MD5 variant used by Traktor
        """
        ctx = [A, B, C, D]
        for i in range(4):
            md5_step(ctx, audio_id_bytes[i * 64:i * 64 + 64])

        # this is what a true md5 would do (after exactly 256 bytes of input):
        # md5Step(ctx, bytes.fromhex('8000000000000000000000000000000000000000000000000000000000000000000000000
        #                             0000000000000000000000000000000000000000008000000000000'))
        # and this is what Traktor does:
        md5_step(ctx, bytes(64))

        return ctx

    @staticmethod
    def hash2filename(hash_value: list[int]) -> tuple[int, str]:
        """
        Determine base32ish stripe filename and directory number from hash
        """
        filename = []
        for i in range(4):
            for j in range(7):
                filename.append(TraktorHash.ALPHABET[(hash_value[i] >> 5 * j) & 0x1F])
        return hash_value[0] & 127, ''.join(filename)
