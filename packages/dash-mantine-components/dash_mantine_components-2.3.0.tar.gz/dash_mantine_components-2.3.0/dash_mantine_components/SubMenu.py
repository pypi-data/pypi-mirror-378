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


class SubMenu(Component):
    """A SubMenu component.
Sub Menu

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Menu content.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- arrowOffset (number; optional):
    Arrow offset in px, `5` by default.

- arrowPosition (a value equal to: 'center', 'side'; optional):
    Arrow position.

- arrowRadius (number; optional):
    Arrow `border-radius` in px, `0` by default.

- arrowSize (number; optional):
    Arrow size in px, `7` by default.

- attributes (boolean | number | string | dict | list; optional):
    Passes attributes to inner elements of a component.  See Styles
    API docs.

- classNames (dict; optional):
    Adds custom CSS class names to inner elements of a component.  See
    Styles API docs.

- clickOutsideEvents (list of strings; optional):
    Events that trigger outside clicks.

- closeDelay (number; optional):
    Close delay in ms, applicable only to trigger=\"hover\" variant.

- closeOnClickOutside (boolean; optional):
    Determines whether dropdown should be closed on outside clicks.

- closeOnEscape (boolean; optional):
    Determines whether dropdown should be closed when Escape key is
    pressed.

- closeOnItemClick (boolean; optional):
    Determines whether Menu should be closed when item is clicked.

- defaultOpened (boolean; optional):
    Uncontrolled menu initial opened state.

- disabled (boolean; optional):
    If set, popover dropdown will not be rendered.

- floatingStrategy (a value equal to: 'absolute', 'fixed'; optional):
    Changes floating ui [position
    strategy](https://floating-ui.com/docs/usefloating#strategy),
    `'absolute'` by default.

- keepMounted (boolean; optional):
    If set dropdown will not be unmounted from the DOM when it is
    hidden, `display: none` styles will be added instead.

- loop (boolean; optional):
    Determines whether arrow key presses should loop though items
    (first to last and last to first).

- menuItemTabIndex (a value equal to: 0, -1; optional):
    Set the `tabindex` on all menu items. Defaults to -1.

- middlewares (dict; optional):
    Floating ui middlewares to configure position handling, `{ flip:
    True, shift: True, inline: False }` by default.

    `middlewares` is a dict with keys:

    - shift (optional)

    - flip (dict; optional)

        `flip` is a dict with keys:

        - mainAxis (boolean; optional):

            The axis that runs along the side of the floating element.

            Determines  whether overflow along this axis is checked to

            perform a flip. @,default,True.

        - crossAxis (optional):

            The axis that runs along the alignment of the floating

            element. Determines  whether overflow along this axis is

            checked to perform a flip.  - `True`: Whether to check cross

            axis overflow for both side and alignment flipping.  -

            `False`: Whether to disable all cross axis overflow checking.

            - `'alignment'`: Whether to check cross axis overflow for

            alignment flipping only. @,default,True.

        - rootBoundary (dict; optional):

            The root clipping area in which overflow will be checked.

            @,default,'viewport'.

            `rootBoundary` is a dict with keys:

            - x (number; required)

            - y (number; required)

            - width (number; required)

            - height (number; required)

        - elementContext (a value equal to: 'reference', 'floating'; optional):

            The element in which overflow is being checked relative to a

            boundary. @,default,'floating'.

        - altBoundary (boolean; optional):

            Whether to check for overflow using the alternate element's

            boundary  (`clippingAncestors` boundary only).

            @,default,False.

        - padding (dict; optional):

            Virtual padding for the resolved overflow detection offsets.

            @,default,0.

            `padding` is a number

              Or dict with keys:

            - top (number; optional)

            - right (number; optional)

            - bottom (number; optional)

            - left (number; optional)

        - fallbackPlacements (list of a value equal to: 'top', 'right', 'bottom', 'left', 'top-end', 'top-start', 'right-end', 'right-start', 'bottom-end', 'bottom-start', 'left-end', 'left-start's; optional):

            Placements to try sequentially if the preferred `placement`

            does not fit. @,default,[oppositePlacement] (computed).

        - fallbackStrategy (a value equal to: 'bestFit', 'initialPlacement'; optional):

            What strategy to use when no placements fit.

            @,default,'bestFit'.

        - fallbackAxisSideDirection (a value equal to: 'end', 'start', 'none'; optional):

            Whether to allow fallback to the perpendicular axis of the

            preferred  placement, and if so, which side direction along

            the axis to prefer. @,default,'none' (disallow fallback).

        - flipAlignment (boolean; optional):

            Whether to flip to placements with the opposite alignment if

            they fit  better. @,default,True.

        - boundary (dict; optional)

            `boundary` is a dict with keys:

            - x (number; required)

            - y (number; required)

            - width (number; required)

            - height (number; required) | list of a list of or a singular dash component, string or numbers

    - inline (boolean | number | string | dict | list; optional)

    - size (optional)

- offset (number; optional):
    Offset of the dropdown element, `8` by default.

- openDelay (number; optional):
    Open delay in ms, applicable only to trigger=\"hover\" variant.

- opened (boolean; optional):
    Controlled menu opened state.

- overlayProps (dict; optional):
    Props passed down to `Overlay` component.

- portalProps (dict; optional):
    Props to pass down to the `Portal` when `withinPortal` is True.

- position (a value equal to: 'top', 'right', 'bottom', 'left', 'top-end', 'top-start', 'right-end', 'right-start', 'bottom-end', 'bottom-start', 'left-end', 'left-start'; optional):
    Dropdown position relative to the target element, `'bottom'` by
    default.

- positionDependencies (list of boolean | number | string | dict | lists; optional):
    `useEffect` dependencies to force update dropdown position, `[]`
    by default.

- radius (number; optional):
    Key of `theme.radius` or any valid CSS value to set border-radius,
    `theme.defaultRadius` by default.

- returnFocus (boolean; optional):
    Determines whether focus should be automatically returned to
    control when dropdown closes, `False` by default.

- shadow (optional):
    Key of `theme.shadows` or any other valid CSS `box-shadow` value.

- styles (boolean | number | string | dict | list; optional):
    Adds inline styles directly to inner elements of a component.  See
    Styles API docs.

- transitionProps (dict; optional):
    Props passed down to the `Transition` component that used to
    animate dropdown presence, use to configure duration and animation
    type, `{ duration: 150, transition: 'fade' }` by default.

    `transitionProps` is a dict with keys:

    - keepMounted (boolean; optional):
        If set element will not be unmounted from the DOM when it is
        hidden, `display: none` styles will be applied instead.

    - transition (optional):
        Transition name or object.

    - duration (number; optional):
        Transition duration in ms, `250` by default.

    - exitDuration (number; optional):
        Exit transition duration in ms, `250` by default.

    - timingFunction (string; optional):
        Transition timing function, `theme.transitionTimingFunction`
        by default.

    - mounted (boolean; required):
        Determines whether component should be mounted to the DOM.

- trapFocus (boolean; optional):
    Determines whether dropdown should trap focus of keyboard events.

- trigger (a value equal to: 'click', 'hover', 'click-hover'; optional):
    Event which should open menu.

- unstyled (boolean; optional):
    Remove all Mantine styling from the component.

- variant (string; optional)

- width (string | number; optional):
    Dropdown width, or `'target'` to make dropdown width the same as
    target element, `'max-content'` by default.

- withArrow (boolean; optional):
    Determines whether component should have an arrow, `False` by
    default.

- withOverlay (boolean; optional):
    Determines whether the overlay should be displayed when the
    dropdown is opened, `False` by default.

- withinPortal (boolean; optional):
    Determines whether dropdown should be rendered within the
    `Portal`, `True` by default.

- zIndex (string | number; optional):
    Dropdown `z-index`, `300` by default."""
    _children_props = ['middlewares.flip.boundary']
    _base_nodes = ['children']
    _namespace = 'dash_mantine_components'
    _type = 'SubMenu'
    TransitionProps = TypedDict(
        "TransitionProps",
            {
            "keepMounted": NotRequired[bool],
            "transition": NotRequired[typing.Union[Literal["fade"], Literal["fade-down"], Literal["fade-up"], Literal["fade-left"], Literal["fade-right"], Literal["skew-up"], Literal["skew-down"], Literal["rotate-right"], Literal["rotate-left"], Literal["slide-down"], Literal["slide-up"], Literal["slide-right"], Literal["slide-left"], Literal["scale-y"], Literal["scale-x"], Literal["scale"], Literal["pop"], Literal["pop-top-left"], Literal["pop-top-right"], Literal["pop-bottom-left"], Literal["pop-bottom-right"]]],
            "duration": NotRequired[NumberType],
            "exitDuration": NotRequired[NumberType],
            "timingFunction": NotRequired[str],
            "mounted": bool
        }
    )

    MiddlewaresFlipRootBoundary = TypedDict(
        "MiddlewaresFlipRootBoundary",
            {
            "x": NumberType,
            "y": NumberType,
            "width": NumberType,
            "height": NumberType
        }
    )

    MiddlewaresFlipPadding = TypedDict(
        "MiddlewaresFlipPadding",
            {
            "top": NotRequired[NumberType],
            "right": NotRequired[NumberType],
            "bottom": NotRequired[NumberType],
            "left": NotRequired[NumberType]
        }
    )

    MiddlewaresFlipBoundary = TypedDict(
        "MiddlewaresFlipBoundary",
            {
            "x": NumberType,
            "y": NumberType,
            "width": NumberType,
            "height": NumberType
        }
    )

    MiddlewaresFlip = TypedDict(
        "MiddlewaresFlip",
            {
            "mainAxis": NotRequired[bool],
            "crossAxis": NotRequired[typing.Union[Literal["alignment"]]],
            "rootBoundary": NotRequired[typing.Union[Literal["viewport"], Literal["document"], "MiddlewaresFlipRootBoundary"]],
            "elementContext": NotRequired[Literal["reference", "floating"]],
            "altBoundary": NotRequired[bool],
            "padding": NotRequired[typing.Union[NumberType, "MiddlewaresFlipPadding"]],
            "fallbackPlacements": NotRequired[typing.Sequence[Literal["top", "right", "bottom", "left", "top-end", "top-start", "right-end", "right-start", "bottom-end", "bottom-start", "left-end", "left-start"]]],
            "fallbackStrategy": NotRequired[Literal["bestFit", "initialPlacement"]],
            "fallbackAxisSideDirection": NotRequired[Literal["end", "start", "none"]],
            "flipAlignment": NotRequired[bool],
            "boundary": NotRequired[typing.Union["MiddlewaresFlipBoundary", Literal["clippingAncestors"], typing.Sequence[ComponentType]]]
        }
    )

    Middlewares = TypedDict(
        "Middlewares",
            {
            "shift": NotRequired[typing.Union[typing.Any]],
            "flip": NotRequired[typing.Union["MiddlewaresFlip"]],
            "inline": NotRequired[typing.Any],
            "size": NotRequired[typing.Union[typing.Any]]
        }
    )


    def __init__(
        self,
        children: typing.Optional[ComponentType] = None,
        variant: typing.Optional[str] = None,
        opened: typing.Optional[bool] = None,
        defaultOpened: typing.Optional[bool] = None,
        trapFocus: typing.Optional[bool] = None,
        closeOnItemClick: typing.Optional[bool] = None,
        loop: typing.Optional[bool] = None,
        closeOnEscape: typing.Optional[bool] = None,
        trigger: typing.Optional[Literal["click", "hover", "click-hover"]] = None,
        openDelay: typing.Optional[NumberType] = None,
        closeDelay: typing.Optional[NumberType] = None,
        closeOnClickOutside: typing.Optional[bool] = None,
        clickOutsideEvents: typing.Optional[typing.Sequence[str]] = None,
        menuItemTabIndex: typing.Optional[Literal[0, -1]] = None,
        id: typing.Optional[typing.Union[str, dict]] = None,
        position: typing.Optional[Literal["top", "right", "bottom", "left", "top-end", "top-start", "right-end", "right-start", "bottom-end", "bottom-start", "left-end", "left-start"]] = None,
        offset: typing.Optional[typing.Union[NumberType]] = None,
        positionDependencies: typing.Optional[typing.Sequence[typing.Any]] = None,
        keepMounted: typing.Optional[bool] = None,
        transitionProps: typing.Optional["TransitionProps"] = None,
        width: typing.Optional[typing.Union[str, NumberType]] = None,
        middlewares: typing.Optional["Middlewares"] = None,
        withArrow: typing.Optional[bool] = None,
        arrowSize: typing.Optional[NumberType] = None,
        arrowOffset: typing.Optional[NumberType] = None,
        arrowRadius: typing.Optional[NumberType] = None,
        arrowPosition: typing.Optional[Literal["center", "side"]] = None,
        withinPortal: typing.Optional[bool] = None,
        portalProps: typing.Optional[dict] = None,
        zIndex: typing.Optional[typing.Union[str, NumberType]] = None,
        radius: typing.Optional[typing.Union[NumberType, Literal["xs"], Literal["sm"], Literal["md"], Literal["lg"], Literal["xl"]]] = None,
        shadow: typing.Optional[typing.Union[Literal["xs"], Literal["sm"], Literal["md"], Literal["lg"], Literal["xl"]]] = None,
        disabled: typing.Optional[bool] = None,
        returnFocus: typing.Optional[bool] = None,
        floatingStrategy: typing.Optional[Literal["absolute", "fixed"]] = None,
        overlayProps: typing.Optional[dict] = None,
        withOverlay: typing.Optional[bool] = None,
        classNames: typing.Optional[dict] = None,
        styles: typing.Optional[typing.Any] = None,
        unstyled: typing.Optional[bool] = None,
        attributes: typing.Optional[typing.Any] = None,
        **kwargs
    ):
        self._prop_names = ['children', 'id', 'arrowOffset', 'arrowPosition', 'arrowRadius', 'arrowSize', 'attributes', 'classNames', 'clickOutsideEvents', 'closeDelay', 'closeOnClickOutside', 'closeOnEscape', 'closeOnItemClick', 'defaultOpened', 'disabled', 'floatingStrategy', 'keepMounted', 'loop', 'menuItemTabIndex', 'middlewares', 'offset', 'openDelay', 'opened', 'overlayProps', 'portalProps', 'position', 'positionDependencies', 'radius', 'returnFocus', 'shadow', 'styles', 'transitionProps', 'trapFocus', 'trigger', 'unstyled', 'variant', 'width', 'withArrow', 'withOverlay', 'withinPortal', 'zIndex']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'arrowOffset', 'arrowPosition', 'arrowRadius', 'arrowSize', 'attributes', 'classNames', 'clickOutsideEvents', 'closeDelay', 'closeOnClickOutside', 'closeOnEscape', 'closeOnItemClick', 'defaultOpened', 'disabled', 'floatingStrategy', 'keepMounted', 'loop', 'menuItemTabIndex', 'middlewares', 'offset', 'openDelay', 'opened', 'overlayProps', 'portalProps', 'position', 'positionDependencies', 'radius', 'returnFocus', 'shadow', 'styles', 'transitionProps', 'trapFocus', 'trigger', 'unstyled', 'variant', 'width', 'withArrow', 'withOverlay', 'withinPortal', 'zIndex']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(SubMenu, self).__init__(children=children, **args)

setattr(SubMenu, "__init__", _explicitize_args(SubMenu.__init__))
