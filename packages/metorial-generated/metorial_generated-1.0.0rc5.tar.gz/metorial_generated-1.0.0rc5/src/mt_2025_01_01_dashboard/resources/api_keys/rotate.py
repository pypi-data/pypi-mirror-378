from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class ApiKeysRotateOutput:
  object: str
  id: str
  status: str
  secret_redacted: str
  secret_redacted_long: str
  type: str
  name: str
  machine_access: Dict[str, Any]
  created_at: datetime
  updated_at: datetime
  secret: Optional[str] = None
  description: Optional[str] = None
  deleted_at: Optional[datetime] = None
  last_used_at: Optional[datetime] = None
  expires_at: Optional[datetime] = None
  reveal_info: Optional[Dict[str, Any]] = None


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapApiKeysRotateOutput:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> ApiKeysRotateOutput:
    return ApiKeysRotateOutput(
      object=data.get("object"),
      id=data.get("id"),
      status=data.get("status"),
      secret_redacted=data.get("secret_redacted"),
      secret_redacted_long=data.get("secret_redacted_long"),
      secret=data.get("secret"),
      type=data.get("type"),
      name=data.get("name"),
      description=data.get("description"),
      machine_access=data.get("machine_access")
      and {
        "object": data.get("machine_access", {}).get("object"),
        "id": data.get("machine_access", {}).get("id"),
        "status": data.get("machine_access", {}).get("status"),
        "type": data.get("machine_access", {}).get("type"),
        "name": data.get("machine_access", {}).get("name"),
        "actor": data.get("machine_access", {}).get("actor")
        and {
          "object": data.get("machine_access", {}).get("actor", {}).get("object"),
          "id": data.get("machine_access", {}).get("actor", {}).get("id"),
          "type": data.get("machine_access", {}).get("actor", {}).get("type"),
          "organization_id": data.get("machine_access", {})
          .get("actor", {})
          .get("organization_id"),
          "actor_id": data.get("machine_access", {}).get("actor", {}).get("actor_id"),
          "name": data.get("machine_access", {}).get("actor", {}).get("name"),
          "email": data.get("machine_access", {}).get("actor", {}).get("email"),
          "image_url": data.get("machine_access", {}).get("actor", {}).get("image_url"),
          "created_at": data.get("machine_access", {})
          .get("actor", {})
          .get("created_at")
          and datetime.fromisoformat(
            data.get("machine_access", {}).get("actor", {}).get("created_at")
          ),
          "updated_at": data.get("machine_access", {})
          .get("actor", {})
          .get("updated_at")
          and datetime.fromisoformat(
            data.get("machine_access", {}).get("actor", {}).get("updated_at")
          ),
        },
        "instance": data.get("machine_access", {}).get("instance")
        and {
          "object": data.get("machine_access", {}).get("instance", {}).get("object"),
          "id": data.get("machine_access", {}).get("instance", {}).get("id"),
          "status": data.get("machine_access", {}).get("instance", {}).get("status"),
          "slug": data.get("machine_access", {}).get("instance", {}).get("slug"),
          "name": data.get("machine_access", {}).get("instance", {}).get("name"),
          "type": data.get("machine_access", {}).get("instance", {}).get("type"),
          "organization_id": data.get("machine_access", {})
          .get("instance", {})
          .get("organization_id"),
          "project": data.get("machine_access", {}).get("instance", {}).get("project")
          and {
            "object": data.get("machine_access", {})
            .get("instance", {})
            .get("project", {})
            .get("object"),
            "id": data.get("machine_access", {})
            .get("instance", {})
            .get("project", {})
            .get("id"),
            "status": data.get("machine_access", {})
            .get("instance", {})
            .get("project", {})
            .get("status"),
            "slug": data.get("machine_access", {})
            .get("instance", {})
            .get("project", {})
            .get("slug"),
            "name": data.get("machine_access", {})
            .get("instance", {})
            .get("project", {})
            .get("name"),
            "organization_id": data.get("machine_access", {})
            .get("instance", {})
            .get("project", {})
            .get("organization_id"),
            "created_at": data.get("machine_access", {})
            .get("instance", {})
            .get("project", {})
            .get("created_at")
            and datetime.fromisoformat(
              data.get("machine_access", {})
              .get("instance", {})
              .get("project", {})
              .get("created_at")
            ),
            "updated_at": data.get("machine_access", {})
            .get("instance", {})
            .get("project", {})
            .get("updated_at")
            and datetime.fromisoformat(
              data.get("machine_access", {})
              .get("instance", {})
              .get("project", {})
              .get("updated_at")
            ),
          },
          "created_at": data.get("machine_access", {})
          .get("instance", {})
          .get("created_at")
          and datetime.fromisoformat(
            data.get("machine_access", {}).get("instance", {}).get("created_at")
          ),
          "updated_at": data.get("machine_access", {})
          .get("instance", {})
          .get("updated_at")
          and datetime.fromisoformat(
            data.get("machine_access", {}).get("instance", {}).get("updated_at")
          ),
        },
        "organization": data.get("machine_access", {}).get("organization")
        and {
          "object": data.get("machine_access", {})
          .get("organization", {})
          .get("object"),
          "id": data.get("machine_access", {}).get("organization", {}).get("id"),
          "status": data.get("machine_access", {})
          .get("organization", {})
          .get("status"),
          "type": data.get("machine_access", {}).get("organization", {}).get("type"),
          "slug": data.get("machine_access", {}).get("organization", {}).get("slug"),
          "name": data.get("machine_access", {}).get("organization", {}).get("name"),
          "organization_id": data.get("machine_access", {})
          .get("organization", {})
          .get("organization_id"),
          "image_url": data.get("machine_access", {})
          .get("organization", {})
          .get("image_url"),
          "created_at": data.get("machine_access", {})
          .get("organization", {})
          .get("created_at")
          and datetime.fromisoformat(
            data.get("machine_access", {}).get("organization", {}).get("created_at")
          ),
          "updated_at": data.get("machine_access", {})
          .get("organization", {})
          .get("updated_at")
          and datetime.fromisoformat(
            data.get("machine_access", {}).get("organization", {}).get("updated_at")
          ),
        },
        "user": data.get("machine_access", {}).get("user")
        and {
          "object": data.get("machine_access", {}).get("user", {}).get("object"),
          "id": data.get("machine_access", {}).get("user", {}).get("id"),
          "status": data.get("machine_access", {}).get("user", {}).get("status"),
          "type": data.get("machine_access", {}).get("user", {}).get("type"),
          "email": data.get("machine_access", {}).get("user", {}).get("email"),
          "name": data.get("machine_access", {}).get("user", {}).get("name"),
          "first_name": data.get("machine_access", {})
          .get("user", {})
          .get("first_name"),
          "last_name": data.get("machine_access", {}).get("user", {}).get("last_name"),
          "image_url": data.get("machine_access", {}).get("user", {}).get("image_url"),
          "created_at": data.get("machine_access", {}).get("user", {}).get("created_at")
          and datetime.fromisoformat(
            data.get("machine_access", {}).get("user", {}).get("created_at")
          ),
          "updated_at": data.get("machine_access", {}).get("user", {}).get("updated_at")
          and datetime.fromisoformat(
            data.get("machine_access", {}).get("user", {}).get("updated_at")
          ),
        },
        "deleted_at": data.get("machine_access", {}).get("deleted_at")
        and datetime.fromisoformat(data.get("machine_access", {}).get("deleted_at")),
        "last_used_at": data.get("machine_access", {}).get("last_used_at")
        and datetime.fromisoformat(data.get("machine_access", {}).get("last_used_at")),
        "created_at": data.get("machine_access", {}).get("created_at")
        and datetime.fromisoformat(data.get("machine_access", {}).get("created_at")),
        "updated_at": data.get("machine_access", {}).get("updated_at")
        and datetime.fromisoformat(data.get("machine_access", {}).get("updated_at")),
      },
      deleted_at=data.get("deleted_at")
      and datetime.fromisoformat(data.get("deleted_at")),
      last_used_at=data.get("last_used_at")
      and datetime.fromisoformat(data.get("last_used_at")),
      expires_at=data.get("expires_at")
      and datetime.fromisoformat(data.get("expires_at")),
      created_at=data.get("created_at")
      and datetime.fromisoformat(data.get("created_at")),
      updated_at=data.get("updated_at")
      and datetime.fromisoformat(data.get("updated_at")),
      reveal_info=data.get("reveal_info")
      and {
        "until": data.get("reveal_info", {}).get("until")
        and datetime.fromisoformat(data.get("reveal_info", {}).get("until")),
        "forever": data.get("reveal_info", {}).get("forever"),
      },
    )

  @staticmethod
  def to_dict(
    value: Union[ApiKeysRotateOutput, Dict[str, Any], None],
  ) -> Optional[Dict[str, Any]]:
    if value is None:
      return None
    if isinstance(value, dict):
      return value
    # assume dataclass for generated models
    return dataclasses.asdict(value)


from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class ApiKeysRotateBody:
  current_expires_at: Optional[datetime] = None


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapApiKeysRotateBody:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> ApiKeysRotateBody:
    return ApiKeysRotateBody(
      current_expires_at=data.get("current_expires_at")
      and datetime.fromisoformat(data.get("current_expires_at"))
    )

  @staticmethod
  def to_dict(
    value: Union[ApiKeysRotateBody, Dict[str, Any], None],
  ) -> Optional[Dict[str, Any]]:
    if value is None:
      return None
    if isinstance(value, dict):
      return value
    # assume dataclass for generated models
    return dataclasses.asdict(value)
