from metorial_util_endpoint import (
  BaseMetorialEndpoint,
  MetorialEndpointManager,
  MetorialRequest,
)
from ..resources import (
  mapDashboardInstanceServersVersionsListOutput,
  DashboardInstanceServersVersionsListOutput,
  mapDashboardInstanceServersVersionsListQuery,
  DashboardInstanceServersVersionsListQuery,
  mapDashboardInstanceServersVersionsGetOutput,
  DashboardInstanceServersVersionsGetOutput,
)


class MetorialDashboardInstanceServersVersionsEndpoint(BaseMetorialEndpoint):
  """Servers in Metorial are version controlled. Metorial automatically updates servers to the latest version when available. These endpoints help you keep track of server versions in the Metorial catalog."""

  def __init__(self, config: MetorialEndpointManager):
    super().__init__(config)

  def list(
    self,
    instanceId: str,
    serverId: str,
    query: DashboardInstanceServersVersionsListQuery = None,
  ) -> DashboardInstanceServersVersionsListOutput:
    """
    List server versions
    Retrieve all versions for a given server

    :param instanceId: str
    :param serverId: str
    :param query: DashboardInstanceServersVersionsListQuery
    :return: DashboardInstanceServersVersionsListOutput
    """
    request = MetorialRequest(
      path=["dashboard", "instances", instanceId, "servers", serverId, "versions"],
      query=mapDashboardInstanceServersVersionsListQuery.to_dict(query)
      if query is not None
      else None,
    )
    return self._get(request).transform(
      mapDashboardInstanceServersVersionsListOutput.from_dict
    )

  def get(
    self, instanceId: str, serverId: str, serverVersionId: str
  ) -> DashboardInstanceServersVersionsGetOutput:
    """
    Get server version
    Retrieve details for a specific server version

    :param instanceId: str
    :param serverId: str
    :param serverVersionId: str
    :return: DashboardInstanceServersVersionsGetOutput
    """
    request = MetorialRequest(
      path=[
        "dashboard",
        "instances",
        instanceId,
        "servers",
        serverId,
        "versions",
        serverVersionId,
      ]
    )
    return self._get(request).transform(
      mapDashboardInstanceServersVersionsGetOutput.from_dict
    )
