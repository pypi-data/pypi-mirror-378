# AUTO GENERATED FILE - DO NOT EDIT

import typing  # noqa: F401
from typing_extensions import TypedDict, NotRequired, Literal # noqa: F401
from dash.development.base_component import Component, _explicitize_args

ComponentType = typing.Union[
    str,
    int,
    float,
    Component,
    None,
    typing.Sequence[typing.Union[str, int, float, Component, None]],
]

NumberType = typing.Union[
    typing.SupportsFloat, typing.SupportsInt, typing.SupportsComplex
]


class ModalStack(Component):
    """A ModalStack component.
Use ModalStack component to render multiple modals at the same time

Keyword arguments:

- children (list of dicts; optional):
    ManagedModal content.

    `children` is a list of dicts with keys:

    - type (string; required)

    - props (boolean | number | string | dict | list; required)

    - key (string; required)

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- aria-* (string; optional):
    Wild card aria attributes.

- close (string; optional):
    Closes one or more modals by ID. Accepts a single ID (string or
    dict) or a list of IDs.

- closeAll (boolean; optional):
    Closes all modals in the ModalStack.

- data-* (string; optional):
    Wild card data attributes.

- loading_state (dict; optional):
    Object that holds the loading state object coming from
    dash-renderer. For use with dash<3.

    `loading_state` is a dict with keys:

    - is_loading (boolean; required):
        Determines if the component is loading or not.

    - prop_name (string; required):
        Holds which property is loading.

    - component_name (string; required):
        Holds the name of the component that is loading.

- open (string; optional):
    Opens one or more modals by ID. Accepts a single ID (string or
    dict) or a list of IDs.

- state (dict; optional):
    Current opened state of each modal. Read only.

    `state` is a dict with keys:


- tabIndex (number; optional):
    tab-index.

- toggle (string; optional):
    Toggles one or more modals by ID. Accepts a single ID (string or
    dict) or a list of IDs."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_mantine_components'
    _type = 'ModalStack'
    State = TypedDict(
        "State",
            {

        }
    )

    LoadingState = TypedDict(
        "LoadingState",
            {
            "is_loading": bool,
            "prop_name": str,
            "component_name": str
        }
    )


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        state: typing.Optional["State"] = None,
        open: typing.Optional[typing.Union[str]] = None,
        close: typing.Optional[typing.Union[str]] = None,
        toggle: typing.Optional[typing.Union[str]] = None,
        closeAll: typing.Optional[bool] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        tabIndex: typing.Optional[NumberType] = None,
        loading_state: typing.Optional["LoadingState"] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'aria-*', 'close', 'closeAll', 'data-*', 'loading_state', 'open', 'state', 'tabIndex', 'toggle']
        self._valid_wildcard_attributes =            ['data-', 'aria-']
        self.available_properties = ['children', 'id', 'aria-*', 'close', 'closeAll', 'data-*', 'loading_state', 'open', 'state', 'tabIndex', 'toggle']
        self.available_wildcard_properties =            ['data-', 'aria-']
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(ModalStack, self).__init__(children=children, **args)

setattr(ModalStack, "__init__", _explicitize_args(ModalStack.__init__))
