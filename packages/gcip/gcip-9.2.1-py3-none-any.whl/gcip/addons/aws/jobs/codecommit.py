from dataclasses import dataclass, field
from typing import Any

from gcip.addons.git.jobs.git import Mirror
from gcip.addons.linux.scripts.package_manager import (
    install_packages,
)
from gcip.core.variables import PredefinedVariables


@dataclass(kw_only=True)
class MirrorToCodecommit(Mirror):
    """
    This job clones the CI_COMMIT_REF_NAME of the current repository and forcefully pushes this REF to a AWS CodeCommit repository.

    This job requires following IAM permissions:

        - codecommit:CreateRepository
        - codecommit:GetRepository
        - codecommit:CreateBranch
        - codecommit:GitPush
        - codecommit:TagResource

    You could also limit the resource to `!Sub arn:aws:codecommit:${AWS::Region}:${AWS::AccountId}:<repository-name>`.

    Args:
        repository_name (Optional str): The name of the target Codecommit repository. Defaults to CI_PROJECT_PATH_SLUG.
        aws_region (Optional str): The AWS region you want to operate in. When not set, it would be curl'ed from the current
            EC2 instance metadata.
        infrastructure_tags (Optional str): Only if the ECR would be created on the first call, these AWS Tags becomes applied to
          the AWS Codecommit resource. Changed values won't change the tags on an already existing ECR. This string must have the
          pattern: `Tag1=Value1,Tag2=Value2`
        mirror_opts (Optional[MirrorOpts]): Options for the upstream git.Mirror job.
    """

    # hide unnecessary fields from superclass
    run_only_for_repository_url: str | None = field(
        init=False
    )  # no Gitlab CI pipeline will run on Codecommit
    remote_repository: str = field(
        default="${GCIP_REMOTE_REPO_URL}", init=False
    )  # overwrite this field from the parent

    # custom fields
    repository_name: str | None = PredefinedVariables.CI_PROJECT_PATH_SLUG
    aws_region: str | None = None
    infrastructure_tags: str | None = None

    def render(self) -> dict[str, Any]:
        self.script_hook: list[str] = []

        infrastructure_tags_option = ""
        if self.infrastructure_tags:
            infrastructure_tags_option = f'--tags "{self.infrastructure_tags}"'

        if self.aws_region:
            self.script_hook.append(f"export AWS_DEFAULT_REGION={self.aws_region}")
        else:
            self.script_hook.extend(
                [
                    # To prevent the error 'curl: (48) An unknown option was passed in to libcurl'
                    # we install also "curl-dev".
                    # https://stackoverflow.com/a/41651363/1768273
                    install_packages("curl", "curl-dev", "jq"),
                    "export AWS_DEFAULT_REGION=$(curl --silent http://169.254.169.254/latest/dynamic/instance-identity/document | jq -r .region)",
                ]
            )

        get_repo_url_string = (
            f'GCIP_REMOTE_REPO_URL=$(aws codecommit get-repository --repository-name "{self.repository_name}" --output text'
            " --query repositoryMetadata.cloneUrlHttp"
            f' || aws codecommit create-repository --repository-name "{self.repository_name}" {infrastructure_tags_option} --output text'
            " --query repositoryMetadata.cloneUrlHttp)"
        )

        self.script_hook.extend(
            [
                install_packages("aws-cli"),
                get_repo_url_string,
                "git config --local credential.helper '!aws codecommit credential-helper $@'",
                "git config --local credential.UseHttpPath true",
            ]
        )
        return super().render()
