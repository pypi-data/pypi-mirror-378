"""This module represents the Gitlab CI [Job](https://docs.gitlab.com/ee/ci/yaml/#job-keywords)

It contains the general `Job` class as well as a special `TriggerJob` class. The latter one is a subclass
of `Job` but has on the one hand reduced capabilities, on the other hand it has the additional functionality
to trigger other pipelines.

Here is a simple example how you define and use a `Job`:

```python
from gcip import Pipeline, Job

pipeline = Pipeline()
job = Job(stage="build", script="build my artefact")
pipeline.add_children(job, name="artifact")
pipeline.write_yaml()

# stages:
#   - build
# build-artifact:
#   stage: build
#   script: build my artifact
```

A `Job` has always a `script` and at least one of `stage` or `name`.
The `stage` will be used for the name of the stage of the job and the
job name itself, whereas `name` is only used for the job`s name. When adding
a job to a `gcip.core.pipeline.Pipeline` or a `gcip.core.sequence.Sequence`
you can and should define a `name` or `stage` too. This is how you
distinguish between two jobs of the same kind added to a pipeline:

```python
def create_build_job(artifact: str, job_name: str = "artifact", job_stage: str = "build") -> Job:
    return Job(name=job_name, stage=job_stage, script=f"build my {artifact}")

pipeline.add_children(create_build_job("foo"), name="bar")
pipeline.add_children(create_build_job("john"), name="deere")

# stages:
#   - build
# build-artifact-bar:
#   stage: build
#   script: build my foo
# build-artifact-deere:
#     stage: build
#     script: build my john
```

Again `name` or `stage` decide whether to add the string to the
stage of a job or not:

```python
def create_build_job(job_name: str = "artifact", job_stage: str = "build", artifact: str) -> Job:
    return Job(name=job_name, stage=job_stage, script=f"build my {artifact}")

pipeline.add_children(create_build_job("foo"), stage="bar")
pipeline.add_children(create_build_job("john"), stage="deere")

# stages:
#   - build_bar
#   - build_deere
# build-bar-artifact:
#   stage: build_bar
#   script: build my foo
# build-deere-artifact:
#     stage: build_deere
#     script: build my john
```

This also decides whether to run the jobs in parralel or sequential. When using
`stage` and adding the string also to the jobs stage the stages for both jobs
differ. When using `name` only the name of the jobs differ but the name of the stage
remains the same.

An `Job` object has a lot of methods for further configuration of typical Gitlab CI
[Job keywords]/https://docs.gitlab.com/ee/ci/yaml/#job-keywords), like
configuring tags, rules, variables and so on. Methods with names staring with..

* **`set_*`** will initally set or overwrite any previous setting, like `set_image()`
* **`add_*`** will append a value to previous ones, like `add_tags()`
* **`append_*`** will do the same as `add_*`, but for values where order matters. So it
   explicitly adds a value to the end of a list of previous values, like `append_rules()`
* **`prepend_*`** is the counterpart to `append_*` and will add a value to the beginning
  of a list of previous values, like `prepend_rules()`
"""

from __future__ import annotations

import copy
import re
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    AnyStr,
)

from . import OrderedSetType
from .artifacts import Artifacts
from .cache import Cache
from .environment import Environment
from .image import Image
from .include import Include
from .need import Need
from .retry import Retry
from .rule import Rule
from .when import WhenStatement

if TYPE_CHECKING:
    from .sequence import Sequence

__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach", "Daniel von Eßen"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"


class ScriptArgumentNotAllowedError(Exception):
    """
    This Exception could be raised if the argument 'scripts' is in given `kwargs`.

    This exception is mainly for subclasses of `Job` which define their custom `script` but
    besides pass arbitrary keyword arguments to the super init method. Then the user should
    not be allowed to set the `script` argument.

    ```
    class MyJob(Job):
        def __init__(self, *, myarg, **kwargs):
            if "script" in kwargs:
                        raise ScriptArgumentNotAllowedError()
            super().__init__(script="foobar", name=f"foo_{myarg}", **kwargs)
    ```
    """

    def __init__(self) -> None:
        super().__init__(
            (
                "The argument 'script' is not supported by this subclass of 'Job', "
                "because the class provides it custom script. However you can "
                "prepend/append scripts as usual."
            )
        )


