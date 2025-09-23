import logging

from urllib.parse import urljoin, quote
from datetime import datetime, timezone
import uuid
from typing import Dict

from src.libs.http_client import HttpClient # Assuming HttpClient exists
from src.config.afterbuy import settings # Assuming settings exists
from src.parser.html_utils.login_util import LoginHtmlUtil
from src.parser.exceptions import ParsingError, LoginFailedError # Import specific exceptions


class LoginClient(HttpClient):
    """
    **Description**: A client for logging into and interacting with the Afterbuy web interface
    with brand-specific credentials and maintaining an authenticated session.

    **Attributes**:
    - `BASE_LOGIN_URL`: *str* - The base URL for the login endpoint.
    - `WTREALM`: *str* - Constant for the wtrealm parameter.
    - `WREPLY`: *str* - Constant for the wreply parameter.
    - `WHR`: *str* - Constant for the whr parameter.
    - `base_url`: *str* - The base URL for the Afterbuy instance (JV or XL).
    - `html_util`: *LoginHtmlUtil* - Utility for parsing login-related HTML.
    - `login_payload`: *Dict[str, str]* - The payload for the login form submission.

    **Methods**:
    - `__init__`: Initializes the client for a specific brand.
    - `__aenter__`: Enters the async context, performing login and returning the client.
    - `__aexit__`: Exits the async context, closing the session.
    - `get_login_url`: Constructs the initial login URL.
    - `login`: Performs the multi-step login process.
    - `check_login_status`: Verifies successful login by checking a page title.
    - `_get_login_payload`: Internal helper to get login credentials.
    - `_simulate_form_submission`: Internal helper to handle a hidden form submission.

    **Usage**: Intended to be used as an async context manager (`async with LoginClient(brand_id) as client:`).
    """

    BASE_LOGIN_URL = "https://login.afterbuy.de/Account/Login?"
    WTREALM = "https://logout.afterbuy.de/"
    WREPLY = "http://logout.afterbuy.de/Federation/Index"
    WHR = "http://afterbuy/trust"

    def __init__(self, brand_id: int):
        """
        **Description**: Initialize the client with brand-specific settings.

        **Input**:
        - `brand_id`: *int* - The ID of the brand (e.g., 1 for JV, 17 for XL).

        **How It Works**:
        - Calls the parent HttpClient constructor.
        - Initializes the LoginHtmlUtil.
        - Determines if the brand is JV or XL based on ID.
        - Sets the base URL for the Afterbuy instance.
        - Prepares the login form payload.
        """
        super().__init__()
        self.html_util = LoginHtmlUtil()
        self._is_jv = brand_id == 1
        self.base_url = f"https://{settings.jv_base_url if self._is_jv else settings.xl_base_url}.afterbuy.de"
        self.login_payload = self._get_login_payload()

    def _get_login_payload(self) -> Dict[str, str]:
        """
        **Description**: Internal helper to return the login payload based on the brand.

        **Output**:
        - *Dict[str, str]* - The dictionary containing login form data.

        **How It Works**:
        - Selects username and password from settings based on whether it's a JV or XL client.
        - Returns a dictionary formatted for the login form submission.
        """
        if self._is_jv:
            username = settings.jv_username
            password = settings.jv_password
        else:
            username = settings.xl_username
            password = settings.xl_password
        return {
            "LoginView": "ABLogin",
            "Username": username,
            "Password": password,
            "B1": "", # Assuming B1 is a submit button value
            "StaySignedIn": "true"
        }

    def get_login_url(self) -> str:
        """
        **Description**: Constructs the initial login URL with dynamic and encoded parameters.

        **Output**:
        - *str* - The fully formed login URL.

        **How It Works**:
        - Generates unique values for wctx and wct.
        - Constructs the woriginRealm URL.
        - Defines URL parameters including encoded values.
        - Joins the base URL and parameters to create the final login URL.
        """
        wctx = str(uuid.uuid4()) # Unique session ID
        wct = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") # UTC timestamp
        worigin_realm = f"{self.base_url}/afterbuy/LoginResult.aspx"

        params = {
            "ReturnUrl": (
                f"/?wa=wsignin1.0&wtrealm={quote(self.WTREALM)}&wct={quote(wct)}"
                f"&wreply={quote(self.WREPLY)}&wctx={quote(wctx)}&whr={quote(self.WHR)}"
                f"&woriginRealm={quote(worigin_realm)}"
            ),
            "wa": "wsignin1.0",
            "wtrealm": self.WTREALM,
            "wct": wct,
            "wreply": self.WREPLY,
            "wctx": wctx,
            "whr": self.WHR,
            "woriginRealm": worigin_realm
        }
        return self.BASE_LOGIN_URL + "&".join(f"{k}={quote(v)}" for k, v in params.items())

    async def __aenter__(self) -> "LoginClient":
        """
        **Description**: Enters the async context, performs the login process, and returns the client instance.

        **Output**:
        - *"LoginClient"* - The authenticated client instance.

        **Exceptions**:
        - `LoginFailedError`: If the login process is unsuccessful.
        - Any exceptions from delegated HTTP requests or HTML parsing will bubble up.

        **How It Works**:
        - Calls `get_session` to perform authentication.
        - Returns `self` if login is successful.
        - `get_session` handles raising `LoginFailedError` on failure.
        """
        logging.debug("Attempting to establish authenticated session.")
        # get_session performs the login and raises LoginFailedError on failure
        return await self.get_session()


    async def __aexit__(self, exc_type: Exception, exc_val: str, exc_tb: str) -> None:
        """
        **Description**: Exits the async context, closing the underlying HTTP session.

        **Input**:
        - `exc_type`: *Exception* - The type of exception raised, if any.
        - `exc_val`: *str* - The exception instance, if any.
        - `exc_tb`: *str* - The traceback, if any.

        **Output**:
        - None

        **How It Works**:
        - Closes the aiohttp client session.
        - Logs session closure and any exception information if present.
        """
        await self.session.close()
        logging.debug("Authenticated session closed.")
        # Note: Error logging of exc_type, exc_val, exc_tb might be redundant if handled globally,
        # but kept here as it was in the original code's context manager exit.
        if exc_type or exc_val or exc_tb:
            logging.error(f"Exception occurred during session context: {exc_type}, {exc_val}, {exc_tb}")
        return


    async def get_session(self) -> "LoginClient":
        """
        **Description**: Performs the login process and returns the client instance if successful.

        **Output**:
        - *"LoginClient"* - The authenticated client instance.

        **Exceptions**:
        - `LoginFailedError`: If the login process fails at any step.
        - Exceptions from delegated HTTP requests or HTML parsing will bubble up.

        **How It Works**:
        - Calls the internal `login` method.
        - If `login` returns `True`, logs success and returns `self`.
        - If `login` returns `False`, logs failure and raises `LoginFailedError`.
        """
        if await self.login():
            logging.info("Successfully logged in.")
            return self
        else:
            logging.error("Login process failed.")
            raise LoginFailedError("Failed to complete login process.")

    async def login(self) -> bool:
        """
        **Description**: Performs the multi-step login process to authenticate with the external service.

        **Output**:
        - *bool* - True if login appears successful, False otherwise.

        **Exceptions**:
        - Exceptions from delegated HTTP requests (`HttpClient.html_request`) or HTML parsing (`LoginHtmlUtil` methods)
          will bubble up.

        **How It Works**:
        - Fetches the initial login page and submits credentials.
        - Parses the response to get a token payload and action URL.
        - Submits the token to finalize the initial login step.
        - Fetches the administration page and simulates submission of a hidden form often required after login.
        - Checks the login status by verifying the title of a known authenticated page.
        - Returns the result of the status check.
        """
        logging.info("Initiating login process...")
        login_url = self.get_login_url()

        # Step 1: Initial login request with credentials
        login_response_text = await self.html_request("POST", login_url, data=self.login_payload)
        login_data = self.html_util.fetch_login_data(login_response_text)
        action_url = urljoin(login_url, login_data["action_url"])

        # Step 2: Submit token to finalize initial login (SSO related step)
        logging.info("Submitting token to finalize initial login...")
        await self.html_request("POST", action_url, data=login_data["token_payload"])

        # Step 3: Handle hidden form submission (often a redirect/setup step)
        logging.info("Simulating hidden form submission...")
        hidden_form_html = await self.html_request("GET", self.base_url + "/afterbuy/administration.aspx")
        await self._simulate_form_submission(hidden_form_html)

        # Step 4: Verify login status
        logging.info("Checking login status...")
        return await self.check_login_status()

    async def check_login_status(self) -> bool:
        """
        **Description**: Checks if login was successful by inspecting the title of a known authenticated page.

        **Output**:
        - *bool* - True if the title indicates a logged-in state, False otherwise.

        **Exceptions**:
        - Exceptions from delegated HTTP requests (`HttpClient.html_request`) or HTML parsing (`LoginHtmlUtil.fetch_title`)
          will bubble up.

        **How It Works**:
        - Fetches the HTML of the eBay lister page.
        - Extracts the page title using the HTML utility.
        - Compares the extracted title to the known title of the login page.
        - Returns True if the titles do not match (indicating successful login), False otherwise.
        """
        ebay_lister_page = await self.html_request("GET", self.base_url + "/afterbuy/ebayliste2.aspx")
        page_title = self.html_util.fetch_title(ebay_lister_page)
        logging.info(f"eBay lister page title check: '{page_title}'")
        # Returns True if the title is NOT the login page title
        return page_title != "Afterbuy - Benutzer-Login"

    async def _simulate_form_submission(self, html_content: str) -> None:
        """
        **Description**: Internal helper to simulate submitting a hidden form found in the HTML.

        **Input**:
        - `html_content`: *str* - The HTML string containing the hidden form.

        **Output**:
        - None

        **Exceptions**:
        - Exceptions from HTML parsing (`LoginHtmlUtil.fetch_hidden_form`) or delegated HTTP requests
          will bubble up.

        **How It Works**:
        - Uses the HTML utility to extract the hidden form's data and action URL.
        - Constructs the full action URL.
        - Submits a POST request to the action URL with the extracted form payload.
        """
        hidden_form_data = self.html_util.fetch_hidden_form(html_content)
        action_url = urljoin(self.base_url, hidden_form_data["action_url"])
        await self.html_request("POST", action_url, data=hidden_form_data["payload"])