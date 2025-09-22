from metorial_util_endpoint import (
  BaseMetorialEndpoint,
  MetorialEndpointManager,
  MetorialRequest,
)
from ..resources import (
  mapDashboardOrganizationsInstancesListOutput,
  DashboardOrganizationsInstancesListOutput,
  mapDashboardOrganizationsInstancesListQuery,
  DashboardOrganizationsInstancesListQuery,
  mapDashboardOrganizationsInstancesGetOutput,
  DashboardOrganizationsInstancesGetOutput,
  mapDashboardOrganizationsInstancesCreateOutput,
  DashboardOrganizationsInstancesCreateOutput,
  mapDashboardOrganizationsInstancesCreateBody,
  DashboardOrganizationsInstancesCreateBody,
  mapDashboardOrganizationsInstancesDeleteOutput,
  DashboardOrganizationsInstancesDeleteOutput,
  mapDashboardOrganizationsInstancesUpdateOutput,
  DashboardOrganizationsInstancesUpdateOutput,
  mapDashboardOrganizationsInstancesUpdateBody,
  DashboardOrganizationsInstancesUpdateBody,
)


class MetorialDashboardOrganizationsInstancesEndpoint(BaseMetorialEndpoint):
  """Read and write instance information"""

  def __init__(self, config: MetorialEndpointManager):
    super().__init__(config)

  def list(
    self, organizationId: str, query: DashboardOrganizationsInstancesListQuery = None
  ) -> DashboardOrganizationsInstancesListOutput:
    """
    List organization instances
    List all organization instances

    :param organizationId: str
    :param query: DashboardOrganizationsInstancesListQuery
    :return: DashboardOrganizationsInstancesListOutput
    """
    request = MetorialRequest(
      path=["dashboard", "organizations", organizationId, "instances"],
      query=mapDashboardOrganizationsInstancesListQuery.to_dict(query)
      if query is not None
      else None,
    )
    return self._get(request).transform(
      mapDashboardOrganizationsInstancesListOutput.from_dict
    )

  def get(
    self, organizationId: str, instanceId: str
  ) -> DashboardOrganizationsInstancesGetOutput:
    """
    Get organization instance
    Get the information of a specific organization instance

    :param organizationId: str
    :param instanceId: str
    :return: DashboardOrganizationsInstancesGetOutput
    """
    request = MetorialRequest(
      path=["dashboard", "organizations", organizationId, "instances", instanceId]
    )
    return self._get(request).transform(
      mapDashboardOrganizationsInstancesGetOutput.from_dict
    )

  def create(
    self, organizationId: str, body: DashboardOrganizationsInstancesCreateBody
  ) -> DashboardOrganizationsInstancesCreateOutput:
    """
    Create organization instance
    Create a new organization instance

    :param organizationId: str
    :param body: DashboardOrganizationsInstancesCreateBody
    :return: DashboardOrganizationsInstancesCreateOutput
    """
    request = MetorialRequest(
      path=["dashboard", "organizations", organizationId, "instances"],
      body=mapDashboardOrganizationsInstancesCreateBody.to_dict(body),
    )
    return self._post(request).transform(
      mapDashboardOrganizationsInstancesCreateOutput.from_dict
    )

  def delete(
    self, organizationId: str, instanceId: str
  ) -> DashboardOrganizationsInstancesDeleteOutput:
    """
    Delete organization instance
    Remove an organization instance

    :param organizationId: str
    :param instanceId: str
    :return: DashboardOrganizationsInstancesDeleteOutput
    """
    request = MetorialRequest(
      path=["dashboard", "organizations", organizationId, "instances", instanceId]
    )
    return self._delete(request).transform(
      mapDashboardOrganizationsInstancesDeleteOutput.from_dict
    )

  def update(
    self,
    organizationId: str,
    instanceId: str,
    body: DashboardOrganizationsInstancesUpdateBody,
  ) -> DashboardOrganizationsInstancesUpdateOutput:
    """
    Update organization instance
    Update the role of an organization instance

    :param organizationId: str
    :param instanceId: str
    :param body: DashboardOrganizationsInstancesUpdateBody
    :return: DashboardOrganizationsInstancesUpdateOutput
    """
    request = MetorialRequest(
      path=["dashboard", "organizations", organizationId, "instances", instanceId],
      body=mapDashboardOrganizationsInstancesUpdateBody.to_dict(body),
    )
    return self._post(request).transform(
      mapDashboardOrganizationsInstancesUpdateOutput.from_dict
    )
