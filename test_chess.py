
from chess import *

b = Board()

assert not b.king_can_castle_short(BLACK_KING)
assert not b.king_can_castle_long(BLACK_KING)

assert not b.king_can_castle_short(WHITE_KING)
assert not b.king_can_castle_long(WHITE_KING)
