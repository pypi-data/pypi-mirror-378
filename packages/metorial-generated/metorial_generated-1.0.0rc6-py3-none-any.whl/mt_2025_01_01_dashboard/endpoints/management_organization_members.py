from metorial_util_endpoint import (
  BaseMetorialEndpoint,
  MetorialEndpointManager,
  MetorialRequest,
)
from ..resources import (
  mapDashboardOrganizationsMembersListOutput,
  DashboardOrganizationsMembersListOutput,
  mapDashboardOrganizationsMembersListQuery,
  DashboardOrganizationsMembersListQuery,
  mapDashboardOrganizationsMembersGetOutput,
  DashboardOrganizationsMembersGetOutput,
  mapDashboardOrganizationsMembersDeleteOutput,
  DashboardOrganizationsMembersDeleteOutput,
  mapDashboardOrganizationsMembersUpdateOutput,
  DashboardOrganizationsMembersUpdateOutput,
  mapDashboardOrganizationsMembersUpdateBody,
  DashboardOrganizationsMembersUpdateBody,
)


class MetorialManagementOrganizationMembersEndpoint(BaseMetorialEndpoint):
  """Read and write organization member information"""

  def __init__(self, config: MetorialEndpointManager):
    super().__init__(config)

  def list(
    self, query: DashboardOrganizationsMembersListQuery = None
  ) -> DashboardOrganizationsMembersListOutput:
    """
    List organization members
    List all organization members

    :param query: DashboardOrganizationsMembersListQuery
    :return: DashboardOrganizationsMembersListOutput
    """
    request = MetorialRequest(
      path=["organization", "members"],
      query=mapDashboardOrganizationsMembersListQuery.to_dict(query)
      if query is not None
      else None,
    )
    return self._get(request).transform(
      mapDashboardOrganizationsMembersListOutput.from_dict
    )

  def get(self, memberId: str) -> DashboardOrganizationsMembersGetOutput:
    """
    Get organization member
    Get the information of a specific organization member

    :param memberId: str
    :return: DashboardOrganizationsMembersGetOutput
    """
    request = MetorialRequest(path=["organization", "members", memberId])
    return self._get(request).transform(
      mapDashboardOrganizationsMembersGetOutput.from_dict
    )

  def delete(self, memberId: str) -> DashboardOrganizationsMembersDeleteOutput:
    """
    Delete organization member
    Remove an organization member

    :param memberId: str
    :return: DashboardOrganizationsMembersDeleteOutput
    """
    request = MetorialRequest(path=["organization", "members", memberId])
    return self._delete(request).transform(
      mapDashboardOrganizationsMembersDeleteOutput.from_dict
    )

  def update(
    self, memberId: str, body: DashboardOrganizationsMembersUpdateBody
  ) -> DashboardOrganizationsMembersUpdateOutput:
    """
    Update organization member
    Update the role of an organization member

    :param memberId: str
    :param body: DashboardOrganizationsMembersUpdateBody
    :return: DashboardOrganizationsMembersUpdateOutput
    """
    request = MetorialRequest(
      path=["organization", "members", memberId],
      body=mapDashboardOrganizationsMembersUpdateBody.to_dict(body),
    )
    return self._post(request).transform(
      mapDashboardOrganizationsMembersUpdateOutput.from_dict
    )
