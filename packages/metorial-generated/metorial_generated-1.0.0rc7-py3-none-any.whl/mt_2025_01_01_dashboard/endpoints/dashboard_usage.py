from typing import Optional, Dict, Any, List, Union
from metorial_util_endpoint import (
  BaseMetorialEndpoint,
  MetorialEndpointManager,
  MetorialRequest,
)
from ..resources import (
  mapDashboardUsageTimelineOutput,
  DashboardUsageTimelineOutput,
  mapDashboardUsageTimelineQuery,
  DashboardUsageTimelineQuery,
)


class MetorialDashboardUsageEndpoint(BaseMetorialEndpoint):
  """Get usage information"""

  def __init__(self, config: MetorialEndpointManager):
    super().__init__(config)

  def timeline(
    self, organizationId: str, query: DashboardUsageTimelineQuery = None
  ) -> DashboardUsageTimelineOutput:
    """
    Get organization
    Get the current organization information

    :param organizationId: str
    :param query: DashboardUsageTimelineQuery
    :return: DashboardUsageTimelineOutput
    """
    request = MetorialRequest(
      path=["dashboard", "organizations", organizationId, "usage", "timeline"],
      query=mapDashboardUsageTimelineQuery.to_dict(query)
      if query is not None
      else None,
    )
    return self._get(request).transform(mapDashboardUsageTimelineOutput.from_dict)
