from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from urllib.parse import urlencode

import httpx
import pkce
from fastapi import APIRouter
from loguru import logger as log
from pyzurecli import AzureCLI
from starlette.requests import Request
from starlette.responses import RedirectResponse
from toomanyconfigs import CWD
from toomanyconfigs.core import TOMLConfig

from .sessions import Session

DEBUG = True


# noinspection PyUnresolvedReferences
class MSFTOAuthCFG(TOMLConfig):
    client_id: str = None
    tenant_id: str = "common"
    scopes: str = "User.Read Organization.Read.All"


@dataclass
class MSFTOAuthCallback:
    code: str
    state: str
    session_state: str


@dataclass
class MSFTOAuthTokenResponse:
    token_type: str
    scope: str
    expires_in: int
    ext_expires_in: int
    access_token: str


class MicrosoftOAuth(CWD, APIRouter):
    def __init__(
            self,
            server,
            **cfg_kwargs
    ):
        from . import SessionedServer
        self.server: SessionedServer = server
        if not isinstance(server, SessionedServer): raise TypeError(
            "Passed server is not an instance of Sessioned Server")
        self.sessions = self.server.sessions
        self.url = self.server.url
        self.prefix = "/microsoft_oauth"
        self.redirect_uri = self.url + self.prefix + "/callback"

        CWD.__init__(
            self,
            "msftoauth2.toml",
        )
        self.cfg_file: Path = self.msftoauth2
        self.cfg_kwargs = cfg_kwargs
        _ = self.cfg
        self.tenant_id = self.cfg.tenant_id  # Now that we're doing auth by getting tenants from user's all urls should be common
        self.scopes = self.cfg.scopes

        APIRouter.__init__(
            self,
            prefix=self.prefix
        )

        @self.get("/")
        async def redirect():
            return RedirectResponse(self.redirect_uri)

        @self.get("/callback")
        async def callback(request: Request):
            params = request.query_params
            log.debug(f"{self}: Received auth callback with params: ")
            for param in params:
                log.debug(f"  - {param}={str(params[param])[:10]}...")
            try:
                params = MSFTOAuthCallback(**params)
                session = self.sessions[params.state]

                if not session:
                    log.error("Session not found for state")
                    raise ValueError("Invalid session state")

                log.debug(f"Retrieved session: {session}")

                if not hasattr(session, 'verifier'):
                    log.error(f"{self}: Session missing verifier attribute")
                    log.debug(
                        f"{self}: Session attributes: {[attr for attr in dir(session) if not attr.startswith('_')]}")
                    raise ValueError("OAuth session missing PKCE verifier")

                if not session.verifier:
                    log.error("Session verifier is empty")
                    raise ValueError("OAuth session verifier is empty")

                log.debug(f"Using verifier: {session.verifier[:10]}...")

            except Exception as e:
                log.error(f"OAuth callback failed: {type(e).__name__}: {str(e)}")
                from . import SessionedServer
                server: SessionedServer = self.server
                return server.popup_error(500, e)

            session.code = params.code

            token_request = self.build_access_token_request(session)  # type: ignore
            async with httpx.AsyncClient() as client:
                response = await client.send(token_request)
                if response.status_code == 200:
                    creds = MSFTOAuthTokenResponse(**response.json())
                    setattr(session, "oauth_token_data", creds)
                    log.debug(f"{self}: Successfully exchanged code for token")
                    setattr(session, "authenticated", True)
                    log.debug(f"{self}: Updated session:\n  - {session}")
                    key = self.sessions.session_name
                    response = self.login_successful
                    response.set_cookie(
                        key=key,
                        value=session.token,
                        httponly=True
                    )
                    return response
                else:
                    log.error(f"Token exchange failed: {response.status_code} - {response.text}")
                    raise Exception(f"Token exchange failed: {response.status_code}")

        self.bypass_routes = []
        for route in self.routes:
            self.bypass_routes.append(route.path)

    def __repr__(self):
        return f"[MicrosoftOAuth]"

    @cached_property
    def azure_cli(self) -> AzureCLI | None:
        return AzureCLI(
            cwd=self.cwd,
            redirect_uri=self.redirect_uri
        )

    @cached_property
    def cfg(self):
        if not self.cfg_kwargs.get("client_id"):
            client_id = self.azure_cli.app_registration.client_id
            self.cfg_kwargs["client_id"] = client_id
        cfg = MSFTOAuthCFG.create(
            _source=self.cfg_file,
            prompt_empty_fields=False,
            **self.cfg_kwargs
        )
        if not cfg.client_id: raise RuntimeError
        return cfg

    @cached_property
    def client_id(self):
        return self.cfg.client_id

    def build_auth_code_request(self, session: Session) -> httpx.Request:
        """Build Microsoft OAuth authorization URL with fresh PKCE"""
        code_verifier = pkce.generate_code_verifier(length=43)
        code_challenge = pkce.get_code_challenge(code_verifier)

        session.verifier = code_verifier  # Direct assignment instead of setattr
        log.debug(f"{self}: Stored verifier in session: {session.verifier}...")
        log.debug(f"{self}: Session after storing verifier: {session}")
        log.debug(f"{self}: Generated code_challenge: {code_challenge}")

        base_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"

        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "response_mode": "query",
            "scope": self.scopes,
            "state": session.token,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }

        log.debug(f"{self}: Building request with the following params:")
        for param in params:
            log.debug(f"  -{param}={params.get(param)[:10]}")

        url = f"{base_url}?{urlencode(params)}"
        log.debug(f"Built OAuth URL: {url}")

        client = httpx.Client()
        request = client.build_request("GET", url)

        return request

    def build_access_token_request(self, session) -> httpx.Request:
        """Build the POST request to exchange authorization code for access token"""
        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"

        try:
            data = {
                "client_id": self.client_id,
                "scope": self.scopes,
                "code": session.code,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
                "code_verifier": session.verifier,
                # Note: No client_secret needed for public clients using PKCE
            }
        except Exception:
            raise Exception

        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        client = httpx.Client()
        return client.build_request("POST", url, data=data, headers=headers)

    def build_logout_request(self, session: Session, redirect_uri: str) -> httpx.Request:
        """Build Microsoft OAuth logout URL"""

        base_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/logout"

        params = {
            "post_logout_redirect_uri": redirect_uri
        }

        # Add logout_hint if we have user info
        if hasattr(session, 'user') and session.user:
            if hasattr(session.user, 'userPrincipalName'):
                params["logout_hint"] = session.user.userPrincipalName
                log.debug(f"{self}: Added logout_hint: {session.user.userPrincipalName}")

        log.debug(f"{self}: Building logout request with the following params:")
        for param in params:
            log.debug(f"  -{param}={params.get(param)}")

        url = f"{base_url}?{urlencode(params)}"
        log.debug(f"Built logout URL: {url}")

        client = httpx.Client()
        request = client.build_request("GET", url)

        return request

    @cached_property
    def login_successful(self):
        return self.server.default_templater.safe_render(
            "login_success.html",
            redirect_url=self.url
        )

    def welcome(self, name):
        return self.server.default_templater.safe_render(
            "welcome.html",
            user=name,
            redirect_url=self.url
        )
