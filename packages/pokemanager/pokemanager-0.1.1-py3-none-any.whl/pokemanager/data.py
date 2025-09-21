"""."""

from dataclasses import InitVar, dataclass, field
from typing import Optional

from pokemanager.const import SCORES, TYPE, Dual, Scores, Type


@dataclass(frozen=True)
class Soul:
    """A Pokémon Soul."""

    name: str
    nickname: str
    elected_type: InitVar[TYPE]
    auxiliary_type: InitVar[Optional[TYPE]] = None
    type1: Type = field(init=False)
    type2: Optional[Type] = field(init=False)
    lost: bool = False
    dead: bool = False
    score: float = field(init=False)

    def __post_init__(self, elected_type: TYPE, auxiliary_type: Optional[TYPE]):
        """Set dual and score after initialization."""
        object.__setattr__(self, "type1", Type[elected_type])
        if auxiliary_type is None:
            object.__setattr__(self, "type2", None)
            object.__setattr__(self, "score", Scores[frozenset((elected_type,))])
        else:
            object.__setattr__(self, "type2", Type[auxiliary_type])
            object.__setattr__(self, "score", Scores[frozenset((elected_type, auxiliary_type))])


@dataclass(frozen=True)
class Pokemon:
    """A Pokémon."""

    party: bool = field(init=False)
    met: str = field(init=False)
    name: str
    nickname: str
    elected_type: InitVar[TYPE]
    auxiliary_type: InitVar[Optional[TYPE]] = None
    type1: Type = field(init=False)
    type2: Optional[Type] = field(init=False)
    lost: bool = False
    dead: bool = False
    score: float = field(init=False)

    def __post_init__(self, elected_type: TYPE, auxiliary_type: Optional[TYPE]):
        """Set dual and score after initialization."""
        object.__setattr__(self, "type1", Type[elected_type])
        if auxiliary_type is None:
            object.__setattr__(self, "type2", None)
            object.__setattr__(self, "score", Scores[frozenset((elected_type,))])
        else:
            object.__setattr__(self, "type2", Type[auxiliary_type])
            object.__setattr__(self, "score", Scores[frozenset((elected_type, auxiliary_type))])


@dataclass(frozen=True)
class Soullink:
    """A soullink between two Pokémon souls."""

    party: bool
    met: str
    p1: Soul
    p2: Soul

    def is_lost(self) -> bool:
        """Check if either soul is lost."""
        return self.p1.lost or self.p2.lost

    def is_dead(self) -> bool:
        """Check if either soul is dead."""
        return self.p1.dead or self.p2.dead

    def is_lost_or_dead(self) -> bool:
        """Check if either soul is lost or dead."""
        return self.is_dead() or self.is_lost()

    def get_data(self) -> list[bool | str]:
        """Get soullink data as a list."""
        return [
            self.party,
            self.met,
            self.p1.type1.name,
            self.p1.type2.name if self.p1.type2 else "",
            self.p1.name,
            self.p1.nickname,
            self.p1.lost,
            self.p1.dead,
            self.p2.type1.name,
            self.p2.type2.name if self.p2.type2 else "",
            self.p2.name,
            self.p2.nickname,
            self.p2.lost,
            self.p2.dead,
        ]
