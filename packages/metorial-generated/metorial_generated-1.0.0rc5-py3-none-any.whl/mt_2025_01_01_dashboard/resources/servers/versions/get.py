from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class ServersVersionsGetOutput:
  object: str
  id: str
  identifier: str
  server_id: str
  server_variant_id: str
  get_launch_params: str
  source: Union[Dict[str, Any], Dict[str, Any]]
  schema: Dict[str, Any]
  server: Dict[str, Any]
  created_at: datetime


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapServersVersionsGetOutput:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> ServersVersionsGetOutput:
    return ServersVersionsGetOutput(
      object=data.get("object"),
      id=data.get("id"),
      identifier=data.get("identifier"),
      server_id=data.get("server_id"),
      server_variant_id=data.get("server_variant_id"),
      get_launch_params=data.get("get_launch_params"),
      source=data.get("source"),
      schema=data.get("schema")
      and {
        "id": data.get("schema", {}).get("id"),
        "fingerprint": data.get("schema", {}).get("fingerprint"),
        "schema": data.get("schema", {}).get("schema"),
        "server_id": data.get("schema", {}).get("server_id"),
        "server_variant_id": data.get("schema", {}).get("server_variant_id"),
        "server_version_id": data.get("schema", {}).get("server_version_id"),
        "created_at": data.get("schema", {}).get("created_at")
        and datetime.fromisoformat(data.get("schema", {}).get("created_at")),
      },
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
      created_at=data.get("created_at")
      and datetime.fromisoformat(data.get("created_at")),
    )

  @staticmethod
  def to_dict(
    value: Union[ServersVersionsGetOutput, Dict[str, Any], None],
  ) -> Optional[Dict[str, Any]]:
    if value is None:
      return None
    if isinstance(value, dict):
      return value
    # assume dataclass for generated models
    return dataclasses.asdict(value)
