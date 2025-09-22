from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class ManagementOrganizationProjectsCreateOutput:
  object: str
  id: str
  status: str
  slug: str
  name: str
  organization_id: str
  created_at: datetime
  updated_at: datetime


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapManagementOrganizationProjectsCreateOutput:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> ManagementOrganizationProjectsCreateOutput:
    return ManagementOrganizationProjectsCreateOutput(
      object=data.get("object"),
      id=data.get("id"),
      status=data.get("status"),
      slug=data.get("slug"),
      name=data.get("name"),
      organization_id=data.get("organization_id"),
      created_at=data.get("created_at")
      and datetime.fromisoformat(data.get("created_at")),
      updated_at=data.get("updated_at")
      and datetime.fromisoformat(data.get("updated_at")),
    )

  @staticmethod
  def to_dict(
    value: Union[ManagementOrganizationProjectsCreateOutput, Dict[str, Any], None],
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
class ManagementOrganizationProjectsCreateBody:
  name: str


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapManagementOrganizationProjectsCreateBody:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> ManagementOrganizationProjectsCreateBody:
    return ManagementOrganizationProjectsCreateBody(name=data.get("name"))

  @staticmethod
  def to_dict(
    value: Union[ManagementOrganizationProjectsCreateBody, Dict[str, Any], None],
  ) -> Optional[Dict[str, Any]]:
    if value is None:
      return None
    if isinstance(value, dict):
      return value
    # assume dataclass for generated models
    return dataclasses.asdict(value)
