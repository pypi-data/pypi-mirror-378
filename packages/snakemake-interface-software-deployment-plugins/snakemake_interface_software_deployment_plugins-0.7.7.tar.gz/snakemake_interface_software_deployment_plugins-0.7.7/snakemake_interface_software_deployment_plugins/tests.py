from abc import ABC, abstractmethod
import asyncio
from copy import deepcopy
from typing import Optional, Type
import subprocess as sp

import pytest

from snakemake_interface_software_deployment_plugins import (
    CacheableEnvBase,
    DeployableEnvBase,
    EnvBase,
    EnvSpecBase,
    EnvSpecSourceFile,
    PinnableEnvBase,
    SoftwareReport,
)
from snakemake_interface_software_deployment_plugins.settings import (
    SoftwareDeploymentSettingsBase,
)


_TEST_SDM_NAME = "test-sdm"


class TestSoftwareDeploymentBase(ABC):
    __test__ = False
    shell_executable = ["bash", "-l", "-c"]

    @abstractmethod
    def get_env_spec(self) -> EnvSpecBase:
        """
        If the software deployment provider does not support deployable environments,
        this method should return args for an existing environment spec that can be used
        for testing
        """
        ...

    @abstractmethod
    def get_env_cls(self) -> Type[EnvBase]:
        """
        Return the environment class that should be tested.
        """
        ...

    @abstractmethod
    def get_test_cmd(self) -> str:
        """
        Return a test command that should be executed within the environment
        with exit code 0 (i.e. without error).
        """
        ...

    @abstractmethod
    def get_settings(
        self,
    ) -> Optional[SoftwareDeploymentSettingsBase]: ...

    @abstractmethod
    def get_settings_cls(self) -> Optional[Type[SoftwareDeploymentSettingsBase]]: ...

    def test_envspec_str(self):
        print("env spec", str(self.get_env_spec()))

    def test_default_settings(self):
        settings_cls = self.get_settings_cls()
        if settings_cls is None:
            pytest.skip("No settings class defined.")
        settings_cls()

    def test_shellcmd(self, tmp_path):
        env = self._get_env(tmp_path)

        if env.is_deployable():
            pytest.skip("Environment is deployable, using test_deploy instead.")

        cmd = self.get_test_cmd()
        decorated_cmd = env.managed_decorate_shellcmd(cmd)
        assert cmd != decorated_cmd
        assert (
            env.run_cmd(decorated_cmd).returncode == 0
        )

    def test_deploy(self, tmp_path):
        env = self._get_env(tmp_path)
        self._deploy(env, tmp_path)
        cmd = env.managed_decorate_shellcmd(self.get_test_cmd())
        assert env.run_cmd(cmd).returncode == 0

    def test_cache(self, tmp_path):
        env = self._get_env(tmp_path)
        if not env.is_cacheable():
            pytest.skip("Environment either not deployable or not cacheable.")

        assert isinstance(env, CacheableEnvBase)

        asyncio.run(env.cache_assets())

        self._deploy(env, tmp_path)

        assert any(env.cache_path.iterdir())

    def test_pin(self, tmp_path):
        env = self._get_env(tmp_path)
        if not env.is_pinnable():
            pytest.skip("Environment is not pinnable.")

        assert isinstance(env, PinnableEnvBase)

        asyncio.run(env.pin())
        assert env.pinfile.exists()
        print("Pinfile content:", env.pinfile.read_text(), sep="\n")
        self._deploy(env, tmp_path)

    def test_report_software(self, tmp_path):
        env = self._get_env(tmp_path)
        rep = env.report_software()
        assert all(isinstance(s, SoftwareReport) for s in rep)

    def test_identity_attributes(self):
        spec = self.get_env_spec()
        assert all(
            isinstance(attr, str) and hasattr(spec, attr)
            for attr in spec.identity_attributes()
        )

    def test_source_path_attributes(self):
        spec = self.get_env_spec()

        def is_source_file_or_none(attr: str) -> bool:
            val = getattr(spec, attr)
            return val is None or isinstance(val, EnvSpecSourceFile)

        assert all(
            isinstance(attr, str)
            and hasattr(spec, attr)
            and is_source_file_or_none(attr)
            for attr in spec.source_path_attributes()
        ), "bug in plugin: all source path attributes must be of type EnvSpecSourceFile"

    def _get_cached_env_spec(self):
        spec = deepcopy(self.get_env_spec())
        for attr in spec.source_path_attributes():
            source_file = getattr(spec, attr)
            if source_file is not None:
                source_file.cached = source_file.path_or_uri
        return spec

    def _get_env(self, tmp_path) -> EnvBase:
        env_cls = self.get_env_cls()
        spec = self._get_cached_env_spec()

        tempdir = tmp_path / "temp"
        deployment_prefix = tmp_path / "deployments"
        cache_prefix = tmp_path / "cache"
        pinfile_prefix = tmp_path / "pinfiles"
        tempdir.mkdir(parents=True, exist_ok=True)
        deployment_prefix.mkdir(parents=True, exist_ok=True)
        cache_prefix.mkdir(parents=True, exist_ok=True)
        pinfile_prefix.mkdir(parents=True, exist_ok=True)

        return env_cls(
            spec=spec,
            within=None,
            settings=self.get_settings(),
            shell_executable=self.shell_executable,
            tempdir=tempdir,
            deployment_prefix=deployment_prefix,
            cache_prefix=cache_prefix,
            pinfile_prefix=pinfile_prefix,
        )

    def _deploy(self, env: EnvBase, tmp_path):
        if not env.is_deployable():
            pytest.skip("Environment is not deployable.")

        assert isinstance(env, DeployableEnvBase)
        asyncio.run(env.deploy())
        assert any((tmp_path / "deployments").iterdir())
