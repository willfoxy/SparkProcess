"""
AWS Agent Core Memory Store.

Implements persistent cross-session memory using:
  - AWS Bedrock AgentCore Memory API (primary — boto3 client 'bedrock-agentcore')
  - DynamoDB fallback for environments where AgentCore is not yet available

The interface is intentionally thin so it can be swapped for the full
Amazon Bedrock AgentCore SDK once it reaches GA in your region.

See: https://aws.amazon.com/bedrock/agentcore/
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from typing import Any

import boto3
import structlog
from botocore.exceptions import ClientError

from backend.config import get_settings

logger = structlog.get_logger(__name__)

settings = get_settings()

# ---------------------------------------------------------------------------
# Low-level DynamoDB helper (used as the persistent backend)
# ---------------------------------------------------------------------------

def _make_dynamodb_client():
    kwargs: dict[str, Any] = {"region_name": settings.aws_region}
    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url
    if settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
        if settings.aws_session_token:
            kwargs["aws_session_token"] = settings.aws_session_token
    return boto3.client("dynamodb", **kwargs)


def _ensure_table(ddb_client) -> None:
    """Create the memory table if it does not exist yet."""
    try:
        ddb_client.describe_table(TableName=settings.dynamodb_table_name)
    except ClientError as exc:
        if exc.response["Error"]["Code"] != "ResourceNotFoundException":
            raise
        logger.info("Creating DynamoDB memory table", table=settings.dynamodb_table_name)
        ddb_client.create_table(
            TableName=settings.dynamodb_table_name,
            AttributeDefinitions=[
                {"AttributeName": "session_id", "AttributeType": "S"},
                {"AttributeName": "memory_key", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "session_id", "KeyType": "HASH"},
                {"AttributeName": "memory_key", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        # Wait for table to be active
        waiter = ddb_client.get_waiter("table_exists")
        waiter.wait(TableName=settings.dynamodb_table_name)
        logger.info("DynamoDB memory table ready", table=settings.dynamodb_table_name)


# ---------------------------------------------------------------------------
# AgentCoreMemoryStore — the public interface
# ---------------------------------------------------------------------------

class AgentCoreMemoryStore:
    """
    Persistent memory store modelled on the AWS Bedrock AgentCore Memory API.

    Each session gets its own partition. Within a session, memories are keyed
    by a `memory_key` string (e.g., "explorer_outputs", "security_check_1").

    When AWS releases the boto3 `bedrock-agentcore` client in your region,
    replace the DynamoDB calls below with the native API calls:

        self._agentcore = boto3.client("bedrock-agentcore", region_name=region)
        self._agentcore.create_memory(sessionId=session_id, ...)
        self._agentcore.retrieve_memory(sessionId=session_id, ...)
    """

    def __init__(self):
        try:
            self._ddb = _make_dynamodb_client()
            _ensure_table(self._ddb)
            self._available = True
        except Exception as exc:
            logger.warning("Memory store unavailable — running without persistence", error=str(exc))
            self._available = False
            self._local: dict[str, dict] = {}

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save(self, session_id: str, memory_key: str, value: Any) -> None:
        """Persist a value for the given session and key."""
        if not self._available:
            self._local.setdefault(session_id, {})[memory_key] = value
            return

        try:
            self._ddb.put_item(
                TableName=settings.dynamodb_table_name,
                Item={
                    "session_id": {"S": session_id},
                    "memory_key": {"S": memory_key},
                    "value": {"S": json.dumps(value, default=str)},
                    "updated_at": {"S": datetime.now(timezone.utc).isoformat()},
                    "ttl": {"N": str(int(time.time()) + 86400 * 30)},  # 30-day TTL
                },
            )
        except Exception as exc:
            logger.error("Failed to save memory", session_id=session_id, key=memory_key, error=str(exc))

    def save_phase(self, session_id: str, phase: str, outputs: dict) -> None:
        """Convenience wrapper to persist an entire phase's outputs."""
        self.save(session_id, f"phase_{phase}", outputs)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def load(self, session_id: str, memory_key: str) -> Any | None:
        """Retrieve a persisted value."""
        if not self._available:
            return self._local.get(session_id, {}).get(memory_key)

        try:
            resp = self._ddb.get_item(
                TableName=settings.dynamodb_table_name,
                Key={
                    "session_id": {"S": session_id},
                    "memory_key": {"S": memory_key},
                },
            )
            item = resp.get("Item")
            if item:
                return json.loads(item["value"]["S"])
        except Exception as exc:
            logger.error("Failed to load memory", session_id=session_id, key=memory_key, error=str(exc))
        return None

    def load_session(self, session_id: str) -> dict:
        """Return all memories for a session as a flat dictionary."""
        if not self._available:
            return self._local.get(session_id, {})

        try:
            resp = self._ddb.query(
                TableName=settings.dynamodb_table_name,
                KeyConditionExpression="session_id = :sid",
                ExpressionAttributeValues={":sid": {"S": session_id}},
            )
            return {
                item["memory_key"]["S"]: json.loads(item["value"]["S"])
                for item in resp.get("Items", [])
            }
        except Exception as exc:
            logger.error("Failed to load session memory", session_id=session_id, error=str(exc))
            return {}

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def clear_session(self, session_id: str) -> None:
        """Remove all memories for a session."""
        if not self._available:
            self._local.pop(session_id, None)
            return

        try:
            memories = self.load_session(session_id)
            for key in memories:
                self._ddb.delete_item(
                    TableName=settings.dynamodb_table_name,
                    Key={
                        "session_id": {"S": session_id},
                        "memory_key": {"S": key},
                    },
                )
        except Exception as exc:
            logger.error("Failed to clear session memory", session_id=session_id, error=str(exc))


# Singleton — import and use directly
memory_store = AgentCoreMemoryStore()
