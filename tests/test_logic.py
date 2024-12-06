import unittest
import datetime
from unittest.mock import patch, MagicMock, Mock

import django
import oas.logic as logic
from oas.logic import publication_event_handler
from submission.models import Article
from utils.testing import helpers
from django.core.management import call_command
from utils import install
from journal.models import Issue
from submission.models import Licence
from core import models as core_models

SETTINGS_PATH = "plugins/oas/install/settings.json"


class MockResponse(Mock):
    def __init__(self, content=None, ok=True):
        self.content = content or ""
        self._ok = ok

    @property
    def text(self):
        return self.content

    @property
    def ok(self):
        return self._ok


class TestPublicationEventHandler(django.test.TestCase):
    def setUp(self):
        press = helpers.create_press()
        self.journal, _ = helpers.create_journals()
        self.journal.save()
        call_command("load_default_settings")
        self.journal.publisher = "oas"
        self.journal.code = "oas"
        self.journal.save()

        install.update_settings(self.journal, file_path=SETTINGS_PATH)

        self.section = helpers.create_section(
            journal=self.journal,
            name="A Section",
        )

        self.article = self._create_article(
            date_published=datetime.date(day=1, month=7, year=2019)
        )
        self.encoded_article = """
        {
        "admin": {
            "publisher_record_id": null
        },
        "bibjson":{
        "end_page": null,
            "identifier":[
                {
                    "id":"0000-0000",
                    "type":"eissn"
                },
                {
                    "id": null,
                    "type": "doi"
                }
            ],
            "author":[
                {
                    "name":"Testla Musketeer",
                    "affiliation":"OLH",
                    "orcid_id": "https://orcid.org/0000-0000-0000-0000"
                }
            ],
            "journal":{
                "volume":"1",
                "license":[
                    {
                    "title":"All rights reserved",
                    "url":"https://creativecommons.org/licenses/authors",
                    "open_access":true
                    }
                ],
                "publisher":"oas",
                "title":"Journal One",
                "number":"1",
                "language":[
                    "en"
                ]
            },
            "keywords":[

            ],
            "year": "2019",
            "month": "7",
            "start_page": null,
            "subject": null,
            "title":"The art of writing test titles",
            "link":[
                {
                    "url":"http://localhost/doaj/article/id/%s/",
                    "content_type":"text/html",
                    "type":"fulltext"
                }
            ],
            "abstract":"The test abstract"
            }
        }
        """ % (self.article.pk)

    def _create_article(self, **kwargs):
        kwargs.setdefault("abstract", "The test abstract")
        kwargs.setdefault("title", "The art of writing test titles")
        kwargs.setdefault("date_published", datetime.datetime.now())
        kwargs.setdefault("journal", self.journal)
        article = Article(**kwargs)
        article.section = self.section
        article.date_submitted = datetime.datetime.now()
        article.date_accepted = datetime.datetime.now()
        article.date_published = datetime.datetime.now()
        article.save()

        author = helpers.create_user("author@doaj.com")
        author.orcid = "0000-0000-0000-0000"
        author.first_name = "Testla"
        author.last_name = "Musketeer"
        author.institution = "OAS"
        author.save()
        article.authors.add(author)
        article.owner = author

        issue = Issue.objects.create(
            journal=self.journal,
            volume=1,
            issue=1,
        )
        article.primary_issue = issue

        article.license = Licence.objects.all()[0]

        _file = core_models.File.objects.create(
            mime_type="A/FILE",
            original_filename="test.pdf",
            uuid_filename="UUID",
            label="A file",
            description="Oh yes, it's a file",
            owner=author,
            is_galley=True,
            privacy="owner",
        )
        pdf_galley = core_models.Galley.objects.create(
            article=article, file=_file, label="PDF"
        )
        article.galley_set.add(pdf_galley)
        article.save()
        article.snapshot_authors(article)
        return article

    @staticmethod
    def mocked_requests_get_bad_auth(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        if args[0] == "https://setting/authorize":
            return MockResponse({"token": "a token value"}, 300)
        elif args[0] == "https://setting/message":
            return MockResponse({"message": "Success"}, 200)

        return MockResponse(None, 404)

    @patch("plugins.oas.logic.get_plugin_settings")
    @patch("plugins.oas.logic.build_payload")
    @patch("plugins.oas.logic.send_payload")
    @patch("plugins.oas.logic.authorize")
    @patch(
        "plugins.oas.logic.requests.post",
        side_effect=mocked_requests_get_bad_auth,
    )
    def test_authorization_failure(
        self,
        mock_get,
        mock_authorize,
        mock_send_payload,
        mock_build_payload,
        mock_get_plugin_settings,
    ):
        mock_request = MagicMock()
        mock_request.journal.get_setting = MagicMock(
            return_value="https://setting"
        )

        mock_article = self._create_article()

        mock_get_plugin_settings.return_value = (
            True,
            "email",
            True,
            "password",
            "url",
            "sandbox_url",
        )
        mock_authorize.return_value = ("token", True)
        mock_build_payload.return_value = {"payload": "data"}
        mock_send_payload.return_value = ({"response": "success"}, True)
        logic.build_authorization_json = MagicMock(
            return_value={"email": "abc"}
        )

        with patch("oas.logic.messages") as mock_messages:
            kwargs = {"request": mock_request, "article": mock_article}
            publication_event_handler(**kwargs)

            mock_messages.add_message.assert_called_once_with(
                mock_request,
                mock_messages.ERROR,
                "Failed to authorize with OA Switchboard.",
            )

    @staticmethod
    def mocked_requests_get(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        if args[0] == "https://setting/authorize":
            return MockResponse({"token": "a token value"}, 200)
        elif args[0] == "https://setting/message":
            return MockResponse({"message": "Success"}, 200)

        return MockResponse(None, 404)

    @patch("plugins.oas.logic.get_plugin_settings")
    @patch("plugins.oas.logic.build_payload")
    @patch("plugins.oas.logic.send_payload")
    @patch("plugins.oas.logic.authorize")
    @patch("plugins.oas.logic.requests.post", side_effect=mocked_requests_get)
    def test_successful_message_send(
        self,
        mock_get,
        mock_authorize,
        mock_send_payload,
        mock_build_payload,
        mock_get_plugin_settings,
    ):
        mock_request = MagicMock()
        mock_request.journal.get_setting = MagicMock(
            return_value="https://setting"
        )

        mock_article = self._create_article()

        mock_get_plugin_settings.return_value = (
            True,
            "email",
            True,
            "password",
            "url",
            "sandbox_url",
        )
        mock_authorize.return_value = ("token", True)
        mock_build_payload.return_value = {"payload": "data"}
        mock_send_payload.return_value = ({"response": "success"}, True)
        logic.build_authorization_json = MagicMock(
            return_value={"email": "abc"}
        )

        with patch("oas.logic.messages") as mock_messages:
            kwargs = {"request": mock_request, "article": mock_article}
            publication_event_handler(**kwargs)

            mock_messages.add_message.assert_called_once_with(
                mock_request,
                mock_messages.SUCCESS,
                "p1-pio message sent to OA Switchboard.",
            )

    @staticmethod
    def mocked_requests_get_fail(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

        if args[0] == "https://setting/authorize":
            return MockResponse({"token": "a token value"}, 200)
        elif args[0] == "https://setting/message":
            return MockResponse(
                {"error": True, "errorMessage": ["You are a fool"]}, 200
            )

        return MockResponse(None, 404)

    @patch("plugins.oas.logic.get_plugin_settings")
    @patch("plugins.oas.logic.build_payload")
    @patch("plugins.oas.logic.send_payload")
    @patch("plugins.oas.logic.authorize")
    @patch(
        "plugins.oas.logic.requests.post", side_effect=mocked_requests_get_fail
    )
    def test_successful_message_send_failure(
        self,
        mock_get,
        mock_authorize,
        mock_send_payload,
        mock_build_payload,
        mock_get_plugin_settings,
    ):
        mock_request = MagicMock()
        mock_request.journal.get_setting = MagicMock(
            return_value="https://setting"
        )

        mock_article = self._create_article()

        mock_get_plugin_settings.return_value = (
            True,
            "email",
            True,
            "password",
            "url",
            "sandbox_url",
        )
        mock_authorize.return_value = ("token", True)
        mock_build_payload.return_value = {"payload": "data"}
        mock_send_payload.return_value = ({"response": "success"}, True)
        logic.build_authorization_json = MagicMock(
            return_value={"email": "abc"}
        )

        with patch("oas.logic.messages") as mock_messages:
            kwargs = {"request": mock_request, "article": mock_article}
            publication_event_handler(**kwargs)

            mock_messages.add_message.assert_called_once_with(
                mock_request,
                mock_messages.ERROR,
                "Failed to send p1-pio message to OA Switchboard:         ['You are a fool']",
            )


if __name__ == "__main__":
    unittest.main()
