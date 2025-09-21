# -*- coding: utf-8 -*-

import base64

from .lazy_imports import bs4


def extract_email_name(text: str) -> str:
    """
    Extract the name part from an email string.

    Example: "John Doe <john.doe@email.com>" -> "John Doe"
    """
    return text.split("<")[0].strip()


def extract_email_address(text: str) -> str:
    """
    Extract the email address part from an email string.

    Example: "John Doe <john.doe@email.com>" -> "john.doe@email.com"
    """
    return text.split("<", 1)[-1].split(">", 1)[0].strip()


def create_email_deeplink(
    thread_id_or_message_id: str,
    acc: str | None = None,
):
    if acc is None:
        acc = "0"
    return f"https://mail.google.com/mail/u/{acc}/#all/{thread_id_or_message_id}"


def b64decode_with_auto_padding(s: str) -> str:
    s = s.replace("-", "+").replace("_", "/")
    s += "=" * (-len(s) % 4)
    return base64.b64decode(s).decode("utf-8")


def html_to_text(html: str) -> str:
    soup = bs4.BeautifulSoup(html, "html.parser")
    return soup.text
