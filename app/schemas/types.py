from typing import Annotated

from pydantic import EmailStr, StringConstraints

Email = EmailStr

Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=30,
        pattern=r"^[a-zA-Z0-9_]+$",
    ),
]

Password = Annotated[
    str,
    StringConstraints(
        min_length=8,
        max_length=128,
    ),
]

DocumentTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=255,
    ),
]

SearchQuery = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        max_length=255,
    ),
]