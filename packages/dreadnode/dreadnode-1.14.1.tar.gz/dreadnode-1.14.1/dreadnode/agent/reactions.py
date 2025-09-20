import typing as t

import rigging as rg
from pydantic import ConfigDict, Field
from pydantic.dataclasses import dataclass

if t.TYPE_CHECKING:
    from dreadnode.agent.events import AgentEvent


@dataclass
class Reaction(Exception): ...  # noqa: N818


@dataclass
class Continue(Reaction):
    messages: list[rg.Message] = Field(repr=False)


@dataclass
class Retry(Reaction):
    messages: list[rg.Message] | None = Field(None, repr=False)


@dataclass
class RetryWithFeedback(Reaction):
    feedback: str


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Fail(Reaction):
    error: Exception | str


@dataclass
class Finish(Reaction):
    reason: str | None = None


@t.runtime_checkable
class Hook(t.Protocol):
    def __call__(self, event: "AgentEvent") -> "t.Awaitable[Reaction | None]": ...
