# Low-Code Flow-Programming Tool for Event-Driven Systems

This is a customization overlay for [PyFlow](https://wonderworks-software.github.io/PyFlow/) ([GitHub](https://github.com/wonderworks-software/PyFlow)) used in the *VeBaS-UAV* project.

## Setup

Install the package via
```console
pip install -e .
```

Set the following environment variables (see below for alternative startup with e.g. vscode):
- `ROBINSON_WS`: path to `/vebas/app/target_based/`
- `ROBINSON_NS`: namespace for the mqtt topics to work with`"vebas/seedling_detection/channel_1"`
- `ROBINSON_MODE`: name of the environment configuration in `vebas/app/target_based/config.yaml`

e.g.:
```console
export ROBINSON_WS=/home/ubuntu/projects/vebas/app/target_based/
export ROBINSON_NS="vebas/seedling_detection/channel_1"
export ROBINSON_MODE="dev-airsim-ssh"
```

Start the application via
```console
robinson-flow
```

**Alternative for vscode:**

start the `__main__.py` with below configuration in the `launch.json`
```json
"env": {
    "ROBINSON_WS": "/home/ubuntu/projects/vebas/app/target_based/",
    "ROBINSON_NS": "vebas/seedling_detection/channel_1",
    "ROBINSON_MODE": "dev-airsim-ssh",
}
```

## Set Up User Interface
After first start of the application some configuration has to be done.

To include the packages for your project go to 
<kbd>Edit</kbd> > <kbd>Preferences</kbd>

- in **Additional Package Locations** fill in the path of the resources. In case of Vebas e.g.: `/home/ubuntu/projects/robinson_flow/robinson_flow/pyflow_nodes`

- Press <kbd>SaveAndClose</kbd> and **restart** the application.

From the top menu select: <kbd>Tools</kbd> > <kbd>PyFlowBase</kbd> and open the folowing panels
- <kbd>Nodebox</kbd>
- <kbd>Properties</kbd>

From the top menu open the *RobinsonDockTools* panel:
<kbd>Tools</kbd> > <kbd>Robinson</kbd> > <kbd>RobinsonDockTools</kbd>


### Export

Export flow graphs from the top menu <kbd>File</kbd> > <kbd>CustomIO</kbd> > <kbd>Robinson</kbd> > <kbd>Robinson Exporter</kbd> > <kbd>Export</kbd>

The export generates the following files:

- `<flowname>.pygraph.py`

    Actual python script that is executed when the flow graph is executed.

- `<flowname>.pygraph`

    Configuration file.

- `<flowname>.pygraph.yaml`

    Use a `pygraph.local.yaml` for specialised settings that are only for the current workspace.

# Contribute

A `settings.json` file for `vscode` is included in the repository *for a minimum of common configuration rules*. When using `vscode` this means that there are specific local configuration options that have to be adopted, since the GitHub pipeline will fail otherwise.

When *not* using `vscode`, please make sure that your editor supports a *"format on save"-ish* option. Also `pre-commit` should be utilized, see below.

## Python linting and formatting

The following packages are **mandatory**:
- `black`

The following packages are recommended:
- `bandit`
- `flake8`
- `pycodestyle`
- `pydocstyle`

All of them will be installed through adopting the packages in `requirements.txt` (activated vebas environment assumed).
```console
pip install -r requirements.txt
```

## git pre-commits

[See the official tutorial for a general introduction](https://pre-commit.com/index.html#intro) on `pre-commit`. We utilize `pre-commit` to ensure that all code that is pushed to the repository follows certain code quality rules.

As of now this is only for Python code. The rules are set by `black`, [see the official documentation](https://github.com/psf/black) for more detal.

The `pre-commit` configuration (`.pre-commit-config.yaml`) has already been added to the project repository. Run the following line to use it:
```console
pre-commit install
```
> `pre-commit installed at .git/hooks/pre-commit`

Now `pre-commit` will run automatically on `git commit`.

You can check if it is working and also initialize the first use by running the following command in the project root:
```console
pre-commit run --all-files
```
> `All done! ✨ 🍰 ✨`

# License Acknowledgement

The original PyFlow was released unter Apache License 2.0
https://github.com/wonderworks-software/PyFlow/blob/master/LICENSE