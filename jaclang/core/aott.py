"""
AOTT: Automated Operational Type Transformation.

This has all the necessary functions to perform the AOTT operations.
"""

import re
from enum import Enum
from typing import Any

from jaclang.core.registry import Registry, Scope, SemInfo


PROMPT_TEMPLATE = """
[System Prompt]
This is an operation you must perform and return the output values. Neither, the methodology, extra sentences nor the code are not needed.
Input/Type formatting: Explanation of the Input (variable_name) (type) = value

[Information]
{information}

[Inputs Information]
{inputs_information}

[Output Information]
{output_information}

[Type Explanations]
{type_explanations}

[Action]
{action}

{reason_suffix}
"""  # noqa E501

WITH_REASON_SUFFIX = """
Reason and return the output result(s) only, adhering to the provided Type in the following format

[Reasoning] <Reason>
[Output] <Result>
"""

WITHOUT_REASON_SUFFIX = """Generate and return the output result(s) only, adhering to the provided Type in the following format

[Output] <result>
"""  # noqa E501


def aott_raise(
    information: str,
    inputs_information: str,
    output_information: str,
    type_explanations: str,
    action: str,
    reason: bool,
) -> str:
    """AOTT Raise uses the information (Meanings types values) provided to generate a prompt(meaning in)."""
    return PROMPT_TEMPLATE.format(
        information=information,
        inputs_information=inputs_information,
        output_information=output_information,
        type_explanations=type_explanations,
        action=action,
        reason_suffix=WITH_REASON_SUFFIX if reason else WITHOUT_REASON_SUFFIX,
    )


def aott_lower(meaning_out: str, output_type_info: tuple) -> Any:  # noqa: ANN401
    """AOTT Lower uses the meaning out provided by the language model and return the result in the desired type."""
    return meaning_out


def get_info_types(
    scope: Scope, mod_registry: Registry, incl_info: list[tuple[str, str]]
) -> tuple:
    """Filter the registry data based on the scope and return the info string."""
    collected_types = []
    avail_scopes = []
    while scope:
        avail_scopes.append(str(scope))
        scope = scope.parent

    filtered_registry = {
        _scope: sem_info_list
        for _scope, sem_info_list in mod_registry.registry.items()
        if str(_scope) in avail_scopes
    }

    def find_sem_info(
        _registry: dict[Scope, list[SemInfo]], name: str
    ) -> SemInfo | None:
        for sem_info_list in _registry.values():
            for sem_info in sem_info_list:
                if sem_info.name == name:
                    return sem_info
        return None

    info_str = []
    for incl in incl_info:
        sem_info = find_sem_info(filtered_registry, incl[0])
        if sem_info and sem_info.type:
            collected_types.extend(extract_non_primary_type(sem_info.type))
            info_str.append(
                f"{sem_info.semstr} ({sem_info.name}) ({sem_info.type}) = {get_object_string(incl[1])}"
            )
    return ("\n".join(info_str), collected_types)


def get_object_string(obj: Any) -> Any:  # noqa: ANN401
    """Get the string representation of the input object."""
    if isinstance(obj, str):
        return f'"{obj}"'
    elif isinstance(obj, (int, float, bool)):
        return str(obj)
    elif isinstance(obj, list):
        return "[" + ", ".join(get_object_string(item) for item in obj) + "]"
    elif isinstance(obj, tuple):
        return "(" + ", ".join(get_object_string(item) for item in obj) + ")"
    elif isinstance(obj, dict):
        return (
            "{"
            + ", ".join(
                f"{get_object_string(key)}: {get_object_string(value)}"
                for key, value in obj.items()
            )
            + "}"
        )
    elif isinstance(obj, Enum):
        return f"{obj.__class__.__name__}.{obj.name}"
    elif hasattr(obj, "__dict__"):
        args = ", ".join(
            f"{key}={get_object_string(value)}"
            for key, value in vars(obj).items()
            if key != "_jac_"
        )
        return f"{obj.__class__.__name__}({args})"
    else:
        return str(obj)


def get_all_type_explanations(type_list: list, mod_registry: Registry) -> dict:
    """Get all type explanations from the input type list."""
    collected_type_explanations = {}
    for type_item in type_list:
        type_explanation = get_type_explanation(type_item, mod_registry)
        if type_explanation is not None:
            type_explanation_str, nested_types = type_explanation
            if type_item not in collected_type_explanations:
                collected_type_explanations[type_item] = type_explanation_str
            if nested_types:
                nested_collected_type_explanations = get_all_type_explanations(
                    list(nested_types), mod_registry
                )
                for k, v in nested_collected_type_explanations.items():
                    if k not in collected_type_explanations:
                        collected_type_explanations[k] = v
    return collected_type_explanations


def get_type_explanation(
    type_str: str, mod_registry: Registry
) -> tuple[str, set[Any]] | None:
    """Get the type explanation of the input type string."""
    main_registry_type_info = None
    scope = None
    for k, v in registry_data.items():
        if isinstance(v, dict):
            for i, j in v.items():
                if i == type_str:
                    main_registry_type_info = j
                    scope = k
                    break
    if not main_registry_type_info:
        return None
    type_type = main_registry_type_info[0]
    type_semstr = main_registry_type_info[1]
    type_info = registry_data[f"{scope}.{type_str}({type_type})"]
    type_info_str = []
    type_info_types = []
    if type_type == "Enum" and isinstance(type_info, dict):
        for k, v in type_info.items():
            if isinstance(v, list):
                type_info_str.append(f"{v[1]} ({k}) (EnumItem)")
    elif type_type in ["obj", "class", "node", "edge"] and isinstance(type_info, dict):
        for k, v in type_info.items():
            if isinstance(v, list):
                type_info_str.append(f"{v[1]} ({k}) ({v[0]})")
                if extract_non_primary_type(v[0]):
                    type_info_types.extend(extract_non_primary_type(v[0]))
    return (
        f"{type_semstr} ({type_str}) ({type_type}) = {', '.join(type_info_str)}",
        set(type_info_types),
    )


def extract_non_primary_type(type_str: str) -> list:
    """Extract non-primary types from the type string."""
    if not type_str:
        return []
    pattern = r"(?:\[|,\s*|\|)([a-zA-Z_][a-zA-Z0-9_]*)|([a-zA-Z_][a-zA-Z0-9_]*)"
    matches = re.findall(pattern, type_str)
    primary_types = [
        "str",
        "int",
        "float",
        "bool",
        "list",
        "dict",
        "tuple",
        "set",
        "Any",
        "None",
    ]
    non_primary_types = [m for t in matches for m in t if m and m not in primary_types]
    return non_primary_types


def get_type_annotation(data: Any) -> str:  # noqa: ANN401
    """Get the type annotation of the input data."""
    if isinstance(data, dict):
        class_name = next(
            (value.__class__.__name__ for value in data.values() if value is not None),
            None,
        )
        if class_name:
            return f"dict[str, {class_name}]"
        else:
            return "dict[str, Any]"
    else:
        return str(type(data).__name__)
