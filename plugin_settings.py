"""
The pluin setup and settings file for the OAS plugin.
"""

from events import logic as events_logic
from utils import plugins
from utils.install import update_settings

PLUGIN_NAME = "OA Switchboard Plugin"
DISPLAY_NAME = "OA Switchboard"
DESCRIPTION = "Support for OA Switchboard functionality"
AUTHOR = "Martin Paul Eve"
VERSION = "0.1"
SHORT_NAME = "oas"
MANAGER_URL = "oas_manager"
JANEWAY_VERSION = "1.7.0"


class OasPlugin(plugins.Plugin):
    """
    The plugin class for the OAS plugin
    """

    plugin_name = PLUGIN_NAME
    display_name = DISPLAY_NAME
    description = DESCRIPTION
    author = AUTHOR
    short_name = SHORT_NAME
    manager_url = MANAGER_URL

    version = VERSION
    janeway_version = JANEWAY_VERSION


def install():
    """
    Install the plugin
    """
    OasPlugin.install()
    update_settings(file_path="plugins/oas/install/settings.json")


def hook_registry():
    """
    Register the plugin hooks
    """
    return {
        "journal_editor_nav_block": {
            "module": "plugins.oas.hooks",
            "function": "menu_hook",
        },
    }


def register_for_events():
    """
    Register for events
    """
    # note that import must be here to avoid circular imports
    from plugins.oas import logic

    events_logic.Events.register_for_event(
        events_logic.Events.ON_ARTICLE_PUBLISHED,
        logic.publication_event_handler,
    )