class JobFilter:
    def __init__(
        self,
        *,
        script: str | list[str] | None = None,
        name: str | None = None,
        stage: str | None = None,
        image: Image | str | None = None,
        allow_failure: bool | str | int | list[int] | None = None,
        variables: dict[str, str] | None = None,
        tags: str | list[str] | None = None,
        rules: Rule | list[Rule] | None = None,
        dependencies: str | Job | Sequence | list[str | Job | Sequence] | None = None,
        needs: str
        | Need
        | Job
        | Sequence
        | list[str | Need | Job | Sequence]
        | None = None,
        artifacts: Artifacts | list[str] | None = None,
        cache: Cache | list[str] | None = None,
        when: WhenStatement | None = None,
        timeout: str | None = None,
        resource_group: str | None = None,
        environment: Environment | str | None = None,
        retry: Retry | int | None = None,
    ) -> None:
        """
        This class is used to check if Jobs matches certain criterias.

        When created, you could use the `equals` method, to check if `Job`s match the `JobFilter` criterias:

        ```
        filter = JobFilter(script="foo.*")
        job = Job(stage="test", script="foobar")
        assert filter.match(job)
        ```

        Check the arguments for all optional criterias:

        Args:
            script (str |  list[str] | None, optional): Could be a single or a list of regular expressions. A job matches if for every regex provided
                there is a matching script in the job. Defaults to None.
            name (str | None, optional): A job matches if the regex provided matches the jobs name. ATTENTION: A jobs name is always composed of the name
                and stage parameter given to its init-Method, separated by a dash. Also all underscores are replaced by a dash. Defaults to None.
            stage (str | None, optional): A job matches if the regex provided matches the jobs stage. ATTENTION: A jobs stage is always the stage given to
                the jobs init-Method with all dashres replaces by underscores. Defaults to None.
            image (Image |  str | None, optional): A job matches depending on the type of the value provided. If the parameter a regex (str), a job
                matches if the regex matches to the jobs image name. If the parameter is an `Image`, a job matches if the attributes of the `Image` provided
                equals to the `Image` attributes of the job. Defaults to None.
            allow_failure (bool | None): A job matches if `allow_failure` matches to the value of this filter. The filter allows two special string
                values 'untouched' - which filters out jobs whose 'allow_failure' value has not been set before - as well as 'none' - which filters out
                jobs whose 'allow_failure' value has explicitly been set to None by the user.
            variables (dict[str, str] | None, optional): The keys of the dictionary provided are variable names, the values are regular expressions.
                A job matches if it contains all variable names provided and their values matches the appropriate regular expressions. Defaults to None.
            tags (str |  list[str] | None): Could be a single or a list of regular expressions. A job matches if for every regex provided there is a
                matching tag in the job. Defaults to None.
            rules (Rule |  list[Rule] | None, optional): A job matches if he contains all rules provided. The rules are compared by their equality
                of their attributes. Defaults to None.
            dependencies (str |  Job |  Sequence |  list[str |  Job |  Sequence] | None): A Job matches depending on the type of the value provided.
                If the value is a (list of) `Job`s or `Sequence`s, a job matches if that jobs `dependencies` contains all the Jobs and Sequences provided.
                Jobs and Sequences are compared by their identity. If the value is a list of strings representing regular expressions, a job matches if for
                every regex provided there is a need whith a job name matching to this regex. If the dependency is a sequence, at least one job from the sequence
                must match. Defaults to None.
            needs (list[str |  Need |  Job |  Sequence] | None, optional): A job matches depending on the type of the value provided. If the value is a
                 (list of) `Job`s, `Sequence`s or `Need`s, a job matches if that jobs `needs` contains all the Jobs, Sequences and Needs provided. Jobs and
                 Sequences are compared by their identity. Needs are compared by their equality of their attributes. If the value is a list of strings
                 representing regular expressions, a job matches if for every regex provided there is a need whith a job name matching to this regex. If the
                 Need is a sequence, at least one job from the last stage must match. Defaults to None.
            artifacts (Artifacts |  list[str] | None, optional): A job matches depending on the type of the value provided. If the value is an
                `Artifacts`, a job matches if its artifacts properties equals to the provided artifacts properties. If the value is a list of strings as
                regular expressions, a job matches if for every regex provided there is at least one matching path in the jobs artifacts object.
                Defaults to None.
            cache (Cache |  list[str] | None, optional): A job matches depending on the type of the value provided. If the value is a `Cache`,
                a job matches if its `Cache` properties equals to the provided cache properties. If the value is a list of strings as regular expressions,
                a job matches if for every regex provided there is at least one matching path in the jobs artifacts object.
                ATTENTION: A caches internal path always starts with './'.  Defaults to None.
            when (WhenStatement | None, optional): A job matches, if the value of the WhenStatement enum is equal to the one of the filter.
            timeout (str | None): A job matches if the value is equal to the one of the filter.
            resource_group (str | None): A job matches if the value is equal to the one of the filter.
            environment (Environment |  str | None, optional): A job matches depending on the type of the value provided. If the parameter a regex (str), a job
                matches if the regex matches to the jobs environment name. If the parameter is an `Environment`, a job matches if the attributes of the `Environment` provided
                equals to the `Environment` attributes of the job. Defaults to None.
            retry (Retry, int | None): A job matches if either the given Retry objects match or the Jobs retry max count matches to the given number.
        """
        self._script: list[str] | None
        if isinstance(script, str):
            self._script = [script]
        else:
            self._script = script

        self._name = name
        self._stage = stage
        self._image = image
        self._allow_failure = allow_failure
        self._variables = variables

        self._tags: list[str] | None
        if isinstance(tags, str):
            self._tags = [tags]
        else:
            self._tags = tags

        self._rules: list[Rule] | None
        if isinstance(rules, Rule):
            self._rules = [rules]
        else:
            self._rules = rules

        # late import to avoid circular dependencies
        from .sequence import Sequence

        self._dependencies: list[str | Job | Sequence] | None
        if (
            isinstance(dependencies, str)
            or isinstance(dependencies, Job)
            or isinstance(dependencies, Sequence)
        ):
            self._dependencies = [dependencies]
        else:
            self._dependencies = dependencies

        self._needs: list[str | Need | Job | Sequence] | None
        if (
            isinstance(needs, str)
            or isinstance(needs, Need)
            or isinstance(needs, Job)
            or isinstance(needs, Sequence)
        ):
            self._needs = [needs]
        else:
            self._needs = needs
        self._artifacts = artifacts
        self._cache = cache
        self._when = when
        self._timeout = timeout
        self._resource_group = resource_group
        self._environment = environment
        self._retry = retry

    # flake8: noqa: C901
    def match(self, job: Job) -> bool:
        if self._script:
            for script in self._script:
                match_in_this_iteration = False
                for job_script in job._scripts:
                    if re.match(script, job_script):
                        match_in_this_iteration = True
                        break
                if not match_in_this_iteration:
                    return False

        if self._name and not re.match(self._name, job._name):
            return False

        if self._stage and not re.match(self._stage, job._stage):
            return False

        if self._image:
            if not job._image:
                return False
            elif isinstance(self._image, Image) and not self._image._equals(job._image):
                return False
            elif isinstance(self._image, str) and not re.match(
                self._image, str(job._image.render()["name"])
            ):
                return False

        if self._allow_failure:
            if job._allow_failure is None:
                if self._allow_failure != "none":
                    return False
            elif self._allow_failure != job._allow_failure:
                return False

        if self._variables:
            for key in self._variables.keys():
                if key not in job._variables:
                    return False
                elif not re.match(self._variables[key], job._variables[key]):
                    return False

        if self._tags:
            for tag in self._tags:
                match_in_this_iteration = False
                for job_tag in job._tags.keys():
                    if re.match(tag, job_tag):
                        match_in_this_iteration = True
                        break
                if not match_in_this_iteration:
                    return False

        if self._rules:
            for self_rule in self._rules:
                match_in_this_iteration = False
                for job_rule in job._rules:
                    if self_rule._equals(job_rule):
                        match_in_this_iteration = True
                        break
                if not match_in_this_iteration:
                    return False

        if self._dependencies:
            if job._dependencies is None:
                return False
            else:
                # because the language checker does not recognise we have already checked, that
                # `job._dependencies` is not None, we need to create a new variable that we use in the
                # following code. The language checker accepts `job_dependencies` as not None
                job_dependencies = job._dependencies

            # late import to avoid circular dependencies
            from .sequence import Sequence

            for dependency in self._dependencies:
                if (
                    isinstance(dependency, Job) or isinstance(dependency, Sequence)
                ) and dependency not in job_dependencies:
                    return False

                match_in_this_iteration = False
                if isinstance(dependency, str):
                    for job_dependency in job_dependencies:
                        if isinstance(job_dependency, Job) and re.match(
                            dependency, job_dependency._name
                        ):
                            match_in_this_iteration = True
                            break
                        elif isinstance(job_dependency, Sequence):
                            for job in job_dependency.nested_jobs:
                                if re.match(dependency, job._name):
                                    match_in_this_iteration = True
                                    break
                            if match_in_this_iteration:
                                break
                    if not match_in_this_iteration:
                        return False

        if self._needs:
            if job._needs is None:
                return False
            else:
                # because the language checker does not recognise we have already checked, that
                # `job._needs` is not None, we need to create a new variable that we use in the
                # following code. The language checker accepts `job_needs` as not None
                job_needs = job._needs

            # late import to avoid circular dependencies
            from .sequence import Sequence

            for need in self._needs:
                if (
                    isinstance(need, Job) or isinstance(need, Sequence)
                ) and need not in job_needs:
                    return False

                match_in_this_iteration = False
                if isinstance(need, Need):
                    for job_need in job_needs:
                        if isinstance(job_need, Need) and need._equals(job_need):
                            match_in_this_iteration = True
                            break
                    if not match_in_this_iteration:
                        return False

                match_in_this_iteration = False
                if isinstance(need, str):
                    for job_need in job_needs:
                        if (
                            isinstance(job_need, Need)
                            and job_need._job
                            and re.match(need, job_need._job)
                        ):
                            match_in_this_iteration = True
                            break
                        elif isinstance(job_need, Job) and re.match(
                            need, job_need._name
                        ):
                            match_in_this_iteration = True
                            break
                        elif isinstance(job_need, Sequence):
                            for job in job_need.last_jobs_executed:
                                if re.match(need, job._name):
                                    match_in_this_iteration = True
                                    break
                            if match_in_this_iteration:
                                break
                    if not match_in_this_iteration:
                        return False

        if self._artifacts:
            if isinstance(self._artifacts, Artifacts):
                if not self._artifacts._equals(job._artifacts):
                    return False
            elif isinstance(self._artifacts, list):
                for artifact in self._artifacts:
                    match_in_this_iteration = False
                    for job_artifact_path in job.artifacts._paths:
                        if re.match(artifact, job_artifact_path):
                            match_in_this_iteration = True
                            break

                    if not match_in_this_iteration:
                        return False

        if self._cache:
            if not job._cache:
                return False
            if isinstance(self._cache, Cache):
                if not self._cache._equals(job._cache):
                    return False
            elif isinstance(self._cache, list):
                for regex in self._cache:
                    match_in_this_iteration = False
                    for path in job._cache._paths:
                        if re.match(regex, path):
                            match_in_this_iteration = True
                            break
                    if not match_in_this_iteration:
                        return False

        if self._when:
            if not job._when:
                return False
            if not self._when == job._when:
                return False

        if self._timeout:
            if not job._timeout:
                return False
            if self._timeout != job._timeout:
                return False

        if self._resource_group:
            if not job._resource_group:
                return False
            if self._resource_group != job._resource_group:
                return False

        if self._environment:
            if not job._environment:
                return False
            elif isinstance(
                self._environment, Environment
            ) and not self._environment._equals(job._environment):
                return False
            elif isinstance(self._environment, str) and not re.match(
                self._environment, str(job._environment.render()["name"])
            ):
                return False

        if self._retry:
            if not job._retry:
                return False
            elif isinstance(self._retry, Retry) and not self._retry._equals(job._retry):
                return False
            elif isinstance(self._retry, int) and self._retry != job._retry.max:
                return False

        return True


