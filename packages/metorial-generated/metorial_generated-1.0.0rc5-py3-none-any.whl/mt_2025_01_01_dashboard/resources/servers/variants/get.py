from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class ServersVariantsGetOutput:
  object: str
  id: str
  identifier: str
  server: Dict[str, Any]
  source: Union[Dict[str, Any], Dict[str, Any]]
  created_at: datetime
  current_version: Optional[Dict[str, Any]] = None


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapServersVariantsGetOutput:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> ServersVariantsGetOutput:
    return ServersVariantsGetOutput(
      object=data.get("object"),
      id=data.get("id"),
      identifier=data.get("identifier"),
      server=data.get("server")
      and {
        "object": data.get("server", {}).get("object"),
        "id": data.get("server", {}).get("id"),
        "name": data.get("server", {}).get("name"),
        "description": data.get("server", {}).get("description"),
        "type": data.get("server", {}).get("type"),
        "created_at": data.get("server", {}).get("created_at")
        and datetime.fromisoformat(data.get("server", {}).get("created_at")),
        "updated_at": data.get("server", {}).get("updated_at")
        and datetime.fromisoformat(data.get("server", {}).get("updated_at")),
      },
      current_version=data.get("current_version")
      and {
        "object": data.get("current_version", {}).get("object"),
        "id": data.get("current_version", {}).get("id"),
        "identifier": data.get("current_version", {}).get("identifier"),
        "server_id": data.get("current_version", {}).get("server_id"),
        "server_variant_id": data.get("current_version", {}).get("server_variant_id"),
        "get_launch_params": data.get("current_version", {}).get("get_launch_params"),
        "source": data.get("current_version", {}).get("source"),
        "schema": data.get("current_version", {}).get("schema")
        and {
          "id": data.get("current_version", {}).get("schema", {}).get("id"),
          "fingerprint": data.get("current_version", {})
          .get("schema", {})
          .get("fingerprint"),
          "schema": data.get("current_version", {}).get("schema", {}).get("schema"),
          "server_id": data.get("current_version", {})
          .get("schema", {})
          .get("server_id"),
          "server_variant_id": data.get("current_version", {})
          .get("schema", {})
          .get("server_variant_id"),
          "server_version_id": data.get("current_version", {})
          .get("schema", {})
          .get("server_version_id"),
          "created_at": data.get("current_version", {})
          .get("schema", {})
          .get("created_at")
          and datetime.fromisoformat(
            data.get("current_version", {}).get("schema", {}).get("created_at")
          ),
        },
        "server": data.get("current_version", {}).get("server")
        and {
          "object": data.get("current_version", {}).get("server", {}).get("object"),
          "id": data.get("current_version", {}).get("server", {}).get("id"),
          "name": data.get("current_version", {}).get("server", {}).get("name"),
          "description": data.get("current_version", {})
          .get("server", {})
          .get("description"),
          "type": data.get("current_version", {}).get("server", {}).get("type"),
          "created_at": data.get("current_version", {})
          .get("server", {})
          .get("created_at")
          and datetime.fromisoformat(
            data.get("current_version", {}).get("server", {}).get("created_at")
          ),
          "updated_at": data.get("current_version", {})
          .get("server", {})
          .get("updated_at")
          and datetime.fromisoformat(
            data.get("current_version", {}).get("server", {}).get("updated_at")
          ),
        },
        "created_at": data.get("current_version", {}).get("created_at")
        and datetime.fromisoformat(data.get("current_version", {}).get("created_at")),
      },
      source=data.get("source"),
      created_at=data.get("created_at")
      and datetime.fromisoformat(data.get("created_at")),
    )

  @staticmethod
  def to_dict(
    value: Union[ServersVariantsGetOutput, Dict[str, Any], None],
  ) -> Optional[Dict[str, Any]]:
    if value is None:
      return None
    if isinstance(value, dict):
      return value
    # assume dataclass for generated models
    return dataclasses.asdict(value)
