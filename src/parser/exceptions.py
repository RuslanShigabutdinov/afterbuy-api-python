

class ParsingError(Exception):
    """
    **Description**: Raised when an error occurs during HTML parsing.

    **Cause**: Typically due to unexpected HTML structure or missing data.

    **Usage**: Used by HTML utility classes when expected data cannot be extracted.
    """


class FabricsNotFound(Exception):
    """
    **Description**: Raised when required fabrics are not found during a parsing operation.

    **Cause**: Indicates that the necessary fabric data is missing, potentially due to a syncing issue.

    **Usage**: Used by services when they cannot find expected fabric entities.
    """

class LoginFailedError(Exception):
    """
    **Description**: Raised when the login process to the external service fails.

    **Cause**: Incorrect credentials, service unavailability, or unexpected login flow changes.

    **Usage**: Used by the LoginClient when authentication fails.
    """