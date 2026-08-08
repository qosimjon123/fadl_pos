---
name: fadl-pos-frappe
description: Guides Fadl POS development with the imported OpenAEC Frappe/ERPNext skills. Use when working in frappe-bench/apps/fadl_pos, Frappe hooks, whitelisted APIs, DocTypes, permissions, custom fields, migrations, fixtures, client scripts, POS login, QR/token auth, bench commands, or tests.
---

# Fadl POS Frappe

## Use Imported Frappe Skills

This project imports the OpenAEC Frappe Claude Skill Package into `.cursor/skills/`.

Before implementing or reviewing Fadl POS work, load the relevant skills:

- Client-side form behavior: `frappe-syntax-clientscripts`, `frappe-impl-clientscripts`, `frappe-errors-clientscripts`.
- Whitelisted methods and API endpoints: `frappe-syntax-whitelisted`, `frappe-impl-whitelisted`, `frappe-core-api`, `frappe-errors-api`.
- Hooks, migrations, fixtures, and app structure: `frappe-syntax-hooks`, `frappe-syntax-hooks-events`, `frappe-impl-hooks`, `frappe-syntax-customapp`, `frappe-impl-customapp`.
- DocTypes, controllers, and lifecycle methods: `frappe-syntax-doctypes`, `frappe-syntax-controllers`, `frappe-impl-controllers`, `frappe-errors-controllers`.
- Database and permissions: `frappe-core-database`, `frappe-core-permissions`, `frappe-errors-database`, `frappe-errors-permissions`.
- Bench, deployment, and tests: `frappe-ops-bench`, `frappe-ops-app-lifecycle`, `frappe-testing-unit`, `frappe-testing-cicd`.

For the full catalog and routing guide, read `.cursor/reference/frappe-claude-skill-index.md`.

## Local Fadl POS Rules

- Fadl POS is migrating to an isolated-module template (Django-app-like): each functional area gets its own top-level `fadl_pos/<feature>/` package with hardcoded file names — `controller.py` (actions), `permission.py`, `serializer.py` (Pydantic v2, validators as `@field_validator` methods), `whitelist.py` (`@frappe.whitelist()` entry points), `events.py`, and (only when the feature has a real document-status machine) `workflow.py`. Shared primitives for all of these live in `fadl_pos/core/`. Not-yet-migrated features keep the older `api/<feature>.py` + `services/<feature>_service.py` + `schemas/{input,output}.py` layout. See `fadl_pos/login/` for the reference implementation of the new template.
- Keep Fadl POS changes inside `frappe-bench/apps/fadl_pos` unless the user explicitly asks to modify Frappe/ERPNext core.
- For core DocTypes like `User`, create Custom Fields from app code or use a linked custom DocType; do not rely on Customize Form.
- Put persistent schema/customization setup in app hooks, migrations, fixtures, or install/migrate helpers so it survives deploys.
- For whitelisted endpoints, validate inputs, enforce permissions, and return predictable JSON payloads.
- Never log or expose API secrets, PINs, decrypted QR payloads, `qr_encrypted_data`, or token material.
- Prefer focused `bench --site <site> ...` verification and tests after behavior changes.

## When Unsure

- Use `frappe-agent-interpreter` to clarify vague requests.
- Use `frappe-agent-debugger` for tracebacks, bench console inspection, and runtime failures.
- Use `frappe-agent-validator` before finalizing larger changes.
