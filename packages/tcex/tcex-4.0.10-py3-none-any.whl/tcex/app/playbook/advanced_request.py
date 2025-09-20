"""TcEx Framework Module"""

# standard library
import contextlib
import json
import logging
from mimetypes import MimeTypes
from typing import cast

# third-party
from requests import Response, Session
from requests.exceptions import RequestException

from ...app.playbook import Playbook
from ...input.model.advanced_request_model import AdvancedRequestModel
from ...logger.trace_logger import TraceLogger

# get tcex logger
_logger: TraceLogger = logging.getLogger(__name__.split('.', maxsplit=1)[0])  # type: ignore


class AdvancedRequest:
    """App Feature Advanced Request Module

    Args:
        inputs: The instance of App inputs.
        playbooks: An instance Playbooks.
        session: An instance of Requests Session object.
        output_prefix: The output prefix.
        timeout: The timeout value for the request.
    """

    def __init__(
        self,
        model: AdvancedRequestModel,
        playbook: Playbook,
        session: Session,
        output_prefix: str,
        timeout: int = 600,
    ):
        """Initialize instance properties."""
        self.model = model
        self.playbook = playbook
        self.output_prefix = output_prefix
        self.session = session
        self.timeout = timeout or 600

        # properties
        self.allow_redirects: bool = True
        self.data: bytes | dict | str | None = None
        self.headers: dict = {}
        self.log = _logger
        self.max_mb: int = 500
        self.mt = MimeTypes()
        self.params: dict = {}

    def configure_body(self):
        """Configure Body"""
        self.data = self.model.tc_adv_req_body
        if self.data is not None:
            # INT-1386
            with contextlib.suppress(AttributeError):
                self.data = self.data.encode('utf-8')  # type: ignore

        if self.model.tc_adv_req_urlencode_body:
            # the user has selected to urlencode the body, which indicates that
            # the body is a JSON string and should be converted to a dict
            self.data = cast('str', self.data)
            try:
                self.data = json.loads(self.data)
            except ValueError:  # pragma: no cover
                self.log.exception('Failed loading body as JSON data.')

    def configure_headers(self):
        """Configure Headers

        [{
            "key": "User-Agent",
            "value": "TcEx MyApp: 1.0.0",
        }]
        """
        for header_data in self.model.tc_adv_req_headers or []:
            value = header_data['value']
            self.headers[str(header_data.get('key'))] = str(value)

    def configure_params(self):
        """Configure Params

        [{
            "count": "500",
            "page": "1",
        }]
        """
        for param_data in self.model.tc_adv_req_params or []:
            param = param_data.get('key')
            values = param_data['value']
            if not isinstance(values, list):
                values = [values]
            for value in values:
                if not value and self.model.tc_adv_req_exclude_null_params:
                    self.log.warning(
                        f'Query parameter {param} has a null/empty value '
                        'and will not be added to the request.'
                    )
                else:
                    self.params.setdefault(param, []).append(str(value))

    def request(self) -> Response | None:
        """Make the HTTP request."""
        if self.model.tc_adv_req_path is None:
            return None

        # configure body
        self.configure_body()

        # configure headers
        self.configure_headers()

        # configure params
        self.configure_params()

        # make http request
        try:
            response = self.session.request(
                allow_redirects=self.allow_redirects,
                data=self.data,
                headers=self.headers,
                method=self.model.tc_adv_req_http_method,
                params=self.params,
                timeout=self.timeout,
                url=self.model.tc_adv_req_path,
            )
        except RequestException as ex:  # pragma: no cover
            ex_msg = f'Exception during request ({ex}).'
            raise RuntimeError(ex_msg) from ex

        # write outputs as soon as they are available
        self.playbook.create.variable(
            f'{self.output_prefix}.request.headers', json.dumps(dict(response.headers)), 'String'
        )
        self.playbook.create.variable(
            f'{self.output_prefix}.request.ok', str(response.ok).lower(), 'String'
        )
        self.playbook.create.variable(
            f'{self.output_prefix}.request.reason', response.reason, 'String'
        )
        self.playbook.create.variable(
            f'{self.output_prefix}.request.status_code', str(response.status_code), 'String'
        )
        self.playbook.create.variable(
            f'{self.output_prefix}.request.url',
            response.request.url or self.model.tc_adv_req_path,
            'String',
        )

        # get response size
        response_bytes: int = len(response.content)
        response_mb: float = response_bytes / 1000000
        self.log.info(f'Response MB: {response_mb}')
        if response_mb > self.max_mb:  # pragma: no cover
            ex_msg = 'Download was larger than maximum supported 500 MB.'
            raise RuntimeError(ex_msg)

        # write content after size validation
        self.playbook.create.variable(
            f'{self.output_prefix}.request.content', response.text, 'String'
        )
        self.playbook.create.variable(
            f'{self.output_prefix}.request.content.binary', response.content, 'Binary'
        )

        # fail if fail_on_error is selected and not ok
        if self.model.tc_adv_req_fail_on_error and not response.ok:
            ex_msg = f'Failed for status ({response.status_code})'
            raise RuntimeError(ex_msg)

        return response
