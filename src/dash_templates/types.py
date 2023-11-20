from typing import Callable, List, Optional, TypedDict, Union

from dash.development.base_component import Component


class DashPage(TypedDict):
    module: str
    path: str
    relative_path: str
    """
    The path with requests_pathname_prefix prefixed before it.
    Use this path when specifying local URL paths that will work in
    environments regardless of what requests_pathname_prefix is.
    In some deployment environments, like Dash Enterprise,
    requests_pathname_prefix is set to the application name,
    e.g. my-dash-app. When working locally, requests_pathname_prefix
    might be unset and so a relative URL like /page-2 can just be /page-2.
    However, when the app is deployed to a URL like /my-dash-app,
    then relative_path will be /my-dash-app/page-2.
    """

    path_template: Optional[str]
    name: str
    order: int
    title: str
    description: Union[str, Callable]
    image: Optional[str]
    image_url: Optional[str]
    redirect_from: Optional[List[str]]
    layout: Union[Callable, Component]

    # Custom properties

    disabled: Optional[bool]
    """
    Disable the menu entry
    """

    icon: Optional[str]
    """
    The name of the Dash Iconify icon, check all icons here:
    https://icon-sets.iconify.design/
    """

    right_content: Optional[Component]
    """
    An optional component to draw on the right of the menu entry
    """
