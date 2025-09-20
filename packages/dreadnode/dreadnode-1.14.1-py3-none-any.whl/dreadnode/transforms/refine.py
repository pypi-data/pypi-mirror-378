import typing as t
from collections import defaultdict
from textwrap import dedent, indent

import rigging as rg

from dreadnode.common_types import AnyDict
from dreadnode.meta import Config
from dreadnode.transforms.base import Transform

if t.TYPE_CHECKING:
    from ulid import ULID

    from dreadnode.optimization.trial import Trial

T = t.TypeVar("T")


class Input(rg.Model):
    guidance: str = rg.element()
    context: str = rg.element()


class Refinement(rg.Model):
    reasoning: str = rg.element()
    prompt: str = rg.element()


@rg.prompt
def refine(input: Input) -> Refinement:  # type: ignore [empty-body]
    """
    You will improve, refine, and create an updated prompt based on context and guidance.
    """


def llm_refine(
    model: str | rg.Generator,
    guidance: str,
    *,
    model_params: AnyDict | None = None,
    name: str = "llm_refine",
) -> Transform[t.Any, str]:
    """
    A generic transform that uses an LLM to refine a candidate.

    Args:
        model: The model to use for refining the candidate.
        guidance: The guidance to use for refining the candidate. Can be a string or a Lookup that resolves to a string.
        model_params: Optional model parameters (e.g. temperature, max_tokens)
        name: The name of the transform.
    """

    async def transform(
        object: t.Any,
        *,
        model: str | rg.Generator = Config(model, help="The model to use", expose_as=str),  # noqa: B008
        guidance: str = guidance,
        model_params: AnyDict | None = model_params,
    ) -> str:
        generator: rg.Generator
        if isinstance(model, str):
            generator = rg.get_generator(
                model,
                params=rg.GenerateParams.model_validate(model_params) if model_params else None,
            )
        elif isinstance(model, rg.Generator):
            generator = model
        else:
            raise TypeError("Model must be a string identifier or a Generator instance.")

        refiner_input = Input(context=str(object), guidance=guidance)
        refinement = await refine.bind(generator)(refiner_input)
        return refinement.prompt

    return Transform(transform, name=name)


def adapt_prompt_trials(trials: "list[Trial[str]]") -> str:
    """
    Adapter which can be used to create attempt context from a set of prompt/response trials.

    Trials are assumed to be a str candidate holding the prompt, and an output object
    that is (or includes) the model's response to the prompt.

    The list is assumed to be ordered by relevancy, and is reversed when
    formatting so the context is presented in ascending order of relevancy to the model.
    """
    context_parts = [
        dedent(f"""
        <attempt score={trial.score:.2f}>
            <prompt>{trial.candidate}</prompt>
            <response>{trial.output}</response>
        </attempt>
        """)
        for trial in reversed(trials)
    ]
    return "\n".join(context_parts)


def adapt_prompt_trials_as_graph(trials: "list[Trial[str]]") -> str:
    """
    Builds a clean, nested XML graph string from a list of Trials for an LLM prompt.

    This should be used in contexts where you want to provide the model with
    a clear view of the trial graph structure, including parent-child relationships.

    Key Features:
    - Maps noisy ULIDs to clean, zero-indexed integers for prompt clarity.
    - Represents the graph structure directly through nested XML tags.
    - Handles multiple root nodes and disconnected subgraphs gracefully.
    """
    if not trials:
        return ""

    trial_map: dict[ULID, Trial] = {trial.id: trial for trial in trials}
    ulid_to_int_map: dict[ULID, int] = {ulid: i for i, ulid in enumerate(trial_map.keys())}
    children_map = defaultdict(list)
    root_nodes: list[Trial] = []

    for trial in trials:
        if trial.parent_id is None or trial.parent_id not in trial_map:
            root_nodes.append(trial)
        else:
            children_map[trial.parent_id].append(trial)

    root_nodes.sort(key=lambda t: ulid_to_int_map[t.id])

    def _format_node(trial: "Trial") -> str:
        int_id = ulid_to_int_map[trial.id]
        parent_attr = ""
        if trial.parent_id and trial.parent_id in ulid_to_int_map:
            parent_int_id = ulid_to_int_map[trial.parent_id]
            parent_attr = f" parent_id={parent_int_id}"

        children = sorted(children_map.get(trial.id, []), key=lambda t: ulid_to_int_map[t.id])

        formatted_children = ""
        if children_parts := [_format_node(child) for child in children]:
            formatted_children = "\n" + indent("\n".join(children_parts), "  ")

        return dedent(f"""
        <attempt id={int_id}{parent_attr} score={trial.score:.2f}>
            <prompt>{trial.candidate}</prompt>
            <response>{trial.output}</response>{formatted_children}
        </attempt>
        """).strip()

    return "\n".join([_format_node(root) for root in root_nodes])
