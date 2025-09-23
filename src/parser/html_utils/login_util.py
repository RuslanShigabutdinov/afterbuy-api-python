from typing import Dict, Any, List, cast
from lxml import html
from lxml.etree import _Element as Element

from src.parser.exceptions import ParsingError

class LoginHtmlUtil:
    """
    **Description**: Utility class for parsing HTML related to the login process
    of the external service.

    **Methods**:
    - `fetch_login_data`: Extracts login form data.
    - `fetch_hidden_form`: Extracts data from a specific hidden form.
    - `fetch_title`: Extracts the HTML page title.

    **Usage**: Used by the LoginClient to parse response HTML.
    """
    @staticmethod
    def fetch_login_data(html_content: str) -> Dict[str, Any]:
        """
        **Description**: Extracts login data (token payload and action URL) from HTML content.

        **Input**:
        - `html_content`: *str* - The HTML string to parse.

        **Output**:
        - *Dict[str, Any]* - A dictionary with 'token_payload' and 'action_url'.

        **Exceptions**:
        - `ParsingError`: If required form elements or attributes are missing.

        **How It Works**:
        - Parses the HTML to find the first form element.
        - Extracts 'wresult' and 'wctx' input values.
        - Extracts the form's 'action' URL.
        - Raises ParsingError if any required elements or attributes are not found.
        """
        tree: Element = html.fromstring(html_content)
        forms: List[Element] = tree.xpath('//form')
        if not forms:
            raise ParsingError("No <form> elements found in HTML content")

        form: Element = forms[0]
        wresult_inputs: List[Element] = form.xpath(".//input[@name='wresult']")
        wctx_inputs: List[Element] = form.xpath(".//input[@name='wctx']")
        if not wresult_inputs or not wctx_inputs:
            raise ParsingError("Required <input> elements (wresult or wctx) not found in form")

        wresult_input: Element = wresult_inputs[0]
        wctx_input: Element = wctx_inputs[0]

        action_url: str | None = form.get("action")
        if action_url is None:
            raise ParsingError("Form action URL is missing")

        wresult_value: str | None = wresult_input.get("value")
        wctx_value: str | None = wctx_input.get("value")
        if wresult_value is None or wctx_value is None:
            raise ParsingError("Required input values (wresult or wctx) are missing")

        token_payload: Dict[str, str] = {
            "wa": "wsignin1.0",
            "wresult": wresult_value,
            "wctx": wctx_value
        }
        return {"token_payload": token_payload, "action_url": action_url}

    @staticmethod
    def fetch_hidden_form(html_content: str) -> Dict[str, Any]:
        """
        **Description**: Extracts data from a hidden form in HTML content.

        **Input**:
        - `html_content`: *str* - The HTML string to parse.

        **Output**:
        - *Dict[str, Any]* - A dictionary with 'payload' (form inputs) and 'action_url'.

        **Exceptions**:
        - `ParsingError`: If the hidden form or its action URL is missing, or inputs are not found.

        **How It Works**:
        - Parses the HTML to find a form with `name='hiddenform'`.
        - Extracts all input elements within the form.
        - Builds a dictionary payload from input names and values.
        - Extracts the form's 'action' URL.
        - Raises ParsingError if the form, its action, or inputs are not found.
        """
        tree: Element = html.fromstring(html_content)
        forms: List[Element] = tree.xpath("//form[@name='hiddenform']")
        if not forms:
            raise ParsingError("No hidden form with name='hiddenform' found in HTML content")

        form: Element = forms[0]
        form_inputs: List[Element] = form.xpath(".//input[@name]")
        if not form_inputs:
            raise ParsingError("No inputs found in hidden form")

        payload: Dict[str, str] = {
            cast(str, input_elem.get("name")): input_elem.get("value", "")
            for input_elem in form_inputs
        }
        action_url: str | None = form.get("action")
        if action_url is None:
            raise ParsingError("Hidden form action URL is missing")

        return {"payload": payload, "action_url": action_url}

    @staticmethod
    def fetch_title(html_content: str) -> str:
        """
        **Description**: Extracts the page title from HTML content.

        **Input**:
        - `html_content`: *str* - The HTML string to parse.

        **Output**:
        - *str* - The stripped title text.

        **Exceptions**:
        - `ParsingError`: If no title element is found.

        **How It Works**:
        - Parses the HTML to find the `<title>` element.
        - Extracts and returns the text content, stripped of whitespace.
        - Raises ParsingError if no title is found.
        """
        tree: Element = html.fromstring(html_content)
        titles: List[str] = tree.xpath("//title/text()")
        if not titles:
            raise ParsingError("No <title> element found in HTML content")

        return titles[0].strip()