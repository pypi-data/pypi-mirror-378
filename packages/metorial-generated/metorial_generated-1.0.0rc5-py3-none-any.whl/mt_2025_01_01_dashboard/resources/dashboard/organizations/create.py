from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class DashboardOrganizationsCreateOutput:
  object: str
  id: str
  status: str
  type: str
  slug: str
  name: str
  organization_id: str
  image_url: str
  created_at: datetime
  updated_at: datetime


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapDashboardOrganizationsCreateOutput:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> DashboardOrganizationsCreateOutput:
    return DashboardOrganizationsCreateOutput(
      object=data.get("object"),
      id=data.get("id"),
      status=data.get("status"),
      type=data.get("type"),
      slug=data.get("slug"),
      name=data.get("name"),
      organization_id=data.get("organization_id"),
      image_url=data.get("image_url"),
      created_at=data.get("created_at")
      and datetime.fromisoformat(data.get("created_at")),
      updated_at=data.get("updated_at")
      and datetime.fromisoformat(data.get("updated_at")),
    )

  @staticmethod
  def to_dict(
    value: Union[DashboardOrganizationsCreateOutput, Dict[str, Any], None],
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
class DashboardOrganizationsCreateBody:
  name: str


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapDashboardOrganizationsCreateBody:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> DashboardOrganizationsCreateBody:
    return DashboardOrganizationsCreateBody(name=data.get("name"))

  @staticmethod
  def to_dict(
    value: Union[DashboardOrganizationsCreateBody, Dict[str, Any], None],
  ) -> Optional[Dict[str, Any]]:
    if value is None:
      return None
    if isinstance(value, dict):
      return value
    # assume dataclass for generated models
    return dataclasses.asdict(value)
