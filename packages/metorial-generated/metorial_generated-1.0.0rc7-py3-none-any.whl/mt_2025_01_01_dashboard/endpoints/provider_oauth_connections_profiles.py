from typing import Optional, Dict, Any, List, Union
from metorial_util_endpoint import (
  BaseMetorialEndpoint,
  MetorialEndpointManager,
  MetorialRequest,
)
from ..resources import (
  mapDashboardInstanceProviderOauthConnectionsProfilesListOutput,
  DashboardInstanceProviderOauthConnectionsProfilesListOutput,
  mapDashboardInstanceProviderOauthConnectionsProfilesListQuery,
  DashboardInstanceProviderOauthConnectionsProfilesListQuery,
  mapDashboardInstanceProviderOauthConnectionsProfilesGetOutput,
  DashboardInstanceProviderOauthConnectionsProfilesGetOutput,
)


class MetorialProviderOauthConnectionsProfilesEndpoint(BaseMetorialEndpoint):
  """Manage provider OAuth connection profile information"""

  def __init__(self, config: MetorialEndpointManager):
    super().__init__(config)

  def list(
    self,
    connectionId: str,
    query: DashboardInstanceProviderOauthConnectionsProfilesListQuery = None,
  ) -> DashboardInstanceProviderOauthConnectionsProfilesListOutput:
    """
    List provider OAuth connection profiles
    List provider OAuth connection profiles for a specific connection

    :param connectionId: str
    :param query: DashboardInstanceProviderOauthConnectionsProfilesListQuery
    :return: DashboardInstanceProviderOauthConnectionsProfilesListOutput
    """
    request = MetorialRequest(
      path=["provider-oauth", "connections", connectionId, "profiles"],
      query=mapDashboardInstanceProviderOauthConnectionsProfilesListQuery.to_dict(query)
      if query is not None
      else None,
    )
    return self._get(request).transform(
      mapDashboardInstanceProviderOauthConnectionsProfilesListOutput.from_dict
    )

  def get(
    self, connectionId: str, profileId: str
  ) -> DashboardInstanceProviderOauthConnectionsProfilesGetOutput:
    """
    Get provider OAuth connection profile
    Get the information of a specific provider OAuth connection profile

    :param connectionId: str
    :param profileId: str
    :return: DashboardInstanceProviderOauthConnectionsProfilesGetOutput
    """
    request = MetorialRequest(
      path=["provider-oauth", "connections", connectionId, "profiles", profileId]
    )
    return self._get(request).transform(
      mapDashboardInstanceProviderOauthConnectionsProfilesGetOutput.from_dict
    )
