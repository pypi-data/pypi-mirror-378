import os
from dataclasses import InitVar, dataclass, field
from typing import Any

from gcip.addons.container.config import DockerClientConfig
from gcip.addons.container.images import PredefinedImages
from gcip.addons.container.registries import Registry
from gcip.core.job import Job
from gcip.core.variables import PredefinedVariables


@dataclass(kw_only=True)
class Copy(Job):
    """
    Creates a job to copy container images with `crane`.
    See [`crane`](https://github.com/google/go-containerregistry/tree/main/cmd/crane)

    Copying an image is usfull, if you want to have container images as close as possible
    to your cluster or servers.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: crane-copy
    * stage: deploy
    * image: PredefinedImages.CRANE

    Args:
        src_registry (str): Registry URL to copy container image from.
        dst_registry (str): Registry URL to copy container image to.
        docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
            used by crane to authenticate against given registries. Defaults to None.
    """

    src_registry: Registry | str
    src_repository: str = PredefinedVariables.CI_PROJECT_NAME
    src_tag: str | None = None
    dst_registry: Registry | str | None = None
    dst_repository: str | None = None
    dst_tag: str | None = None
    docker_client_config: DockerClientConfig | None = None
    jobName: InitVar[str] = "crane-copy"
    jobStage: InitVar[str] = "deploy"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.CRANE)

    def render(self) -> dict[str, Any]:
        if self.docker_client_config:
            self._scripts = self.docker_client_config.get_shell_command()
        else:
            self._scripts = []

        src_image_uri = f"{self.src_registry}/{self.src_repository}"
        if self.src_tag:
            src_image_uri += f":{self.src_tag}"

        dst_image_uri = (
            str(self.dst_registry) if self.dst_registry else str(self.src_registry)
        )
        if self.dst_repository:
            dst_image_uri += f"/{self.dst_repository}"
        else:
            dst_image_uri += f"/{self.src_repository}"

        if self.dst_tag:
            dst_image_uri += f":{self.dst_tag}"
        elif self.src_tag:
            dst_image_uri += f":{self.src_tag}"

        self._scripts.extend(
            [
                f"crane copy {src_image_uri} {dst_image_uri}",
            ]
        )

        return super().render()


@dataclass(kw_only=True)
class Push(Job):
    """
    Creates a job to push container image to remote container registry with `crane`.

    The image to copy must be in a `tarball` format. It gets validated with crane
    and is pushed to `dst_registry` destination registry.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: crane-push
    * stage: deploy
    * image: PredefinedImages.CRANE

    Args:
        dst_registry (str): Registry URL to copy container image to.
        tar_path (str | None, optional): Path where to find the container image tarball.
            If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_DIR`. Defaults to None.
        image_name (str | None, optional): Container image name, searched for in `image_path` and gets `.tar` appended.
            If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_NAME`. Defaults to None.
        image_tag (str | None): The tag the image will be tagged with.
            Defaults to `PredefinedVariables.CI_COMMIT_REF_NAME` or `PredefinedVariables.CI_COMMIT_TAG`.
        docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
            to authenticate against given registries. Defaults to a `DockerClientConfig` with login to the official Docker Hub
            and expecting credentials given as environment variables `REGISTRY_USER` and `REGISTRY_LOGIN`.
    """

    dst_registry: Registry | str
    tar_path: str = PredefinedVariables.CI_PROJECT_DIR
    image_name: str = PredefinedVariables.CI_PROJECT_NAME
    image_tag: str | None = None
    docker_client_config: DockerClientConfig = field(
        default_factory=lambda: DockerClientConfig().add_auth(registry=Registry.DOCKER)
    )
    jobName: InitVar[str] = "crane-push"
    jobStage: InitVar[str] = "deploy"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        if not self.image_tag:
            if PredefinedVariables.CI_COMMIT_TAG:
                self.image_tag = PredefinedVariables.CI_COMMIT_TAG
            else:
                self.image_tag = PredefinedVariables.CI_COMMIT_REF_NAME

        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.CRANE)

    def render(self) -> dict[str, Any]:
        image_path = self.image_name.replace("/", "_")

        self._scripts = self.docker_client_config.get_shell_command()
        self._scripts.extend(
            [
                f"crane push {self.tar_path}/{image_path}.tar {self.dst_registry}/{self.image_name}:{self.image_tag}",
            ]
        )

        if self.image_tag in ["main", "master"]:
            self._scripts.append(
                f"crane push {self.tar_path}/{image_path}.tar {self.dst_registry}/{self.image_name}:latest"
            )

        return super().render()


@dataclass(kw_only=True)
class Pull(Job):
    """
    Creates a job to pull container image from remote container registry with `crane`.

    This subclass of `Job` will configure following defaults for the superclass:

    * name: crane
    * stage: pull
    * image: PredefinedImages.CRANE

    Args:
        src_registry (str): Registry URL to pull container image from.
        image_name (str): Container image with namespace to pull from `src_registry`.
            If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_NAME`. Defaults to None.
        image_tag (str): Tag of the image which will be pulled. Defaults to "latest".
        tar_path (str | None, optional): Path where to save the container image tarball.
            If `None` it defaults internally to `PredefinedVariables.CI_PROJECT_DIR`. Defaults to None.
        docker_client_config (Optional[DockerClientConfig], optional): Creates the Docker configuration file base on objects settings,
            to authenticate against given registries. Defaults to a `DockerClientConfig` with login to the official Docker Hub
            and expecting credentials given as environment variables `REGISTRY_USER` and `REGISTRY_LOGIN`.
    """

    src_registry: Registry | str
    image_name: str = PredefinedVariables.CI_PROJECT_NAME
    image_tag: str = "latest"
    tar_path: str = PredefinedVariables.CI_PROJECT_DIR
    docker_client_config: DockerClientConfig = field(
        default_factory=lambda: DockerClientConfig().add_auth(registry=Registry.DOCKER)
    )
    jobName: InitVar[str] = "crane"
    jobStage: InitVar[str] = "pull"

    def __post_init__(self, jobName: str, jobStage: str) -> None:
        super().__init__(script="", name=jobName, stage=jobStage)
        self.set_image(PredefinedImages.CRANE)

    def render(self) -> dict[str, Any]:
        image_path = self.image_name.replace("/", "_")

        self._scripts = self.docker_client_config.get_shell_command()

        self._scripts.extend(
            [
                f"mkdir -p {os.path.normpath(self.tar_path)}",
                f"crane pull {self.src_registry}/{self.image_name}:{self.image_tag} {self.tar_path}/{image_path}.tar",
            ]
        )
        return super().render()
