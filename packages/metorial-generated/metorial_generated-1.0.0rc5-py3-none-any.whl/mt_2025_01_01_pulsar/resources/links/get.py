from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from datetime import datetime


@dataclass
class LinksGetOutput:
  object: str
  id: str
  file_id: str
  url: str
  created_at: datetime
  expires_at: Optional[datetime] = None


from typing import Any, Dict, Optional, Union
from datetime import datetime
import dataclasses


class mapLinksGetOutput:
  @staticmethod
  def from_dict(data: Dict[str, Any]) -> LinksGetOutput:
    return LinksGetOutput(
      object=data.get("object"),
      id=data.get("id"),
      file_id=data.get("file_id"),
      url=data.get("url"),
      created_at=data.get("created_at")
      and datetime.fromisoformat(data.get("created_at")),
      expires_at=data.get("expires_at")
      and datetime.fromisoformat(data.get("expires_at")),
    )

  @staticmethod
  def to_dict(
    value: Union[LinksGetOutput, Dict[str, Any], None],
  ) -> Optional[Dict[str, Any]]:
    if value is None:
      return None
    if isinstance(value, dict):
      return value
    # assume dataclass for generated models
    return dataclasses.asdict(value)
