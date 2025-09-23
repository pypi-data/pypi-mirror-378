from hpcflow.sdk import app as sdk_app
from hpcflow.sdk.config import ConfigOptions

from matflow._version import __version__


# provide access to app attributes:
__getattr__ = sdk_app.get_app_attribute

# ensure docs/help can see dynamically loaded attributes:
__all__ = sdk_app.get_app_module_all()
__dir__ = sdk_app.get_app_module_dir()

# set app-level config options:
config_options = ConfigOptions(
    directory_env_var="MATFLOW_CONFIG_DIR",
    default_directory="~/.matflow-new",
    default_known_configs_dir="github://hpcflow:matflow-configs@main",
)

# load built in template components:
template_components = sdk_app.App.load_builtin_template_component_data(
    "matflow.data.template_components"
)

# initialise the App object:
app: sdk_app.App = sdk_app.App(
    name="MatFlow",
    version=__version__,
    module=__name__,
    docs_import_conv="mf",
    description="Materials science workflow manager",
    gh_org="hpcflow",
    gh_repo="matflow-new",
    template_components=template_components,
    scripts_dir="data.scripts",  # relative to root package
    workflows_dir="data.workflows",  # relative to root package
    config_options=config_options,
    demo_data_dir="matflow.data.demo_data",
    demo_data_manifest_dir="matflow.data.demo_data_manifest",
    docs_url="https://docs.matflow.io/stable",
)  #: |app|

# defer import to allow us to use the app logger in the ParameterValue classes:
from matflow.param_classes import *
