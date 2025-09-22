from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class ServerRunErrorGroupsGetOutput:
  object: str
  id: str
  code: str
  message: str
  fingerprint: str
  count: float
  created_at: datetime
  first_seen_at: datetime
  last_seen_at: datetime
  default_error: Optional[Dict[str, Any]] = None


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapServerRunErrorGroupsGetOutput:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> ServerRunErrorGroupsGetOutput:
    return ServerRunErrorGroupsGetOutput(
      object=data.get("object"),
      id=data.get("id"),
      code=data.get("code"),
      message=data.get("message"),
      fingerprint=data.get("fingerprint"),
      count=data.get("count"),
      default_error=data.get("default_error")
      and {
        "object": data.get("default_error", {}).get("object"),
        "id": data.get("default_error", {}).get("id"),
        "code": data.get("default_error", {}).get("code"),
        "message": data.get("default_error", {}).get("message"),
        "metadata": data.get("default_error", {}).get("metadata"),
        "server_run": data.get("default_error", {}).get("server_run")
        and {
          "object": data.get("default_error", {}).get("server_run", {}).get("object"),
          "id": data.get("default_error", {}).get("server_run", {}).get("id"),
          "type": data.get("default_error", {}).get("server_run", {}).get("type"),
          "status": data.get("default_error", {}).get("server_run", {}).get("status"),
          "server_version_id": data.get("default_error", {})
          .get("server_run", {})
          .get("server_version_id"),
          "server": data.get("default_error", {}).get("server_run", {}).get("server")
          and {
            "object": data.get("default_error", {})
            .get("server_run", {})
            .get("server", {})
            .get("object"),
            "id": data.get("default_error", {})
            .get("server_run", {})
            .get("server", {})
            .get("id"),
            "name": data.get("default_error", {})
            .get("server_run", {})
            .get("server", {})
            .get("name"),
            "description": data.get("default_error", {})
            .get("server_run", {})
            .get("server", {})
            .get("description"),
            "type": data.get("default_error", {})
            .get("server_run", {})
            .get("server", {})
            .get("type"),
            "created_at": data.get("default_error", {})
            .get("server_run", {})
            .get("server", {})
            .get("created_at")
            and datetime.fromisoformat(
              data.get("default_error", {})
              .get("server_run", {})
              .get("server", {})
              .get("created_at")
            ),
            "updated_at": data.get("default_error", {})
            .get("server_run", {})
            .get("server", {})
            .get("updated_at")
            and datetime.fromisoformat(
              data.get("default_error", {})
              .get("server_run", {})
              .get("server", {})
              .get("updated_at")
            ),
          },
          "server_deployment": data.get("default_error", {})
          .get("server_run", {})
          .get("server_deployment")
          and {
            "object": data.get("default_error", {})
            .get("server_run", {})
            .get("server_deployment", {})
            .get("object"),
            "id": data.get("default_error", {})
            .get("server_run", {})
            .get("server_deployment", {})
            .get("id"),
            "name": data.get("default_error", {})
            .get("server_run", {})
            .get("server_deployment", {})
            .get("name"),
            "description": data.get("default_error", {})
            .get("server_run", {})
            .get("server_deployment", {})
            .get("description"),
            "metadata": data.get("default_error", {})
            .get("server_run", {})
            .get("server_deployment", {})
            .get("metadata"),
            "created_at": data.get("default_error", {})
            .get("server_run", {})
            .get("server_deployment", {})
            .get("created_at")
            and datetime.fromisoformat(
              data.get("default_error", {})
              .get("server_run", {})
              .get("server_deployment", {})
              .get("created_at")
            ),
            "updated_at": data.get("default_error", {})
            .get("server_run", {})
            .get("server_deployment", {})
            .get("updated_at")
            and datetime.fromisoformat(
              data.get("default_error", {})
              .get("server_run", {})
              .get("server_deployment", {})
              .get("updated_at")
            ),
            "server": data.get("default_error", {})
            .get("server_run", {})
            .get("server_deployment", {})
            .get("server")
            and {
              "object": data.get("default_error", {})
              .get("server_run", {})
              .get("server_deployment", {})
              .get("server", {})
              .get("object"),
              "id": data.get("default_error", {})
              .get("server_run", {})
              .get("server_deployment", {})
              .get("server", {})
              .get("id"),
              "name": data.get("default_error", {})
              .get("server_run", {})
              .get("server_deployment", {})
              .get("server", {})
              .get("name"),
              "description": data.get("default_error", {})
              .get("server_run", {})
              .get("server_deployment", {})
              .get("server", {})
              .get("description"),
              "type": data.get("default_error", {})
              .get("server_run", {})
              .get("server_deployment", {})
              .get("server", {})
              .get("type"),
              "created_at": data.get("default_error", {})
              .get("server_run", {})
              .get("server_deployment", {})
              .get("server", {})
              .get("created_at")
              and datetime.fromisoformat(
                data.get("default_error", {})
                .get("server_run", {})
                .get("server_deployment", {})
                .get("server", {})
                .get("created_at")
              ),
              "updated_at": data.get("default_error", {})
              .get("server_run", {})
              .get("server_deployment", {})
              .get("server", {})
              .get("updated_at")
              and datetime.fromisoformat(
                data.get("default_error", {})
                .get("server_run", {})
                .get("server_deployment", {})
                .get("server", {})
                .get("updated_at")
              ),
            },
          },
          "server_session": data.get("default_error", {})
          .get("server_run", {})
          .get("server_session")
          and {
            "object": data.get("default_error", {})
            .get("server_run", {})
            .get("server_session", {})
            .get("object"),
            "id": data.get("default_error", {})
            .get("server_run", {})
            .get("server_session", {})
            .get("id"),
            "status": data.get("default_error", {})
            .get("server_run", {})
            .get("server_session", {})
            .get("status"),
            "mcp": data.get("default_error", {})
            .get("server_run", {})
            .get("server_session", {})
            .get("mcp")
            and {
              "object": data.get("default_error", {})
              .get("server_run", {})
              .get("server_session", {})
              .get("mcp", {})
              .get("object"),
              "version": data.get("default_error", {})
              .get("server_run", {})
              .get("server_session", {})
              .get("mcp", {})
              .get("version"),
              "connection_type": data.get("default_error", {})
              .get("server_run", {})
              .get("server_session", {})
              .get("mcp", {})
              .get("connection_type"),
              "client": data.get("default_error", {})
              .get("server_run", {})
              .get("server_session", {})
              .get("mcp", {})
              .get("client")
              and {
                "object": data.get("default_error", {})
                .get("server_run", {})
                .get("server_session", {})
                .get("mcp", {})
                .get("client", {})
                .get("object"),
                "name": data.get("default_error", {})
                .get("server_run", {})
                .get("server_session", {})
                .get("mcp", {})
                .get("client", {})
                .get("name"),
                "version": data.get("default_error", {})
                .get("server_run", {})
                .get("server_session", {})
                .get("mcp", {})
                .get("client", {})
                .get("version"),
                "capabilities": data.get("default_error", {})
                .get("server_run", {})
                .get("server_session", {})
                .get("mcp", {})
                .get("client", {})
                .get("capabilities"),
              },
              "server": data.get("default_error", {})
              .get("server_run", {})
              .get("server_session", {})
              .get("mcp", {})
              .get("server")
              and {
                "object": data.get("default_error", {})
                .get("server_run", {})
                .get("server_session", {})
                .get("mcp", {})
                .get("server", {})
                .get("object"),
                "name": data.get("default_error", {})
                .get("server_run", {})
                .get("server_session", {})
                .get("mcp", {})
                .get("server", {})
                .get("name"),
                "version": data.get("default_error", {})
                .get("server_run", {})
                .get("server_session", {})
                .get("mcp", {})
                .get("server", {})
                .get("version"),
                "capabilities": data.get("default_error", {})
                .get("server_run", {})
                .get("server_session", {})
                .get("mcp", {})
                .get("server", {})
                .get("capabilities"),
              },
            },
            "usage": data.get("default_error", {})
            .get("server_run", {})
            .get("server_session", {})
            .get("usage")
            and {
              "total_productive_message_count": data.get("default_error", {})
              .get("server_run", {})
              .get("server_session", {})
              .get("usage", {})
              .get("total_productive_message_count"),
              "total_productive_client_message_count": data.get("default_error", {})
              .get("server_run", {})
              .get("server_session", {})
              .get("usage", {})
              .get("total_productive_client_message_count"),
              "total_productive_server_message_count": data.get("default_error", {})
              .get("server_run", {})
              .get("server_session", {})
              .get("usage", {})
              .get("total_productive_server_message_count"),
            },
            "session_id": data.get("default_error", {})
            .get("server_run", {})
            .get("server_session", {})
            .get("session_id"),
            "created_at": data.get("default_error", {})
            .get("server_run", {})
            .get("server_session", {})
            .get("created_at")
            and datetime.fromisoformat(
              data.get("default_error", {})
              .get("server_run", {})
              .get("server_session", {})
              .get("created_at")
            ),
          },
          "created_at": data.get("default_error", {})
          .get("server_run", {})
          .get("created_at")
          and datetime.fromisoformat(
            data.get("default_error", {}).get("server_run", {}).get("created_at")
          ),
          "updated_at": data.get("default_error", {})
          .get("server_run", {})
          .get("updated_at")
          and datetime.fromisoformat(
            data.get("default_error", {}).get("server_run", {}).get("updated_at")
          ),
          "started_at": data.get("default_error", {})
          .get("server_run", {})
          .get("started_at")
          and datetime.fromisoformat(
            data.get("default_error", {}).get("server_run", {}).get("started_at")
          ),
          "stopped_at": data.get("default_error", {})
          .get("server_run", {})
          .get("stopped_at")
          and datetime.fromisoformat(
            data.get("default_error", {}).get("server_run", {}).get("stopped_at")
          ),
        },
        "created_at": data.get("default_error", {}).get("created_at")
        and datetime.fromisoformat(data.get("default_error", {}).get("created_at")),
      },
      created_at=data.get("created_at")
      and datetime.fromisoformat(data.get("created_at")),
      first_seen_at=data.get("first_seen_at")
      and datetime.fromisoformat(data.get("first_seen_at")),
      last_seen_at=data.get("last_seen_at")
      and datetime.fromisoformat(data.get("last_seen_at")),
    )

  @staticmethod
  def to_dict(
    value: Union[ServerRunErrorGroupsGetOutput, Dict[str, Any], None],
  ) -> Optional[Dict[str, Any]]:
    if value is None:
      return None
    if isinstance(value, dict):
      return value
    # assume dataclass for generated models
    return dataclasses.asdict(value)
