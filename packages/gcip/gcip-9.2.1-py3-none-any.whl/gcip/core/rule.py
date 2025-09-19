"""This module represents the Gitlab CI [rules](https://docs.gitlab.com/ee/ci/yaml/#rules) keyword.

Use rules to include or exclude jobs in pipelines.

```
my_job.prepend_rules(
    Rule(
        if_statement='$CI_COMMIT_BRANCH == "master"',
        changes: ["Dockerfile", "gcip/**/**"],
        exists: ["Dockerfile"],
        when=WhenStatement.ON_FAILURE,
        allow_failure: True,
        variables: { "SOME_VARIABLE": "foobar" },
        )
    )
```
"""

from __future__ import annotations

import copy

from gcip.core.when import WhenStatement

__author__ = "Thomas Steinbach"
__copyright__ = "Copyright 2020 DB Systel GmbH"
__credits__ = ["Thomas Steinbach", "Daniel von Eßen"]
# SPDX-License-Identifier: Apache-2.0
__license__ = "Apache-2.0"
__maintainer__ = "Thomas Steinbach"
__email__ = "thomas.t.steinbach@deutschebahn.com"


class Rule:
    """This module represents the Gitlab CI [rules](https://docs.gitlab.com/ee/ci/yaml/#rules) keyword.

    Use `rules` to include or exclude jobs in pipelines.

    Args:
        if_statement (str], optional): The [rules:if clause | None(https://docs.gitlab.com/ee/ci/yaml/#when) which decides when
            a job to the pipeline. Defaults to None.
        when (WhenStatement, optional): The [when](https://docs.gitlab.com/ee/ci/yaml/#when) attribute which decides when to run a job.
            Defaults to 'None', which means not set.
        allow_failure (bool, optional): The [allow_failure](https://docs.gitlab.com/ee/ci/yaml/#allow_failure) attribute which let a
            job fail without impacting the rest of the CI suite. Defaults to 'None', which means not set.
        changes (list[str]]): The [changes | None(https://docs.gitlab.com/ee/ci/yaml/#ruleschanges) attribute which adds a job
            to the pipeline by checking for changes on specific files
        exists (list[str]]): The [exists | None(https://docs.gitlab.com/ee/ci/yaml/#rulesexists) attribute which allows to run
            a job when a certain files exist in the repository
        variables (dict[str, str]]): The [variables | None(https://docs.gitlab.com/ee/ci/yaml/#rulesvariables) attribute allows
            defining or overwriting variables when the conditions are met
    """

    def __init__(
        self,
        *,
        if_statement: str | None = None,
        when: WhenStatement | None = None,
        allow_failure: bool | None = None,
        changes: list[str] | None = None,
        exists: list[str] | None = None,
        variables: dict[str, str] | None = None,
    ) -> None:
        self._if = if_statement
        self._changes = changes
        self._when = when
        self._exists = exists
        self._allow_failure = allow_failure
        self._variables = variables if variables is not None else {}

    def never(self) -> Rule:
        """
        This method returns a copy of this rule with the `when` attribute set to `WhenStatement.NEVER`.

        This method is intended to be used for predefined rules. For instance you have defined an
        often used rule `on_master` whose if statement checks if the pipeline is executed on branch
        `master`. Then you can either run a job, if on master...

        ```
        my_job.append_rules(on_master)
        ```

        ... or do not run a job if on master...

        ```
        my_job.append_rules(on_master.never())
        ```

        Returns:
            Rule: A new rule object with `when` set to `WhenStatement.NEVER`.
        """
        rule_copy = copy.deepcopy(self)
        rule_copy._when = WhenStatement.NEVER
        return rule_copy

    def add_variables(self, **variables: str) -> Rule:
        """
        Adds one or more [variables](https://docs.gitlab.com/ee/ci/yaml/#variables), each as keyword argument,
        to the rule.

        Args:
            **variables (str): Each variable would be provided as keyword argument:
        ```
        rule.add_variables(GREETING="hello", LANGUAGE="python")
        ```

        Returns:
            `Rule`: The modified `Rule` object.
        """
        self._variables.update(variables)
        return self

    def _equals(self, rule: Rule | None) -> bool:
        """
        Returns:
            bool: True if self equals to `rule`.
        """
        if not rule:
            return False

        return self.render() == rule.render()

    def render(self) -> dict[str, str | bool | list[str] | dict[str, str]]:
        """Return a representation of this Rule object as dictionary with static values.

        The rendered representation is used by the gcip to dump it
        in YAML format as part of the .gitlab-ci.yml pipeline.

        Returns:
            dict[str, Any]: A dictionary representing the rule object in Gitlab CI.
        """
        rendered_rule: dict[str, str | bool | list[str] | dict[str, str]] = {}
        if self._if:
            rendered_rule.update({"if": self._if})

        if self._changes:
            rendered_rule["changes"] = self._changes

        if self._exists:
            rendered_rule["exists"] = self._exists

        if self._variables:
            rendered_rule["variables"] = self._variables

        if self._allow_failure is not None:
            rendered_rule["allow_failure"] = self._allow_failure

        if self._when:
            rendered_rule["when"] = self._when.value

        return rendered_rule
