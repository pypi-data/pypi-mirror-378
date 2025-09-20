from dataclasses import dataclass


import snakemake_interface_common.plugin_registry.plugin


@dataclass
class SoftwareDeploymentSettingsBase(
    snakemake_interface_common.plugin_registry.plugin.SettingsBase
):
    """Base class for software deployment settings.

    Software deployment plugins can define a subclass of this class,
    named 'SoftwareDeploymentProviderSettings'.
    """

    pass


@dataclass
class CommonSettings:
    """Common settings for software deployment plugins.

    This class is used to define common settings for software deployment plugins.

    Attributes
    ----------
    provides : str
        The kind of the software environment provided (e.g. conda, container).
        This should not return something describing the tool to provide the software
        environment but the resulting environment itself. For example,
        it should return "conda" instead of mamba, rattler, pixi etc., or
        "container" instead of docker, singularity, podman, or
        "envmodules" instead of lmod, environment-modules, etc.
        Snakemake will ensure that the user only activates one plugin per provided
        kind.
    """

    provides: str

    def __post_init__(self):
        if not self.provides.isidentifier():
            raise ValueError(
                "CommonSettings.provides must be a valid Python identifier, but "
                f"is {self.provides}."
            )
