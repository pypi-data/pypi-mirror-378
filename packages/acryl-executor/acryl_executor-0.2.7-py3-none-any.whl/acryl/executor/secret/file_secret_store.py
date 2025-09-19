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
import os
from typing import Union

from pydantic import BaseModel

from acryl.executor.secret.secret_store import SecretStore

logger = logging.getLogger(__name__)


class FileSecretStoreConfig(BaseModel):
    basedir: str = "/mnt/secrets"
    max_length: int = 1024768


# Simple SecretStore implementation that fetches Secret values from the local files.
class FileSecretStore(SecretStore):
    def __init__(self, config):
        self.config = config

    def get_secret_values(self, secret_names: list[str]) -> dict[str, Union[str, None]]:
        values = {}
        for secret_name in secret_names:
            values[secret_name] = self.get_secret_value(secret_name)
        return values

    def get_secret_value(self, secret_name: str) -> Union[str, None]:
        secret_path = os.path.join(self.config.basedir, secret_name)
        if os.path.exists(secret_path):
            with open(secret_path) as f:
                secret_value = f.read(self.config.max_length + 1)
                if len(secret_value) > self.config.max_length:
                    logger.warning(
                        f"Secret {secret_name} is longer than {self.config.max_length} and will be truncated."
                    )
                return secret_value[: self.config.max_length].rstrip()
        return None

    def get_id(self) -> str:
        return "file"

    def close(self) -> None:
        pass

    @classmethod
    def create(cls, config: dict) -> "FileSecretStore":
        parsed_config = FileSecretStoreConfig.parse_obj(config)
        return cls(parsed_config)
