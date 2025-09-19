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

import asyncio
import logging
import os
import subprocess
import sys
from collections import deque
from pathlib import Path

from acryl.executor.common.config import ConfigModel
from acryl.executor.context.execution_context import ExecutionContext
from acryl.executor.context.executor_context import ExecutorContext
from acryl.executor.execution.runner import (
    LogHolder,
    SubprocessRunner,
    VenvConfig,
    setup_venv,
)
from acryl.executor.execution.sub_process_task_common import (
    SubProcessRecipeTaskArgs,
    SubProcessTaskUtil,
)
from acryl.executor.execution.task import Task, TaskError

logger = logging.getLogger(__name__)


class SubProcessTestConnectionTaskConfig(ConfigModel):
    tmp_dir: str = "/tmp/datahub/ingest"


class SubProcessTestConnectionTaskArgs(SubProcessRecipeTaskArgs):
    pass


class SubProcessTestConnectionTask(Task):
    config: SubProcessTestConnectionTaskConfig
    tmp_dir: str  # Location where tmp files will be written (recipes)
    ctx: ExecutorContext

    @classmethod
    def create(cls, config: dict, ctx: ExecutorContext) -> "Task":
        config_parsed = SubProcessTestConnectionTaskConfig.parse_obj(config)
        return cls(config_parsed, ctx)

    def __init__(
        self, config: SubProcessTestConnectionTaskConfig, ctx: ExecutorContext
    ):
        self.config = config
        self.tmp_dir = config.tmp_dir
        self.ctx = ctx

    async def execute(self, args: dict, ctx: ExecutionContext) -> None:
        exec_id = ctx.exec_id  # The unique execution id.

        exec_out_dir = f"{self.tmp_dir}/{exec_id}"

        # 0. Validate arguments
        validated_args = SubProcessTestConnectionTaskArgs.parse_obj(args)

        # 1. Resolve the recipe (combine it with others)
        recipe: dict = SubProcessTaskUtil._resolve_recipe(
            validated_args.recipe, execution_ctx=ctx, executor_ctx=self.ctx
        )
        plugin: str = SubProcessTaskUtil._get_plugin_from_recipe(recipe)

        # 2. Write recipe file to local FS (requires write permissions to /tmp directory)
        recipe_file_path = SubProcessTaskUtil._write_recipe_to_file(
            exec_out_dir, recipe
        )

        # Prepare or resolve venv in Python (minimal change)
        venv_config = VenvConfig(
            version=validated_args.version,
            main_plugin=plugin,
            extra_pip_requirements=validated_args.extra_pip_requirements,
            extra_pip_plugins=validated_args.extra_pip_plugins,
            extra_env_vars=validated_args.extra_env_vars,
        )
        venv_setup_logs = LogHolder()
        venv_runner = SubprocessRunner(logs=venv_setup_logs)
        try:
            venv_ref = await setup_venv(
                venv_config=venv_config,
                runner=venv_runner,
                tmp_dir=Path(exec_out_dir),
            )
        except Exception as e:
            raise TaskError(f"Failed to set up virtual environment: {e}") from e

        # 3. Spin off subprocess to run the test-connection script with venv path
        command_script: str = "run_test_connection.sh"
        report_out_file: str = f"{exec_out_dir}/connection_report.json"
        stdout_lines: deque = deque(maxlen=SubProcessTaskUtil.MAX_LOG_LINES)

        ingest_process = subprocess.Popen(
            [
                command_script,
                str(venv_ref.venv_loc),
                recipe_file_path,
                report_out_file,
            ],
            env={
                **validated_args.get_combined_env_vars(),
                **venv_ref.extra_envs(),
                "VENV_PATH": str(venv_ref.venv_loc),
            },
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        try:
            while ingest_process.poll() is None:
                assert ingest_process.stdout
                line = ingest_process.stdout.readline()

                sys.stdout.write(line)
                stdout_lines.append(line)
                await asyncio.sleep(0)

            return_code = ingest_process.poll()

        except asyncio.CancelledError:
            # Terminate the running child process
            ingest_process.terminate()
            raise

        finally:
            if os.path.exists(report_out_file):
                with open(report_out_file) as structured_report_fp:
                    ctx.get_report().set_structured_report(structured_report_fp.read())

            ctx.get_report().set_logs(
                SubProcessTaskUtil._format_log_lines(stdout_lines)
            )

            # Cleanup by removing the exec out directory
            SubProcessTaskUtil._remove_directory(exec_out_dir)

        if return_code != 0:
            # Failed
            ctx.get_report().report_info("Failed to execute 'datahub test connection'")
            raise TaskError("Failed to execute 'datahub test connection'")

        # Report Successful execution
        ctx.get_report().report_info("Successfully executed 'datahub test connection'")

    def close(self) -> None:
        pass
