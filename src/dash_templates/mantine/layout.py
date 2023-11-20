from typing import Optional
import dash_mantine_components as dmc
from dash import (
    get_app,
    dcc,
    html,
    page_container,
    page_registry,
    callback,
    clientside_callback,
    Input,
    Output,
    State,
)
from dash.dash import _ID_LOCATION
from dash_iconify import DashIconify

from dash_templates.types import DashPage


sidemenu = html.Div()

theme_toggle_button = html.Div(
    dmc.ActionIcon(
        DashIconify(icon="gg:dark-mode", width=22),
        variant="outline",
        radius=30,
        size=36,
        color="yellow",
        id="color-scheme-toggle",
    ),
    style={"display": "flex", "justifyContent": "center", "paddingBottom": 24},
)


@callback(Output(sidemenu, "children"), Input(_ID_LOCATION, "pathname"))
def render_sidemenu(pathname: str):
    # Create a dictionary to organize pages by their parent
    pages_by_parent = {}
    for page in page_registry.values():
        parts = page["path"].split("/")

        if len(parts) == 2:
            # Top level page
            parent = None
        else:
            parent = "/".join(parts[:-1])

        if "children" not in page:
            page["children"] = []
        pages_by_parent[parent] = pages_by_parent.get(parent, []) + [page]

    def is_any_child_active(page: DashPage) -> bool:
        children = pages_by_parent.get(page["path"], [])

        if children:
            return any(pathname == child["path"] for child in children)
        else:
            return pathname == page["path"]

    # Recursive function to build menu items
    def build_menu_item(page: DashPage):
        children = pages_by_parent.get(page["path"], [])
        is_active = pathname == page["path"]
        label = dmc.Group([page["name"], page.get("right_content")], position="apart")

        if children:
            any_child_active = is_any_child_active(page)

            return dmc.NavLink(
                label=label,
                href=page["path"],
                icon=DashIconify(icon=page["icon"]) if "icon" in page else None,
                childrenOffset=28,
                active=is_active or any_child_active,
                variant="light" if is_active else "subtle",
                disabled=page.get("disabled", False),
                opened=is_active or any_child_active,
                children=[build_menu_item(child) for child in children],
            )
        else:
            return dmc.NavLink(
                label=label,
                href=page["path"],
                icon=DashIconify(icon=page["icon"]) if "icon" in page else None,
                disabled=page.get("disabled", False),
                active=is_active,
            )

    # Build menu items for top-level pages
    top_level_pages = pages_by_parent.get(None, [])
    menu_items = [build_menu_item(page) for page in top_level_pages]

    return html.Nav(menu_items)


clientside_callback(
    """ function(data) { return data } """,
    Output("mantine-theme-provider", "theme"),
    Input("theme-store", "data"),
)

clientside_callback(
    """function(n_clicks, data) {
        if (data) {
            if (n_clicks) {
                const scheme = data["colorScheme"] == "dark" ? "light" : "dark"
                return { colorScheme: scheme }
            }
            return dash_clientside.no_update
        } else {
            return { colorScheme: "light" }
        }
    }""",
    Output("theme-store", "data"),
    Input("color-scheme-toggle", "n_clicks"),
    State("theme-store", "data"),
)


def get_default_logo(title: str):
    return dmc.Stack(
        [
            dmc.ThemeIcon(
                DashIconify(icon="ph:rocket-duotone", width=82),
                variant="gradient",
                gradient={"from": "teal", "to": "blue", "deg": 60},
                size=96,
            ),
            dmc.Text(title.upper(), size="sm", pt=8, sx={"letterSpacing": 1}),
        ],
        align="center",
        spacing=2,
        mb=48,
    )


def get_layout(
    logo=None,
    announce=None,
    announce_height: int = 32,
    announce_color: str = None,
    theme: Optional[dict] = None,
):
    app = get_app()

    return dmc.MantineProvider(
        id="mantine-theme-provider",
        theme={
            "colorScheme": "light",
            **(theme or {}),
        },
        inherit=True,
        withGlobalStyles=True,
        withNormalizeCSS=True,
        children=[
            dmc.NotificationsProvider(
                html.Div(
                    [
                        html.Div(id="notifications-container"),
                        dcc.Store(id="theme-store", storage_type="local"),
                        announce
                        and html.Div(
                            announce,
                            style={
                                "display": "flex",
                                "height": announce_height,
                                "justifyContent": "center",
                                "alignItems": "center",
                                "backgroundColor": announce_color
                                or dmc.theme.DEFAULT_COLORS["grape"][7],
                            },
                        ),
                        dmc.Navbar(
                            fixed=True,
                            p="lg",
                            pt=48,
                            width={"base": 300},
                            height="100vh",
                            position={
                                "left": 0,
                                "top": announce_height * bool(announce),
                            },
                            children=[
                                logo or get_default_logo(app.title),
                                dmc.ScrollArea(
                                    offsetScrollbars=True,
                                    type="scroll",
                                    sx={"flexGrow": 1},
                                    children=[
                                        sidemenu,
                                    ],
                                ),
                                theme_toggle_button,
                            ],
                        ),
                        html.Div(
                            dmc.Container([page_container]),
                            style={
                                "marginLeft": 300,
                                "paddingTop": 16,
                                "minHeight": f"calc(100vh - {announce_height * bool(announce)}px)",
                            },
                        ),
                    ]
                )
            )
        ],
    )
