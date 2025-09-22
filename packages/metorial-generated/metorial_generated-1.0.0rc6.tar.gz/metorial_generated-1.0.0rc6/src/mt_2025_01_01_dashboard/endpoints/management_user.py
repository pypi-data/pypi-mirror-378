from metorial_util_endpoint import (
  BaseMetorialEndpoint,
  MetorialEndpointManager,
  MetorialRequest,
)
from ..resources import (
  mapManagementUserGetOutput,
  ManagementUserGetOutput,
  mapManagementUserUpdateOutput,
  ManagementUserUpdateOutput,
  mapManagementUserUpdateBody,
  ManagementUserUpdateBody,
  mapManagementUserDeleteOutput,
  ManagementUserDeleteOutput,
  mapManagementUserDeleteBody,
  ManagementUserDeleteBody,
)


class MetorialManagementUserEndpoint(BaseMetorialEndpoint):
  """Read and write user information"""

  def __init__(self, config: MetorialEndpointManager):
    super().__init__(config)

  def get(self) -> ManagementUserGetOutput:
    """
    Get user
    Get the current user information


    :return: ManagementUserGetOutput
    """
    request = MetorialRequest(path=["user"])
    return self._get(request).transform(mapManagementUserGetOutput.from_dict)

  def update(self, body: ManagementUserUpdateBody) -> ManagementUserUpdateOutput:
    """
    Update user
    Update the current user information

    :param body: ManagementUserUpdateBody
    :return: ManagementUserUpdateOutput
    """
    request = MetorialRequest(
      path=["user"],
      body=mapManagementUserUpdateBody.to_dict(body),
    )
    return self._post(request).transform(mapManagementUserUpdateOutput.from_dict)

  def delete(self, body: ManagementUserDeleteBody) -> ManagementUserDeleteOutput:
    """
    Update user
    Update the current user information

    :param body: ManagementUserDeleteBody
    :return: ManagementUserDeleteOutput
    """
    request = MetorialRequest(
      path=["user"],
      body=mapManagementUserDeleteBody.to_dict(body),
    )
    return self._post(request).transform(mapManagementUserDeleteOutput.from_dict)
