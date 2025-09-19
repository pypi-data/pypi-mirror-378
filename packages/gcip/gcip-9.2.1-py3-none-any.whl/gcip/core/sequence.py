"""A Sequence collects multiple `gcip.core.job.Job`s and/or other `gcip.core.sequence.Sequence`s into a group.

This concept is no official representation of a Gitlab CI keyword. But it is such a powerful
extension of the Gitlab CI core funtionality and an essential building block of the gcip, that
it is conained in the `gcip.core` module.

A Sequence offers a mostly similar interface like `gcip.core.job.Job`s that allows to modify
all Jobs and child Sequences contained into that parent Sequence. For example: Instad of calling
`add_tag()` on a dozens of Jobs you can call `add_tag()` on the sequence that contain those Jobs.
The tag will then be applied to all Jobs in that Sequence and recursively to all Jobs within child
Sequenes of that Sequence.

Sequences must be added to a `gcip.core.pipeline.Pipeline`, either directly or as part of other Sequences.
That means Sequences are not meant to be a throw away configuration container for a bunch ob Jobs.
This is because adding a Job to a Sequence creates a copy of that Job, which will be inderectly added to
the `Pipeline` by that Sequence. Not adding that Sequence to a Pipeline means also not adding its Jobs
to the Pipeline. If other parts of the Pipeline have dependencies to those Jobs, they will be broken.

As said before, adding a Job to a Sequence creates copies of that Job. To void conflicts between Jobs,
you should set `name` and/or `stage` when adding the job (or child sequence). The sequence will add
the `name`/`stage` to the ones of the Job, when rendering the pipeline. If you do not set those
identifiers, or you set equal name/stages for jobs and sequences, you provoke having two or more
jobs having the same name in the pipeline. The gcip will raise a ValueError, to avoid unexpected
pipeline behavior. You can read more information in the chapter "Stages allow reuse of jobs
and sequences" of the user documantation.
"""

from __future__ import annotations

import copy
from typing import Any

from . import OrderedSetType
from .artifacts import Artifacts
from .cache import Cache
from .environment import Environment
from .image import Image
from .job import Job, JobFilter
from .need import Need
from .retry import Retry
from .rule import Rule
from .when import WhenStatement

__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach", "Daniel von Eßen"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"

# TODO: Use removeprefix beginning with python3.8
# This is a compatibility implementation of ChildDict.
ChildDict = dict[str, Any]
# class ChildDict(TypedDict):
#     """This data structure is supposed to store one child of a `Sequence` with all required information about that child."""

#     child: Job |  Sequence
#     """The child to store - a `gcip.core.job.Job` or `Sequence`."""
#     stage: str | None
#     """The stage with whom the `child` was added to the `Sequence`."""
#     name: str | None
#     """The name with whom the `child` was added to the `Sequence`."""