class Job:
    """This class represents the Gitlab CI [Job](https://docs.gitlab.com/ee/ci/yaml/#job-keywords)

    Attributes:
        script (AnyStr |  list[str]): The [script(s)](https://docs.gitlab.com/ee/ci/yaml/#script) to be executed.
        name (str | None): The name of the job. In opposite to `stage` only the name is set and not the stage of the job.
            If `name` is set, than the jobs stage has no value, which defaults to the 'test' stage.
            Either `name` or `stage` must be set. Defaults to `None`.
        stage (str | None): The name and stage of the job. In opposite to `name` also the jobs stage will be setup with this value.
            Either `name` or `stage` must be set. Defaults to `None`.
        allow_failure (bool]): The [allow_failure | None(https://docs.gitlab.com/ee/ci/yaml/#allow_failure) keyword of the Job.
            Defaults to `None` (unset).
    """

    def __init__(
        self,
        *,
        script: AnyStr | list[str],
        name: str | None = None,
        stage: str | None = None,
        image: Image | str | None = None,
        allow_failure: bool | str | int | list[int] | None = None,
        variables: dict[str, str] | None = None,
        tags: list[str] | None = None,
        rules: list[Rule] | None = None,
        dependencies: list[Job | Sequence] | None = None,
        needs: list[Need | Job | Sequence] | None = None,
        artifacts: Artifacts | None = None,
        cache: Cache | None = None,
        when: WhenStatement | None = None,
        environment: Environment | str | None = None,
        retry: Retry | int | None = None,
        timeout: str | None = None,
        resource_group: str | None = None,
    ) -> None:
        self._image: Image | None = None
        self._variables: dict[str, str] = {}
        self._tags: OrderedSetType = {}
        self._rules: list[Rule] = []
        self._dependencies: list[Job | Sequence] | None = None
        self._needs: list[Need | Job | Sequence] | None = None
        self._scripts: list[str]
        self._scripts_to_prepend: list[str] = []
        self._scripts_to_append: list[str] = []
        self._artifacts: Artifacts | None = artifacts
        self._cache: Cache | None = cache
        self._environment: Environment | None = None
        self._retry: Retry | None = None
        self._parents: list[Sequence] = list()
        self._original: Job | None
        self._when: WhenStatement | None = when
        self._timeout: str | None = timeout
        self._resource_group: str | None = resource_group

        if stage and name:
            self._name = f"{name}-{stage}"
            self._stage = stage
        elif stage:
            self._name = stage
            self._stage = stage
        elif name:
            self._name = name
            # default for unset stages is 'test' -> https://docs.gitlab.com/ee/ci/yaml/#stages
            self._stage = "test"
        else:
            raise ValueError(
                "At least one of the parameters `name` or `stage` have to be set."
            )

        self._name = self._name.replace("_", "-")
        self._stage = self._stage.replace("-", "_")

        if isinstance(script, str):
            self._scripts = [script]
        elif isinstance(script, list):
            self._scripts = script
        else:
            raise AttributeError(
                "script parameter must be of type string or list of strings"
            )

        # internally self._allow_failure is set to a special value 'untouched' indicating this value is untouched by the user.
        # This is because the user can set the value from outside to True, False or None, indicating the value should not be rendered.
        # 'untouched' allows for sequences to determine, if this value should be initialized or not.
        self._allow_failure: bool | str | int | list[int] | None = (
            allow_failure if allow_failure is not None else "untouched"
        )

        if image:
            self.set_image(image)
        if tags:
            self.add_tags(*tags)
        if rules:
            self.append_rules(*rules)
        if dependencies:
            self.add_dependencies(*dependencies)
        if needs:
            self.add_needs(*needs)
        if variables:
            self.add_variables(**variables)
        if environment:
            self.set_environment(environment)
        if retry:
            self.set_retry(retry)

    @property
    def name(self) -> str:
        """The name of the Job

        This property is affected by the rendering process, where `gcip.core.sequence.Sequence`s will
        populate the job name depending on their names. That means you can be sure to get the jobs
        final name when rendered.
        """
        return self._name

    @property
    def stage(self) -> str:
        """The [stage](https://docs.gitlab.com/ee/ci/yaml/#stage) keyword of the Job

        This property is affected by the rendering process, where `gcip.core.sequence.Sequence`s will
        populate the job stage depending on their stages. That means you can be sure to get the jobs
        final stage when rendered.
        """
        return self._stage

    @property
    def image(self) -> Image | None:
        """The [image](https://docs.gitlab.com/ee/ci/yaml/#image) keyword of the Job"""
        return self._image

    @property
    def allow_failure(self) -> bool | str | int | list[int] | None:
        """The [allow_failure](https://docs.gitlab.com/ee/ci/yaml/#allow_failure) keyword of the Job.

        A value of `None` means this key is unset and thus not contained in the rendered output.
        """
        if (
            self._allow_failure is None
            or isinstance(self._allow_failure, bool)
            or isinstance(self._allow_failure, int)
            or isinstance(self._allow_failure, list)
        ):
            return self._allow_failure
        return None

    @property
    def variables(self) -> dict[str, str]:
        """The [variables](https://docs.gitlab.com/ee/ci/yaml/#variables) keyword of the Job"""
        return self._variables

    @property
    def tags(self) -> list[str]:
        """The [tags](https://docs.gitlab.com/ee/ci/yaml/#tags) keyword of the Job"""
        return list(self._tags.keys())

    @property
    def rules(self) -> list[Rule]:
        """The [rules](https://docs.gitlab.com/ee/ci/yaml/#rules) keyword of the Job"""
        return self._rules

    @property
    def dependencies(self) -> list[Job | Sequence] | None:
        """The [dependencies](https://docs.gitlab.com/ee/ci/yaml/#dependencies) keyword of the Job"""
        return self._dependencies

    @property
    def needs(self) -> list[Need | Job | Sequence] | None:
        """The [needs](https://docs.gitlab.com/ee/ci/yaml/#needs) keyword of the Job"""
        return self._needs

    @property
    def scripts(self) -> list[str]:
        """The [script](https://docs.gitlab.com/ee/ci/yaml/#script) keyword of the Job"""
        return self._scripts

    @property
    def cache(self) -> Cache | None:
        """The [cache](https://docs.gitlab.com/ee/ci/yaml/#cache) keyword of the Job"""
        return self._cache

    @property
    def when(self) -> WhenStatement | None:
        """The [when](https://docs.gitlab.com/ee/ci/yaml/#when) keyword of the Job"""
        return self._when

    @property
    def timeout(self) -> str | None:
        """The [timeout](https://docs.gitlab.com/ee/ci/yaml/#timeout) keyword of the Job"""
        return self._timeout

    @property
    def resource_group(self) -> str | None:
        """The [resource_group](https://docs.gitlab.com/ee/ci/yaml/#resource_group) keyword of the Job"""
        return self._resource_group

    @property
    def environment(self) -> Environment | None:
        """The [environment](https://docs.gitlab.com/ee/ci/yaml/#environmentname) keyword of the Job"""
        return self._environment

    @property
    def retry(self) -> Retry | None:
        """The [retry](https://docs.gitlab.com/ee/ci/yaml/#retry) keyword of the Job"""
        return self._retry

    @property
    def artifacts(self) -> Artifacts:
        """The [artifacts](https://docs.gitlab.com/ee/ci/yaml/#artifacts) keyword of the Job."""
        if not self._artifacts:
            self._artifacts = Artifacts()
        return self._artifacts

    def _extend_name(self, name: str | None) -> None:
        """This method is used by `gcip.core.sequence.Sequence`s to populate the jobs name."""
        if name:
            self._name = name.replace("_", "-") + f"-{self._name}"

    def _extend_stage_value(self, stage: str | None) -> None:
        """This method is used by `gcip.core.sequence.Sequence`s to populate the jobs stage."""
        if stage:
            self._stage += "_" + stage.replace("-", "_")

    def _extend_stage(self, stage: str | None) -> None:
        """This method is used by `gcip.core.sequence.Sequence`s to populate the jobs name and stage."""
        if stage:
            self._extend_name(stage)
            self._extend_stage_value(stage)

    def _add_parent(self, parent: Sequence) -> None:
        """This method is called by `gcip.core.sequence.Sequence`s when the job is added to that sequence.

        The job needs to know its parents when `_get_all_instance_names()` is called.
        """
        self._parents.append(parent)

    def prepend_scripts(self, *scripts: str) -> Job:
        """Inserts one or more [script](https://docs.gitlab.com/ee/ci/yaml/#script)s before the current scripts.

        Returns:
            `Job`: The modified `Job` object.
        """
        self._scripts_to_prepend = list(scripts) + self._scripts_to_prepend
        return self

    def append_scripts(self, *scripts: str) -> Job:
        """Adds one or more [script](https://docs.gitlab.com/ee/ci/yaml/#script)s after the current scripts.

        Returns:
            `Job`: The modified `Job` object.
        """
        self._scripts_to_append.extend(scripts)
        return self

    def add_variables(self, **variables: str) -> Job:
        """Adds one or more [variables](https://docs.gitlab.com/ee/ci/yaml/#variables), each as keyword argument,
        to the job.

        Args:
            **variables (str): Each variable would be provided as keyword argument:
        ```
        job.add_variables(GREETING="hello", LANGUAGE="python")
        ```

        Returns:
            `Job`: The modified `Job` object.
        """
        self._variables.update(variables)
        return self

    def add_tags(self, *tags: str) -> Job:
        """Adds one or more [tags](https://docs.gitlab.com/ee/ci/yaml/#tags) to the job.

        Returns:
            `Job`: The modified `Job` object.
        """
        for tag in tags:
            self._tags[tag] = None
        return self

    def set_tags(self, *tags: str) -> Job:
        """Set the [tags](https://docs.gitlab.com/ee/ci/yaml/#tags) to the job.

        Returns:
            `Job`: The modified `Job` object.
        """
        self._tags = {}
        self.add_tags(*tags)
        return self

    def set_cache(self, cache: Cache | None) -> Job:
        """Sets the [cache](https://docs.gitlab.com/ee/ci/yaml/#cache) keyword of the Job.

        Any previous values will be overwritten.

        Args:
            cache (Cache | None): See `gcip.core.cache.Cache` class.

        Returns:
            Sequence: Returns the modified `Job` object.
        """
        if cache:
            self._cache = cache
        return self

    def set_when(self, when: WhenStatement | None) -> Job:
        """Sets the [when](https://docs.gitlab.com/ee/ci/yaml/#when) keyword of the Job.

        Any previous values will be overwritten.

        Args:
            when (WhenStatement | None): See `gcip.core.when.WhenStatement` class.

        Returns:
            Sequence: Returns the modified `Job` object.
        """
        if when:
            self._when = when
        return self

    def set_timeout(self, timeout: str | None) -> Job:
        """Sets the [timeout](https://docs.gitlab.com/ee/ci/yaml/#timeout) keyword of the Job.

        Any previous values will be overwritten.

        Args:
            timeout (str | None): A string defining a timespan as in the Gitlab CI documentation.

        Returns:
            Sequence: Returns the modified `Job` object.
        """
        if timeout:
            self._timeout = timeout
        return self

    def set_resource_group(self, resource_group: str | None) -> Job:
        """Sets the [resource_group](https://docs.gitlab.com/ee/ci/yaml/#resource_group) keyword of the Job.

        Any previous values will be overwritten.

        Args:
            resource_group (str | None): A string defining a resource group as in the Gitlab CI documentation.

        Returns:
            Sequence: Returns the modified `Job` object.
        """
        if resource_group:
            self._resource_group = resource_group
        return self

    def set_environment(self, environment: Environment | str | None) -> Job:
        """Sets the environment of this job.

        For a simple environment you can provide the environment as string.
        If you want to set the environment url or other options, you have to provide an Environment object instead.

        Args:
            environment (Environment |  str | None): Can be either `string` or `Environment`.

        Returns:
            Job: Returns the modified :class:`Job` object.
        """
        if environment:
            if isinstance(environment, str):
                environment = Environment(environment)
            self._environment = environment
        return self

    def set_retry(self, retry: Retry | int | None) -> Job:
        """Sets the retry count of this job.

        For a simple retry you can provide the retry count as number.
        If you want to set the when condition or exit codes, you have to provide an retry object instead.

        Args:
            retry (Retry |  int | None): Can be either `int` or `retry`.

        Returns:
            Job: Returns the modified :class:`Job` object.
        """
        if retry:
            if isinstance(retry, int):
                retry = Retry(max=retry)
            self._retry = retry
        return self

    def set_artifacts(self, artifacts: Artifacts | None) -> Job:
        """Sets the [artifacts](https://docs.gitlab.com/ee/ci/yaml/#artifacts) keyword of the Job.

        Any previous values will be overwritten.

        Args:
            artifacts: (Artifacts): See `gcip.core.artifacts.Artifacts` class.

        Returns:
            Sequence: Returns the modified `Job` object.
        """
        if artifacts:
            self._artifacts = artifacts
        return self

    def append_rules(self, *rules: Rule) -> Job:
        """Adds one or more  [rule](https://docs.gitlab.com/ee/ci/yaml/#rules)s behind the current rules of the job.

        Args:
            *rules (Rule): See `gcip.core.rule.Rule` class.

        Returns:
            Sequence: Returns the modified `Job` object.
        """
        self._rules.extend(rules)
        return self

    def prepend_rules(self, *rules: Rule) -> Job:
        """Inserts one or more  [rule](https://docs.gitlab.com/ee/ci/yaml/#rules)s before the current rules of the job.

        Args:
            *rules (Rule): See `gcip.core.rule.Rule` class.

        Returns:
            Sequence: Returns the modified `Job` object.
        """
        self._rules = list(rules) + self._rules
        return self

    def add_dependencies(self, *dependencies: Job | Sequence) -> Job:
        """Add one or more [dependencies](https://docs.gitlab.com/ee/ci/yaml/#dependencies) to the job.

        Args:
            *dependencies (Need |  Job |  Sequence):

        Returns:
            Sequence: Returns the modified `Job` object.
        """
        if self._dependencies is None:
            self._dependencies = []
        self._dependencies.extend(dependencies)
        return self

    def set_dependencies(self, dependencies: list[Job | Sequence] | None) -> Job:
        """Set/overwrite the list of [dependencies](https://docs.gitlab.com/ee/ci/yaml/index.html#dependencies) of this job.

        Args:
           dependencies (list[Job |  Sequence] | None): A list of `Need`s, `Job`s or `Sequence`s this job
               depends on. If the list is empty, the job dependencies nothing and would immediately run. If `None` given,
               then the `dependencies` keyword of this job will not be rendered in the pipeline output.

        Returns:
            Sequence: Returns the modified `Job` object.
        """
        self._dependencies = dependencies
        return self

    def add_needs(self, *needs: Need | Job | Sequence) -> Job:
        """Add one or more [needs](https://docs.gitlab.com/ee/ci/yaml/#needs) to the job.

        Args:
            *needs (Need |  Job |  Sequence):

        Returns:
            Sequence: Returns the modified `Job` object.
        """
        if self._needs is None:
            self._needs = []
        self._needs.extend(needs)
        return self

    def set_needs(self, needs: list[Need | Job | Sequence] | None) -> Job:
        """Set/overwrite the list of [needs](https://docs.gitlab.com/ee/ci/yaml/#needs) of this job.

        Args:
           needs (list[Need |  Job |  Sequence] | None): A list of `Need`s, `Job`s or `Sequence`s this job
               depends on. If the list is empty, the job needs nothing and would immediately run. If `None` given,
               then the `needs` keyword of this job will not be rendered in the pipeline output.

        Returns:
            Sequence: Returns the modified `Job` object.
        """
        self._needs = needs
        return self

    def set_image(self, image: Image | str | None) -> Job:
        """Sets the image of this job.

        For a simple container image you can provide the origin of the image.
        If you want to set the entrypoint, you have to provide an Image object instead.

        Args:
            image (Image |  str | None): Can be either `string` or `Image`.

        Returns:
            Job: Returns the modified :class:`Job` object.
        """
        if image:
            if isinstance(image, str):
                image = Image(image)
            self._image = image
        return self

    def set_allow_failure(
        self, allow_failure: bool | str | int | list[int] | None
    ) -> Job:
        """Sets `allow_failure` for this job.

        Args:
            allow_failure (bool |  str |  int |  list[int] | None): The value `None` means that `allow_failure`
                is unset and is not rendered in the output of this job.
        """
        self._allow_failure = allow_failure
        return self

    def _get_all_instance_names(self) -> set[str]:
        """Query all the possible names this job can have by residing within parent `gcip.core.sequence.Sequence`s.

        The possible image names are built by the `name` of this job plus all the possible prefix values from
        parent parent `gcip.core.sequence.Sequence`s. The prefix values from parent sequences are their names
        prefixed with the names of the parent parent sequences and so on.

        Imagine Job `A` resides within following sequenes:

        ```
        B:
          A
        C:
          D:
            A
        ```

        Then the instance names of `A` would be `B-A` and `C-D-A`.
        """
        instance_names: set[str] = set()
        for parent in self._parents:
            for prefix in parent._get_all_instance_names(self):
                if prefix:
                    instance_names.add(f"{prefix}-{self._name}")
                else:
                    instance_names.add(self._name)
        return instance_names

    def _copy(self) -> Job:
        """Returns an independent, deep copy object of this job.

        Returns:
            `Job`: A copy of this job which, when modified, has no effects on this source job.
        """
        job_copy = copy.deepcopy(self)
        job_copy._original = self
        return job_copy

    def render(self) -> dict[str, Any]:
        """Return a representation of this Job object as dictionary with static values.

        The rendered representation is used by the gcip to dump it
        in YAML format as part of the .gitlab-ci.yml pipeline.

        Returns:
            dict[str, Any]: A dictionary representing the job object in Gitlab CI.
        """
        # late import to avoid circular dependencies
        from .sequence import Sequence

        rendered_job: dict[str, Any] = {}

        if self._image:
            rendered_job["image"] = self._image.render()

        # self._allow_failure should not be rendered when its value is None or
        # the internal special value 'untouched'
        if isinstance(self._allow_failure, bool):
            rendered_job["allow_failure"] = self._allow_failure
        elif isinstance(self._allow_failure, int):
            rendered_job["allow_failure"] = {"exit_codes": [self._allow_failure]}
        elif isinstance(self._allow_failure, list):
            rendered_job["allow_failure"] = {"exit_codes": self._allow_failure}

        if self._dependencies is not None:
            dependency_jobs: list[Job] = list()
            for dependency in self._dependencies:
                if isinstance(dependency, Job):
                    dependency_jobs.append(dependency)
                elif isinstance(dependency, Sequence):
                    for job in dependency.nested_jobs:
                        dependency_jobs.append(job)
                else:
                    raise TypeError(
                        f"Dependency '{dependency}' is of type {type(dependency)}."
                    )

            dependency_names: set[str] = set()
            for job in dependency_jobs:
                dependency_names.update(job._get_all_instance_names())

            rendered_job["dependencies"] = sorted(dependency_names)

        if self._needs is not None:
            need_jobs: list[Job] = list()
            rendered_needs: list[dict[str, str | bool]] = list()
            for need in self._needs:
                if isinstance(need, Job):
                    need_jobs.append(need)
                elif isinstance(need, Sequence):
                    for job in need.last_jobs_executed:
                        need_jobs.append(job)
                elif isinstance(need, Need):
                    rendered_needs.append(need.render())
                else:
                    raise TypeError(f"Need '{need}' is of type {type(need)}.")

            job_names: set[str] = set()
            for job in need_jobs:
                job_names.update(job._get_all_instance_names())

            for name in job_names:
                rendered_needs.append(Need(name).render())

            # sort needs by the name of the referenced job or pipeline
            rendered_needs = sorted(
                rendered_needs,
                key=lambda need: need["job"] if "job" in need else need["pipeline"],
            )

            rendered_job["needs"] = rendered_needs

        rendered_job.update(
            {
                "stage": self._stage,
                "script": [
                    *self._scripts_to_prepend,
                    *self._scripts,
                    *self._scripts_to_append,
                ],
            }
        )

        if self._variables:
            rendered_job["variables"] = self._variables

        if self._rules:
            rendered_rules = []
            for rule in self._rules:
                rendered_rules.append(rule.render())
            rendered_job.update({"rules": rendered_rules})

        if self._cache:
            rendered_job.update({"cache": self._cache.render()})

        if self._when:
            rendered_job.update({"when": self._when.value})

        if self._timeout:
            rendered_job.update({"timeout": self._timeout})

        if self._resource_group:
            rendered_job.update({"resource_group": self._resource_group})

        if self._artifacts:
            rendered_artifacts = self._artifacts.render()
            if rendered_artifacts:
                rendered_job.update({"artifacts": rendered_artifacts})

        if self._tags.keys():
            rendered_job["tags"] = list(self._tags.keys())

        if self._environment:
            rendered_job["environment"] = self._environment.render()

        if self._retry:
            rendered_job["retry"] = self._retry.render()

        return rendered_job


