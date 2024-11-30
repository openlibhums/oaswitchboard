__copyright__ = "Copyright 2024 Birkbeck, University of London"
__author__ = "Martin Paul Eve"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck University of London"

import json

import requests
from django.http import HttpRequest
from utils import setting_handler
from utils.logger import get_logger

logger = get_logger(__name__)


def publication_event_handler(**kwargs):
    request = kwargs.get("request", None)
    article = kwargs.get("article", None)

    if request is None:
        logger.warning(
            "Received article published notification"
            "but there was no request object."
        )
        return

    if article is None:
        logger.warning(
            "Received article published notification"
            "but there was no article object."
        )
        return

    logger.info(f"Received article published notification on {article.title}")

    # get the per-journal settings for the plugin
    (
        oas_enabled,
        oas_email,
        oas_sandbox,
        oas_password,
        oas_url,
        oas_sandbox_url,
    ) = get_plugin_settings(request)

    # setup switchboard option
    switchboard = oas_sandbox and oas_enabled
    url_to_use = oas_sandbox_url if switchboard else oas_url
    auth_url = f"{url_to_use}authorize"

    # try authorization
    token, success = authorize(auth_url, oas_email, oas_password, url_to_use)

    if not success:
        return


def authorize(auth_url, oas_email, oas_password, url_to_use):
    """
    Obtain a bearer token from the OA Switchboard
    :param auth_url: the URL to authorize with
    :param oas_email: the email to use
    :param oas_password: the password to use
    :param url_to_use: the base URL to use
    :return:
    """
    authorization_json = build_authorization_json(oas_email, oas_password)

    r = requests.post(
        f"{url_to_use}authorize", data=json.dumps(authorization_json)
    )

    if r.status_code != 200:
        logger.error(
            f"Failed to authorize with OA Switchboard {auth_url}: "
            f"{r.status_code}"
        )
        return None, False

    authorization_response = r.json()

    if "error" in authorization_response:
        logger.error(
            f"Failed to authorize with OA Switchboard {auth_url}: "
            f"{authorization_response['errorMessage']}"
        )

        return None, False

    # get the token
    if "token" not in authorization_response:
        logger.error(
            f"Failed to authorize with OA Switchboard {auth_url}: "
            "no token returned"
        )
        return None, False

    token = authorization_response.get("token", None)
    organisation = authorization_response.get("organisation", None)
    logger.info(f"Logged in to OA Switchboard as {organisation}")

    return token, True


def build_authorization_json(oas_email, oas_password):
    """
    Build the authorization JSON for the OA Switchboard
    :param oas_email: the email to use
    :param oas_password: the password to use
    """
    return {
        "email": oas_email,
        "password": oas_password,
    }


def get_plugin_settings(request: HttpRequest):
    """
    Get the plugin settings for the OA Switchboard plugin
    :param request: the request object
    """
    oas_enabled = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_send"
    )
    oas_email = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_email"
    )
    oas_sandbox = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_sandbox"
    )
    oas_password = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_password"
    )
    oas_url = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_url"
    )
    oas_sandbox_url = request.journal.get_setting(
        "plugin:oaswitchboard_plugin", "oas_sandbox_url"
    )

    return (
        oas_enabled,
        oas_email,
        oas_sandbox,
        oas_password,
        oas_url,
        oas_sandbox_url,
    )


def save_plugin_settings(
    oas_email,
    oas_enabled,
    oas_password,
    oas_sandbox,
    oas_sandbox_url,
    oas_url,
    request,
):
    """
    Save the plugin settings for the OA Switchboard plugin
    :param oas_email: the email
    :param oas_enabled: whether the plugin is enabled
    :param oas_password: the password
    :param oas_sandbox: whether the plugin is in sandbox mode
    :param oas_sandbox_url: the sandbox URL
    :param oas_url: the live URL
    :param request: the request object (to specify the journal)
    """
    setting_handler.save_setting(
        setting_group_name="plugin:oaswitchboard_plugin",
        setting_name="oas_send",
        journal=request.journal,
        value=oas_enabled,
    )
    setting_handler.save_setting(
        setting_group_name="plugin:oaswitchboard_plugin",
        setting_name="oas_email",
        journal=request.journal,
        value=oas_email,
    )
    setting_handler.save_setting(
        setting_group_name="plugin:oaswitchboard_plugin",
        setting_name="oas_sandbox",
        journal=request.journal,
        value=oas_sandbox,
    )
    setting_handler.save_setting(
        setting_group_name="plugin:oaswitchboard_plugin",
        setting_name="oas_password",
        journal=request.journal,
        value=oas_password,
    )
    setting_handler.save_setting(
        setting_group_name="plugin:oaswitchboard_plugin",
        setting_name="oas_url",
        journal=request.journal,
        value=oas_url,
    )
    setting_handler.save_setting(
        setting_group_name="plugin:oaswitchboard_plugin",
        setting_name="oas_sandbox_url",
        journal=request.journal,
        value=oas_sandbox_url,
    )
