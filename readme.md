# Mamoge flow

# 2. Contribute

The `settings.json` file for `vscode` is included in the repository for a minimum of common configuration rules. When using `vscode` this means that there are specific local configuration options that have to be adopted, since the GitHub pipeline will fail otherwise.

When *not* using `vscode`, please make sure that your editor supports a *"format on save"-ish* option. Also `pre-commit` should be utilized, see below.

## 2.1. Python linting and formatting

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

## 2.2. git pre-commits

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