class TriggerStrategy(Enum):
    """This class represents the [trigger:strategy](https://docs.gitlab.com/ee/ci/yaml/#linking-pipelines-with-triggerstrategy)
    keyword."""

    DEPEND = "depend"
    """Use this strategy to force the `TriggerJob` to wait for the downstream (multi-project or child) pipeline to complete."""


class TriggerJob(Job):
    """This class represents the [trigger](https://docs.gitlab.com/ee/ci/yaml/#trigger) job.

    Jobs with trigger can only use a [limited set of keywords](https://docs.gitlab.com/ee/ci/multi_project_pipelines.html#limitations).
    For example, you can’t run commands with `script`.

    Simple example:

    ```python
    trigger_job = TriggerJob(
        stage="trigger-other-job",
        project="myteam/other-project",
        branch="main",
        strategy=TriggerStrategy.DEPEND,
    )
    trigger_job.append_rules(rules.on_tags().never(), rules.on_main())
    ```

    Args:
        project (str | None): The full name of another Gitlab project to trigger (multi-project pipeline trigger)
            Mutually exclusive with `includes`. Defaults to None.
        branch (str | None): The branch of `project` the pipeline should be triggered of. Defaults to None.
        includes (list[Include] | None): Include a pipeline to trigger (Parent-child pipeline trigger)
            Mutually exclusiv with `project`. Defaults to None.
        strategy (TriggerStrategy | None): Determines if the result of this pipeline depends on the triggered downstream pipeline
            (use `TriggerStrategy.DEPEND`) or if just "fire and forget" the downstream pipeline (use `None`). Defaults to None.

    Raises:
        ValueError: If both `project` and `includes` are given.
        ValueError: When the limit of three child pipelines is exceeded. See https://docs.gitlab.com/ee/ci/parent_child_pipelines.html
            for more information.
    """

    def __init__(
        self,
        name: str | None = None,
        stage: str | None = None,
        project: str | None = None,
        branch: str | None = None,
        includes: Include | list[Include] | None = None,
        strategy: TriggerStrategy | None = None,
    ) -> None:
        if includes and project:
            raise ValueError(
                (
                    "You cannot specify 'include' and 'project' together. Either 'include' or 'project' is possible."
                )
            )
        if not includes and not project:
            raise ValueError("Neither 'includes' nor 'project' is given.")

        super().__init__(name=name, stage=stage, script="none")

        self._project = project
        self._branch = branch
        self._strategy = strategy

        if not includes:
            self._includes = None
        elif isinstance(includes, Include):
            self._includes = [includes]
        elif isinstance(includes, list):
            if len(includes) > 3:
                raise ValueError(
                    (
                        "The length of 'includes' is limited to three."
                        "See https://docs.gitlab.com/ee/ci/parent_child_pipelines.html for more information."
                    )
                )
            self._includes = includes
        else:
            raise AttributeError(
                "script parameter must be of type string or list of strings"
            )

    def render(self) -> dict[Any, Any]:
        """Return a representation of this TriggerJob object as dictionary with static values.

        The rendered representation is used by the gcip to dump it
        in YAML format as part of the .gitlab-ci.yml pipeline.

        Returns:
            dict[str, Any]: A dictionary representing the trigger job object in Gitlab CI.
        """
        rendered_job = super().render()

        # remove unsupported keywords from TriggerJob
        rendered_job.pop("script")

        if "image" in rendered_job:
            rendered_job.pop("image")

        if "tags" in rendered_job:
            rendered_job.pop("tags")

        if "artifacts" in rendered_job:
            rendered_job.pop("artifacts")

        if "cache" in rendered_job:
            rendered_job.pop("cache")

        trigger: dict[str, str | list[dict[str, str]]] = {}

        # Child pipelines
        if self._includes:
            trigger.update(
                {
                    "include": [include.render() for include in self._includes],
                }
            )

        # Multiproject pipelines
        if self._project:
            trigger.update(
                {
                    "project": self._project,
                }
            )
            if self._branch:
                trigger.update({"branch": self._branch})

        if self._strategy:
            trigger.update({"strategy": self._strategy.value})

        rendered_job = {"trigger": trigger, **rendered_job}

        return rendered_job


