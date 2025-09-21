# -*- coding: utf-8 -*-

"""
Gmail API Client Builders

This module provides builder classes for creating authenticated Gmail API clients
with different credential storage strategies. Supports both local file storage
and AWS Parameter Store for OAuth2 tokens and client secrets.

The module implements the builder pattern to abstract credential management
while maintaining consistent authentication flow across different environments.
"""

import typing as T
import json
import dataclasses
from pathlib import Path

from func_args.api import REQ, BaseFrozenModel

import google.auth.exceptions
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from .lazy_imports import aws_ssm

if T.TYPE_CHECKING:  # pragma: no cover
    from googleapiclient._apis.gmail.v1 import GmailResource
    from mypy_boto3_ssm import SSMClient


class TokenNotFound(Exception):
    """
    Exception raised when OAuth2 token cannot be found or accessed.

    This exception is raised when attempting to read stored credentials
    that don't exist or are inaccessible in the configured storage location.
    """
    pass


@dataclasses.dataclass(frozen=True)
class ClientBuilder(BaseFrozenModel):
    """
    Abstract base class for Gmail API client authentication builders.

    Provides the core OAuth2 authentication flow for Gmail API access while
    allowing different credential storage strategies through subclasses.
    Handles token refresh, re-authentication when needed, and service creation.

    :param scopes: List of Gmail API scopes to request during authentication

    **Examples**:
        Local file storage::

            builder = LocalPathClientBuilder(
                scopes=["https://www.googleapis.com/auth/gmail.readonly"],
                path_client_secrets=Path("~/.google/client_secrets.json"),
                path_token=Path("~/.google/token.json")
            )
            gmail_service = builder.auth()

        AWS Parameter Store::

            builder = AwsParameterStoreClientBuilder(
                scopes=["https://www.googleapis.com/auth/gmail.readonly"],
                ssm_client=boto3.client("ssm"),
                param_name_client_secrets="/app/gmail/client_secrets",
                param_name_token="/app/gmail/token"
            )
            gmail_service = builder.auth()

    .. note::
        Subclasses must implement credential storage methods for their
        specific storage backend (local files, cloud storage, etc.).
    """
    scopes: list[str] = dataclasses.field(default=REQ)

    def read_client_secrets_config(self) -> dict:
        """
        Read OAuth2 client secrets configuration from storage.

        :returns: Client secrets configuration dictionary containing
                 client_id, client_secret, and other OAuth2 parameters

        :raises NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError

    def read_token_config(self) -> dict:
        """
        Read stored OAuth2 token configuration from storage.

        :returns: Token configuration dictionary containing access_token,
                 refresh_token, and token metadata

        :raises TokenNotFound: When token cannot be found or accessed
        :raises NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError

    def write_token_config(self, data: dict):
        """
        Store OAuth2 token configuration to persistent storage.

        Called automatically after successful authentication or token refresh
        to persist credentials for future use.

        :param data: Token configuration dictionary to store

        :raises NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError

    def get_flow(self) -> InstalledAppFlow:
        """
        Create OAuth2 flow for interactive user authentication.

        Builds an OAuth2 flow using client secrets and requested scopes.
        Used when initial authentication or re-authentication is required.

        :returns: Configured OAuth2 flow ready for user interaction
        """
        return InstalledAppFlow.from_client_config(
            client_config=self.read_client_secrets_config(),
            scopes=self.scopes,
        )

    def get_creds(self) -> Credentials:
        """
        Load existing OAuth2 credentials from stored token.

        Reconstructs credentials object from previously stored token data.
        These credentials may need refresh if expired.

        :returns: OAuth2 credentials object loaded from storage

        :raises TokenNotFound: When stored token cannot be found
        """
        return Credentials.from_authorized_user_info(
            info=self.read_token_config(),
            scopes=self.scopes,
        )

    def auth(self) -> "GmailResource":
        """
        Authenticate and create Gmail API service client.

        Handles the complete OAuth2 authentication flow including:
        - Loading existing credentials if available
        - Refreshing expired tokens automatically
        - Prompting for re-authentication when necessary
        - Storing updated credentials for future use

        :returns: Authenticated Gmail API service client ready for use

        .. note::
            On first run or when refresh fails, opens a web browser for
            user authentication. Subsequent runs use stored credentials.
        """
        # Try to load existing credentials from storage
        try:
            creds = self.get_creds()
        except TokenNotFound:
            creds = None

        # Check if we need to authenticate or refresh credentials
        if not creds or not creds.valid:
            need_re_auth = True

            # Attempt automatic token refresh if refresh token exists
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    need_re_auth = False
                except google.auth.exceptions.RefreshError:
                    # Refresh failed, will need full re-authentication
                    pass

            # Perform interactive authentication if refresh failed or no creds
            if need_re_auth:
                flow = self.get_flow()
                # Opens browser for user consent, uses random port
                creds = flow.run_local_server(port=0)

            # Persist credentials for future use
            self.write_token_config(json.loads(creds.to_json()))

        # Build and return authenticated Gmail service client
        service: "GmailResource" = build(
            "gmail",
            "v1",
            credentials=creds,
        )
        return service


@dataclasses.dataclass(frozen=True)
class LocalPathClientBuilder(ClientBuilder):
    """
    Gmail client builder using local file system for credential storage.

    Stores OAuth2 client secrets and tokens as JSON files on the local
    filesystem. Ideal for development environments and single-user applications.

    :param scopes: Gmail API scopes to request during authentication
    :param path_client_secrets: Path to JSON file containing OAuth2 client secrets
    :param path_token: Path to JSON file for storing OAuth2 tokens

    **Examples**:
        Development setup with home directory storage::

            from pathlib import Path

            builder = LocalPathClientBuilder(
                scopes=["https://www.googleapis.com/auth/gmail.readonly"],
                path_client_secrets=Path.home() / ".google" / "client_secrets.json",
                path_token=Path.home() / ".google" / "token.json"
            )
            gmail_service = builder.auth()

        Shared project configuration::

            builder = LocalPathClientBuilder(
                scopes=["https://www.googleapis.com/auth/gmail.modify"],
                path_client_secrets=Path("config/gmail_secrets.json"),
                path_token=Path("config/gmail_token.json")
            )

    .. note::
        Ensure proper file permissions on credential files to protect
        sensitive authentication data from unauthorized access.
    """
    path_client_secrets: Path = dataclasses.field(default=REQ)
    path_token: Path = dataclasses.field(default=REQ)

    def read_client_secrets_config(self) -> dict:
        """
        Read OAuth2 client secrets from local JSON file.

        :returns: Client secrets configuration dictionary

        :raises FileNotFoundError: If client secrets file doesn't exist
        :raises json.JSONDecodeError: If file contains invalid JSON
        """
        text = self.path_client_secrets.read_text(encoding="utf-8")
        return json.loads(text)

    def read_token_config(self) -> dict:
        """
        Read OAuth2 token from local JSON file.

        :returns: Token configuration dictionary

        :raises TokenNotFound: If token file doesn't exist
        :raises json.JSONDecodeError: If file contains invalid JSON
        """
        try:
            text = self.path_token.read_text(encoding="utf-8")
        except FileNotFoundError:
            raise TokenNotFound(f"Token file not found at {self.path_token}")
        return json.loads(text)

    def write_token_config(self, data: dict):
        """
        Write OAuth2 token to local JSON file.

        Creates parent directories if they don't exist and writes token
        data with human-readable formatting.

        :param data: Token configuration dictionary to store
        """
        # Ensure parent directory exists for token file
        self.path_token.parent.mkdir(parents=True, exist_ok=True)
        self.path_token.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def write_client_secrets_config(self, data: dict):
        """
        Write OAuth2 client secrets to local JSON file.

        Utility method for programmatically storing client secrets.
        Creates parent directories if they don't exist.

        :param data: Client secrets configuration dictionary to store
        """
        # Ensure parent directory exists for client secrets file
        self.path_client_secrets.parent.mkdir(parents=True, exist_ok=True)
        self.path_client_secrets.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


@dataclasses.dataclass(frozen=True)
class AwsParameterStoreClientBuilder(ClientBuilder):
    """
    Gmail client builder using AWS Systems Manager Parameter Store.

    Stores OAuth2 credentials as encrypted parameters in AWS SSM Parameter Store.
    Ideal for production environments, CI/CD pipelines, and multi-instance
    deployments where centralized credential management is required.

    :param scopes: Gmail API scopes to request during authentication
    :param ssm_client: Configured AWS SSM client for parameter operations
    :param param_name_client_secrets: SSM parameter name for client secrets
    :param param_name_token: SSM parameter name for OAuth2 tokens

    **Examples**:
        Production environment with AWS profile::

            import boto3

            builder = AwsParameterStoreClientBuilder(
                scopes=["https://www.googleapis.com/auth/gmail.readonly"],
                ssm_client=boto3.Session(profile_name="prod").client("ssm"),
                param_name_client_secrets="/app/gmail/client_secrets",
                param_name_token="/app/gmail/token"
            )
            gmail_service = builder.auth()

        Cross-account deployment::

            # Using assumed role credentials
            ssm_client = boto3.client(
                "ssm",
                aws_access_key_id=assumed_credentials["AccessKeyId"],
                aws_secret_access_key=assumed_credentials["SecretAccessKey"],
                aws_session_token=assumed_credentials["SessionToken"]
            )

            builder = AwsParameterStoreClientBuilder(
                scopes=["https://www.googleapis.com/auth/gmail.modify"],
                ssm_client=ssm_client,
                param_name_client_secrets="/shared/gmail/secrets",
                param_name_token="/shared/gmail/token"
            )

    .. note::
        Parameters are stored as SecureString type for encryption at rest.
        Ensure proper IAM permissions for ssm:GetParameter and ssm:PutParameter.
    """
    ssm_client: "SSMClient" = dataclasses.field(default=REQ)
    param_name_client_secrets: str = dataclasses.field(default=REQ)
    param_name_token: str = dataclasses.field(default=REQ)

    def _read_param(self, name: str):
        """
        Read and decrypt parameter from AWS Systems Manager.

        :param name: SSM parameter name to retrieve

        :returns: Parsed JSON data from parameter value

        :raises TokenNotFound: If parameter doesn't exist in SSM
        :raises json.JSONDecodeError: If parameter contains invalid JSON
        """
        # Retrieve parameter with decryption enabled for SecureString type
        param = aws_ssm.get_parameter(
            ssm_client=self.ssm_client,
            name=name,
            with_decryption=True,
        )
        if param is None:
            raise TokenNotFound(f"AWS Parameter not found: {name}")
        return json.loads(param.value)

    def read_client_secrets_config(self) -> dict:
        """
        Read OAuth2 client secrets from AWS Parameter Store.

        :returns: Client secrets configuration dictionary

        :raises TokenNotFound: If client secrets parameter doesn't exist
        """
        return self._read_param(self.param_name_client_secrets)

    def read_token_config(self) -> dict:
        """
        Read OAuth2 token from AWS Parameter Store.

        :returns: Token configuration dictionary

        :raises TokenNotFound: If token parameter doesn't exist
        """
        return self._read_param(self.param_name_token)

    def _write_param(self, name: str, data: dict):
        """
        Write parameter to AWS Systems Manager as encrypted SecureString.

        Only updates the parameter if the value has changed to avoid
        unnecessary API calls and parameter version increments.

        :param name: SSM parameter name to write
        :param data: Dictionary data to store as JSON
        """
        # Store as SecureString for encryption at rest
        aws_ssm.put_parameter_if_changed(
            ssm_client=self.ssm_client,
            name=name,
            value=json.dumps(data, ensure_ascii=False),
            type=aws_ssm.ParameterType.SECURE_STRING,
        )

    def write_token_config(self, data: dict):
        """
        Write OAuth2 token to AWS Parameter Store.

        :param data: Token configuration dictionary to store
        """
        self._write_param(self.param_name_token, data)

    def write_client_secrets_config(self, data: dict):
        """
        Write OAuth2 client secrets to AWS Parameter Store.

        Utility method for programmatically storing client secrets.

        :param data: Client secrets configuration dictionary to store
        """
        self._write_param(self.param_name_client_secrets, data)
