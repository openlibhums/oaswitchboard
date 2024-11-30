__copyright__ = "Copyright 2024 Birkbeck, University of London"
__author__ = "Martin Paul Eve"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck University of London"

import json

import requests
from utils import setting_handler
from utils.logger import get_logger

logger = get_logger(__name__)


def publication_event_handler(**kwargs):
    """
    The main entry point for the OA Switchboard plugin
    :param kwargs: the keyword arguments that include request and article
    """
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

    # try authorization
    token, success = authorize(oas_email, oas_password, url_to_use)
    if not success:
        return

    # build the payload message
    payload = build_payload(article)
    print(payload)

    # send the payload


def build_header():
    """
    Build the header for the OA Switchboard
    """
    return {
        "type": "p1",
        "version": "v2",
        "to": {
            "address": "https://ror.org/broadcast",
        },
        "persistent": True,
        "pio": True,
    }


def build_credit(article, author):
    """
    Build the CRediT block if it exists
    :param article: the article
    :param author: the author
    :return:
    """
    return (
        article.credit_roles_frozen[author]
        if hasattr(article, "credit_roles_frozen")
        else []
    )


def build_ror(author):
    """
    Build the ROR item if it exists
    :param author: the author to build the ROR for
    """
    affil = author.affiliation()

    if hasattr(affil, "organization"):
        org = affil.organization
    else:
        return ""

    return org.ror if hasattr(org, "ror") else ""


def build_authors(article):
    """
    Build the authors for the OA Switchboard
    :param article: the article to build the authors for
    """
    authors = []
    author_list = article.frozen_authors()
    for author in author_list:
        authors.append(
            {
                "listingorder": author.order + 1,
                "lastName": author.last_name,
                "firstName": author.first_name,
                "ORCID": author.frozen_orcid,
                "creditroles": build_credit(article, author),
                "isCorrespondingAuthor": author.is_correspondence_author,
                "institutions": [
                    {
                        "sourceaffiliation": author.affiliation(),
                        "name": author.affiliation(),
                        "ror": build_ror(author),
                    }
                ],
                "affiliation": author.affiliation(),
            }
        )

    return authors


def build_funders(article):
    """
    Build the funders for the OA Switchboard
    :param article: the article to build the funders for
    """
    funders = []
    for funder in article.funders:
        funders.append(
            {
                "name": funder.name,
                "ror": funder.ror if hasattr(funder, "ror") else "",
            }
        )

    return funders


def build_article(article):
    """
    Build the article for the OA Switchboard
    :param article: the article to build the article for
    """
    return {
        "title": article.title,
        "doi": article.doi,
        "type": article.jats_article_type,
        "funders": build_funders(article),
    }


def build_data(article):
    """
    Build the data for the OA Switchboard
    :param article: the article to build the data for
    """
    return {
        "timing": "VoR",
        "authors": build_authors(article),
        "article": build_article(article),
    }


def build_payload(article):
    """
    Build the payload for the OA Switchboard
    :param article: the article to build the payload for
    """
    return {
        "header": build_header(),
        "data": build_data(article),
    }


def authorize(oas_email, oas_password, url_to_use):
    """
    Obtain a bearer token from the OA Switchboard
    :param oas_email: the email to use
    :param oas_password: the password to use
    :param url_to_use: the base URL to use
    :return:
    """

    if not url_to_use.endswith("/"):
        url_to_use += "/"

    auth_url = f"{url_to_use}authorize"
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
    participant = authorization_response.get("participant", None)
    organisation = (
        participant.get("organisation", None) if participant else None
    )

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


def get_plugin_settings(request):
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