class PagesJob(Job):
    def __init__(self) -> None:
        """
        This is a special kind of jobs which deploys Gitlab Pages.

        This job has the static name `pages` and the static artifacts path `./public`. Both preconfigurations
        can't be altered and are required for deploying Gitlab Pages properly. All methods which would typically
        alter the name, stage and artifacts of a job are overwritten with an empty implementation.

        This job is only for deploying Gitlab Pages artifacts within the `./public` artifacts path. To create the
        artifacts you have to run jobs, that generate those artifacts within the same `./public` artifacts path,
        before this PagesJob in the pipeline.

        Because the name of the job can't be altered, this job may only exist once in the generated pipeline output.
        Typically you should add the PagesJob to the `gcip.core.pipeline.Pipeline`.

        The PagesJob is also preconfigured with the stage `pages` and the image `alpine:latest`. To change the stage
        of this job, use the `set_stage()` method. Please mention to run this job in a stage after all jobs, that
        fill the `public` artifacts path with content.

        Here a simple example how to use the GitlabPages job:

        ```
        pipeline = Pipeline()
        pipeline.add_children(
            Job(stage="deploy", script="./create-html.sh").add_artifacts_paths("public"),
            PagesJob(),
        )
        ```
        """
        super().__init__(stage="pages", script="echo 'Publishing Gitlab Pages'")
        self._name = "pages"
        super().artifacts.add_paths("public")
        super().set_image("busybox:latest")

    def set_stage(self, stage: str) -> PagesJob:
        """Set the name of this jobs stage to a value other than `pages`.

        Args:
            stage (str): A valid Gitlab CI Job stage name.

        Returns:
            PagesJob: The modified PagesJob object.
        """
        self._stage = stage
        return self

    def _extend_name(self, name: str | None) -> None:
        """
        The jobs name `pages` is fixed and can't be altered.
        """

    def _extend_stage(self, stage: str | None) -> None:
        """
        The stage name can't be altered from parent sequences.
        """

    def _extend_stage_value(self, stage: str | None) -> None:
        pass

    def _get_all_instance_names(self) -> set[str]:
        """
        There should be only one instance of the job with the name `pages`.

        Returns:
            set[str]: `set("pages")`
        """
        return set(self._name)

    def _copy(self) -> Job:
        """
        There should be only one instance of this job, that is why this method
        does not return a copy of this job but the job itself.
        """
        return self

    def add_artifacts_paths(self, *paths: str) -> Job:
        """
        This job does not accept further artifact paths than `./public` and thus
        ignores this call.
        """
        return self
