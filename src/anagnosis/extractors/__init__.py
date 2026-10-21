"""Feature extractors, one module per family."""
from .surface import Surface
from .syntax import Syntax
from .vocabulary import Vocabulary

ALL = [Surface(), Vocabulary(), Syntax()]
