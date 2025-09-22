from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class ManagementOrganizationInvitesGetOutput:
  object: str
  id: str
  status: str
  role: str
  type: str
  email: str
  organization: Dict[str, Any]
  invited_by: Dict[str, Any]
  invite_link: Dict[str, Any]
  created_at: datetime
  updated_at: datetime
  deleted_at: datetime
  expires_at: datetime
  accepted_at: datetime
  rejected_at: datetime


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapManagementOrganizationInvitesGetOutput:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> ManagementOrganizationInvitesGetOutput:
    return ManagementOrganizationInvitesGetOutput(
      object=data.get("object"),
      id=data.get("id"),
      status=data.get("status"),
      role=data.get("role"),
      type=data.get("type"),
      email=data.get("email"),
      organization=data.get("organization")
      and {
        "object": data.get("organization", {}).get("object"),
        "id": data.get("organization", {}).get("id"),
        "status": data.get("organization", {}).get("status"),
        "type": data.get("organization", {}).get("type"),
        "slug": data.get("organization", {}).get("slug"),
        "name": data.get("organization", {}).get("name"),
        "organization_id": data.get("organization", {}).get("organization_id"),
        "image_url": data.get("organization", {}).get("image_url"),
        "created_at": data.get("organization", {}).get("created_at")
        and datetime.fromisoformat(data.get("organization", {}).get("created_at")),
        "updated_at": data.get("organization", {}).get("updated_at")
        and datetime.fromisoformat(data.get("organization", {}).get("updated_at")),
      },
      invited_by=data.get("invited_by")
      and {
        "object": data.get("invited_by", {}).get("object"),
        "id": data.get("invited_by", {}).get("id"),
        "type": data.get("invited_by", {}).get("type"),
        "organization_id": data.get("invited_by", {}).get("organization_id"),
        "actor_id": data.get("invited_by", {}).get("actor_id"),
        "name": data.get("invited_by", {}).get("name"),
        "email": data.get("invited_by", {}).get("email"),
        "image_url": data.get("invited_by", {}).get("image_url"),
        "created_at": data.get("invited_by", {}).get("created_at")
        and datetime.fromisoformat(data.get("invited_by", {}).get("created_at")),
        "updated_at": data.get("invited_by", {}).get("updated_at")
        and datetime.fromisoformat(data.get("invited_by", {}).get("updated_at")),
      },
      invite_link=data.get("invite_link")
      and {
        "object": data.get("invite_link", {}).get("object"),
        "id": data.get("invite_link", {}).get("id"),
        "key": data.get("invite_link", {}).get("key"),
        "key_redacted": data.get("invite_link", {}).get("key_redacted"),
        "url": data.get("invite_link", {}).get("url"),
        "created_at": data.get("invite_link", {}).get("created_at")
        and datetime.fromisoformat(data.get("invite_link", {}).get("created_at")),
      },
      created_at=data.get("created_at")
      and datetime.fromisoformat(data.get("created_at")),
      updated_at=data.get("updated_at")
      and datetime.fromisoformat(data.get("updated_at")),
      deleted_at=data.get("deleted_at")
      and datetime.fromisoformat(data.get("deleted_at")),
      expires_at=data.get("expires_at")
      and datetime.fromisoformat(data.get("expires_at")),
      accepted_at=data.get("accepted_at")
      and datetime.fromisoformat(data.get("accepted_at")),
      rejected_at=data.get("rejected_at")
      and datetime.fromisoformat(data.get("rejected_at")),
    )

  @staticmethod
  def to_dict(
    value: Union[ManagementOrganizationInvitesGetOutput, Dict[str, Any], None],
  ) -> Optional[Dict[str, Any]]:
    if value is None:
      return None
    if isinstance(value, dict):
      return value
    # assume dataclass for generated models
    return dataclasses.asdict(value)
