from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from nummus import exceptions as exc
from nummus.models import Tag

if TYPE_CHECKING:

    from sqlalchemy import orm


def test_init_properties(session: orm.Session, rand_str: str) -> None:
    d = {"name": rand_str}

    t = Tag(**d)
    session.add(t)
    session.commit()

    assert t.name == d["name"]


def test_short() -> None:
    with pytest.raises(exc.InvalidORMValueError):
        Tag(name="a")
