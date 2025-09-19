"""
The Pipeline is the root container for all `gcip.core.job.Job`s and `gcip.core.sequence.Sequence`s

There are two options to create a pipeline and write its output.
First, you can use the pipelines context manager.
```python
with gcip.Pipeline as pipe:
    pipe.add_children(gcip.Job(name="my-job", script="date"))
```
The second method is just creating an object from `gcip.Pipeline`, but you are responsible
for calling the `Pipeline.write_yaml()` method.
```python
pipeline = gcip.Pipeline()
pipeline.add_children(gcip.Job(name"my-job", script="date"))
pipeline.write_yaml()  # Here you have to call `write_yaml()`
```
"""

from __future__ import annotations

from typing import Any, Union

from gcip.core.workflow import Workflow

from . import OrderedSetType
from .include import Include
from .job import Job
from .sequence import Sequence
from .service import Service

__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach", "Daniel von Eßen"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"


class JobNameConflictError(Exception):
    """This exception is used by the `Pipeline` when two rendered jobs have the same name.

    When two or more jobs have the same name within a pipeline means that one job will overwrite
    all those other jobs. This is absolutely nonsense and could (nearly?) never be the intention of
    the user, so he must be informed about that exception.

    Attributes:
        job (Job): A `gcip.core.job.Job` whose name equals to another job already added to the rendered pipeline.
    """

    def __init__(self, job: Job):
        super().__init__(
            (
                f"Two jobs have the same name '{job.name}' when rendering the pipeline."
                "\nPlease fix this by providing a different name and/or stage when adding those jobs to"
                " their sequences/pipeline."
            )
        )


class Pipeline(Sequence):
    def __init__(
        self,
        *,
        includes: Union[Include, list[Include]] | None = None,
        workflow: Workflow | None = None,
    ):
        """A Pipeline is the uppermost container of `gcip.core.job.Job`s and `gcip.core.sequence.Sequence`s.

        A Pipeline is a `gcip.core.sequence.Sequence` itself but has the additional method `Pipeline.write_yaml()`.
        This method is responsible for writing the whole Gitlab CI pipeline to a YAML file which could then feed
        the dynamic child pipeline.

        Args:
            includes (Union[Include, list[Include]] | None): You can add global `gcip.core.include.Include`s to the pipeline.
                [Gitlab CI Documentation](https://docs.gitlab.com/ee/ci/yaml/#include): _"Use include to include external YAML files
                in your CI/CD configuration."_ Defaults to None.
            workflow (Workflow | None): The workflow configuration for the pipeline. Defaults to None.

        Raises:
            ValueError: If `includes` is not of type `Include` or `list` of `Includes`
        """
        self._services: list[Service] = list()
        self._workflow = workflow

        if not includes:
            self._includes = []
        elif isinstance(includes, Include):
            self._includes = [includes]
        elif isinstance(includes, list):
            self._includes = includes
        else:
            raise ValueError(
                "Parameter include must of type gcip.Include or list[gcip.Include]"
            )
        super().__init__()

    @property
    def workflow(self) -> Workflow | None:
        return self._workflow

    def set_workflow(self, workflow: Workflow | None) -> None:
        """Set the workflow configuration for the pipeline.

        Args:
            workflow (Workflow | None): The workflow configuration to set.
        """
        self._workflow = workflow

    def add_services(self, *services: str | Service) -> Pipeline:
        """Add one or more `gcip.core.service.Service`s to the pipeline.

        Gitlab CI Documentation: _"The services keyword defines a Docker image that runs during a job linked to the Docker image
        that the image keyword defines."_

        Args:
            services (Union[str, Service]): Simply use strings to name the services to link to the pipeline.
                Use objects of the `gcip.core.service.Service` class for more complex service configurations.

        Returns:
            `Pipeline`: The modified `Pipeline` object.
        """
        for service in services:
            if isinstance(service, str):
                service = Service(service)
            self._services.append(service)
        return self

    def add_include(self, include: Include) -> Pipeline:
        """Let you add global `gcip.core.include.Include`s to the pipeline.
        [Gitlab CI Documentation](https://docs.gitlab.com/ee/ci/yaml/#include): _"Use include to include external YAML files
        in your CI/CD configuration."_

        Returns:
            `Pipeline`: The modified `Pipeline` object.
        """
        self._includes.append(include)
        return self

    def add_children(
        self,
        *jobs_or_sequences: Job | Sequence,
        stage: str | None = None,
        name: str | None = None,
    ) -> Pipeline:
        """
        Just calls `super().add_children()` but returns self as type `Pipeline`.

        See `gcip.core.sequence.Sequence.add_children()`
        """
        super().add_children(*jobs_or_sequences, stage=stage, name=name)
        return self

    def render(self) -> dict[str, Any]:
        """Return a representation of this Pipeline object as dictionary with static values.

        The rendered representation is used by the gcip to dump it
        in YAML format as part of the .gitlab-ci.yml pipeline.

        Return:
            dict[str, Any]: A dictionary prepresenting the pipeline object in Gitlab CI.
        """
        stages: OrderedSetType = {}
        pipeline: dict[str, Any] = {}
        job_copies = self.populated_jobs

        for job in job_copies:
            # use the keys of dictionary as ordered set
            stages[job.stage] = None

        if self._includes:
            pipeline["include"] = [include.render() for include in self._includes]

        if self._workflow is not None:
            pipeline["workflow"] = self._workflow.render()

        if self._services:
            pipeline["services"] = [service.render() for service in self._services]

        pipeline["stages"] = list(stages.keys())
        for job in job_copies:
            if job.name in pipeline:
                raise JobNameConflictError(job)

            pipeline[job.name] = job.render()
        return pipeline

    def write_yaml(self, filename: str = "generated-config.yml") -> None:
        """
        Create the Gitlab CI YAML file from this pipeline object.

        Use that YAML file to trigger a child pipeline.

        Args:
            filename (str, optional): The file name of the created yaml file. Defaults to "generated-config.yml".
        """
        import yaml

        with open(filename, "w") as generated_config:
            generated_config.write(
                yaml.dump(self.render(), default_flow_style=False, sort_keys=False)
            )

    def __enter__(self) -> Pipeline:
        return self

    def __exit__(
        self,
        exc_type: Any | None,
        exc_value: Any | None,
        exc_traceback: Any | None,
    ) -> None:
        self.write_yaml()
