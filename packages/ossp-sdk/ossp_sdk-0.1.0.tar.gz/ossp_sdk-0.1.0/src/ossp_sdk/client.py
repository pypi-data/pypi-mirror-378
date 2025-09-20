"""OSSP CloudEvents client."""

from __future__ import annotations

import json
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger(__name__)


def _maybe_validate(payload: Dict[str, Any], event_type: str, schema_dir: Optional[str]) -> None:
    """Validate payload against the JSON Schema if validation is enabled."""
    if not os.getenv("OSSP_VALIDATE"):
        return

    if not schema_dir:
        logger.warning("OSSP_VALIDATE is set but no schema directory provided; skipping validation.")
        return

    schema_filename = f"{event_type}.schema.json"
    schema_path = os.path.join(schema_dir, schema_filename)

    if not os.path.isfile(schema_path):
        logger.error("Schema file not found for event type %s at %s", event_type, schema_path)
        raise FileNotFoundError(schema_path)

    try:
        import jsonschema
    except ImportError as exc:  # pragma: no cover
        logger.error("jsonschema is required for validation but is not installed.")
        raise exc

    with open(schema_path, "r", encoding="utf-8") as handle:
        schema = json.load(handle)

    jsonschema.validate(instance=payload, schema=schema)


class OSSPClient:
    """CloudEvents 1.0 client for the Open Safety Signal Protocol."""

    def __init__(
        self,
        collector_endpoint: Optional[str] = None,
        auth_token: Optional[str] = None,
        source_uri: Optional[str] = None,
        dataschema_base: str = "https://ossp.io/schema/v1.0.0",
        schema_dir: Optional[str] = None,
        timeout_seconds: float = 2.0,
        max_retries: int = 3,
        backoff_base_seconds: float = 0.2,
        idempotency_key: Optional[str] = None,
    ) -> None:
        self.collector_endpoint = collector_endpoint or os.getenv("OSSP_COLLECTOR_ENDPOINT")
        self.auth_token = auth_token or os.getenv("OSSP_AUTH_TOKEN")
        self.source_uri = source_uri or os.getenv("OSSP_SOURCE_URI", "urn:default:python-sdk")
        self.dataschema_base = dataschema_base.rstrip("/")
        self.schema_dir = schema_dir or os.getenv("OSSP_SCHEMA_DIR")
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.backoff_base_seconds = backoff_base_seconds
        self.idempotency_key = idempotency_key
        self._session = requests.Session()

        self.headers: Dict[str, str] = {
            "Content-Type": "application/cloudevents+json; charset=utf-8",
            "User-Agent": f"ossp-sdk/{os.getenv('OSSP_SDK_VERSION', '0.1.0')}",
        }
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"
        if self.idempotency_key:
            self.headers["Idempotency-Key"] = self.idempotency_key

        if not self.collector_endpoint:
            logger.info("OSSP collector endpoint not set; events will be logged locally.")

    def emit(
        self,
        event_type: str,
        resource: Dict[str, Any],
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
        subject: Optional[str] = None,
        dataschema: Optional[str] = None,
        extra_headers: Optional[Dict[str, str]] = None,
        traceparent: Optional[str] = None,
        tracestate: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Emit an OSSP CloudEvent and optionally send it to a collector."""
        if not resource or not resource.get("model_id") or not resource.get("environment"):
            logger.warning("resource.model_id and resource.environment should be provided for OSSP events.")

        cloud_event: Dict[str, Any] = {
            "specversion": "1.0",
            "id": str(uuid.uuid4()),
            "type": event_type,
            "source": self.source_uri,
            "time": datetime.now(timezone.utc).isoformat(),
            "datacontenttype": "application/json",
            "dataschema": dataschema or f"{self.dataschema_base}/{event_type}.schema.json",
            "data": {**data, "resource": resource},
        }

        if subject:
            cloud_event["subject"] = subject
        if correlation_id:
            cloud_event["correlationid"] = correlation_id

        # optional W3C trace context as HTTP headers
        if traceparent:
            self.headers["traceparent"] = traceparent
        if tracestate:
            self.headers["tracestate"] = tracestate

        _maybe_validate(cloud_event["data"], event_type, self.schema_dir)

        payload = json.dumps(cloud_event, separators=(",", ":"))

        if self.collector_endpoint:
            headers = dict(self.headers)
            if extra_headers:
                headers.update(extra_headers)
            attempt = 0
            import random, time
            while True:
                try:
                    response = self._session.post(
                        self.collector_endpoint,
                        data=payload,
                        headers=headers,
                        timeout=self.timeout_seconds,
                    )
                    if response.status_code in (429, 500, 502, 503, 504):
                        raise requests.HTTPError(f"retryable {response.status_code}", response=response)
                    response.raise_for_status()
                    logger.debug("OSSP event sent successfully.")
                    break
                except requests.RequestException as exc:
                    attempt += 1
                    if attempt > self.max_retries:
                        logger.error("Failed to send OSSP event after %d attempts: %s", attempt - 1, exc)
                        break
                    sleep_s = self.backoff_base_seconds * (2 ** (attempt - 1)) * (1 + 0.2 * random.random())
                    time.sleep(sleep_s)
        else:
            logger.info("[OSSP CE] %s", payload)

        return cloud_event
