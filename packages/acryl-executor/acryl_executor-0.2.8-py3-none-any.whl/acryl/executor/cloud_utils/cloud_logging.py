# Copyright 2021 Acryl Data, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import Any, Optional

from datahub.ingestion.graph.client import DataHubGraph

logger = logging.getLogger(__name__)

CLOUD_LOGGING_CONFIGS_QUERY = """query cloudLoggingConfigsResolver {
  cloudLoggingConfigsResolver {
    remote_executor_logging_enabled
  }
}"""


class CloudLoggingConfig:
    def __init__(self, graph: DataHubGraph):
        self.graph = graph

    def _parse_cloud_logging_configs_response(
        self, response_data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        """
        Parse GraphQL response to extract executor credentials.

        Args:
            response_data: Raw GraphQL response data
            executor_pool_id: The executor pool ID to find credentials for

        Returns:
            Dictionary containing AWS credentials if found, None otherwise
        """

        cloud_logging_config = response_data.get("cloudLoggingConfigsResolver")

        if cloud_logging_config:
            logger.debug("Found cloud logging configuration")
            return {
                "s3_bucket": cloud_logging_config.get("s3_bucket"),
                "s3_prefix": cloud_logging_config.get("s3_prefix"),
                "remote_executor_logging_enabled": cloud_logging_config.get(
                    "remote_executor_logging_enabled"
                ),
            }

        logger.warning("No cloud logging configuration found")
        return None

    def get_cloud_logging_config(self) -> Optional[dict[str, Any]]:
        """
        Fetch cloud logging configuration from DataHub GraphQL API.
        Returns:
            Dictionary containing cloud logging configuration if found, None otherwise
        """
        res_data = self.graph.execute_graphql(CLOUD_LOGGING_CONFIGS_QUERY)
        if res_data is None:
            logger.error("Failed to fetch cloud logging configuration")
            return None

        return self._parse_cloud_logging_configs_response(res_data)