class Sequence:
    """A Sequence collects multiple `gcip.core.job.Job`s and/or other `gcip.core.sequence.Sequence`s into a group."""

    def __init__(self) -> None:
        super().__init__()
        self._children: list[ChildDict] = list()
        self._image_for_initialization: Image | str | None = None
        self._image_for_replacement: Image | str | None = None
        self._environment_for_initialization: Environment | str | None = None
        self._environment_for_replacement: Environment | str | None = None
        self._retry_for_initialization: Retry | int | None = None
        self._retry_for_replacement: Retry | int | None = None
        self._when_for_initialization: WhenStatement | None = None
        self._when_for_replacement: WhenStatement | None = None
        self._timeout_for_initialization: str | None = None
        self._timeout_for_replacement: str | None = None
        self._resource_group_for_initialization: str | None = None
        self._resource_group_for_replacement: str | None = None
        self._allow_failure_for_initialization: bool | str | int | list[int] | None = (
            "untouched"
        )
        self._allow_failure_for_replacement: bool | str | int | list[int] | None = (
            "untouched"
        )
        self._variables: dict[str, str] = {}
        self._variables_for_initialization: dict[str, str] = {}
        self._variables_for_replacement: dict[str, str] = {}
        self._tags: OrderedSetType = {}
        self._tags_for_initialization: OrderedSetType = {}
        self._tags_for_replacement: OrderedSetType = {}
        self._artifacts: Artifacts | None = None
        self._artifacts_for_initialization: Artifacts | None = None
        self._artifacts_for_replacement: Artifacts | None = None
        self._cache: Cache | None = None
        self._cache_for_initialization: Cache | None = None
        self._scripts_to_prepend: list[str] = []
        self._scripts_to_append: list[str] = []
        self._rules_to_append: list[Rule] = []
        self._rules_to_prepend: list[Rule] = []
        self._rules_for_initialization: list[Rule] = []
        self._rules_for_replacement: list[Rule] = []
        self._dependencies: list[Job | Sequence] | None = None
        self._dependencies_for_initialization: list[Job | Sequence] | None = None
        self._dependencies_for_replacement: list[Job | Sequence] | None = None
        self._needs: list[Need | Job | Sequence] | None = None
        self._needs_for_initialization: list[Need | Job | Sequence] | None = None
        self._needs_for_replacement: list[Need | Job | Sequence] | None = None
        self._parents: list[Sequence] = list()

    def _add_parent(self, parent: Sequence) -> None:
        self._parents.append(parent)

    def add_children(
        self,
        *jobs_or_sequences: Job | Sequence,
        stage: str | None = None,
        name: str | None = None,
    ) -> Sequence:
        """Add `gcip.core.job.Job`s or other `gcip.core.sequence.Sequence`s to this sequence.

        Adding a child creates a copy of that child. You should provide a name or stage
        when adding children, to make them different from other places where they will be used.

        Args:
            jobs_or_sequences (Job |  Sequence): One or more jobs or sequences to be added to this sequence.
            stage (str | None, optional): Adds a stages component to all children added. Defaults to None.
            name (str | None, optional): Adds a name component to all children added. Defaults to None.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        for child in jobs_or_sequences:
            child._add_parent(self)
            self._children.append({"child": child, "stage": stage, "name": name})
        return self

    def add_variables(self, **variables: str) -> Sequence:
        """Calling `gcip.core.job.Job.add_variables()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._variables.update(variables)
        return self

    def initialize_variables(self, **variables: str) -> Sequence:
        """Calling `gcip.core.job.Job.add_variables()` to all jobs within this sequence that haven't been added variables before.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._variables_for_initialization.update(variables)
        return self

    def override_variables(self, **variables: str) -> Sequence:
        """Calling `gcip.core.job.Job.add_variables()` to all jobs within this sequence and overriding any previously added variables to that jobs.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._variables_for_replacement.update(variables)
        return self

    def set_cache(self, cache: Cache) -> Sequence:
        """Calling `gcip.core.job.Job.set_cache()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._cache = cache
        return self

    def initialize_cache(self, cache: Cache) -> Sequence:
        """Calling `gcip.core.job.Job.set_cache()` to all jobs within this sequence that haven't been set the cache before.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._cache_for_initialization = cache
        return self

    def set_artifacts(self, artifacts: Artifacts) -> Sequence:
        """Sets `gcip.core.job.Job.artifacts` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._artifacts = artifacts
        return self

    def initialize_artifacts(self, artifacts: Artifacts) -> Sequence:
        """Sets `gcip.core.job.Job.artifacts` to all jobs within this sequence that haven't been set the artifacs before.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._artifacts_for_initialization = artifacts
        return self

    def override_artifacts(self, artifacts: Artifacts) -> Sequence:
        """Calling `gcip.core.job.Job.set_artifacts()` to all jobs within this sequence and overriding any previously added artifacts to that jobs.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._artifacts_for_initialization = artifacts
        return self

    def add_tags(self, *tags: str) -> Sequence:
        """Calling `gcip.core.job.Job.add_tags()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        for tag in tags:
            self._tags[tag] = None
        return self

    def initialize_tags(self, *tags: str) -> Sequence:
        """Calling `gcip.core.job.Job.add_tags()` to all jobs within this sequence that haven't been added tags before.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        for tag in tags:
            self._tags_for_initialization[tag] = None
        return self

    def override_tags(self, *tags: str) -> Sequence:
        """Calling `gcip.core.job.Job.add_tags()` to all jobs within this sequence and overriding any previously added tags to that jobs.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        for tag in tags:
            self._tags_for_replacement[tag] = None
        return self

    def append_rules(self, *rules: Rule) -> Sequence:
        """Calling `gcip.core.job.Job.append_rules()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._rules_to_append.extend(rules)
        return self

    def prepend_rules(self, *rules: Rule) -> Sequence:
        """Calling `gcip.core.job.Job.prepend_rules()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._rules_to_prepend = list(rules) + self._rules_to_prepend
        return self

    def initialize_rules(self, *rules: Rule) -> Sequence:
        """Calling `gcip.core.job.Job.append_rules()` to all jobs within this sequence that haven't been added rules before.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._rules_for_initialization.extend(rules)
        return self

    def override_rules(self, *rules: Rule) -> Sequence:
        """Calling `gcip.core.job.Job.override_rules()` to all jobs within this sequence and overriding any previously added rules to that jobs.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._rules_for_replacement.extend(rules)
        return self

    def add_dependencies(self, *dependencies: Job | Sequence) -> Sequence:
        """Calling `gcip.core.job.Job.add_dependencies()` to all jobs within the first stage of this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if self._dependencies is None:
            self._dependencies = []
        self._dependencies.extend(dependencies)
        return self

    def initialize_dependencies(self, *dependencies: Job | Sequence) -> Sequence:
        """Calling `gcip.core.job.Job.set_dependencies()` to all jobs within the first stage of this sequence that haven't been added dependencies before.
        An empty parameter list means that jobs will get an empty dependency list and thus does not download artifacts by default.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._dependencies_for_initialization = list(dependencies)
        return self

    def override_dependencies(self, *dependencies: Job | Sequence) -> Sequence:
        """
        Calling `gcip.core.job.Job.set_dependencies()` to all jobs within the first stage of this sequence and overriding any previously added
        dependencies to that jobs.
        An empty parameter list means that jobs will get an empty dependency list and thus does not download artifacts.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._dependencies_for_replacement = list(dependencies)
        return self

    def add_needs(self, *needs: Need | Job | Sequence) -> Sequence:
        """Calling `gcip.core.job.Job.add_need()` to all jobs within the first stage of this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if self._needs is None:
            self._needs = []
        self._needs.extend(needs)
        return self

    def initialize_needs(self, *needs: Need | Job | Sequence) -> Sequence:
        """Calling `gcip.core.job.Job.set_needs()` to all jobs within the first stage of this sequence that haven't been added needs before.
        An empty parameter list means that jobs will get an empty dependency list and thus does not depend on other jobs by default.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._needs_for_initialization = list(needs)
        return self

    def override_needs(self, *needs: Need | Job | Sequence) -> Sequence:
        """Calling `gcip.core.job.Job.set_needs()` to all jobs within the first stage of this sequence and overriding any previously added needs to that jobs.
        An empty parameter list means that jobs will get an empty dependency list and thus does not depend on other jobs.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._needs_for_replacement = list(needs)
        return self

    def prepend_scripts(self, *scripts: str) -> Sequence:
        """Calling `gcip.core.job.Job.prepend_scripts()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._scripts_to_prepend = list(scripts) + self._scripts_to_prepend
        return self

    def append_scripts(self, *scripts: str) -> Sequence:
        """Calling `gcip.core.job.Job.append_scripts()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._scripts_to_append.extend(scripts)
        return self

    def initialize_image(self, image: Image | str) -> Sequence:
        """Calling `gcip.core.job.Job.set_image()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if image:
            self._image_for_initialization = image
        return self

    def override_image(self, image: Image | str) -> Sequence:
        """Calling `gcip.core.job.Job.set_image()` to all jobs within this sequence overriding any previous set value.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if image:
            self._image_for_replacement = image
        return self

    def initialize_environment(self, environment: Environment | str | None) -> Sequence:
        """Calling `gcip.core.job.Job.set_environment()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if environment:
            self._environment_for_initialization = environment
        return self

    def override_environment(self, environment: Environment | str | None) -> Sequence:
        """Calling `gcip.core.job.Job.set_environment()` to all jobs within this sequence overriding any previous set value.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if environment:
            self._environment_for_replacement = environment
        return self

    def initialize_retry(self, retry: Retry | int | None) -> Sequence:
        """Calling `gcip.core.job.Job.set_retry()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if retry:
            self._retry_for_initialization = retry
        return self

    def override_retry(self, retry: Retry | int | None) -> Sequence:
        """Calling `gcip.core.job.Job.set_retry()` to all jobs within this sequence overriding any previous set value.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if retry:
            self._retry_for_replacement = retry
        return self

    def initialize_when(self, when: WhenStatement | None) -> Sequence:
        """Calling `gcip.core.job.Job.set_when()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if when:
            self._when_for_initialization = when
        return self

    def override_when(self, when: WhenStatement | None) -> Sequence:
        """Calling `gcip.core.job.Job.set_when()` to all jobs within this sequence overriding any previous set value.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if when:
            self._when_for_replacement = when
        return self

    def initialize_timeout(self, timeout: str | None) -> Sequence:
        """Calling `gcip.core.job.Job.set_timeout()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if timeout:
            self._timeout_for_initialization = timeout
        return self

    def override_timeout(self, timeout: str | None) -> Sequence:
        """Calling `gcip.core.job.Job.set_timeout()` to all jobs within this sequence overriding any previous set value.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if timeout:
            self._timeout_for_replacement = timeout
        return self

    def initialize_resource_group(self, resource_group: str | None) -> Sequence:
        """Calling `gcip.core.job.Job.set_resource_group()` to all jobs within this sequence.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if resource_group:
            self._resource_group_for_initialization = resource_group
        return self

    def override_resource_group(self, resource_group: str | None) -> Sequence:
        """Calling `gcip.core.job.Job.set_resource_group()` to all jobs within this sequence overriding any previous set value.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        if resource_group:
            self._resource_group_for_replacement = resource_group
        return self

    def initialize_allow_failure(
        self, allow_failure: bool | str | int | list[int] | None
    ) -> Sequence:
        """Calling `gcip.core.job.Job.set_allow_failure()` to all jobs within this sequence that haven't been set the allow_failure before.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._allow_failure_for_initialization = allow_failure
        return self

    def override_allow_failure(
        self, allow_failure: bool | str | int | list[int] | None
    ) -> Sequence:
        """Calling `gcip.core.job.Job.set_allow_failure()` to all jobs within this sequence overriding any previous set value.

        Returns:
            `Sequence`: The modified `Sequence` object.
        """
        self._allow_failure_for_replacement = allow_failure
        return self

    def _get_all_instance_names(self, child: Job | Sequence) -> set[str]:
        """Return all instance names from the given child.

        That means all combinations of the childs name and stage within this
        sequence and all parent sequences.
        """

        # first get all instance names from parents of this sequence
        own_instance_names: set[str] = set()
        for parent in self._parents:
            own_instance_names.update(parent._get_all_instance_names(self))

        # second get all instance names of the child within this sequence
        child_instance_names: set[str] = set()
        child_instance_name: str
        for item in self._children:
            if item["child"] is child:
                child_name = item["name"]
                child_stage = item["stage"]
                if child_stage:
                    if child_name:
                        child_instance_name = f"{child_name}-{child_stage}"
                    else:
                        child_instance_name = child_stage
                elif child_name:
                    child_instance_name = child_name
                else:
                    child_instance_name = ""

                # all job names have '-' instead of '_'
                child_instance_names.add(child_instance_name.replace("_", "-"))

        # third combine all instance names of this sequences
        # with all instance names of the child
        return_values: set[str] = set()
        if own_instance_names:
            for child_instance_name in child_instance_names:
                for instance_name in own_instance_names:
                    if child_instance_name and instance_name:
                        return_values.add(f"{instance_name}-{child_instance_name}")
                    elif child_instance_name:
                        return_values.add(child_instance_name)
                    else:
                        return_values.add(instance_name)
        else:
            return_values = child_instance_names

        return return_values

    @property
    def last_jobs_executed(self) -> list[Job]:
        """This property returns all Jobs from the last stage of this sequence.

        This is typically be requested from a job which has setup this sequence as need,
        to determine all actual jobs of this sequence as need.
        """
        all_jobs = self.populated_jobs
        stages: dict[str, None] = {}
        for job in all_jobs:
            # use the keys of dictionary as ordered set
            stages[job.stage] = None

        last_stage = list(stages.keys())[-1]
        last_executed_jobs: list[Job] = list()
        for job in all_jobs:
            if job._stage == last_stage:
                if job._original:
                    last_executed_jobs.append(job._original)
                else:
                    raise AttributeError(
                        "job._original is None, because the job is not a copy of another job"
                    )

        return last_executed_jobs

    def find_jobs(
        self, *job_filters: JobFilter, include_sequence_attributes: bool = False
    ) -> set[Job]:
        """
        Find recursively all jobs matching one or more criterias.

        This sequence is looking for all its jobs and recursively for all jobs of
        its sub-sequences for jobs matching the `job_filters`. A job must match all
        criterias of a job_filter but must match at least one job_filter to be in the
        set of jobs returned. Or in other words, a job must match all criterias of at
        least one job_filter.

        Args:
            *job_filters (JobFilter): One or more filters to select the jobs returned.
            include_sequence_attributes (bool): **IMPORTANT!** This flag affect the result.
                When set to `True`, when matching jobs to the `job_filters` also attributes
                inherited from parent sequences, where the job resides, in were considered. On the
                one hand this makes the search for jobs more natural, as you are looking for
                jobs like they were in the final yaml output. On the other hand it might be
                confusing that the jobs returned from the search are not containing the attributes
                you used when searching for that jobs. That is because those attributes
                are then inherited from parent sequences and not contained in the job itself.
                **ATTENTION:** Imagine two sequences contain the identical (not equal!) job object. In the resulting
                yaml pipeline this job is contained twice, but with different attributes, he inherits
                from his sequences. If you find and modify this job by the attributes of only one of
                its sequences. Nevertheless when editing the job, the changes will be made on the
                identical job object of both sequences. So you might only want to search and replace
                an attribute of only one resulting job in the final yaml pipeline, but in fact set the
                attributes for both resulting jobs, as you set the attribute on the job and not the
                sequence.
                If you only want to search jobs by attributes the jobs really have, then you have
                to set that flag to `False`. In this case the result may be confusing, because
                you might miss jobs in the result that clearly have attributes you are looking for
                in the final yaml pipeline. This is when those jobs only inherit those attributes
                from their parent pipelines.
                Because of the fact, that you accidentially modify two resulting jobs in the final
                yaml pipeline, by editing the identical job object contained in different sequences,
                the default value of `include_sequence_attributes` is `False`. When you set it to
                `True` you have to consider this fact.

        Returns:
            Set[Job]: The set contains all jobs, that match all criterias of at least
                one job filter.
        """
        jobs: set[Job] = set()

        if include_sequence_attributes:
            for job in self.populated_jobs:
                for filter in job_filters:
                    if filter.match(job):
                        if job._original:
                            jobs.add(job._original)
                        else:
                            raise AttributeError(
                                "job._original is None, because the job is not a copy of another job"
                            )
        else:
            for item in self._children:
                child = item["child"]
                if isinstance(child, Job):
                    for filter in job_filters:
                        if filter.match(child):
                            jobs.add(child)
                elif isinstance(child, Sequence):
                    jobs.update(
                        child.find_jobs(
                            *job_filters,
                            include_sequence_attributes=include_sequence_attributes,
                        )
                    )
                else:
                    raise TypeError(
                        f"child in self._children is of wront type: {type(child)}"
                    )
        return jobs

    @property
    def nested_jobs(self) -> list[Job]:
        """Returns all jobs of this this sequences as well as jobs of sub-sequences recursively."""
        all_jobs: list[Job] = []
        for item in self._children:
            child = item["child"]
            if isinstance(child, Job):
                all_jobs.append(child)
            elif isinstance(child, Sequence):
                all_jobs.extend(child.nested_jobs)
            else:
                raise ValueError(
                    f"Unexpected error. Sequence child is of unknown type '{type(child)}'."
                )
        return all_jobs

    @property
    def populated_jobs(self) -> list[Job]:
        """Returns a list with populated copies of all nested jobs of this sequence.

        Populated means, that all attributes of a Job which depends on its context are resolved
        to their final values. The context is primarily the sequence within the jobs resides but
        also dependencies to other jobs and sequences. Thus this sequence will apply its own
        configuration, like variables to add, tags to set, etc., to all its jobs and sequences.

        Copies means what it says, that the returned job are not the same job objects, originally
        added to this sequence, but copies of them.

        Nested means, that also jobs from sequences within this sequence, are returned, as well
        as jobs from sequences within sequences within this sequence and so on.

        Returns:
            list[Job]: A list of copies of all nested jobs of this sequence with their final attribute values.
        """
        all_jobs: list[Job] = []
        for item in self._children:
            child = item["child"]
            child_name = item["name"]
            child_stage = item["stage"]
            if isinstance(child, Sequence):
                for job_copy in child.populated_jobs:
                    job_copy._extend_stage(child_stage)
                    job_copy._extend_name(child_name)
                    all_jobs.append(job_copy)
            elif isinstance(child, Job):
                job_copy = child._copy()
                job_copy._extend_stage(child_stage)
                job_copy._extend_name(child_name)
                all_jobs.append(job_copy)

        if all_jobs:
            first_job = all_jobs[0]
            if self._needs_for_initialization is not None and first_job._needs is None:
                first_job.set_needs(copy.deepcopy(self._needs_for_initialization))
            if self._needs_for_replacement is not None:
                first_job.set_needs(copy.deepcopy(self._needs_for_replacement))
            if self._needs is not None:
                first_job.add_needs(*copy.deepcopy(self._needs))
            for job in all_jobs[1:]:
                if job._stage == first_job.stage:
                    if (
                        self._needs_for_initialization is not None
                        and job._needs is None
                    ):
                        job.set_needs(copy.deepcopy(self._needs_for_initialization))
                    if self._needs_for_replacement is not None:
                        job.set_needs(copy.deepcopy(self._needs_for_replacement))
                    if self._needs is not None:
                        job.add_needs(*copy.deepcopy(self._needs))

        for job in all_jobs:
            if self._image_for_initialization and not job._image:
                job.set_image(copy.deepcopy(self._image_for_initialization))
            if self._image_for_replacement:
                job.set_image(copy.deepcopy(self._image_for_replacement))

            if self._environment_for_initialization and not job._environment:
                job.set_environment(copy.deepcopy(self._environment_for_initialization))
            if self._environment_for_replacement:
                job.set_environment(copy.deepcopy(self._environment_for_replacement))

            if self._retry_for_initialization and not job._retry:
                job.set_retry(copy.deepcopy(self._retry_for_initialization))
            if self._retry_for_replacement:
                job.set_retry(copy.deepcopy(self._retry_for_replacement))

            if self._when_for_initialization and not job._when:
                job.set_when(copy.deepcopy(self._when_for_initialization))
            if self._when_for_replacement:
                job.set_when(copy.deepcopy(self._when_for_replacement))

            if self._timeout_for_initialization and not job._timeout:
                job.set_timeout(self._timeout_for_initialization)
            if self._timeout_for_replacement:
                job.set_timeout(self._timeout_for_replacement)

            if self._resource_group_for_initialization and not job._resource_group:
                job.set_resource_group(self._resource_group_for_initialization)
            if self._resource_group_for_replacement:
                job.set_resource_group(self._resource_group_for_replacement)

            if (
                self._allow_failure_for_initialization != "untouched"
                and job._allow_failure == "untouched"
            ):
                job._allow_failure = self._allow_failure_for_initialization
            if self._allow_failure_for_replacement != "untouched":
                job._allow_failure = self._allow_failure_for_replacement

            if self._variables_for_initialization and not job._variables:
                job._variables = copy.deepcopy(self._variables_for_initialization)
            if self._variables_for_replacement:
                job._variables = copy.deepcopy(self._variables_for_replacement)
            job.add_variables(**copy.deepcopy(self._variables))

            if self._cache_for_initialization and not job._cache:
                job._cache = copy.deepcopy(self._cache_for_initialization)
            job.set_cache(copy.deepcopy(self._cache))

            if self._artifacts_for_initialization and (
                not job.artifacts.paths and not job.artifacts.reports
            ):
                job._artifacts = copy.deepcopy(self._artifacts_for_initialization)
            if self._artifacts_for_replacement:
                job._artifacts = copy.deepcopy(self._artifacts_for_replacement)
            job.set_artifacts(copy.deepcopy(self._artifacts))

            if (
                self._dependencies_for_initialization is not None
                and job._dependencies is None
            ):
                job.set_dependencies(
                    copy.deepcopy(self._dependencies_for_initialization)
                )
            if self._dependencies_for_replacement is not None:
                job.set_dependencies(copy.deepcopy(self._dependencies_for_replacement))
            if self._dependencies is not None:
                job.add_dependencies(*copy.deepcopy(self._dependencies))

            if self._tags_for_initialization and not job._tags:
                job._tags = copy.deepcopy(self._tags_for_initialization)
            if self._tags_for_replacement:
                job._tags = copy.deepcopy(self._tags_for_replacement)
            job.add_tags(*list(copy.deepcopy(self._tags).keys()))

            if self._rules_for_initialization and not job._rules:
                job._rules = copy.deepcopy(self._rules_for_initialization)
            if self._rules_for_replacement:
                job._rules = copy.deepcopy(self._rules_for_replacement)
            job.append_rules(*copy.deepcopy(self._rules_to_append))
            job.prepend_rules(*copy.deepcopy(self._rules_to_prepend))

            job.prepend_scripts(*copy.deepcopy(self._scripts_to_prepend))
            job.append_scripts(*copy.deepcopy(self._scripts_to_append))

        return all_jobs
