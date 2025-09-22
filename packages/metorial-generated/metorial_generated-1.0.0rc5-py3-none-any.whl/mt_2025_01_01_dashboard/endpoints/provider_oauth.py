from metorial_util_endpoint import (
  BaseMetorialEndpoint,
  MetorialEndpointManager,
  MetorialRequest,
)
from ..resources import (
  mapProviderOauthDiscoverOutput,
  ProviderOauthDiscoverOutput,
  mapProviderOauthDiscoverBody,
  ProviderOauthDiscoverBody,
)


class MetorialProviderOauthEndpoint(BaseMetorialEndpoint):
  """Get OAuth connection template information"""

  def __init__(self, config: MetorialEndpointManager):
    super().__init__(config)

  def discover(self, organizationId: str, body: ProviderOauthDiscoverBody):
    """
    Discover OAuth Configuration
    Discover OAuth configuration from a discovery URL

    :param organizationId: str
    :param body: ProviderOauthDiscoverBody
    :return: ProviderOauthDiscoverOutput
    """
    request = MetorialRequest(
      path=[
        "dashboard",
        "organizations",
        organizationId,
        "provider-oauth-discovery",
      ],
      body=mapProviderOauthDiscoverBody.to_dict(body),
    )
    return self._post(request).transform(mapProviderOauthDiscoverOutput.from_dict)
