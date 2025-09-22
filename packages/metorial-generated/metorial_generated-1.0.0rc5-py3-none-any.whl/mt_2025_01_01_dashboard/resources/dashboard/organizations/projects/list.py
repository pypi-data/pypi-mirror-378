from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class DashboardOrganizationsProjectsListOutput:
  items: List[Dict[str, Any]]
  pagination: Dict[str, Any]


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapDashboardOrganizationsProjectsListOutput:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> DashboardOrganizationsProjectsListOutput:
    return DashboardOrganizationsProjectsListOutput(
      items=[
        {
          "object": item.get("object"),
          "id": item.get("id"),
          "status": item.get("status"),
          "slug": item.get("slug"),
          "name": item.get("name"),
          "organization_id": item.get("organization_id"),
          "created_at": item.get("created_at")
          and datetime.fromisoformat(item.get("created_at")),
          "updated_at": item.get("updated_at")
          and datetime.fromisoformat(item.get("updated_at")),
        }
        for item in data.get("items", [])
      ],
      pagination=data.get("pagination")
      and {
        "has_more_before": data.get("pagination", {}).get("has_more_before"),
        "has_more_after": data.get("pagination", {}).get("has_more_after"),
      },
    )

  @staticmethod
  def to_dict(
    value: Union[DashboardOrganizationsProjectsListOutput, Dict[str, Any], None],
  ) -> Optional[Dict[str, Any]]:
    if value is None:
      return None
    if isinstance(value, dict):
      return value
    # assume dataclass for generated models
    return dataclasses.asdict(value)


from typing import Any, Dict, List, Optional, Union
from datetime import datetime

DashboardOrganizationsProjectsListQuery = Any


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapDashboardOrganizationsProjectsListQuery:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> DashboardOrganizationsProjectsListQuery:
    data

  @staticmethod
  def to_dict(
    value: Union[DashboardOrganizationsProjectsListQuery, Dict[str, Any], None],
  ) -> Optional[Dict[str, Any]]:
    if value is None:
      return None
    if isinstance(value, dict):
      return value
    # assume dataclass for generated models
    return dataclasses.asdict(value)
