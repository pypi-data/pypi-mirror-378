from typing import Optional, Dict, Any, List, Union
from metorial_util_endpoint import (
  BaseMetorialEndpoint,
  MetorialEndpointManager,
  MetorialRequest,
)
from ..resources import (
  mapDashboardInstanceServerRunsListOutput,
  DashboardInstanceServerRunsListOutput,
  mapDashboardInstanceServerRunsListQuery,
  DashboardInstanceServerRunsListQuery,
  mapDashboardInstanceServerRunsGetOutput,
  DashboardInstanceServerRunsGetOutput,
)


class MetorialDashboardInstanceServerRunsEndpoint(BaseMetorialEndpoint):
  """Each time an MCP server is executed by the Metorial platform, a server run is created. This allows you to track the execution of MCP servers, including their status and associated sessions. Metorial may create multiple server runs for a single session or session connection."""

  def __init__(self, config: MetorialEndpointManager):
    super().__init__(config)

  def list(
    self, instanceId: str, query: DashboardInstanceServerRunsListQuery = None
  ) -> DashboardInstanceServerRunsListOutput:
    """
    List server runs
    List all server runs

    :param instanceId: str
    :param query: DashboardInstanceServerRunsListQuery
    :return: DashboardInstanceServerRunsListOutput
    """
    request = MetorialRequest(
      path=["dashboard", "instances", instanceId, "server-runs"],
      query=mapDashboardInstanceServerRunsListQuery.to_dict(query)
      if query is not None
      else None,
    )
    return self._get(request).transform(
      mapDashboardInstanceServerRunsListOutput.from_dict
    )

  def get(
    self, instanceId: str, serverRunId: str
  ) -> DashboardInstanceServerRunsGetOutput:
    """
    Get server run
    Get the information of a specific server run

    :param instanceId: str
    :param serverRunId: str
    :return: DashboardInstanceServerRunsGetOutput
    """
    request = MetorialRequest(
      path=["dashboard", "instances", instanceId, "server-runs", serverRunId]
    )
    return self._get(request).transform(
      mapDashboardInstanceServerRunsGetOutput.from_dict
    )
