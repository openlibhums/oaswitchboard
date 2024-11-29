__copyright__ = "Copyright 2024 Birkbeck, University of London"
__author__ = "Martin Paul Eve"
__license__ = "AGPL v3"
__maintainer__ = "Birkbeck University of London"


def publication_event_handler(**kwargs):
    request = kwargs.get("request", None)
    article = kwargs.get("article", None)

    if request is None or article is None:
        return

    print(f"Received article published notification on {article.title}")
