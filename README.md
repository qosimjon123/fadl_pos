### Fadl Pos

POS for ERPNEXT developed by FadlTech team

API request/response contracts for functionality not yet migrated to the isolated module template live in `fadl_pos/schemas/` (Pydantic v2): `input.py` for RPC/query bodies, `output.py` for whitelist responses. Migrated functionality (e.g. `fadl_pos/login/`) keeps its own `serializer.py` instead — see `fadl_pos/core/` for the shared `controller.py`/`permission.py`/`serializer.py`/`workflow.py`/`events.py` module template.

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app fadl_pos
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/fadl_pos
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade
### CI

This app can use GitHub Actions for CI. The following workflows are configured:

- CI: Installs this app and runs unit tests on every push to `develop` branch.
- Linters: Runs [Frappe Semgrep Rules](https://github.com/frappe/semgrep-rules) and [pip-audit](https://pypi.org/project/pip-audit/) on every pull request.


### License

unlicense
