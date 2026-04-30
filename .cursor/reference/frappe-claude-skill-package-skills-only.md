---
name: frappe-agent-architect
description: >
  Use when designing multi-app Frappe architectures, deciding whether to split functionality into separate apps, or implementing cross-app communication patterns.
  Prevents monolithic app sprawl, circular dependencies between apps, and broken override chains.
  Covers multi-app architecture decisions, app dependency management, cross-app hooks, override patterns, when to split vs extend, shared DocType strategies.
  Keywords: architecture, multi-app, app splitting, cross-app, dependencies, override, extend, monolith, modular, how to structure frappe apps, when to split apps, app design, multi-app planning..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Multi-App Architecture Agent

Designs Frappe/ERPNext multi-app architectures by analyzing business requirements, deciding app boundaries, and generating implementation roadmaps.

**Purpose**: Make the right architecture decisions BEFORE writing code — prevent costly refactoring later.

## When to Use This Agent

```
ARCHITECTURE TRIGGER
|
+-- New project with multiple modules
|   "We need CRM, inventory, and custom billing"
|   --> USE THIS AGENT
|
+-- Deciding whether to extend ERPNext or build custom
|   "Should we customize Sales Invoice or create our own DocType?"
|   --> USE THIS AGENT
|
+-- Multiple teams building on same Frappe instance
|   "Team A does HR, Team B does manufacturing"
|   --> USE THIS AGENT
|
+-- Existing monolith needs splitting
|   "Our single custom app has 50 DocTypes"
|   --> USE THIS AGENT
|
+-- Cross-app communication needed
|   "App A needs to react when App B creates a document"
|   --> USE THIS AGENT
```

## Architecture Workflow

```
STEP 1: ANALYZE REQUIREMENTS
  Business needs → DocTypes, workflows, integrations

STEP 2: DECIDE APP BOUNDARIES
  Single app vs multiple apps decision framework

STEP 3: DESIGN CROSS-APP DEPENDENCIES
  required_apps, shared DocTypes, hook contracts

STEP 4: DESIGN DATA MODEL
  DocTypes, relationships, naming conventions

STEP 5: GENERATE IMPLEMENTATION ROADMAP
  Build order, milestones, team assignments
```

See [references/workflow.md](references/workflow.md) for detailed steps.

## Step 1: Requirement Analysis Matrix

Map each business requirement to Frappe mechanisms:

| Requirement Type | Frappe Mechanism | Example |
|-----------------|-----------------|---------|
| Data storage | DocType | "Track customer contracts" |
| Business rules | Controller/Server Script | "Auto-calculate totals" |
| Approval flow | Workflow | "Manager must approve orders >10k" |
| Scheduled tasks | Scheduler/hooks.py | "Daily report email" |
| External sync | Integration/API | "Sync with Shopify" |
| Custom UI | Client Script/Page | "Dashboard for warehouse" |
| Reports | Script Report/Query Report | "Monthly sales by region" |
| Permissions | Role Permission | "Sales team sees own data only" |
| Print output | Print Format (Jinja) | "Custom invoice layout" |
| Portal access | Website/Portal | "Customer can view orders" |

## Step 2: App Boundary Decision Framework

### Single App: Use When

- Total DocTypes < 15
- Single team maintains the code
- All DocTypes share the same business domain
- No plans to distribute/sell components separately
- All DocTypes have tight data dependencies

### Multiple Apps: Use When

- Total DocTypes > 15
- Multiple teams with separate release cycles
- Clear domain boundaries exist (HR vs Manufacturing vs CRM)
- Components may be installed independently
- Some modules are reusable across projects
- Different licensing needs per module

### Decision Tree

```
HOW MANY DOCTYPES?
|
+-- < 15 total
|   +-- Single domain? --> SINGLE APP
|   +-- Multiple domains? --> Consider splitting
|
+-- 15-30 total
|   +-- Tight coupling between all? --> SINGLE APP (with modules)
|   +-- Clear domain boundaries? --> 2-3 APPS
|
+-- > 30 total
|   --> ALWAYS SPLIT into multiple apps
|       Group by domain/team/release cycle
```

See [references/decision-tree.md](references/decision-tree.md) for the complete decision framework.

## Step 3: Cross-App Dependency Patterns

### required_apps Declaration

ALWAYS declare dependencies explicitly in `hooks.py`:

```python
# myapp/hooks.py
required_apps = ["frappe", "erpnext"]  # NEVER omit frappe
```

### Dependency Rules

- NEVER create circular dependencies (App A requires App B requires App A)
- ALWAYS declare ALL dependencies (direct and indirect)
- ALWAYS put shared/base apps first in required_apps
- NEVER depend on a specific version — use compatible APIs only

### Dependency Diagram Pattern

```
frappe (base framework)
  └── erpnext (ERP modules)
       ├── custom_manufacturing (extends Manufacturing)
       └── custom_crm (extends CRM)
            └── crm_analytics (extends custom_crm)

RULE: Dependencies flow DOWN only. Never up, never sideways.
```

### Cross-App Communication Patterns

| Pattern | Mechanism | Use When |
|---------|-----------|----------|
| **Hook Events** | `doc_events` in hooks.py | App B reacts to App A's documents |
| **Shared DocType** | Link fields to other app's DocTypes | Apps share reference data |
| **API Call** | `frappe.call()` to whitelisted method | Loose coupling between apps |
| **Custom Fields** | `fixtures` with Custom Field | Extend another app's DocType without modifying it |
| **Override** | `extend_doctype_class` (v16) or `doc_events` | Modify another app's behavior |
| **Signals** | `frappe.publish_realtime()` | Real-time notifications between apps |

## Step 4: Data Model Design

### DocType Relationship Types

| Relationship | Implementation | Example |
|-------------|---------------|---------|
| One-to-Many | Child Table DocType | Invoice → Invoice Items |
| Many-to-One | Link field | Invoice → Customer |
| Many-to-Many | Link DocType (intermediary) | Student → Course (via Enrollment) |
| One-to-One | Link field + unique validation | Employee → User |
| Self-referential | Link to same DocType | Employee → Reports To (Employee) |

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| App name | lowercase, underscores | `custom_manufacturing` |
| DocType name | Title Case, spaces | `Production Order` |
| Field name | lowercase, underscores | `production_date` |
| Controller | snake_case filename | `production_order.py` |
| Module | Title Case | `Manufacturing` |

### Data Model Rules

- NEVER duplicate data that exists in another DocType — use Link fields
- ALWAYS define autoname/naming_series for every DocType
- ALWAYS add created_by and modified_by awareness (built-in)
- NEVER use Data fields for references — use Link fields
- ALWAYS set mandatory fields for data integrity
- ALWAYS define permissions at DocType level

## App Composition Patterns

### Pattern 1: Base + Vertical

```
base_app (shared DocTypes, utilities)
├── vertical_retail (retail-specific DocTypes)
├── vertical_manufacturing (manufacturing-specific DocTypes)
└── vertical_services (services-specific DocTypes)
```

**Use when**: Building industry-specific solutions on shared foundation.

### Pattern 2: Core + Extensions

```
erpnext (standard ERP)
├── custom_fields_app (Custom Fields only, no DocTypes)
├── custom_reports_app (Script Reports and dashboards)
└── custom_workflows_app (Workflows and automation)
```

**Use when**: Extending ERPNext without modifying core. Keeps upgrades clean.

### Pattern 3: Shared Utilities

```
frappe_utils (shared library: PDF generation, email templates, etc.)
├── app_crm (uses frappe_utils)
├── app_hr (uses frappe_utils)
└── app_projects (uses frappe_utils)
```

**Use when**: Multiple apps need the same utility functions.

### Pattern 4: Marketplace App

```
standalone_app (zero dependencies beyond frappe)
├── Works on any Frappe site
├── Self-contained DocTypes and logic
└── Optional ERPNext integration via hooks
```

**Use when**: Building for distribution/sale on Frappe marketplace.

## ERPNext Extension Patterns

### Custom Fields vs Custom DocTypes vs Override

| Approach | Use When | Pros | Cons |
|----------|----------|------|------|
| **Custom Fields** | Adding 1-10 fields to existing DocType | Survives upgrades, no code | Limited logic, UI clutter |
| **Custom DocType** | New business entity not in ERPNext | Full control, clean design | No built-in ERPNext logic |
| **Controller Override** | Modifying existing ERPNext behavior | Full Python access | Fragile on upgrades |
| **Server Script** | Simple validation/automation | No custom app needed | Sandbox limitations |
| **Client Script** | UI customization | No custom app needed | JS only, no server logic |

### Extension Decision Rules

- ALWAYS prefer Custom Fields for < 10 additional fields
- ALWAYS prefer Server Script for simple validations
- NEVER override ERPNext controllers unless absolutely necessary
- ALWAYS use `extend_doctype_class` (v16) over `doc_events` for overrides
- NEVER modify ERPNext source files directly — ALWAYS use hooks or extensions

## Common Architecture Mistakes

| Mistake | Why It Fails | Correct Approach |
|---------|-------------|-----------------|
| Circular app dependencies | Install/update breaks | Restructure dependency tree |
| One mega-app with 50+ DocTypes | Unmaintainable, slow tests | Split by domain into 3-5 apps |
| Duplicating ERPNext DocTypes | Data inconsistency, double maintenance | Extend with Custom Fields + hooks |
| No `required_apps` declaration | Silent failures on fresh install | ALWAYS declare all dependencies |
| Shared database tables between apps | Tight coupling, migration conflicts | Use Link fields and API calls |
| Modifying ERPNext source files | Lost on every upgrade | Use hooks, Custom Fields, extensions |
| No module organization within app | Files scattered, hard to navigate | Group DocTypes into modules |
| Hardcoded site/company names | Breaks on multi-site/multi-company | Use `frappe.defaults` and filters |

## Agent Output Format

ALWAYS produce architecture output in this format:

```markdown
## Architecture Design

### Requirements Summary
| # | Requirement | DocTypes | Mechanism |
|---|------------|----------|-----------|

### App Structure
[Diagram showing apps and dependencies]

### App Inventory
| App | Module(s) | DocTypes | Dependencies |
|-----|-----------|----------|-------------|

### Data Model
| DocType | App | Key Fields | Relationships |
|---------|-----|------------|---------------|

### Cross-App Communication
| Source App | Target App | Mechanism | Trigger |
|-----------|-----------|-----------|---------|

### ERPNext Extensions
| Extension Type | Target DocType | Purpose |
|---------------|---------------|---------|

### Implementation Roadmap
| Phase | App(s) | Deliverables | Dependencies |
|-------|--------|-------------|-------------|

### Risk Assessment
| Risk | Mitigation |
|------|-----------|

### Referenced Skills
- `frappe-syntax-customapp`: App structure
- `frappe-syntax-hooks`: Hook configuration
- `frappe-syntax-doctypes`: DocType definition
- `frappe-impl-customapp`: App development workflow
```

See [references/decision-tree.md](references/decision-tree.md) for complete decision frameworks.
See [references/examples.md](references/examples.md) for architecture design examples.
---
name: frappe-agent-debugger
description: >
  Use when debugging Frappe errors, using bench console for live inspection, analyzing tracebacks, or reading Frappe log files.
  Prevents wasted debugging time from ignoring log context, misreading tracebacks, and not using bench console effectively.
  Covers bench console, frappe.logger, error log DocType, traceback analysis, common error patterns, log file locations, pdb/debugger integration, VS Code DAP, profiling, Frappe Recorder, mariadb diagnostics.
  Keywords: debug, bench console, traceback, error log, frappe.logger, pdb, debugging, log analysis, inspect, VS Code, DAP, profiling, recorder, mariadb, monitor, ERPNext error, how to debug, find the bug, what went wrong, stack trace, error message..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Debugging Agent

Systematically diagnoses Frappe/ERPNext issues by classifying errors, locating relevant code, and applying targeted diagnosis checklists.

**Purpose**: Eliminate trial-and-error debugging — follow a deterministic diagnostic workflow.

## When to Use This Agent

```
ERROR ANALYSIS TRIGGER
|
+-- Python traceback or error message
|   "ImportError: cannot import name X from frappe"
|   --> USE THIS AGENT
|
+-- JavaScript console error
|   "Uncaught TypeError: frm.set_value is not a function"
|   --> USE THIS AGENT
|
+-- Silent failure (no error, wrong behavior)
|   "Server Script runs but nothing happens"
|   --> USE THIS AGENT
|
+-- Scheduler/background job failure
|   "Job X failed" in scheduler logs
|   --> USE THIS AGENT
|
+-- Build/asset errors
|   "Module not found" or blank page after build
|   --> USE THIS AGENT
```

## Debugging Workflow

```
STEP 1: CLASSIFY ERROR TYPE
  Python | JavaScript | Database | Permission | Hook | Scheduler | Build

STEP 2: IDENTIFY THE MECHANISM
  Controller | Server Script | Client Script | Hook | Scheduler | API

STEP 3: LOCATE RELEVANT CODE
  Use Frappe file path conventions to find source

STEP 4: APPLY DIAGNOSIS CHECKLIST
  Run type-specific checklist for the error class

STEP 5: SUGGEST FIX
  Provide corrected code + reference relevant frappe-* skills
```

See [references/workflow.md](references/workflow.md) for detailed steps.

## Step 1: Error Classification

| Error Type | Indicators | Primary Tool |
|------------|-----------|--------------|
| **Python** | Traceback with `.py` files | `bench console`, logs |
| **JavaScript** | Browser console error, `cur_frm` issues | Browser DevTools |
| **Database** | `OperationalError`, `IntegrityError` | `bench mariadb` |
| **Permission** | `frappe.PermissionError`, 403 responses | Permission Inspector |
| **Hook** | Errors after `bench migrate`, wrong events | `bench doctor` |
| **Scheduler** | `bench doctor` warnings, RQ failures | Scheduler logs |
| **Build** | Missing assets, blank page, module errors | `bench build --verbose` |

## Step 2: Mechanism Identification

| Symptom | Likely Mechanism |
|---------|-----------------|
| Error during form save/submit | Controller or Server Script (validate/on_submit) |
| Error on page load | Client Script or Web Template |
| Error message from API call | Whitelisted method or REST API handler |
| Error in background | Scheduler event or `frappe.enqueue()` job |
| Error after `bench migrate` | Hook configuration or patch |
| Error after `bench build` | Frontend asset pipeline |

## Step 3: File Path Conventions

ALWAYS check these locations based on the mechanism:

| Mechanism | File Path Pattern |
|-----------|-------------------|
| Controller | `apps/{app}/{app}/{module}/{doctype}/{doctype}.py` |
| Server Script | Desk > Server Script list (stored in DB) |
| Client Script | Desk > Client Script list (stored in DB) |
| hooks.py | `apps/{app}/{app}/hooks.py` |
| Scheduler | `apps/{app}/{app}/tasks.py` or hooks.py `scheduler_events` |
| Whitelisted | `apps/{app}/{app}/{module}/*.py` (search for `@frappe.whitelist`) |
| Jinja | `apps/{app}/{app}/templates/` |
| Patches | `apps/{app}/{app}/patches/` |

## Step 4: Diagnosis Checklists (Quick Reference)

### Python Errors

| Error Pattern | Likely Cause | Fix |
|---------------|-------------|-----|
| `AttributeError: 'NoneType'` | `frappe.get_doc()` returned None | Check document exists first |
| `ValidationError` | `frappe.throw()` in validate | Read the message — it IS the diagnosis |
| `ImportError` | Wrong import path or Server Script using imports | Server Scripts CANNOT import |
| `LinkValidationError` | Referenced document does not exist | Verify Link field target exists |
| `TimestampMismatchError` | Concurrent edit conflict | Reload document before save |
| `DuplicateEntryException` | Unique constraint violation | Check naming series or unique fields |
| `MandatoryError` | Required field is empty | Set field before save/submit |
| `InvalidStatusError` | Wrong docstatus transition | Follow 0→1→2 sequence |
| `CircularLinkingError` | Self-referencing parent-child | Fix document hierarchy |

### JavaScript Errors

| Error Pattern | Likely Cause | Fix |
|---------------|-------------|-----|
| `frm.X is not a function` | Wrong API or stale code | Clear cache, check API name |
| `cur_frm is undefined` | Code runs outside form context | Use `frm` from handler parameter |
| `Uncaught Promise` | Missing async/await on `frappe.call` | Add callback or await |
| `field undefined` in `frm.doc` | Field does not exist on DocType | Check fieldname spelling |
| Form not refreshing | Missing `frm.refresh_fields()` | Add refresh after `set_value` |

### Database Errors

| Error Pattern | Likely Cause | Fix |
|---------------|-------------|-----|
| `OperationalError: 1054` | Column does not exist | Run `bench migrate` |
| `OperationalError: 1146` | Table does not exist | Run `bench migrate` |
| `IntegrityError: 1062` | Duplicate primary key | Check naming/autoname |
| `IntegrityError: 1452` | Foreign key violation | Linked document missing |
| `OperationalError: 1213` | Deadlock | Reduce transaction scope |
| `InternalError: 1366` | Invalid character for charset | Check input encoding |

### Permission Errors

| Error Pattern | Likely Cause | Fix |
|---------------|-------------|-----|
| `frappe.PermissionError` | User lacks role permission | Check Role Permission Manager |
| 403 on API call | Missing `frappe.has_permission()` or wrong `@frappe.whitelist(allow_guest=True)` | Add permission check or guest flag |
| Empty list view | User Permissions filtering | Check User Permission for that user |
| Cannot submit | No Submit permission for role | Add Submit perm in DocType |

## Debug Tools

### bench console (Python REPL)
```bash
bench --site {site} console
# Then:
frappe.get_doc("Sales Invoice", "SINV-00001")  # Inspect document
frappe.db.sql("SELECT name FROM `tabSales Invoice` LIMIT 5")  # Raw SQL
frappe.get_hooks("doc_events")  # Inspect active hooks
frappe.get_all("Server Script", filters={"disabled": 0}, fields=["name", "script_type"])
```

### bench mariadb (SQL shell)
```bash
bench --site {site} mariadb
-- Then:
SHOW CREATE TABLE `tabSales Invoice`;
SELECT * FROM `tabError Log` ORDER BY creation DESC LIMIT 10;
```

### bench doctor
```bash
bench doctor  # Check scheduler, workers, background jobs
```

### frappe.logger()
```python
logger = frappe.logger("my_debug", allow_site=True)
logger.info(f"Variable value: {my_var}")
# Logs to: sites/{site}/logs/my_debug.log
```

### Browser DevTools
```
Console tab  → JavaScript errors
Network tab  → Failed API calls (check response body for traceback)
Application tab → Session/cookie issues
```

## Log File Locations

| Log | Path | Contains |
|-----|------|----------|
| Frappe web | `sites/{site}/logs/frappe.log` | Web request errors |
| Worker | `sites/{site}/logs/worker.log` | Background job errors |
| Scheduler | `sites/{site}/logs/scheduler.log` | Scheduled task output |
| Custom logger | `sites/{site}/logs/{name}.log` | `frappe.logger("{name}")` output |
| Bench | `~/.bench/logs/bench.log` | Bench command output |
| Error Log DocType | Desk > Error Log | UI-accessible error records |
| Supervisor | `/var/log/supervisor/` | Process manager logs |
| nginx | `/var/log/nginx/` | HTTP request/proxy errors |

## Common Error Patterns Table

| Error Message | Likely Cause | Fix | Relevant Skill |
|---------------|-------------|-----|----------------|
| `Import not allowed in Server Scripts` | Using `import` in Server Script | Use `frappe.utils.*` or move to Controller | `frappe-errors-serverscripts` |
| `Cannot read properties of undefined` | JS accessing field before form load | Add `frm.doc.field` null check | `frappe-errors-clientscripts` |
| `DocType X not found` | Missing app install or migration | `bench migrate` or `bench install-app` | `frappe-ops-bench` |
| `Scheduler is not running` | Workers stopped | `bench doctor`, restart workers | `frappe-ops-bench` |
| `BrokenPipeError` | gunicorn timeout on long operation | Use `frappe.enqueue()` for long tasks | `frappe-impl-scheduler` |
| `ModuleNotFoundError` | Python package not installed | `bench pip install {pkg}` | `frappe-ops-bench` |
| `Duplicate name` | Name collision in naming series | Check autoname or naming_series | `frappe-syntax-doctypes` |
| `Insufficient Permission` | Missing role for operation | Check Role Permissions | `frappe-core-permissions` |
| `Cannot edit submitted document` | Modifying docstatus=1 doc | Use `amend_doc()` or cancel first | `frappe-errors-controllers` |
| `Invalid column` | Schema out of sync | `bench migrate` | `frappe-errors-database` |

## Agent Output Format

ALWAYS produce debugging output in this format:

```markdown
## Debug Report

### Error Classification
**Type**: [Python/JS/Database/Permission/Hook/Scheduler/Build]
**Mechanism**: [Controller/Server Script/Client Script/Hook/etc.]

### Root Cause
[One-sentence diagnosis]

### Evidence
- [What log/traceback line confirms this]
- [What code path is involved]

### Fix
[Corrected code or configuration change]

### Verification Steps
1. [How to confirm the fix works]
2. [What to check in logs/UI]

### Referenced Skills
- `frappe-*`: [what was consulted]
```

## Debugging Decision Tree

```
ERROR RECEIVED
|
+-- Has traceback?
|   +-- YES: Read LAST line first (actual error)
|   |   +-- Contains ".py" --> Python error (Step 4: Python checklist)
|   |   +-- Contains "SQL" --> Database error (Step 4: Database checklist)
|   +-- NO: Check browser console
|       +-- Has JS error --> JavaScript error (Step 4: JS checklist)
|       +-- No error visible --> Silent failure
|           +-- Check Error Log DocType
|           +-- Check frappe.log
|           +-- Add frappe.logger() statements
|
+-- Error after bench command?
|   +-- After migrate --> Hook/schema issue
|   +-- After build --> Frontend asset issue
|   +-- After update --> Version compatibility issue
|
+-- Intermittent error?
    +-- Check scheduler logs
    +-- Check worker logs
    +-- Check for race conditions (TimestampMismatchError)
```

See [references/checklists.md](references/checklists.md) for complete diagnosis checklists.
See [references/examples.md](references/examples.md) for debugging walkthrough examples.
See [references/advanced-debugging.md](references/advanced-debugging.md) for VS Code DAP setup, bench console patterns, mariadb diagnostics, and profiling tools.
---
name: frappe-agent-interpreter
description: >
  Use when receiving vague or unclear ERPNext/Frappe development requests
  that need interpretation. Transforms requirements like 'make invoice
  auto-calculate' or 'add approval workflow' into concrete technical
  specifications. Determines which Frappe mechanisms to use and maps to
  the full 61-skill catalog. Keywords: vague requirement, clarify scope,
  translate business need, technical spec, implementation plan,
  what does this mean, unclear requirement, translate to code, how to build this.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Code Interpreter Agent

Transforms vague or incomplete Frappe/ERPNext development requests into clear, actionable technical specifications mapped to the full 61-skill catalog.

**Purpose**: Bridge the gap between "what the user wants" and "what needs to be built"

## When to Use This Agent

```
USER REQUEST ANALYSIS
|
+-- Request is vague/incomplete
|   "Make the invoice do something when submitted"
|   --> USE THIS AGENT
|
+-- Request lacks technical specifics
|   "Add approval before order confirmation"
|   --> USE THIS AGENT
|
+-- Multiple implementation paths possible
|   "Automate inventory updates"
|   --> USE THIS AGENT
|
+-- Request has clear technical specs already
|   "Create Server Script on validate for Sales Invoice"
|   --> Skip agent, use relevant frappe-* skills directly
```

## Interpretation Workflow

```
STEP 1: EXTRACT INTENT
  - What is the business problem?
  - What should happen? When? To what data?
  - Who should be affected (roles/users)?

STEP 2: IDENTIFY TRIGGER CONTEXT
  - Document lifecycle event? (save/submit/cancel)
  - User action? (button click, field change)
  - Time-based? (daily, hourly, cron)
  - External event? (webhook, API call)

STEP 3: DETERMINE MECHANISM
  - Client Script, Server Script, or Controller?
  - Hooks configuration needed?
  - Custom app required?
  - v16 extend_doctype_class applicable?

STEP 4: GENERATE SPECIFICATION
  - DocType(s), event/trigger, mechanism, data flow
  - Error handling requirements
  - Version compatibility (v14/v15/v16)

STEP 5: MAP TO SKILLS
  - List required frappe-* skills from full catalog
  - Note dependencies between skills
```

See [references/workflow.md](references/workflow.md) for detailed steps.

## Mechanism Selection Matrix

| Requirement Pattern | Mechanism | Custom App? |
|---------------------|-----------|:-----------:|
| "Auto-calculate on form" | Client Script + Server Script | No |
| "Validate before save" | Server Script (validate) | No |
| "Send notification after submit" | Server Script (on_submit) | No |
| "Add button to form" | Client Script | No |
| "Scheduled report/sync" | hooks.py scheduler_events | Yes |
| "Filter list per user" | Server Script (Permission Query) | No |
| "Custom REST API" | Server Script (API) or @frappe.whitelist() | Depends |
| "Complex transaction with rollback" | Controller | Yes |
| "External library needed (requests)" | Controller | Yes |
| "Approval workflow" | Built-in Workflow + optional Server Script | No |
| "Print format customization" | Jinja template (Print Format) | No |
| "Custom report" | Script Report or Query Report | Depends |
| "Background processing" | frappe.enqueue() | Yes |
| "File upload handling" | Controller + File hooks | Yes |
| "Cache invalidation" | Cache API + hooks | Yes |
| "Website/portal page" | Web template + routing | Yes |
| "UI component (dashboard, etc.)" | Page or Custom Page | Yes |

## Clarifying Questions Framework

### 1. WHAT Questions
- What DocType(s) are involved?
- What data needs to change?
- What should the outcome be?

### 2. WHEN Questions
- On form load? On field change? Before/after save?
- Before/after submit? On a schedule? Button click?

### 3. WHO Questions
- All users? Specific roles? Document owner only?

### 4. WHERE Questions
- In the form (UI)? Database only? Report? External system?

### 5. ERROR Questions
- Block the operation? Show warning? Log silently?

### 6. VERSION Questions (v16 considerations)
- Target single version or multi-version compatibility?
- Can we use `extend_doctype_class` (v16) or need `doc_events` (v14+)?
- Type annotations desired? (v16 best practice)

## Output Specification Template

ALWAYS generate specifications in this format:

```markdown
## Technical Specification

### Summary
[One sentence describing what will be built]

### Business Requirement
[Original user request, clarified]

### Implementation

| Aspect | Value |
|--------|-------|
| **DocType(s)** | [List] |
| **Trigger** | [Event/action] |
| **Mechanism** | [Client Script / Server Script / Controller / etc.] |
| **Version** | [v14 / v15 / v16 / all] |

### Data Flow
1. [Step 1]
2. [Step 2]

### Error Handling
[Strategy]

### Required Skills
- [ ] frappe-skill-name - for [purpose]

### Validation Criteria
[How to verify it works]
```

## Complete Skill Catalog (61 skills)

### Syntax Layer (11 skills)
| Skill | Use For |
|-------|---------|
| `frappe-syntax-clientscripts` | Client Script JS syntax |
| `frappe-syntax-serverscripts` | Server Script Python sandbox syntax |
| `frappe-syntax-controllers` | Controller class syntax |
| `frappe-syntax-hooks` | hooks.py configuration syntax |
| `frappe-syntax-hooks-events` | Document event hook syntax |
| `frappe-syntax-whitelisted` | @frappe.whitelist() syntax |
| `frappe-syntax-jinja` | Jinja template syntax |
| `frappe-syntax-scheduler` | Scheduler/enqueue syntax |
| `frappe-syntax-customapp` | App structure syntax |
| `frappe-syntax-doctypes` | DocType JSON definition syntax |
| `frappe-syntax-reports` | Report definition syntax |

### Core Layer (7 skills)
| Skill | Use For |
|-------|---------|
| `frappe-core-database` | Database operations, ORM, raw SQL |
| `frappe-core-permissions` | Permission system, roles, rules |
| `frappe-core-api` | REST API, resource API |
| `frappe-core-workflow` | Workflow engine, states, transitions |
| `frappe-core-notifications` | Email, push, system notifications |
| `frappe-core-files` | File upload, attachment, storage |
| `frappe-core-cache` | Redis cache, cache invalidation |

### Implementation Layer (12 skills)
| Skill | Use For |
|-------|---------|
| `frappe-impl-clientscripts` | Client Script implementation patterns |
| `frappe-impl-serverscripts` | Server Script implementation patterns |
| `frappe-impl-controllers` | Controller implementation patterns |
| `frappe-impl-hooks` | Hook implementation patterns |
| `frappe-impl-whitelisted` | Whitelisted method patterns |
| `frappe-impl-jinja` | Jinja template patterns |
| `frappe-impl-scheduler` | Scheduled task/background job patterns |
| `frappe-impl-customapp` | Custom app development workflow |
| `frappe-impl-reports` | Report building patterns |
| `frappe-impl-workflow` | Workflow implementation patterns |
| `frappe-impl-website` | Website/portal development |
| `frappe-impl-ui-components` | UI component patterns |
| `frappe-impl-integrations` | External system integration |

### Error Layer (7 skills)
| Skill | Use For |
|-------|---------|
| `frappe-errors-clientscripts` | Client Script error patterns |
| `frappe-errors-serverscripts` | Server Script error patterns |
| `frappe-errors-controllers` | Controller error patterns |
| `frappe-errors-hooks` | Hook error patterns |
| `frappe-errors-api` | API error patterns |
| `frappe-errors-permissions` | Permission error patterns |
| `frappe-errors-database` | Database error patterns |

### Ops Layer (8 skills)
| Skill | Use For |
|-------|---------|
| `frappe-ops-bench` | Bench CLI commands |
| `frappe-ops-deployment` | Production deployment |
| `frappe-ops-backup` | Backup and restore |
| `frappe-ops-performance` | Performance tuning |
| `frappe-ops-upgrades` | Version upgrade procedures |
| `frappe-ops-cloud` | Cloud hosting (FC, AWS, etc.) |
| `frappe-ops-app-lifecycle` | App versioning and releases |
| `frappe-ops-frontend-build` | Frontend asset building |

### Testing Layer (2 skills)
| Skill | Use For |
|-------|---------|
| `frappe-testing-unit` | Unit and integration tests |
| `frappe-testing-cicd` | CI/CD pipeline setup |

### Agent Layer (5 skills)
| Skill | Use For |
|-------|---------|
| `frappe-agent-interpreter` | THIS SKILL - requirement interpretation |
| `frappe-agent-validator` | Code validation before deployment |
| `frappe-agent-debugger` | Debugging Frappe issues |
| `frappe-agent-migrator` | Data migration planning |
| `frappe-agent-architect` | Architecture decision-making |

## Skill Dependencies Map

| Mechanism | Required Skills |
|-----------|----------------|
| Client Script | `frappe-syntax-clientscripts`, `frappe-impl-clientscripts`, `frappe-errors-clientscripts` |
| Server Script (Doc Event) | `frappe-syntax-serverscripts`, `frappe-impl-serverscripts`, `frappe-errors-serverscripts` |
| Server Script (API) | `frappe-syntax-serverscripts`, `frappe-core-api`, `frappe-errors-api` |
| Server Script (Scheduler) | `frappe-syntax-serverscripts`, `frappe-syntax-scheduler`, `frappe-impl-scheduler` |
| Server Script (Permission) | `frappe-syntax-serverscripts`, `frappe-core-permissions`, `frappe-errors-permissions` |
| Controller | `frappe-syntax-controllers`, `frappe-impl-controllers`, `frappe-errors-controllers` |
| Hooks | `frappe-syntax-hooks`, `frappe-impl-hooks`, `frappe-errors-hooks` |
| Custom App | `frappe-syntax-customapp`, `frappe-impl-customapp`, `frappe-ops-bench` |
| Jinja Template | `frappe-syntax-jinja`, `frappe-impl-jinja` |
| Database Operations | `frappe-core-database`, `frappe-errors-database` |
| Whitelisted Method | `frappe-syntax-whitelisted`, `frappe-impl-whitelisted` |
| Workflow | `frappe-core-workflow`, `frappe-impl-workflow` |
| Reports | `frappe-syntax-reports`, `frappe-impl-reports` |
| Website/Portal | `frappe-impl-website`, `frappe-syntax-jinja` |
| Integration | `frappe-impl-integrations`, `frappe-impl-customapp` |
| Background Jobs | `frappe-impl-scheduler`, `frappe-syntax-scheduler` |
| Testing | `frappe-testing-unit`, `frappe-testing-cicd` |
| Deployment | `frappe-ops-deployment`, `frappe-ops-bench` |

## Common Pattern Recognition

| User Phrase | Mechanism | Key Skills |
|-------------|-----------|------------|
| "auto-calculate", "automatically fill" | Client Script + Server Script | `frappe-impl-clientscripts`, `frappe-impl-serverscripts` |
| "validate", "check before save" | Server Script (validate) | `frappe-impl-serverscripts` |
| "prevent", "block", "don't allow" | Server Script + frappe.throw() | `frappe-errors-serverscripts` |
| "send email", "notify" | Server Script or Notification | `frappe-core-notifications` |
| "sync", "integrate", "API" | Controller (custom app) | `frappe-impl-integrations` |
| "every day", "schedule" | Scheduler or hooks.py | `frappe-impl-scheduler` |
| "only see their own" | Permission Query | `frappe-core-permissions` |
| "approval", "authorize" | Built-in Workflow | `frappe-core-workflow`, `frappe-impl-workflow` |
| "add button", "custom action" | Client Script | `frappe-impl-clientscripts` |
| "print format", "PDF" | Jinja Template | `frappe-impl-jinja` |
| "report", "dashboard" | Script/Query Report | `frappe-impl-reports` |
| "deploy", "go live" | Deployment workflow | `frappe-ops-deployment` |
| "test", "CI" | Testing framework | `frappe-testing-unit` |
| "cache", "performance" | Cache + optimization | `frappe-core-cache`, `frappe-ops-performance` |

## Version Awareness

ALWAYS consider version compatibility:

| Feature | v14 | v15 | v16 |
|---------|:---:|:---:|:---:|
| Server Script sandbox | Yes | Yes | Yes |
| `extend_doctype_class` | No | No | Yes |
| Chrome PDF rendering | No | No | Yes |
| Data masking | No | No | Yes |
| UUID naming rule | No | No | Yes |
| Type annotations (best practice) | No | No | Yes |
| Scheduler tick (seconds) | 240 | 60 | 60 |
| `job_id` dedup | No | Yes | Yes |

## Agent Output Checklist

Before completing interpretation, ALWAYS verify:

- [ ] Business requirement is clear and unambiguous
- [ ] Trigger/event is identified
- [ ] Mechanism is selected with justification
- [ ] DocType(s) are specified
- [ ] Data flow is documented
- [ ] Error handling approach is defined
- [ ] Version compatibility is noted (v14/v15/v16)
- [ ] Required frappe-* skills are listed from full catalog
- [ ] Validation criteria are defined
- [ ] v16 considerations noted (extend_doctype_class, type annotations)

See [references/checklists.md](references/checklists.md) for detailed checklists.
See [references/examples.md](references/examples.md) for interpretation examples.
---
name: frappe-agent-migrator
description: >
  Use when migrating a Frappe app between major versions, detecting breaking API changes, or resolving post-migration errors.
  Prevents failed migrations from undetected deprecated APIs, removed methods, and changed function signatures.
  Covers breaking change detection v14-v15-v16, deprecated API mapping, migration checklist, common migration errors, automatic fix suggestions.
  Keywords: migration, version upgrade, breaking changes, deprecated API, v14, v15, v16, migrate, compatibility, upgrade ERPNext, version change breaks, after update errors, deprecated method..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Version Migration Assistant

Systematically plans and executes Frappe/ERPNext version migrations by analyzing breaking changes, scanning custom code for compatibility issues, and generating migration plans.

**Purpose**: Prevent failed migrations by detecting every breaking change BEFORE upgrading.

## When to Use This Agent

```
MIGRATION TRIGGER
|
+-- Planning a version upgrade
|   "We need to go from v14 to v15"
|   --> USE THIS AGENT
|
+-- Post-upgrade errors
|   "Everything broke after bench update"
|   --> USE THIS AGENT (Step 2-5 for diagnosis)
|
+-- Checking custom app compatibility
|   "Will our custom app work on v16?"
|   --> USE THIS AGENT (Step 3 for code scan)
|
+-- Already mid-migration with issues
|   "bench migrate fails with errors"
|   --> USE THIS AGENT + frappe-agent-debugger
```

## Migration Workflow

```
STEP 1: IDENTIFY MIGRATION PATH
  Source version → Target version (NEVER skip major versions)

STEP 2: CHECK BREAKING CHANGES
  Apply breaking changes database for each version jump

STEP 3: SCAN CUSTOM CODE
  Grep for deprecated patterns in all custom apps

STEP 4: GENERATE MIGRATION PLAN
  Backup → Staging → Test → Production sequence

STEP 5: GENERATE PATCH LIST
  Specific code changes needed per custom app
```

See [references/workflow.md](references/workflow.md) for detailed steps.

## Step 1: Migration Path Rules

NEVER skip major versions. ALWAYS migrate sequentially:

| Source | Target | Path |
|--------|--------|------|
| v14 | v15 | v14 → v15 |
| v14 | v16 | v14 → v15 → v16 |
| v15 | v16 | v15 → v16 |

### Version Identification
```bash
# Check current versions
bench version
# Output shows: frappe X.Y.Z, erpnext X.Y.Z

# Check available versions
cd apps/frappe && git tag | grep "^v1[456]" | tail -5
```

## Step 2: Breaking Changes Summary

### v14 → v15 Breaking Changes

| Category | Change | Impact | Detection Pattern |
|----------|--------|--------|-------------------|
| Scheduler | Tick interval 240s → 60s | Jobs may run more frequently | Review `scheduler_events` |
| Background Jobs | `job_id` deduplication added | Duplicate jobs now prevented | Check `frappe.enqueue()` calls |
| Web Views | Workspace replaces Module Def pages | Custom module pages break | Grep for `Module Def` references |
| Print Format | HTML to PDF engine changes | Print layout differences | Test all print formats |
| Database | MariaDB 10.6+ required | Server prerequisite | Check `mysql --version` |
| Python | Python 3.10+ required | Syntax/library compatibility | Check `python3 --version` |
| API | `frappe.client.get_list` signature change | Custom API calls may fail | Grep for `frappe.client.get_list` |
| Permissions | Stricter permission checks on API | Guest access may break | Check `allow_guest=True` usage |
| Assets | New frontend build system | Custom JS bundles may break | Test `bench build` |
| Hooks | `boot_session` hook changes | Custom boot data may fail | Grep for `boot_session` |
| Naming | Some naming series changes | Document names may differ | Review `autoname` settings |
| Report | Report Builder changes | Custom reports may need updates | Test all Script Reports |

### v15 → v16 Breaking Changes

| Category | Change | Impact | Detection Pattern |
|----------|--------|--------|-------------------|
| DocType Extension | `extend_doctype_class` replaces `doc_events` override | Controller overrides need refactoring | Grep for `doc_events` with method override |
| Type Annotations | Type hints now best practice | Code style change | Not breaking, but recommended |
| Chrome PDF | New PDF engine (Chrome-based) | Print format rendering changes | Test all print formats |
| Data Masking | New privacy feature | PII fields need configuration | Review sensitive fields |
| UUID Naming | New `uuid` naming rule | Naming logic changes | Check `autoname` settings |
| Python | Python 3.11+ required | Library compatibility | Check `python3 --version` |
| Node.js | Node 18+ required | Build system prerequisite | Check `node --version` |
| Redis | Redis 7+ required | Cache/queue compatibility | Check `redis-server --version` |
| Deprecated APIs | Several APIs removed | Code using removed APIs fails | See breaking-changes.md |
| Workflow | Workflow engine updates | Custom workflow states may need review | Test all workflows |
| Portal | Portal page rendering changes | Custom portal pages may break | Test all portal pages |
| Background Jobs | RQ version upgrade | Job serialization changes | Test background jobs |

See [references/breaking-changes.md](references/breaking-changes.md) for complete details.

## Step 3: Deprecated Pattern Detection

ALWAYS scan custom app code for these patterns:

### v14 → v15 Deprecated Patterns

```bash
# Run these grep commands in apps/{your_app}/ directory:

# 1. Old-style module page references
grep -rn "Module Def" --include="*.py" --include="*.json"

# 2. Old scheduler API
grep -rn "frappe.utils.scheduler" --include="*.py"

# 3. Deprecated client API
grep -rn "frappe.set_route\|cur_page\|page_container" --include="*.js"

# 4. Old-style print format
grep -rn "frappe.get_print\|standard_format" --include="*.py"

# 5. Deprecated database methods
grep -rn "frappe.db.sql_list\|frappe.db.sql_ddl" --include="*.py"
```

### v15 → v16 Deprecated Patterns

```bash
# Run these grep commands in apps/{your_app}/ directory:

# 1. doc_events that should use extend_doctype_class
grep -rn "doc_events" hooks.py

# 2. Old-style controller override
grep -rn "override_doctype_class" --include="*.py"

# 3. Deprecated frappe.utils methods
grep -rn "frappe.utils.now_datetime\b" --include="*.py"

# 4. Old print format API
grep -rn "frappe.utils.pdf\|get_pdf" --include="*.py"

# 5. Removed API calls
grep -rn "frappe.get_hooks\b.*boot_session" --include="*.py"

# 6. Missing type annotations (warning, not error)
grep -rn "def .*whitelist" --include="*.py"
```

## Step 4: Migration Plan Template

ALWAYS generate a migration plan in this format:

```markdown
## Migration Plan: v{source} → v{target}

### Prerequisites
- [ ] Python version: {required}
- [ ] Node.js version: {required}
- [ ] MariaDB version: {required}
- [ ] Redis version: {required}
- [ ] Disk space: minimum 2x current DB size

### Phase 1: Preparation (Day 1)
1. Full backup: `bench --site {site} backup --with-files`
2. Document current state: `bench version > pre-migration-versions.txt`
3. List all custom apps: `bench --site {site} list-apps`
4. Run deprecated pattern scan (Step 3)
5. Fix all detected issues in custom apps

### Phase 2: Staging (Day 2-3)
1. Clone production to staging environment
2. Restore backup on staging: `bench --site staging restore {backup}`
3. Switch branch: `bench switch-to-branch version-{target} frappe erpnext`
4. Run migration: `bench --site staging migrate`
5. Run full test suite on staging

### Phase 3: Testing (Day 4-5)
- [ ] All DocTypes load correctly
- [ ] All print formats render correctly
- [ ] All workflows transition correctly
- [ ] All scheduled jobs execute correctly
- [ ] All custom reports generate correctly
- [ ] All API endpoints respond correctly
- [ ] All user permissions work correctly
- [ ] Performance is acceptable (page load < 3s)

### Phase 4: Production (Day 6)
1. Schedule maintenance window
2. Enable maintenance mode: `bench --site {site} set-maintenance-mode on`
3. Final backup: `bench --site {site} backup --with-files`
4. Switch branch: `bench switch-to-branch version-{target} frappe erpnext`
5. Run migration: `bench --site {site} migrate`
6. Run `bench build --production`
7. Restart: `bench restart` (or `sudo supervisorctl restart all`)
8. Disable maintenance mode: `bench --site {site} set-maintenance-mode off`
9. Verify (Phase 3 checklist again)

### Rollback Plan
1. Stop all services: `sudo supervisorctl stop all`
2. Restore backup: `bench --site {site} restore {backup_path}`
3. Switch back: `bench switch-to-branch version-{source} frappe erpnext`
4. Run migration: `bench --site {site} migrate`
5. Rebuild: `bench build --production`
6. Restart: `sudo supervisorctl restart all`
```

## Step 5: Custom App Patch List

For each deprecated pattern found in Step 3, generate a specific fix:

| File | Line | Current Code | Required Change | Breaking? |
|------|------|-------------|-----------------|-----------|
| `{file}` | `{line}` | `{old_pattern}` | `{new_pattern}` | Yes/No |

### Common Patches (v14 → v15)

| Pattern | Replace With |
|---------|-------------|
| `frappe.db.sql_list(...)` | `frappe.db.get_all(..., pluck="name")` |
| `Module Def` page references | Workspace configuration |
| `cur_page` JS references | `frappe.router` API |
| Old scheduler tick assumptions | Review timing for 60s interval |

### Common Patches (v15 → v16)

| Pattern | Replace With |
|---------|-------------|
| `doc_events` controller override | `extend_doctype_class` in hooks.py |
| Missing `super()` in overrides | Add `super().method()` call |
| `frappe.utils.pdf.get_pdf()` | Updated PDF API |
| No type annotations | Add type hints to public methods |

## Agent Output Format

ALWAYS produce migration output in this format:

```markdown
## Migration Assessment

### Version Path
{source} → {target} (via {intermediate versions if any})

### Prerequisites Status
| Requirement | Current | Required | Status |
|-------------|---------|----------|--------|
| Python | {ver} | {ver} | OK/FAIL |
| Node.js | {ver} | {ver} | OK/FAIL |
| MariaDB | {ver} | {ver} | OK/FAIL |

### Breaking Changes Found: {count}
[List from Step 2]

### Custom Code Issues Found: {count}
[Table from Step 3 scan]

### Migration Plan
[From Step 4]

### Patch List
[From Step 5]

### Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|

### Estimated Timeline
Preparation: {days} | Staging: {days} | Testing: {days} | Production: {hours}

### Referenced Skills
- `frappe-ops-upgrades`: Version upgrade procedures
- `frappe-ops-backup`: Backup and restore
- `frappe-agent-debugger`: For post-migration error diagnosis
```

See [references/checklists.md](references/checklists.md) for complete migration checklists.
See [references/breaking-changes.md](references/breaking-changes.md) for full breaking changes database.
---
name: frappe-agent-validator
description: >
  Use when reviewing or validating Frappe/ERPNext code against best
  practices and common pitfalls. Checks generated code before deployment,
  validates against all 61 frappe-* skills, catches v16 patterns
  (extend_doctype_class, type annotations), validates ops patterns (bench
  commands, deployment), and generates correction reports. Keywords: review
  code, check script, validate deployment, find bugs, code quality,
  check my code, is this correct, code review, before deploying, best practices check.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Code Validator Agent

Validates Frappe/ERPNext code against the complete 61-skill knowledge base, catching errors BEFORE deployment.

**Purpose**: Catch errors before deployment, not after

## When to Use This Agent

```
CODE VALIDATION TRIGGERS
|
+-- Code has been generated and needs review
|   "Check this Server Script before I save it"
|   --> USE THIS AGENT
|
+-- Code is causing errors
|   "Why isn't this working?"
|   --> USE THIS AGENT
|
+-- Pre-deployment validation
|   "Is this production-ready?"
|   --> USE THIS AGENT
|
+-- Code review for best practices
|   "Can this be improved?"
|   --> USE THIS AGENT
|
+-- Ops/deployment validation
|   "Is my bench setup correct?"
|   --> USE THIS AGENT
```

## Validation Workflow

```
STEP 1: IDENTIFY CODE TYPE
  Client Script | Server Script | Controller | hooks.py |
  Jinja | Whitelisted | Bench/Ops | DocType JSON

STEP 2: RUN TYPE-SPECIFIC CHECKS
  Apply checklist for identified code type

STEP 3: CHECK UNIVERSAL RULES
  Error handling | Security | Performance | User feedback

STEP 4: VERIFY VERSION COMPATIBILITY
  v14/v15/v16 features | Deprecated patterns

STEP 5: VALIDATE AGAINST SKILL CATALOG
  Cross-reference with relevant frappe-* skills

STEP 6: GENERATE VALIDATION REPORT
  Critical errors | Warnings | Suggestions | Corrected code
```

See [references/workflow.md](references/workflow.md) for detailed steps.

## Critical Checks by Code Type

### Server Script Checks

| Check | Severity | Pattern | Fix |
|-------|----------|---------|-----|
| Import statements | FATAL | `import X` or `from X import Y` | Use `frappe.utils.X()` directly |
| Wrong doc variable | FATAL | `self.field` or `document.field` | Use `doc.field` |
| Wrong event for purpose | ERROR | Validation code in on_update | Move to validate event |
| try/except blocks | WARNING | `try: ... except:` | Use `frappe.throw()` for validation |
| No null checks | WARNING | `doc.field.lower()` | Add `if doc.field:` guard |

### Client Script Checks

| Check | Severity | Pattern | Fix |
|-------|----------|---------|-----|
| Server-side API calls | FATAL | `frappe.db.get_value()` | Use `frappe.call()` |
| Missing async handling | FATAL | `let x = frappe.call()` | Use callback or async/await |
| No refresh after set_value | ERROR | `frm.set_value()` alone | Add `frm.refresh_field()` |
| Using cur_frm | WARNING | `cur_frm.doc.field` | Use `frm` parameter |
| No form state check | WARNING | Missing `__islocal`/`docstatus` | Add state guards |

### Controller Checks

| Check | Severity | Pattern | Fix |
|-------|----------|---------|-----|
| self.* in on_update | FATAL | `self.field = X` in on_update | Use `self.db_set()` |
| Circular save | FATAL | `self.save()` in lifecycle hook | Remove self.save() |
| Missing super() | ERROR | Override without super() | Add `super().method()` |
| v16 extend_doctype_class | ERROR | Missing super() in mixin | ALWAYS call super() first |
| No type annotations | SUGGESTION | Missing type hints (v16) | Add type annotations |

### hooks.py Checks

| Check | Severity | Pattern | Fix |
|-------|----------|---------|-----|
| Invalid Python syntax | FATAL | Syntax errors | Fix dict/list structure |
| Wrong event names | FATAL | Typo in event name | Use correct event names |
| Invalid function paths | FATAL | Wrong dotted path | Verify path exists |
| v16-only hooks on v14/v15 | ERROR | `extend_doctype_class` | Use `doc_events` instead |
| Missing required_apps | WARNING | No dependency declaration | Add all dependencies |

### Ops/Bench Checks

| Check | Severity | Pattern | Fix |
|-------|----------|---------|-----|
| No migrate after hooks | FATAL | hooks.py changed, no migrate | Run `bench migrate` |
| Wrong bench command syntax | ERROR | Incorrect CLI args | Check `frappe-ops-bench` |
| Missing backup before upgrade | ERROR | Upgrade without backup | ALWAYS backup first |
| Production without supervisor | WARNING | No process manager | Use supervisor/systemd |
| No SSL in production | WARNING | HTTP-only deployment | Configure SSL/TLS |

### DocType JSON Checks

| Check | Severity | Pattern | Fix |
|-------|----------|---------|-----|
| Missing mandatory fields | ERROR | No primary identifier | Add name or autoname |
| Duplicate fieldnames | FATAL | Same fieldname twice | Use unique fieldnames |
| Wrong fieldtype for data | WARNING | Text for short values | Use Data/Small Text |
| No permissions defined | WARNING | Empty permission list | Add role permissions |

## v16 Specific Validations

### extend_doctype_class Pattern
```python
# VALIDATE: Mixin class MUST call super()
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()       # REQUIRED - never skip
        self.custom_validation()

    def on_submit(self):
        super().on_submit()      # REQUIRED - never skip
        self.custom_on_submit()
```

### Type Annotations (v16 best practice)
```python
# v16 recommended pattern
def get_customer_balance(customer: str) -> float:
    ...

# Validate: type hints on public API methods
@frappe.whitelist()
def process_order(order_name: str, action: str = "approve") -> dict:
    ...
```

### Data Masking (v16)
```python
# Validate: sensitive fields should use data masking
# Check if PII fields have mask_with configured in DocType JSON
```

## Universal Validation Rules

### Security Checks (ALL code types)

| Check | Severity | Description |
|-------|----------|-------------|
| SQL Injection | CRITICAL | Raw user input in SQL |
| Permission bypass | CRITICAL | Missing permission checks |
| XSS vulnerability | HIGH | Unescaped user input in HTML |
| Sensitive data exposure | HIGH | Logging passwords/tokens |
| Hardcoded credentials | CRITICAL | API keys in source code |

### Performance Checks (ALL code types)

| Check | Severity | Description |
|-------|----------|-------------|
| Query in loop | HIGH | `frappe.db.*` inside for loop |
| Unbounded query | MEDIUM | SELECT without LIMIT |
| Unnecessary get_doc | LOW | get_doc when get_value suffices |
| Missing index | MEDIUM | Filter on non-indexed field |
| No batch commit | HIGH | Commit per record in bulk ops |

### Error Handling Checks (ALL code types)

| Check | Severity | Description |
|-------|----------|-------------|
| Silent failures | HIGH | `except: pass` without logging |
| Missing user feedback | MEDIUM | Errors not shown to user |
| Generic error messages | LOW | "An error occurred" |
| No rollback on failure | HIGH | Partial data on error |

## Validation Report Format

ALWAYS generate reports in this format:

```markdown
## Code Validation Report

### Code Type: [type]
### Target: [DocType / App / File]
### Event/Trigger: [if applicable]

### CRITICAL ERRORS (Must Fix)
| # | Line | Issue | Fix |
|---|------|-------|-----|

### WARNINGS (Should Fix)
| # | Line | Issue | Recommendation |
|---|------|-------|----------------|

### SUGGESTIONS (Nice to Have)
| # | Line | Suggestion |
|---|------|------------|

### Corrected Code
[If critical errors found, provide corrected version]

### Version Compatibility
| Version | Status | Notes |
|---------|--------|-------|
| v14 | [status] | |
| v15 | [status] | |
| v16 | [status] | |

### Referenced Skills
- frappe-skill-name: [what was validated against]
```

## Validation Depth Levels

| Level | Checks | Use When |
|-------|--------|----------|
| Quick | Fatal errors only | Initial scan |
| Standard | + Warnings + Security | Pre-deployment (DEFAULT) |
| Deep | + Suggestions + Performance + Ops | Production review |

## Skill Catalog Cross-Reference

This validator validates against ALL 61 frappe-* skills:

### Syntax Validation (11 skills)
`frappe-syntax-clientscripts`, `frappe-syntax-serverscripts`, `frappe-syntax-controllers`, `frappe-syntax-hooks`, `frappe-syntax-hooks-events`, `frappe-syntax-whitelisted`, `frappe-syntax-jinja`, `frappe-syntax-scheduler`, `frappe-syntax-customapp`, `frappe-syntax-doctypes`, `frappe-syntax-reports`

### Implementation Validation (12 skills)
`frappe-impl-clientscripts`, `frappe-impl-serverscripts`, `frappe-impl-controllers`, `frappe-impl-hooks`, `frappe-impl-whitelisted`, `frappe-impl-jinja`, `frappe-impl-scheduler`, `frappe-impl-customapp`, `frappe-impl-reports`, `frappe-impl-workflow`, `frappe-impl-website`, `frappe-impl-ui-components`, `frappe-impl-integrations`

### Error Pattern Validation (7 skills)
`frappe-errors-clientscripts`, `frappe-errors-serverscripts`, `frappe-errors-controllers`, `frappe-errors-hooks`, `frappe-errors-api`, `frappe-errors-permissions`, `frappe-errors-database`

### Core Pattern Validation (7 skills)
`frappe-core-database`, `frappe-core-permissions`, `frappe-core-api`, `frappe-core-workflow`, `frappe-core-notifications`, `frappe-core-files`, `frappe-core-cache`

### Ops Validation (8 skills)
`frappe-ops-bench`, `frappe-ops-deployment`, `frappe-ops-backup`, `frappe-ops-performance`, `frappe-ops-upgrades`, `frappe-ops-cloud`, `frappe-ops-app-lifecycle`, `frappe-ops-frontend-build`

### Testing Validation (2 skills)
`frappe-testing-unit`, `frappe-testing-cicd`

## Quick Validation Commands

### Server Script: 5-point check
1. Any `import` statements? --> FATAL
2. Any `self.` references? --> FATAL (use `doc.`)
3. Any `try/except`? --> WARNING (usually wrong)
4. Uses `frappe.throw()` for validation? --> GOOD
5. Uses `doc.field` for access? --> GOOD

### Client Script: 5-point check
1. Any `frappe.db.*` calls? --> FATAL
2. Any `frappe.get_doc()` calls? --> FATAL
3. `frappe.call()` without callback? --> FATAL
4. Uses `frm.doc.field` for access? --> GOOD
5. Uses `frm.refresh_field()` after changes? --> GOOD

### Controller: 5-point check
1. Modifying `self.*` in `on_update`? --> FATAL
2. Missing `super().method()` calls? --> ERROR
3. `self.save()` in lifecycle hook? --> FATAL
4. Imports at top of file? --> GOOD
5. Error handling for external calls? --> GOOD

### hooks.py: 5-point check
1. Valid Python syntax? --> Check
2. Function paths exist? --> Check
3. v16-only hooks marked? --> Check
4. required_apps complete? --> Check
5. Fixture filters present? --> Check

### Bench/Ops: 5-point check
1. `bench migrate` after changes? --> REQUIRED
2. Backup before destructive ops? --> REQUIRED
3. Scheduler enabled? --> Check
4. Workers running? --> Check
5. SSL configured (production)? --> Check

See [references/checklists.md](references/checklists.md) for complete checklists.
See [references/examples.md](references/examples.md) for validation examples.
---
name: frappe-core-api
description: >
  Use when building ERPNext/Frappe API integrations (v14/v15/v16) including
  REST API, RPC API, authentication, webhooks, and rate limiting. Covers
  external API calls, endpoint design, token/OAuth2/session authentication.
  Keywords: API integration, REST endpoint, webhook, token authentication,, how to connect, external API, send data to another system, API not working, 401 error.
  OAuth, frappe.call, external connection, rate limiting.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe API Patterns

> Deterministic patterns for REST, RPC, and webhook integrations with Frappe.

---

## Decision Tree

```
What do you need?
├── CRUD on documents (external client)
│   ├── v14: REST /api/resource/{doctype}
│   └── v15+: REST /api/v2/document/{doctype} (new) or /api/resource/ (still works)
│
├── Call custom server logic (external client)
│   └── RPC: POST /api/method/{dotted.path.to.function}
│
├── Notify external systems on document events
│   └── Webhooks (configured in UI or via DocType)
│
├── Client-side calls (JavaScript in Frappe desk)
│   ├── frappe.xcall() — async/await (RECOMMENDED)
│   └── frappe.call() — callback/promise pattern
│
└── Authentication method?
    ├── Server-to-server integration → Token Auth (RECOMMENDED)
    ├── Third-party app / mobile → OAuth 2.0
    ├── Browser session (short-lived) → Session/Cookie Auth
    └── Quick scripting / testing → Token Auth
```

---

## Authentication Methods

### Token Auth (RECOMMENDED for integrations)

```python
headers = {
    'Authorization': 'token api_key:api_secret',
    'Accept': 'application/json',
    'Content-Type': 'application/json'
}
```

Generate keys: User > Settings > API Access > Generate Keys. ALWAYS store API secret immediately — it is shown only once.

### Basic Auth (alternative token format)

```python
import base64
credentials = base64.b64encode(b'api_key:api_secret').decode()
headers = {'Authorization': f'Basic {credentials}'}
```

### OAuth 2.0 (third-party apps)

```
# Step 1: Authorization redirect
GET /api/method/frappe.integrations.oauth2.authorize
    ?client_id={id}&response_type=code&scope=openid all
    &redirect_uri={uri}&state={random}

# Step 2: Exchange code for token
POST /api/method/frappe.integrations.oauth2.get_token
    grant_type=authorization_code&code={code}
    &redirect_uri={uri}&client_id={id}

# Step 3: Use bearer token
Authorization: Bearer {access_token}

# Refresh token
POST /api/method/frappe.integrations.oauth2.get_token
    grant_type=refresh_token&refresh_token={token}&client_id={id}
```

### Session/Cookie Auth

```python
session = requests.Session()
session.post(url + '/api/method/login', json={'usr': 'email', 'pwd': 'pass'})
# Subsequent requests use session cookie automatically
```

Session cookies expire after ~3 days. NEVER use for long-running integrations.

---

## REST API: Resource CRUD

### Endpoints

| Operation | Method | v14 Endpoint | v15+ v2 Endpoint |
|-----------|--------|--------------|------------------|
| List | GET | `/api/resource/{doctype}` | `/api/v2/document/{doctype}` |
| Create | POST | `/api/resource/{doctype}` | `/api/v2/document/{doctype}` |
| Read | GET | `/api/resource/{doctype}/{name}` | `/api/v2/document/{doctype}/{name}` |
| Update | PUT | `/api/resource/{doctype}/{name}` | PATCH `/api/v2/document/{doctype}/{name}` |
| Delete | DELETE | `/api/resource/{doctype}/{name}` | DELETE `/api/v2/document/{doctype}/{name}` |
| Copy | — | — | GET `/api/v2/document/{doctype}/{name}/copy` [v15+] |
| Doc Method | — | — | POST `/api/v2/document/{doctype}/{name}/method/{method}` [v15+] |

**ALWAYS** include `Accept: application/json` header — without it, Frappe MAY return HTML.

### List Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `fields` | JSON array | Fields to return | `["name"]` |
| `filters` | JSON array | AND conditions | none |
| `or_filters` | JSON array | OR conditions | none |
| `order_by` | string | Sort expression | `modified desc` |
| `limit_start` | int | Pagination offset | `0` |
| `limit_page_length` | int | Page size | `20` |
| `limit` | int | Alias for limit_page_length [v15+] | — |
| `debug` | bool | Show SQL in response | `false` |

### Filter Operators

```python
filters = [["status", "=", "Open"]]
filters = [["amount", ">", 1000]]
filters = [["status", "in", ["Open", "Pending"]]]
filters = [["date", "between", ["2024-01-01", "2024-12-31"]]]
filters = [["reference", "is", "set"]]       # NOT NULL
filters = [["reference", "is", "not set"]]   # IS NULL
filters = [["name", "like", "%INV%"]]
filters = [["status", "not in", ["Cancelled"]]]
```

Full operator list: `=`, `!=`, `>`, `<`, `>=`, `<=`, `like`, `not like`, `in`, `not in`, `is`, `between`.

### Pagination Pattern

```python
import json, requests

def get_all_records(doctype, headers, base_url, page_size=100):
    all_data, offset = [], 0
    while True:
        params = {
            'fields': json.dumps(["name", "modified"]),
            'limit_start': offset,
            'limit_page_length': page_size
        }
        resp = requests.get(f'{base_url}/api/resource/{doctype}',
                            params=params, headers=headers)
        data = resp.json().get('data', [])
        if not data:
            break
        all_data.extend(data)
        if len(data) < page_size:
            break
        offset += page_size
    return all_data
```

### Create with Child Table

```python
requests.post(f'{base_url}/api/resource/Sales Order', json={
    "customer": "CUST-001",
    "items": [
        {"item_code": "ITEM-001", "qty": 5, "rate": 100},
        {"item_code": "ITEM-002", "qty": 2, "rate": 250}
    ]
}, headers=headers)
```

### Update (Partial)

```python
# Only specified fields are changed
requests.put(f'{base_url}/api/resource/Customer/CUST-001',
             json={"customer_group": "Premium"}, headers=headers)
```

### File Upload

```python
requests.post(f'{base_url}/api/method/upload_file',
    files={'file': ('doc.pdf', open('doc.pdf', 'rb'), 'application/pdf')},
    data={'doctype': 'Customer', 'docname': 'CUST-001', 'is_private': 1},
    headers={'Authorization': 'token api_key:api_secret'})
# NOTE: Do NOT set Content-Type header — requests sets multipart boundary automatically
```

---

## RPC API: Custom Methods

### Server-Side Endpoint

```python
@frappe.whitelist()
def get_balance(customer):
    """GET /api/method/myapp.api.get_balance?customer=CUST-001"""
    return frappe.db.get_value("Customer", customer, "outstanding_amount")

@frappe.whitelist(methods=["POST"])
def create_payment(customer, amount):
    """POST /api/method/myapp.api.create_payment"""
    if not frappe.has_permission("Payment Entry", "create"):
        frappe.throw(_("Not permitted"), frappe.PermissionError)
    pe = frappe.new_doc("Payment Entry")
    pe.party_type = "Customer"
    pe.party = customer
    pe.paid_amount = float(amount)
    pe.insert()
    return pe.name

@frappe.whitelist(allow_guest=True)
def public_status():
    """No authentication required."""
    return {"status": "ok"}
```

### Decorator Options

| Option | Effect | Version |
|--------|--------|---------|
| `allow_guest=True` | No authentication needed | All |
| `methods=["POST"]` | Restrict HTTP methods | [v14+] |
| `xss_safe=True` | Skip XSS escaping on response | All |

### Response Structure

```json
// RPC success
{"message": "return_value"}

// REST success
{"data": {...}}

// Error
{"exc_type": "ValidationError", "_server_messages": "[{\"message\": \"...\"}]"}
```

### Client-Side Calls (JavaScript)

```javascript
// RECOMMENDED: async/await with frappe.xcall
const result = await frappe.xcall('myapp.api.get_balance', {
    customer: 'CUST-001'
});

// Alternative: frappe.call with promise
frappe.call({
    method: 'myapp.api.get_balance',
    args: {customer: 'CUST-001'},
    freeze: true,
    freeze_message: __('Loading...')
}).then(r => console.log(r.message));

// Document method (frm.call)
frm.call('get_linked_doc', {throw_if_missing: true})
    .then(r => console.log(r.message));
```

### Standard frappe.client Methods

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `frappe.client.get_value` | POST | Get single field value |
| `frappe.client.get_list` | POST | List with filters |
| `frappe.client.get` | POST | Get full document |
| `frappe.client.insert` | POST | Create document |
| `frappe.client.save` | POST | Update document |
| `frappe.client.delete` | POST | Delete document |
| `frappe.client.submit` | POST | Submit document |
| `frappe.client.cancel` | POST | Cancel document |
| `frappe.client.get_count` | POST | Count documents |

---

## Webhooks

Configure via Webhook DocType in the UI. Events:

| Event | Trigger |
|-------|---------|
| `after_insert` | New document created |
| `on_update` | Every save |
| `on_submit` | After submit (docstatus=1) |
| `on_cancel` | After cancel (docstatus=2) |
| `on_trash` | Before delete |
| `on_update_after_submit` | After amendment |
| `on_change` | On every change |

**Security**: ALWAYS set a Webhook Secret. Frappe adds `X-Frappe-Webhook-Signature` header with base64-encoded HMAC-SHA256 of payload. Verify on receiving end.

**Conditions**: Use Jinja2 — `{{ doc.grand_total > 10000 }}`.

See `references/webhooks-reference.md` for complete handler examples.

---

## HTTP Status Codes

| Code | Meaning | Common Cause |
|------|---------|--------------|
| `200` | Success | — |
| `400` | Bad request | Validation error |
| `401` | Unauthorized | Missing or invalid auth |
| `403` | Forbidden | No permission for operation |
| `404` | Not found | Document does not exist |
| `417` | Expectation failed | Server exception (frappe.throw) |
| `429` | Rate limited | Too many requests |
| `500` | Server error | Unhandled exception |

---

## Critical Rules

1. **ALWAYS** include `Accept: application/json` header in API requests
2. **ALWAYS** add permission checks in `@frappe.whitelist()` methods
3. **ALWAYS** validate and sanitize input in whitelisted methods
4. **ALWAYS** use parameterized queries — NEVER string-interpolate SQL
5. **ALWAYS** use `timeout=30` on external `requests` calls
6. **ALWAYS** store credentials in `frappe.conf` or env vars — NEVER hardcode
7. **ALWAYS** verify webhook signatures with HMAC-SHA256
8. **ALWAYS** paginate list responses — NEVER return unbounded result sets
9. **NEVER** use `allow_guest=True` on state-changing endpoints
10. **NEVER** log credentials or sensitive data
11. **NEVER** use Administrator API keys for integrations — create dedicated API users

---

## Anti-Patterns

| Do NOT | Do Instead |
|--------|------------|
| No permission check in whitelist | `frappe.has_permission()` before action |
| `frappe.db.sql(f"...{user_input}")` | Parameterized `%s` queries |
| `allow_guest=True` + state change | Require authentication |
| Return all records without limit | Paginate with `limit_page_length` |
| Hardcode API credentials | `frappe.conf.get("api_key")` |
| Synchronous heavy processing | `frappe.enqueue()` for long tasks |
| No timeout on external calls | `requests.get(url, timeout=30)` |
| Inconsistent response format | ALWAYS return `{"status": "...", "data": ...}` |

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| `/api/resource/` (v1) | Yes | Yes | Yes |
| `/api/v2/document/` (v2) | No | Yes | Yes |
| `/api/v2/doctype/{dt}/meta` | No | Yes | Yes |
| `/api/v2/doctype/{dt}/count` | No | Yes | Yes |
| `limit` alias parameter | No | Yes | Yes |
| PKCE for OAuth2 | Limited | Yes | Yes |
| Server Script rate limiting | No | Yes | Yes |
| Doc method via v2 URL | No | Yes | Yes |

---

## Reference Files

| File | Contents |
|------|----------|
| [authentication-methods.md](references/authentication-methods.md) | Token, Session, OAuth2 with code examples |
| [rest-api-reference.md](references/rest-api-reference.md) | Complete REST CRUD with filters and pagination |
| [rpc-api-reference.md](references/rpc-api-reference.md) | Whitelisted methods, frappe.call, frappe.xcall |
| [webhooks-reference.md](references/webhooks-reference.md) | Webhook config, security, handler examples |
| [anti-patterns.md](references/anti-patterns.md) | Common mistakes with fixes |
| [examples.md](references/examples.md) | Python/JS/cURL client implementations |

## Related Skills

- `frappe-core-permissions` — Permission system for API endpoints
- `frappe-core-database` — Database queries behind API methods
- `frappe-syntax-hooks` — Hook configuration for webhooks
- `frappe-syntax-controllers` — Controller methods called via API

---

*Verified against Frappe docs 2026-03-20 | Frappe v14/v15/v16*
---
name: frappe-core-cache
description: >
  Use when implementing Redis caching, cache invalidation, or distributed locking in Frappe.
  Prevents stale cache bugs, race conditions from missing locks, and memory bloat from unbounded cache keys.
  Covers frappe.cache(), @redis_cache decorator, cache.get_value/set_value, cache invalidation patterns, frappe.lock, TTL strategies.
  Keywords: cache, Redis, redis_cache, invalidation, locking, frappe.cache, get_value, set_value, TTL, distributed lock, data not refreshing, stale data, cache not clearing, Redis error, slow repeated queries..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Cache & Locking

## Quick Reference

| Action | Method | Notes |
|--------|--------|-------|
| Set value | `frappe.cache.set_value(key, val)` | With optional TTL |
| Get value | `frappe.cache.get_value(key)` | Returns `None` if missing |
| Get or generate | `frappe.cache.get_value(key, generator=fn)` | Calls `fn()` on cache miss |
| Delete value | `frappe.cache.delete_value(key)` | Single key or list of keys |
| Delete by pattern | `frappe.cache.delete_keys(pattern)` | Wildcard `*` matching |
| Hash set | `frappe.cache.hset(name, key, val)` | Redis hash field |
| Hash get | `frappe.cache.hget(name, key)` | Single hash field |
| Hash get all | `frappe.cache.hgetall(name)` | Full hash as dict |
| Hash delete | `frappe.cache.hdel(name, key)` | Remove hash field |
| Hash exists | `frappe.cache.hexists(name, key)` | Returns bool |
| Cached document | `frappe.get_cached_doc(dt, dn)` | Full doc from cache |
| Clear doc cache | `frappe.clear_document_cache(dt, dn)` | Invalidate cached doc |
| Decorator cache | `@redis_cache` | Auto-cache function result |
| Request cache | `frappe.local.cache` | Per-request dict (not Redis) |

---

## Decision Tree

```
What caching pattern do you need?
│
├─ Cache a function result automatically?
│  ├─ Pure function (same args → same result) → @redis_cache
│  └─ Need custom key/TTL → manual get_value/set_value
│
├─ Cache a document?
│  ├─ Read-only access → frappe.get_cached_doc()
│  └─ Need to invalidate → frappe.clear_document_cache()
│
├─ Cache structured data (multiple fields)?
│  └─ Redis hash → hset/hget/hgetall
│
├─ Per-request cache (avoid repeated DB calls in one request)?
│  └─ frappe.local.cache dict
│
├─ Prevent concurrent execution?
│  └─ Distributed lock → frappe.lock("resource_name")
│
└─ Invalidate cache?
   ├─ Single key → delete_value(key)
   ├─ Pattern → delete_keys("prefix*")
   └─ All site cache → frappe.clear_cache()
```

---

## String Operations

### Set and Get

```python
# Set a value (persists until evicted or deleted)
frappe.cache.set_value("exchange_rate_USD", 1.08)

# Set with TTL (expires after N seconds)
frappe.cache.set_value("exchange_rate_USD", 1.08, expires_in_sec=3600)

# Get value (returns None if missing)
rate = frappe.cache.get_value("exchange_rate_USD")

# Get with generator (calls function on cache miss, stores result)
rate = frappe.cache.get_value(
    "exchange_rate_USD",
    generator=lambda: fetch_exchange_rate("USD"),
)
```

### User-Scoped Values

```python
# Store per-user preference
frappe.cache.set_value("dashboard_layout", "compact", user="user@example.com")

# Retrieve for specific user
layout = frappe.cache.get_value("dashboard_layout", user="user@example.com")
```

### Delete

```python
# Single key
frappe.cache.delete_value("exchange_rate_USD")

# Multiple keys
frappe.cache.delete_value(["exchange_rate_USD", "exchange_rate_EUR"])

# Pattern-based deletion (wildcard)
frappe.cache.delete_keys("exchange_rate*")
```

---

## Hash Operations

Use hashes to group related fields under a single key.

```python
# Set hash fields
frappe.cache.hset("config|notifications", "email_enabled", True)
frappe.cache.hset("config|notifications", "sms_enabled", False)
frappe.cache.hset("config|notifications", "max_retries", 3)

# Get single field
email_on = frappe.cache.hget("config|notifications", "email_enabled")

# Get all fields as dict
config = frappe.cache.hgetall("config|notifications")
# {"email_enabled": True, "sms_enabled": False, "max_retries": 3}

# Delete field
frappe.cache.hdel("config|notifications", "sms_enabled")

# Check existence
exists = frappe.cache.hexists("config|notifications", "email_enabled")
```

### Hash with Generator

```python
# hget with generator — calls function on miss
value = frappe.cache.hget(
    "user|permissions",
    "user@example.com",
    generator=lambda: compute_permissions("user@example.com"),
)
```

---

## @redis_cache Decorator

Automatically cache function return values based on arguments.

```python
from frappe.utils.caching import redis_cache

@redis_cache
def get_item_price(item_code, price_list):
    """Expensive query — cached automatically."""
    return frappe.db.get_value("Item Price",
        {"item_code": item_code, "price_list": price_list},
        "price_list_rate",
    )

# First call — hits database, stores in Redis
price = get_item_price("ITEM-001", "Standard Selling")

# Second call — returns from cache
price = get_item_price("ITEM-001", "Standard Selling")

# Clear all cached results for this function
get_item_price.clear_cache()
```

### With TTL

```python
@redis_cache(ttl=300)  # expires after 5 minutes
def get_exchange_rate(from_currency, to_currency):
    return fetch_rate_from_api(from_currency, to_currency)
```

**Rules for @redis_cache:**
- ALWAYS ensure arguments are hashable (strings, numbers, tuples). NEVER pass dicts or lists as arguments.
- ALWAYS call `.clear_cache()` when underlying data changes.
- NEVER use on functions with side effects — the function will NOT execute on cache hits.

---

## frappe.local.cache: Request-Scoped Cache

`frappe.local.cache` is a plain Python dict that lives for the duration of a single HTTP request. It is NOT stored in Redis.

```python
def get_user_settings():
    """Avoid repeated DB calls within a single request."""
    if "user_settings" not in frappe.local.cache:
        frappe.local.cache["user_settings"] = frappe.get_doc(
            "User Settings", frappe.session.user
        )
    return frappe.local.cache["user_settings"]
```

Use `frappe.local.cache` when:
- The same data is needed multiple times in one request
- The data does NOT need to persist across requests
- You want zero Redis overhead

---

## Document Caching

```python
# Get cached document (read-only, no permission check)
settings = frappe.get_cached_doc("System Settings")
item = frappe.get_cached_doc("Item", "ITEM-001")

# Invalidate when document changes
frappe.clear_document_cache("Item", "ITEM-001")

# Cached single value
val = frappe.db.get_value("Item", "ITEM-001", "item_name", cache=True)
```

NEVER modify a document returned by `frappe.get_cached_doc()` — it returns a shared reference. Modifications corrupt the cache for all subsequent reads.

---

## Distributed Locking

Prevent concurrent execution of critical sections using Redis-based locks.

```python
# Context manager (recommended)
with frappe.lock("process_payroll"):
    # Only one worker executes this block at a time
    process_all_salary_slips()
    # Lock auto-released on exit

# Manual lock/unlock
frappe.lock("inventory_sync")
try:
    sync_inventory()
finally:
    frappe.unlock("inventory_sync")  # ALWAYS unlock in finally
```

**Rules:**
- ALWAYS use `with frappe.lock()` (context manager) to guarantee release.
- NEVER hold locks for more than a few seconds — long locks cause worker starvation.
- ALWAYS use descriptive lock names to avoid collisions.

---

## Cache Invalidation Patterns

### Pattern 1: TTL-Based (Time-to-Live)

```python
frappe.cache.set_value("dashboard_stats", compute_stats(), expires_in_sec=300)
```

Best for: Data that can be slightly stale (exchange rates, dashboard aggregates).

### Pattern 2: Event-Based Invalidation

```python
# In hooks.py
doc_events = {
    "Item Price": {
        "on_update": "my_app.cache.invalidate_price_cache",
        "on_trash": "my_app.cache.invalidate_price_cache",
    }
}

# In my_app/cache.py
def invalidate_price_cache(doc, method):
    frappe.cache.delete_keys("item_price*")
    # Or clear specific function cache:
    # get_item_price.clear_cache()
```

Best for: Data that MUST be fresh immediately after changes.

### Pattern 3: Hybrid (TTL + Event)

```python
@redis_cache(ttl=600)
def get_pricing_rules():
    return frappe.get_all("Pricing Rule", fields=["*"])

# Event hook clears cache immediately on change
def on_pricing_rule_update(doc, method):
    get_pricing_rules.clear_cache()
```

Best for: Frequently read data with occasional updates.

---

## Common Cache Keys (Internal)

| Key Pattern | Content |
|-------------|---------|
| `doctype::meta::{dt}` | DocType metadata |
| `user_permissions::{user}` | User permission cache |
| `bootinfo::{user}` | User boot info |
| `notifications::{user}` | Notification counts |
| `document_cache::{dt}::{dn}` | Cached document |

NEVER write to internal cache keys directly. ALWAYS use the documented API methods (`get_cached_doc`, `clear_document_cache`, etc.).

---

## Performance Guidelines

1. **ALWAYS set TTL** on cached values that derive from external data — without TTL, stale data persists until manual invalidation or Redis eviction.
2. **NEVER cache large objects** (>1 MB) — Redis uses pickle serialization, and large values increase serialization overhead and memory usage.
3. **ALWAYS use `frappe.local.cache`** for data needed multiple times within a single request — it avoids Redis round-trips entirely.
4. **NEVER use `frappe.clear_cache()`** as a routine invalidation strategy — it clears ALL cache keys for the site, causing a cold-cache performance hit.
5. **ALWAYS prefix custom cache keys** with your app name (e.g., `myapp|exchange_rate`) to avoid collisions with Frappe internals.

---

## Redis Configuration

Default config: `{bench}/config/redis_cache.conf`

| Setting | Default | Description |
|---------|---------|-------------|
| Port | 13000 | Redis cache port |
| Bind | 127.0.0.1 | Listen address |
| maxmemory-policy | allkeys-lru | Eviction policy |
| maxmemory | 256mb | Max memory (adjustable) |

---

## Key Namespacing

All cache keys are automatically prefixed by Frappe with the site name:

```python
# You write:
frappe.cache.set_value("my_key", "value")

# Redis stores:
# "mysite.localhost|my_key"
```

`frappe.cache.make_key(key, user, shared)` handles prefixing. The `shared=True` parameter removes the site prefix for cross-site keys (rare use case).

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| `frappe.cache.set_value` | Available | Available | Available |
| `@redis_cache` | Not available | Available | Available |
| `@redis_cache(ttl=)` | Not available | Available | Available |
| `frappe.lock` context mgr | Available | Available | Available |
| `frappe.local.cache` | Available | Available | Available |
| `hget` with generator | Available | Available | Available |

---

## See Also

- [references/examples.md](references/examples.md) — Cache implementation patterns
- [references/anti-patterns.md](references/anti-patterns.md) — Common cache mistakes
- [references/api-reference.md](references/api-reference.md) — Complete API signatures
- `frappe-core-database` — Database queries that benefit from caching
- `frappe-core-permissions` — User permission caching
---
name: frappe-core-database
description: >
  Use when performing database operations in ERPNext/Frappe v14-v16. Covers
  frappe.db methods, ORM patterns (frappe.get_doc, frappe.get_list), raw SQL,
  caching patterns, and performance optimization. Prevents common mistakes
  with database transactions and query building. Keywords: frappe.db,
  frappe.get_doc, database query, SQL, ORM, caching, database performance,
  query returns nothing, slow database, how to fetch data, get document by name, frappe.get_list empty.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Database Operations

## Quick Reference

| Action | Method | Permissions |
|--------|--------|-------------|
| Get document | `frappe.get_doc(doctype, name)` | Yes |
| Cached document | `frappe.get_cached_doc(doctype, name)` | No |
| New document | `frappe.new_doc(doctype)` | — |
| Insert | `doc.insert()` | Yes |
| Save | `doc.save()` | Yes |
| Delete document | `frappe.delete_doc(doctype, name)` | Yes |
| List (with perms) | `frappe.db.get_list(doctype, ...)` | Yes |
| List (no perms) | `frappe.get_all(doctype, ...)` | No |
| Single field | `frappe.db.get_value(doctype, name, field)` | No |
| Single DocType | `frappe.db.get_single_value(doctype, field)` | No |
| Cached value | `frappe.db.get_value(..., cache=True)` | No |
| Direct update | `frappe.db.set_value(doctype, name, field, val)` | No |
| Direct update | `doc.db_set(field, value)` | No |
| Exists check | `frappe.db.exists(doctype, name)` | No |
| Count | `frappe.db.count(doctype, filters)` | No |
| Delete rows | `frappe.db.delete(doctype, filters)` | No |
| Raw SQL | `frappe.db.sql(query, values, as_dict)` | No |
| Query Builder | `frappe.qb.from_(doctype).select(...)` | No |

> **"Permissions" = Yes** means user permission filters are applied automatically.

---

## Decision Tree

```
What do you need?
│
├─ Create / Update / Delete a document?
│  ├─ With validations + hooks → frappe.get_doc() + .insert()/.save()/.delete()
│  └─ Direct DB (no hooks) → frappe.db.set_value() or doc.db_set()
│
├─ Read a single document?
│  ├─ Need full object with methods → frappe.get_doc()
│  ├─ Read-only, rarely changes → frappe.get_cached_doc()
│  └─ Only need 1-2 fields → frappe.db.get_value()
│
├─ List of documents?
│  ├─ Respect user permissions → frappe.db.get_list()
│  └─ System/admin context → frappe.get_all()
│
├─ Single DocType value?
│  └─ frappe.db.get_single_value('Settings', 'field')
│
├─ Check existence?
│  └─ frappe.db.exists() — NEVER use get_doc in try/except
│
├─ Complex query (JOINs, aggregates)?
│  ├─ Cross-DB compatible → frappe.qb (Query Builder)
│  └─ DB-specific SQL → frappe.db.sql() with parameters
│
└─ DB-specific logic?
   └─ frappe.db.multisql({'mariadb': q1, 'postgres': q2})
```

**RULE**: ALWAYS use the highest abstraction level: ORM > Database API > Query Builder > Raw SQL.

---

## ORM: Document Operations

### Get Document
```python
doc = frappe.get_doc('Sales Invoice', 'SINV-00001')

# Single DocType (no name needed)
settings = frappe.get_doc('System Settings')

# Cached (read-only, for rarely-changing docs)
company = frappe.get_cached_doc('Company', 'My Company')

# Last created
last_task = frappe.get_last_doc('Task', filters={'status': 'Open'})
```

### Create Document
```python
doc = frappe.get_doc({
    'doctype': 'Task',
    'subject': 'Review report',
    'status': 'Open'
})
doc.insert()

# Alternative
doc = frappe.new_doc('Task')
doc.subject = 'Review report'
doc.insert()
```

### Update Document
```python
# Via ORM — triggers validate, on_update, etc.
doc = frappe.get_doc('Task', 'TASK-001')
doc.status = 'Completed'
doc.save()

# Direct DB — SKIPS all validations and hooks
frappe.db.set_value('Task', 'TASK-001', 'status', 'Completed')

# Direct DB on loaded doc
doc.db_set('status', 'Completed')
doc.db_set('status', 'Completed', update_modified=False)
doc.db_set({'status': 'Completed', 'priority': 'High'})
```

### Delete Document
```python
frappe.delete_doc('Task', 'TASK-001')
# Also removes linked Communications, Comments, etc.
```

### Insert Flags
```python
doc.insert(
    ignore_permissions=True,     # Bypass permission check
    ignore_links=True,           # Skip link validation
    ignore_if_duplicate=True,    # No error on duplicate
    ignore_mandatory=True        # Skip required field check
)
```

> **RULE**: NEVER use multiple ignore flags together unless you have a documented reason. Each flag you add weakens data integrity.

---

## Database API: Reading

### get_value
```python
# Single field → scalar
status = frappe.db.get_value('Task', 'TASK-001', 'status')

# Multiple fields → tuple
subject, status = frappe.db.get_value('Task', 'TASK-001', ['subject', 'status'])

# As dict
data = frappe.db.get_value('Task', 'TASK-001', ['subject', 'status'], as_dict=True)

# With filters instead of name
status = frappe.db.get_value('Task', {'project': 'PROJ-001'}, 'status')

# Cached (for values that rarely change)
country = frappe.db.get_value('Company', 'MyCompany', 'country', cache=True)
```

### get_single_value
```python
timezone = frappe.db.get_single_value('System Settings', 'time_zone')
```

### get_list / get_all
```python
# get_list — applies user permissions
tasks = frappe.db.get_list('Task',
    filters={'status': 'Open'},
    fields=['name', 'subject', 'assigned_to'],
    order_by='creation desc',
    start=0,
    page_length=50
)

# get_all — NO permission check (same API, different default)
all_tasks = frappe.get_all('Task', filters={'status': 'Open'})

# pluck — returns flat list of single field
names = frappe.get_all('Task', filters={'status': 'Open'}, pluck='name')
# Returns: ['TASK-001', 'TASK-002', ...]
```

### exists / count
```python
exists = frappe.db.exists('User', 'admin@example.com')
exists = frappe.db.exists('User', {'email': 'admin@example.com'})

total = frappe.db.count('Task')
open_count = frappe.db.count('Task', {'status': 'Open'})
```

---

## Filter Operators

```python
{'status': 'Open'}                                    # =
{'status': ['!=', 'Cancelled']}                       # !=
{'amount': ['>', 1000]}                               # >
{'amount': ['>=', 1000]}                              # >=
{'status': ['in', ['Open', 'Working']]}               # IN
{'status': ['not in', ['Cancelled', 'Closed']]}       # NOT IN
{'date': ['between', ['2024-01-01', '2024-12-31']]}   # BETWEEN
{'subject': ['like', '%urgent%']}                      # LIKE
{'description': ['is', 'set']}                         # IS NOT NULL
{'description': ['is', 'not set']}                     # IS NULL
```

### Combining Filters
```python
# AND — all conditions in one dict
filters = {'status': 'Open', 'priority': 'High'}

# AND — list format (allows duplicate fields)
filters = [['status', '=', 'Open'], ['priority', '=', 'High']]

# OR — separate parameter
or_filters = {'priority': 'Urgent', 'status': 'Overdue'}
```

---

## Database API: Writing

### set_value
```python
# Single field
frappe.db.set_value('Task', 'TASK-001', 'status', 'Closed')

# Multiple fields
frappe.db.set_value('Task', 'TASK-001', {'status': 'Closed', 'priority': 'Low'})

# Without updating modified timestamp
frappe.db.set_value('Task', 'TASK-001', 'status', 'Closed', update_modified=False)
```

### delete / truncate
```python
# Delete with filters (DML — can be rolled back)
frappe.db.delete('Error Log', {'creation': ['<', '2024-01-01']})

# Truncate (DDL — CANNOT be rolled back)
frappe.db.truncate('Error Log')
```

### bulk_update [v15+]
```python
frappe.db.bulk_update('Task', {
    'TASK-001': {'status': 'Closed'},
    'TASK-002': {'status': 'Closed'}
}, chunk_size=100)
```

---

## Raw SQL: ALWAYS Parameterized

```python
# ✅ CORRECT — parameterized query
results = frappe.db.sql("""
    SELECT name, subject FROM `tabTask`
    WHERE status = %(status)s AND owner = %(owner)s
""", {'status': 'Open', 'owner': frappe.session.user}, as_dict=True)
```

> **CRITICAL**: NEVER use f-strings, % formatting, or string concatenation in SQL. See [SQL Injection Prevention](#sql-injection-prevention).

### Return Types
```python
frappe.db.sql(query)                    # Tuple of tuples (default)
frappe.db.sql(query, as_dict=True)      # List of dicts
frappe.db.sql(query, as_list=True)      # List of lists
```

### Table Naming
ALWAYS use backtick-quoted `tab` prefix: `` `tabSales Invoice` ``, `` `tabTask` ``

### Database-Specific SQL
```python
frappe.db.multisql({
    'mariadb': "SELECT IFNULL(field, 0) FROM `tabDoc`",
    'postgres': "SELECT COALESCE(field, 0) FROM `tabDoc`"
})
```

---

## Query Builder (frappe.qb) [v14+]

The Query Builder uses PyPika under the hood. It generates parameterized SQL automatically.

```python
Task = frappe.qb.DocType('Task')

results = (
    frappe.qb.from_(Task)
    .select(Task.name, Task.subject, Task.status)
    .where(Task.status == 'Open')
    .orderby(Task.creation, order='desc')
    .limit(10)
).run(as_dict=True)
```

### JOINs
```python
SI = frappe.qb.DocType('Sales Invoice')
Customer = frappe.qb.DocType('Customer')

results = (
    frappe.qb.from_(SI)
    .inner_join(Customer).on(SI.customer == Customer.name)
    .select(SI.name, SI.grand_total, Customer.customer_name)
    .where(SI.docstatus == 1)
).run(as_dict=True)
```

### Aggregates
```python
from frappe.query_builder.functions import Count, Sum, Avg

stats = (
    frappe.qb.from_(Task)
    .select(Task.status, Count(Task.name).as_('count'))
    .groupby(Task.status)
).run(as_dict=True)
```

### OR Conditions
```python
customers = frappe.qb.DocType('Customer')
results = (
    frappe.qb.from_(customers)
    .select(customers.name)
    .where(
        (customers.territory == 'US') | (customers.territory == 'UK')
    )
).run(as_dict=True)
```

### Inspect Generated SQL
```python
query = frappe.qb.from_(Task).select('*').where(Task.name == 'X')
sql, params = query.walk()   # Returns (sql_string, param_dict)
sql_str = query.get_sql()    # Returns SQL string
```

> See `references/query-patterns.md` for subqueries, ImportMapper, ConstantColumn, and custom functions.

---

## Caching

### Document Cache
```python
doc = frappe.get_cached_doc('Company', 'My Company')   # Full document
val = frappe.db.get_value('Company', 'X', 'country', cache=True)  # Single value
```

### Redis Cache
```python
frappe.cache.set_value('key', data, expires_in_sec=3600)
data = frappe.cache.get_value('key')
frappe.cache.delete_value('key')
```

### @redis_cache Decorator
```python
from frappe.utils.caching import redis_cache

@redis_cache(ttl=300)
def get_dashboard_data(user):
    return expensive_calculation(user)

# Invalidate
get_dashboard_data.clear_cache()
```

> See `references/caching-patterns.md` for hash operations, invalidation strategies, and best practices.

---

## Transaction Management

The framework manages transactions automatically:

| Context | Commit | Rollback |
|---------|--------|----------|
| POST/PUT request | After success | On uncaught exception |
| GET request | Never | — |
| Background job | After success | On exception |
| Patch | After success | On exception |

### Manual Transactions (rarely needed)
```python
frappe.db.savepoint('before_payment')
try:
    # operations...
    frappe.db.commit()
except Exception:
    frappe.db.rollback(save_point='before_payment')
```

### Transaction Hooks [v15+]
```python
frappe.db.after_commit.add(sync_to_external_system)
frappe.db.after_rollback.add(cleanup_external_state)
```

---

## SQL Injection Prevention

**CRITICAL SECURITY RULE**: NEVER interpolate user input into SQL strings.

```python
# ❌ VULNERABLE — SQL injection risk
frappe.db.sql(f"SELECT * FROM `tabUser` WHERE name = '{user_input}'")
frappe.db.sql("SELECT * FROM `tabUser` WHERE name = '%s'" % user_input)
frappe.db.sql("SELECT * FROM `tabUser` WHERE name = " + user_input)

# ✅ SAFE — parameterized query
frappe.db.sql("SELECT * FROM `tabUser` WHERE name = %(name)s", {'name': user_input})

# ✅ SAFE — ORM / Query Builder (always parameterized)
frappe.get_all('User', filters={'name': user_input})

User = frappe.qb.DocType('User')
frappe.qb.from_(User).select('*').where(User.name == user_input).run()
```

**RULE**: When you MUST use `frappe.db.sql()`, ALWAYS use `%(param)s` placeholders with a dict. The Query Builder (`frappe.qb`) is ALWAYS preferred over raw SQL for new code.

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| Query Builder (frappe.qb) | Yes | Yes | Yes |
| Transaction hooks | No | Yes | Yes |
| `bulk_update` | No | Yes | Yes |
| `run=False` returns | SQL string | SQL string | Query Builder object |
| Aggregate field syntax | String | String | Dict |

### v16 Breaking Changes
```python
# v14/v15 — string aggregates
fields=['count(name) as count']

# v16 — dict aggregates
fields=[{'COUNT': 'name', 'as': 'count'}]

# v14/v15 — run=False returns SQL string
sql = frappe.db.get_list('Task', run=False)

# v16 — run=False returns Query Builder object
qb_obj = frappe.db.get_list('Task', run=False)
sql = qb_obj.get_sql()
```

---

## Critical Rules Summary

1. **NEVER** use string formatting in SQL — ALWAYS use parameterized queries
2. **NEVER** call `frappe.db.commit()` inside controller hooks (validate, on_update, etc.)
3. **ALWAYS** paginate list queries — use `page_length` parameter
4. **ALWAYS** specify fields — NEVER use `fields=['*']` in production
5. **ALWAYS** use `frappe.db.exists()` for existence checks — NEVER try/except with get_doc
6. **ALWAYS** prefix table names with `tab` in raw SQL: `` `tabSales Invoice` ``
7. **NEVER** use multiple ignore flags without documented justification
8. **ALWAYS** use batch fetching to avoid N+1 queries
9. **ALWAYS** prefer `frappe.qb` over `frappe.db.sql()` for new code
10. **NEVER** use `frappe.db.truncate()` without understanding it CANNOT be rolled back

---

## Query Builder: Dedicated Skill

For complex queries (joins, aggregations, subqueries, cross-DB compatibility), see **[frappe-syntax-query-builder](../../syntax/frappe-syntax-query-builder/SKILL.md)**.
- **frappe.db methods** (this skill) — Simple CRUD, get_value, get_list, exists checks
- **frappe.qb** (query-builder skill) — Joins, GROUP BY, HAVING, subqueries, cross-DB functions
- **frappe.db.sql** — Very complex SQL not expressible in qb (ALWAYS parameterized)

## Reference Files

- **[methods-reference.md](references/methods-reference.md)** — Complete API signatures for all database and document methods
- **[query-patterns.md](references/query-patterns.md)** — Query Builder patterns, subqueries, ImportMapper, custom functions
- **[caching-patterns.md](references/caching-patterns.md)** — Redis cache, @redis_cache, hash operations, invalidation
- **[examples.md](references/examples.md)** — Real-world patterns: CRUD, reports, batch processing, transactions
- **[anti-patterns.md](references/anti-patterns.md)** — SQL injection, N+1, commit mistakes, and 10 more anti-patterns
---
name: frappe-core-files
description: >
  Use when handling file uploads, attachments, private/public file access, or S3 storage configuration.
  Prevents broken file URLs, permission leaks on private files, and failed uploads from incorrect MIME handling.
  Covers File DocType, frappe.get_file, upload API, private vs public directories, S3 integration, file URL patterns, attach field types.
  Keywords: file, upload, attachment, File DocType, private, public, S3, file_url, get_file, attach, upload not working, file missing, broken file link, download file, image not showing, attachment error..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe File Management

## Quick Reference

| Action | Method | Notes |
|--------|--------|-------|
| Save file from bytes | `save_file(fname, content, dt, dn)` | Returns File doc |
| Save file from URL | `save_url(file_url, fname, dt, dn)` | Creates File doc from URL |
| Read file content | `frappe.get_file(fname)` | Returns `[filename, content]` |
| Get file path | `get_file_path(file_name)` | Resolves to absolute path |
| Upload via HTTP | `POST /api/method/upload_file` | Multipart form upload |
| Delete file | `frappe.delete_doc("File", name)` | Removes doc + filesystem file |
| Attach print | `frappe.attach_print(dt, dn, print_format)` | Returns `{"fname", "fcontent"}` |
| Get cached doc | `frappe.get_cached_doc("File", name)` | Read-only, cached |

---

## Decision Tree

```
What file operation do you need?
│
├─ Upload a file from user input?
│  ├─ Via web form → Attach field type (auto-handles upload)
│  └─ Via API → POST /api/method/upload_file
│
├─ Create a file programmatically?
│  ├─ From bytes/content → save_file(fname, content, dt, dn)
│  ├─ From external URL → save_url(file_url, fname, dt, dn)
│  └─ Full control → frappe.get_doc({"doctype": "File", ...}).insert()
│
├─ Read file content?
│  ├─ By filename → frappe.get_file(fname)
│  └─ By File doc → file_doc.get_content()
│
├─ Public or private?
│  ├─ Public (anyone with link) → is_private=0, URL: /files/fname
│  └─ Private (permission-based) → is_private=1, URL: /private/files/fname
│
└─ Generate PDF attachment?
   └─ frappe.attach_print(doctype, name, print_format)
```

---

## File DocType: Core Fields

| Field | Type | Description |
|-------|------|-------------|
| `file_name` | Data | Filename without path |
| `file_url` | Data | URL path (e.g., `/files/report.pdf`) |
| `file_type` | Data | Extension (PDF, PNG, DOCX, etc.) |
| `is_private` | Check | 0 = public, 1 = private |
| `is_folder` | Check | True for folder entries |
| `folder` | Link → File | Parent folder |
| `attached_to_doctype` | Link → DocType | Parent document type |
| `attached_to_name` | Data | Parent document name |
| `attached_to_field` | Data | Field name on parent |
| `content_hash` | Data | SHA-256 for deduplication |
| `file_size` | Int | Size in bytes |

---

## File URL Patterns

| Type | URL Pattern | Filesystem Path |
|------|------------|-----------------|
| Public | `/files/{filename}` | `{site}/public/files/{filename}` |
| Private | `/private/files/{filename}` | `{site}/private/files/{filename}` |
| Remote | `https://...` | Not stored locally |
| API | `/api/method/{path}` | Generated dynamically |

Valid URL prefixes: `http://`, `https://`, `/api/method/`, `/files/`, `/private/files/`.

ALWAYS use `/private/files/` for sensitive documents. Public files are accessible to anyone with the URL, including unauthenticated users.

---

## Permission Model

Frappe files use a three-tier permission model:

1. **Administrator** — unrestricted access to all files
2. **Public files** (`is_private=0`) — readable by anyone with the URL (no authentication required for read)
3. **Private files** (`is_private=1`) — access requires:
   - User is the file owner, OR
   - User has explicit share on the file, OR
   - User has read permission on the `attached_to_doctype`/`attached_to_name` document

NEVER store sensitive data as public files. ALWAYS set `is_private=1` for documents containing personal data, financial records, or confidential information.

---

## Programmatic File Operations

### Save File from Content

```python
from frappe.utils.file_manager import save_file

# Save a generated CSV
csv_content = "Name,Amount\nACME,1000\nGlobex,2000"
file_doc = save_file(
    fname="report.csv",
    content=csv_content.encode("utf-8"),
    dt="Sales Invoice",           # attach to this DocType
    dn="SINV-00001",              # attach to this document
    folder="Home/Attachments",    # optional folder
    is_private=1,                 # private file
)
# file_doc.file_url → "/private/files/report.csv"
```

### Save File from URL

```python
from frappe.utils.file_manager import save_url

file_doc = save_url(
    file_url="https://example.com/logo.png",
    filename="company-logo.png",
    dt="Company",
    dn="My Company",
    folder="Home",
    is_private=0,
)
```

### Read File Content

```python
# By filename
filename, content = frappe.get_file("report.csv")

# By File document
file_doc = frappe.get_doc("File", {"file_name": "report.csv"})
content_bytes = file_doc.get_content()
```

### Create File Document Directly

```python
file_doc = frappe.get_doc({
    "doctype": "File",
    "file_name": "generated-report.pdf",
    "attached_to_doctype": "Sales Invoice",
    "attached_to_name": "SINV-00001",
    "is_private": 1,
    "content": pdf_bytes,  # raw bytes — written to disk on insert
}).insert(ignore_permissions=True)
```

### Generate and Attach PDF

```python
# Create PDF attachment dict (for use with sendmail)
pdf_attachment = frappe.attach_print(
    "Sales Invoice",
    "SINV-00001",
    print_format="Standard",
)
# Returns: {"fname": "Sales Invoice - SINV-00001.pdf", "fcontent": <bytes>}

# Save PDF as file attachment
from frappe.utils.file_manager import save_file

pdf = frappe.get_print("Sales Invoice", "SINV-00001", print_format="Standard", as_pdf=True)
save_file("invoice.pdf", pdf, "Sales Invoice", "SINV-00001", is_private=1)
```

---

## File Upload via REST API

```bash
# Upload file attached to a document
curl -X POST https://site.example.com/api/method/upload_file \
  -H "Authorization: token api_key:api_secret" \
  -F "file=@/path/to/document.pdf" \
  -F "doctype=Sales Invoice" \
  -F "docname=SINV-00001" \
  -F "is_private=1"
```

Response:
```json
{
  "message": {
    "name": "FILE-00001",
    "file_name": "document.pdf",
    "file_url": "/private/files/document.pdf",
    "is_private": 1
  }
}
```

---

## File Size and Extension Limits

**Default max file size:** 10 MB per attachment.

Override in `site_config.json`:
```json
{
  "max_file_size": 20971520
}
```

**Max attachments per document:** Set via Customize Form → Max Attachments field on the DocType.

**Check file size programmatically:**
```python
from frappe.utils.file_manager import check_max_file_size
check_max_file_size(content)  # raises MaxFileSizeReachedError if too large
```

---

## Attach Field Types

| Field Type | Stores | UI |
|------------|--------|----|
| `Attach` | Single file URL | File picker + upload button |
| `Attach Image` | Single image URL | Image preview + upload |

Both store the `file_url` string in the field value. The File DocType record is created separately with `attached_to_field` set.

---

## S3 / Cloud Storage Integration

Frappe supports custom file storage via the `delete_file_data_content` hook and custom upload handlers.

### S3 via frappe-s3-attachment or similar app

```python
# In hooks.py of custom app
delete_file_data_content = "my_app.storage.delete_from_s3"
```

ALWAYS test file deletion when using custom storage backends — the default `delete_file_from_filesystem` only handles local files.

### Configuration Pattern

```python
# site_config.json for S3-compatible storage
{
  "s3_bucket": "my-frappe-files",
  "s3_region": "eu-west-1",
  "s3_access_key": "AKIA...",
  "s3_secret_key": "...",
}
```

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| File DocType | Available | Available | Available |
| `content_hash` dedup | Available | Available | Available |
| Image optimization | Manual | Auto (1920x1080, 85%) | Auto |
| Import/Export Zip | Not available | Available | Available |

---

## See Also

- [references/examples.md](references/examples.md) — File operation code examples
- [references/anti-patterns.md](references/anti-patterns.md) — Common file handling mistakes
- `frappe-core-permissions` — Permission model for file access
- `frappe-core-database` — Database operations for File queries
---
name: frappe-core-logging
description: >
  Use when implementing logging, error tracking, or monitoring in Frappe
  v14-v16. Covers frappe.logger() for file-based logging,
  frappe.log_error() for Error Log DocType entries, request logging,
  Sentry integration, and production logging patterns. Prevents common
  mistakes with print(), swapped log_error arguments, and sensitive data.
  Keywords: frappe.logger, log_error, Error Log, logging, Sentry,, where are the logs, how to log errors, error tracking, print not showing, production logs.
  monitor, request logging, error tracking, debug, production.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "3.0"
---

# Frappe Logging & Error Tracking

## Three Logging Mechanisms

| Mechanism | Storage | Use For |
|-----------|---------|---------|
| `frappe.logger()` | File (rotating) | Application logging, debug info, audit trails |
| `frappe.log_error()` | Database (Error Log DocType) | Errors visible in admin UI, persistent tracking |
| `frappe.log()` / `frappe.errprint()` | stderr / request-scoped | Quick debugging only (NOT for production) |

---

## Decision Tree

```
Need to log something?
│
├─ Application logging (info, debug, warnings)?
│  └─ frappe.logger("my_module").info("message")
│     → Writes to sites/{site}/logs/my_module.log
│
├─ Error that admins should see in Desk UI?
│  └─ frappe.log_error(title="Short desc", message=traceback)
│     → Creates Error Log document (queryable, auto-cleanup)
│
├─ Quick debug during development?
│  └─ frappe.errprint(variable) — shows in console
│     → NEVER leave in production code
│
├─ Track all HTTP requests?
│  └─ Set enable_frappe_logger: true in site_config.json
│     → Logs to frappe.web.log
│
├─ Performance monitoring?
│  └─ Set monitor: true in site_config.json
│     → Logs to monitor.json.log (JSON, per-request metrics)
│
└─ External error tracking (Sentry)?
   └─ Set FRAPPE_SENTRY_DSN environment variable
      → Auto-captures unhandled exceptions
```

---

## Quick Reference: frappe.logger()

```python
# Get a logger for your module (ALWAYS specify module name)
logger = frappe.logger("my_app")

# Standard Python logging levels
logger.debug("Detailed diagnostic info")
logger.info("Normal operations: processed 50 records")
logger.warning("Something unexpected but recoverable")
logger.error("Operation failed", exc_info=True)
logger.critical("System-level failure")

# Full signature
frappe.logger(
    module=None,          # Logger name + log filename
    with_more_info=False, # Auto-log request form_dict
    allow_site=True,      # Log under site's logs/ directory
    filter=None,          # Custom logging.Filter
    max_size=100_000,     # Max bytes per log file (100KB default)
    file_count=20         # Rotated files retained (20 default)
)
```

**Log location:** `sites/{site}/logs/{module}.log`
**Rotation:** RotatingFileHandler — 100KB per file, 20 backups (~2MB total per logger)

### Default Log Levels

| Mode | Level | Effect |
|------|-------|--------|
| Development (`_dev_server`) | WARNING | Debug/info suppressed |
| Production | ERROR | Only errors and above |

```python
# Change level dynamically
frappe.utils.logger.set_log_level("DEBUG")
```

---

## Quick Reference: frappe.log_error()

```python
# ALWAYS use keyword arguments (title/message can swap otherwise)
frappe.log_error(
    title="Payment gateway timeout",          # Short description (140 chars max)
    message=frappe.get_traceback(),            # Full error details
    reference_doctype="Payment Entry",        # Related DocType
    reference_name="PE-00001"                 # Related document
)

# Minimal — auto-captures current traceback
try:
    risky_operation()
except Exception:
    frappe.log_error(title="Operation failed")
```

**Error Log cleanup:** Auto-deletes after 30 days. Manual: `frappe.whitelist: clear_error_logs()`

### Auto-Captured Exceptions

Unhandled exceptions (HTTP 500+) are automatically logged to Error Log.

**Excluded from auto-capture:**
- `frappe.AuthenticationError`
- `frappe.CSRFTokenError`
- `frappe.SecurityException`
- `frappe.InReadOnlyMode`

---

## Production Configuration

### site_config.json Keys

| Key | Value | Effect |
|-----|-------|--------|
| `enable_frappe_logger` | `true` | HTTP request logging → `frappe.web.log` |
| `logging` | `2` | Log all SQL queries (debug only!) |
| `monitor` | `true` | Request/job metrics → `monitor.json.log` |
| `disable_error_snapshot` | `true` | Disable auto-capture of exceptions |

### Environment Variables

| Variable | Effect |
|----------|--------|
| `FRAPPE_STREAM_LOGGING=1` | Log to stderr instead of files |
| `FRAPPE_SENTRY_DSN=<dsn>` | Enable Sentry error tracking |
| `ENABLE_SENTRY_DB_MONITORING` | Track SQL queries in Sentry |
| `SENTRY_TRACING_SAMPLE_RATE` | Performance tracing rate (0.0-1.0) |

### Production Log Files

| File | Content |
|------|---------|
| `logs/web.error.log` | HTTP errors (supervisor) |
| `logs/web.log` | Gunicorn stdout |
| `logs/worker.error.log` | Background job errors |
| `logs/frappe.log` | Default frappe logger |
| `logs/frappe.web.log` | HTTP request metadata |
| `logs/monitor.json.log` | Performance metrics (JSON) |
| `sites/{site}/logs/*.log` | Per-site application logs |

---

## Anti-Patterns

| NEVER | ALWAYS | Why |
|-------|--------|-----|
| `print("debug info")` | `frappe.logger("mod").info(...)` | print() disappears in production |
| `frappe.log_error("info msg")` | `frappe.logger().info(...)` | log_error creates Error Log docs, clutters admin UI |
| `frappe.logger()` (no module) | `frappe.logger("my_module")` | No-module mixes with framework logs |
| `frappe.log_error(title, msg)` positional | `frappe.log_error(title=t, message=m)` | Positional args can swap (known quirk) |
| Log passwords/tokens | Mask sensitive data | SiteContextFilter only masks form_dict |
| `frappe.log()` in production | `frappe.logger()` | frappe.log() is debug-only, request-scoped |
| Leave `logging=2` in prod | Only during debugging | Logs ALL SQL queries, massive I/O |

---

## Version Differences

| Feature | v14 | v15+ |
|---------|:---:|:----:|
| `frappe.logger()` | Yes | Yes |
| `frappe.log_error()` | Yes | + `defer_insert` kwarg |
| Error Log trace_id | -- | Added |
| Error Log metadata | -- | JSON request/job context |
| Error snapshots | File-based + scheduled collection | Direct DB insert |
| Sentry integration | Basic | Enhanced (DB monitoring, profiling) |
| `guess_exception_source()` | -- | Identifies which app caused error |
| `FRAPPE_STREAM_LOGGING` | Yes | Yes |

---

## Reference Files

- [Logger API & Patterns](references/logger-patterns.md) — frappe.logger() advanced usage
- [Error Tracking](references/error-tracking.md) — Error Log, Sentry, monitoring
---
name: frappe-core-notifications
description: >
  Use when implementing email notifications, system alerts, Assignment Rules, Auto Repeat, or ToDo items.
  Prevents misconfigured Email Accounts, broken notification templates, and silent delivery failures.
  Covers frappe.sendmail, Notification DocType, Email Account setup, Jinja email templates, Assignment Rules, Auto Repeat scheduling, ToDo API.
  Keywords: notification, email, sendmail, Email Account, Assignment Rule, Auto Repeat, ToDo, alert, template, notify on approval, email when status changes, alert, email not sending, notification not working..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Notification System

## Quick Reference

| Channel | Method | Use Case |
|---------|--------|----------|
| Email | `frappe.sendmail()` | Programmatic email with full control |
| Email | Notification DocType (Email) | No-code email on document events |
| System | `frappe.publish_realtime()` | In-app real-time alerts via socket.io |
| System | Notification DocType (System) | No-code in-app alerts |
| SMS | Notification DocType (SMS) | No-code SMS on document events |
| Slack | Notification DocType (Slack) | No-code Slack webhook messages |
| Assignment | `frappe.desk.form.assign_to.add()` | Assign document to user (creates ToDo) |
| ToDo | `frappe.get_doc({"doctype": "ToDo", ...})` | Direct task creation |
| Comment | `doc.add_comment("Comment", text)` | Timeline comment on document |
| Tag | `doc.add_tag("tag_name")` | Document tagging for filtering |

---

## Decision Tree

```
What notification mechanism do you need?
│
├─ Email on document event (no code)?
│  └─ Notification DocType → Channel: Email
│
├─ Programmatic email with custom logic?
│  └─ frappe.sendmail() in server script or hook
│
├─ Real-time in-app notification?
│  ├─ No-code → Notification DocType → Channel: System Notification
│  └─ Programmatic → frappe.publish_realtime()
│
├─ SMS on document event?
│  └─ Notification DocType → Channel: SMS (requires SMS Settings)
│
├─ Assign document to user?
│  ├─ No-code → Assignment Rule DocType
│  └─ Programmatic → frappe.desk.form.assign_to.add()
│
├─ Recurring document creation?
│  └─ Auto Repeat DocType
│
└─ Add comment or tag?
   ├─ Comment → doc.add_comment("Comment", text="...")
   └─ Tag → doc.add_tag("tag_name")
```

---

## Notification DocType

The Notification DocType enables no-code alerts across four channels.

### Event Triggers

| Event | Fires When |
|-------|------------|
| New | Document is created |
| Save | Document is saved |
| Submit | Document is submitted |
| Cancel | Document is cancelled |
| Value Change | Specific field value changes |
| Days Before | N days before a date field value |
| Days After | N days after a date field value |
| Method | Custom Python method is called |

### Condition Syntax

ALWAYS use Python expressions in the Condition field:

```python
# Status-based
doc.status == "Open"

# Date-based
doc.due_date == nowdate()

# Threshold-based
doc.grand_total > 40000

# Combined
doc.status == "Overdue" and doc.grand_total > 10000
```

Available context: `doc`, `nowdate()`, `frappe.utils.*`.

### Recipient Configuration

| Source | Description |
|--------|-------------|
| Document Field | Email/phone field on the document |
| Role | All users with specified role |
| Custom | Hard-coded email address |
| All Assignees | All users assigned to the document |
| Condition | Jinja expression to filter recipients |

### Jinja Message Template

```html
<h3>Order Overdue</h3>
<p>Transaction {{ doc.name }} has exceeded its due date.</p>

{% if comments %}
Last comment: {{ comments[-1].comment }} by {{ comments[-1].by }}
{% endif %}

<ul>
  <li>Customer: {{ doc.customer }}</li>
  <li>Amount: {{ doc.grand_total }}</li>
</ul>
```

Template variables: `{{ doc }}`, `{{ doc.fieldname }}`, `{{ comments }}`, `{{ nowdate() }}`.

### Attach Print

Set **Attach Print** to include a PDF of the document. Select a **Print Format** for custom layout.

---

## frappe.sendmail(): Programmatic Email

```python
frappe.sendmail(
    recipients=["user@example.com"],       # list of email addresses
    subject="Invoice Due",                  # email subject
    message="<p>Your invoice is due.</p>",  # HTML body
    template="invoice_reminder",            # Jinja template name (optional)
    args={"customer": "ACME"},              # template context variables
    attachments=[{"fname": "inv.pdf", "fcontent": pdf_bytes}],
    reference_doctype="Sales Invoice",      # links email to document
    reference_name="SINV-00001",
    delayed=True,                           # queue via Email Queue (default)
    now=False,                              # True = send immediately, skip queue
    sender="noreply@example.com",           # override sender
    cc=["manager@example.com"],
    bcc=["audit@example.com"],
    reply_to="support@example.com",
    expose_recipients="header",             # show recipients in email header
)
```

**Rules**:
- ALWAYS set `reference_doctype` and `reference_name` when the email relates to a document — this links the email in the document timeline.
- NEVER set `now=True` in production — it blocks the request. Use `delayed=True` (default) to queue via Email Queue.
- ALWAYS ensure an Email Account with "Enable Outgoing" is configured before calling `frappe.sendmail`.

### Email Queue

Emails are queued in the **Email Queue** DocType and sent by the scheduler. Check queue status:

```python
# Check pending emails
pending = frappe.get_all("Email Queue", filters={"status": "Not Sent"}, limit=10)
```

---

## frappe.publish_realtime(): System Notifications

```python
frappe.publish_realtime(
    event="msgprint",                      # event name
    message={"msg": "Task completed!"},    # dict payload
    user="user@example.com",               # target specific user
    doctype="Sales Invoice",               # broadcast to doctype room
    docname="SINV-00001",                  # broadcast to document room
    after_commit=True,                     # emit after transaction commits
)
```

### Room Types

| Room | Audience |
|------|----------|
| `user:{email}` | Single user (set `user=`) |
| `doctype:{dt}` | All users viewing that list |
| `doc:{dt}/{dn}` | All users viewing that document |
| `all` | All Desk users site-wide |
| `task_progress:{id}` | Background task progress |

### Built-in Events

| Event | Purpose |
|-------|---------|
| `msgprint` | Show message dialog to user |
| `list_update` | Refresh document list view |
| `docinfo_update` | Refresh document info sidebar |
| `progress` | Show progress bar |

ALWAYS set `after_commit=True` when publishing from within a database transaction — otherwise the event fires before data is committed and the client may read stale data.

---

## Assignment Rules

Auto-assign documents to users based on conditions (no code).

### Configuration Fields

| Field | Purpose |
|-------|---------|
| Document Type | Which DocType triggers the rule |
| Assign Condition | Python expression (same as Notification) |
| Assignment Days | Limit to specific weekdays |
| Users | List of users to assign to |
| Assignment Rule | Round Robin, Load Balancing, or Based on Field |

### Programmatic Assignment

```python
from frappe.desk.form.assign_to import add, remove, close, clear

# Assign
add({
    "assign_to": ["user@example.com"],
    "doctype": "Task",
    "name": "TASK-00001",
    "description": "Please review this task",
    "priority": "High",
    "date": "2025-12-31",
})

# Remove assignment (cancels ToDo)
remove("Task", "TASK-00001", "user@example.com")

# Close assignment (only assignee can close)
close("Task", "TASK-00001", "user@example.com")

# Clear all assignments
clear("Task", "TASK-00001")
```

NEVER call `close()` as a different user than the assignee — it raises a permission error.

---

## Auto Repeat

Creates recurring copies of documents on a schedule.

| Field | Purpose |
|-------|---------|
| Reference DocType | Which DocType to repeat |
| Reference Document | Source document to copy |
| Frequency | Daily, Weekly, Monthly, Quarterly, Half-yearly, Yearly |
| Start Date / End Date | Schedule window |
| Notify By Email | Send notification on creation |

ALWAYS set an **End Date** on Auto Repeat — open-ended schedules create documents indefinitely and are difficult to debug.

---

## ToDo API

```python
# Create ToDo directly
todo = frappe.get_doc({
    "doctype": "ToDo",
    "allocated_to": "user@example.com",
    "assigned_by": frappe.session.user,
    "description": "Review the quarterly report",
    "priority": "Medium",
    "date": "2025-12-31",
    "status": "Open",
    "reference_type": "Task",
    "reference_name": "TASK-00001",
}).insert(ignore_permissions=True)
```

ToDo statuses: `Open`, `Closed`, `Cancelled`.

---

## Comments and Tags

```python
# Add comment (appears in document timeline)
doc.add_comment("Comment", text="Reviewed and approved")
doc.add_comment("Edit", "Values changed")

# Add/get tags
doc.add_tag("urgent")
tags = doc.get_tags()  # returns list of tag strings
```

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| Notification DocType | All 4 channels | All 4 channels | All 4 channels |
| Minutes Before/After | Not available | Available | Available |
| `frappe.publish_realtime` | Available | Available | Available |
| Assignment Rules | Available | Available | Available |

---

## See Also

- [references/email-system.md](references/email-system.md) — Email Account, Email Queue, Communication linking, Newsletter, Notification Log
- [references/examples.md](references/examples.md) — Full notification workflow examples
- [references/anti-patterns.md](references/anti-patterns.md) — Common mistakes and fixes
- [references/api-reference.md](references/api-reference.md) — Complete API signatures
- `frappe-core-database` — Database operations referenced in notifications
- `frappe-core-permissions` — Permission model for notification access
---
name: frappe-core-permissions
description: >
  Use when implementing the Frappe/ERPNext permission system. Covers roles,
  user permissions, perm levels, data masking, and permission hooks for
  v14/v15/v16. Prevents common access control mistakes and security issues.
  Keywords: permissions, roles, user permissions, perm levels, data masking,, restrict records, who can see what, department access, row-level, user cannot see document, access denied.
  access control, security, has_permission.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Permissions

> Deterministic patterns for the five-layer Frappe permission system.

---

## Permission Layers

| Layer | Controls | Configured Via | Version |
|-------|----------|----------------|---------|
| **Role Permissions** | What users CAN do | DocType permissions table | All |
| **User Permissions** | WHICH records users see | User Permission DocType | All |
| **Perm Levels** | WHICH fields users see/edit | Field `permlevel` property | All |
| **Permission Hooks** | Custom deny logic | `hooks.py` | All |
| **Data Masking** | Masked field values | Field `mask` property | [v16+] |

---

## Decision Tree

```
Need to control access?
├── Who can Create/Read/Write/Delete a DocType? → Role Permissions
├── Which specific records can a user see? → User Permissions
├── Which fields should be hidden? → Perm Levels (permlevel 1+)
├── Which fields show masked values? → Data Masking [v16+]
├── Custom runtime deny logic? → has_permission hook
├── Filter list queries dynamically? → permission_query_conditions hook
└── Share one document with one user? → frappe.share

Checking permissions in code?
├── Before action → frappe.has_permission() or doc.has_permission()
├── Raise on denial → doc.check_permission() or throw=True
├── System bypass → doc.flags.ignore_permissions = True (ALWAYS document why)
└── List query → ALWAYS use frappe.get_list() for user-facing data
```

---

## Permission Types

| Type | API Check | Applies To |
|------|-----------|------------|
| `read` | `frappe.has_permission(dt, "read")` | All DocTypes |
| `write` | `frappe.has_permission(dt, "write")` | All DocTypes |
| `create` | `frappe.has_permission(dt, "create")` | All DocTypes |
| `delete` | `frappe.has_permission(dt, "delete")` | All DocTypes |
| `submit` | `frappe.has_permission(dt, "submit")` | Submittable only |
| `cancel` | `frappe.has_permission(dt, "cancel")` | Submittable only |
| `amend` | `frappe.has_permission(dt, "amend")` | Submittable only |
| `select` | `frappe.has_permission(dt, "select")` | Link fields [v14+] |
| `report` | N/A | Report Builder access |
| `export` | N/A | Excel/CSV export |
| `import` | N/A | Data Import Tool |
| `share` | N/A | Share with other users |
| `print` | N/A | Print/PDF generation |
| `email` | N/A | Send email |
| `mask` | Role permission for unmasked view | Data Masking [v16+] |

---

## Automatic Roles

| Role | Assigned To | Notes |
|------|-------------|-------|
| `Guest` | Everyone (including anonymous) | Public pages |
| `All` | All registered users | Basic authenticated access |
| `Administrator` | Only the Administrator user | ALWAYS has all permissions |
| `Desk User` | System Users only | [v15+] |

---

## Essential API

### Check Permission

```python
# DocType-level
frappe.has_permission("Sales Order", "write")

# Document-level (by name or object)
frappe.has_permission("Sales Order", "write", "SO-00001")
frappe.has_permission("Sales Order", "write", doc=doc)

# For specific user
frappe.has_permission("Sales Order", "read", user="john@example.com")

# Throw on denial
frappe.has_permission("Sales Order", "delete", throw=True)

# Debug mode — prints evaluation steps
frappe.has_permission("Sales Order", "read", debug=True)
print(frappe.local.permission_debug_log)
```

### Document Instance Methods

```python
doc = frappe.get_doc("Sales Order", "SO-00001")

# Returns bool
if doc.has_permission("write"):
    doc.status = "Approved"
    doc.save()

# Raises frappe.PermissionError if denied
doc.check_permission("write")
```

### Get Effective Permissions

```python
from frappe.permissions import get_doc_permissions

perms = get_doc_permissions(doc)
# {'read': 1, 'write': 1, 'create': 0, 'delete': 0, ...}

perms = get_doc_permissions(doc, user="john@example.com")
```

---

## User Permissions (Record-Level)

Restrict users to specific Link field values (e.g., specific Company, Territory).

```python
from frappe.permissions import add_user_permission, remove_user_permission

# Restrict user to one company
add_user_permission(
    doctype="Company",
    name="My Company",
    user="john@example.com",
    is_default=1,            # auto-fill in new documents
    applicable_for="Sales Order"  # only for this DocType (optional)
)

# Remove restriction
remove_user_permission("Company", "My Company", "john@example.com")

# Query current restrictions
from frappe.permissions import get_user_permissions
perms = get_user_permissions("john@example.com")
# {"Company": [{"doc": "My Company", "is_default": 1}], ...}
```

---

## Sharing (Document-Level)

Grant access to a single document for a specific user.

```python
from frappe.share import add as add_share, remove as remove_share

add_share("Sales Order", "SO-00001", "jane@example.com",
          read=1, write=1, share=0, notify=1)

remove_share("Sales Order", "SO-00001", "jane@example.com")

# Share with everyone
add_share("Sales Order", "SO-00001", everyone=1, read=1)
```

---

## Field-Level Permissions (Perm Levels)

Group fields by `permlevel` (0-9). Level 0 MUST be granted before higher levels.

```json
{
  "fields": [
    {"fieldname": "employee_name", "permlevel": 0},
    {"fieldname": "salary",        "permlevel": 1}
  ],
  "permissions": [
    {"role": "Employee",   "permlevel": 0, "read": 1},
    {"role": "HR Manager", "permlevel": 0, "read": 1, "write": 1},
    {"role": "HR Manager", "permlevel": 1, "read": 1, "write": 1}
  ]
}
```

**Rule**: Levels do NOT imply hierarchy. Level 2 is not "higher" than level 1. They are independent field groups.

---

## Data Masking [v16+]

Fields with `mask=1` show masked values (e.g., `****`, `+91-811XXXXXXX`) to users without `mask` permission.

```json
{
  "fieldname": "phone_number", "fieldtype": "Data", "mask": 1
}
```

Grant `mask` permission to roles that MUST see unmasked values:

```json
{"role": "HR Manager", "permlevel": 0, "read": 1, "mask": 1}
```

**CRITICAL**: Data masking does NOT apply to `frappe.db.sql()` or Query Reports with raw SQL. You MUST mask manually in custom SQL queries.

---

## Permission Hooks

### has_permission: Custom Deny Logic

Can only **deny** access. NEVER returns `True` to grant. ALWAYS returns `None` to continue standard checks.

```python
# hooks.py
has_permission = {
    "Sales Order": "myapp.permissions.check_order_permission"
}
```

```python
# myapp/permissions.py
def check_order_permission(doc, ptype, user):
    if ptype == "write" and doc.docstatus == 2:
        if "Sales Manager" not in frappe.get_roles(user):
            return False
    return None  # ALWAYS return None by default
```

### permission_query_conditions: Filter List Queries

Returns SQL WHERE clause fragment. Only affects `get_list()`, NOT `get_all()`.

```python
# hooks.py
permission_query_conditions = {
    "Customer": "myapp.permissions.customer_query"
}
```

```python
def customer_query(user):
    if not user:
        user = frappe.session.user
    if "Sales Manager" in frappe.get_roles(user):
        return ""
    return f"`tabCustomer`.owner = {frappe.db.escape(user)}"
```

**ALWAYS** use `frappe.db.escape()` — NEVER use string concatenation with raw user input.

---

## get_list vs get_all

| Method | User Permissions | Query Hook | Use For |
|--------|------------------|------------|---------|
| `frappe.get_list()` | Applied | Applied | User-facing queries |
| `frappe.get_all()` | Ignored | Ignored | System/background queries |

**ALWAYS** use `get_list()` when returning data to users. `get_all()` bypasses ALL permission filtering.

---

## Common Patterns

### Owner-Only Edit

```json
{"role": "Sales User", "read": 1, "write": 1, "create": 1, "if_owner": 1}
```

### Role-Restricted Endpoint

```python
@frappe.whitelist()
def sensitive_action():
    frappe.only_for(["Manager", "Administrator"])
    # Only reaches here if user has one of these roles
```

### Bypass Permissions (Document Why!)

```python
# On document — ALWAYS add a comment explaining the reason
doc.flags.ignore_permissions = True
doc.save()

# On method call
doc.save(ignore_permissions=True)
doc.insert(ignore_permissions=True)
```

---

## Critical Rules

1. **ALWAYS** use `frappe.has_permission()` — NEVER check roles directly for access control
2. **ALWAYS** use `frappe.get_list()` for user-facing queries — NEVER `get_all()`
3. **ALWAYS** escape SQL in query hooks — `frappe.db.escape(user)`
4. **ALWAYS** prefix table names in query hooks — `` `tabDocType`.fieldname ``
5. **ALWAYS** return `None` in `has_permission` hooks by default — NEVER `True`
6. **ALWAYS** clear cache after permission changes — `frappe.clear_cache()`
7. **ALWAYS** document `ignore_permissions` usage with a comment
8. **NEVER** throw errors in `has_permission` hooks — return `False` to deny
9. **NEVER** grant permlevel 1+ without granting permlevel 0 first
10. **NEVER** assume data masking applies to custom SQL queries [v16+]

---

## Anti-Patterns

| Do NOT | Do Instead |
|--------|------------|
| `if "Role" in frappe.get_roles()` for access | `frappe.has_permission(dt, ptype)` |
| `frappe.get_all()` for user queries | `frappe.get_list()` |
| `return True` in has_permission hook | `return None` |
| `f"owner = '{user}'"` in SQL | `f"owner = {frappe.db.escape(user)}"` |
| `frappe.throw()` in permission hooks | `return False` |
| `frappe.db.set_value()` for user-facing updates | `doc.save()` with permission check |
| Sensitive data in error messages | Generic `frappe.PermissionError` |

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| `select` permission | Yes | Yes | Yes |
| `Desk User` role | No | Yes | Yes |
| Data Masking (`mask` field) | No | No | Yes |
| `mask` permission type | No | No | Yes |
| Custom Permission Types | No | No | Experimental |

---

## Permission Precedence

1. **Administrator** — ALWAYS has all permissions (cannot be restricted)
2. **Role Permissions** — Based on assigned roles
3. **User Permissions** — Restricts to specific document values
4. **has_permission hook** — Can only deny (any `False` = denied)
5. **Sharing** — Grants access to shared documents
6. **if_owner** — Further restricts to owned documents

---

## Reference Files

| File | Contents |
|------|----------|
| [permission-types-reference.md](references/permission-types-reference.md) | All permission types with options |
| [permission-api-reference.md](references/permission-api-reference.md) | Complete API with all signatures |
| [permission-hooks-reference.md](references/permission-hooks-reference.md) | Hook patterns and examples |
| [examples.md](references/examples.md) | Working implementation examples |
| [anti-patterns.md](references/anti-patterns.md) | Common mistakes and fixes |

## Related Skills

- `frappe-core-database` — Database operations that respect permissions
- `frappe-core-api` — API endpoints with permission checks
- `frappe-syntax-controllers` — Controller permission validation
- `frappe-syntax-hooks` — Hook configuration patterns

---

*Verified against Frappe docs 2026-03-20 | Frappe v14/v15/v16*
---
name: frappe-core-search
description: >
  Use when implementing search functionality in Frappe v14-v16.
  Covers link field search (search_link), global search, FullTextSearch
  (Whoosh), SQLiteSearch FTS5 [v15+], Awesomebar customization,
  search_fields configuration, custom search queries, and website search.
  Prevents common mistakes with missing search_fields and permission filtering.
  Keywords: search, search_link, global_search, FullTextSearch, Awesomebar,, search not finding, link field empty, autocomplete not working, global search missing results.
  search_fields, standard_queries, SQLiteSearch, FTS5, Whoosh.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "3.0"
---

# Frappe Search System

## Four Search Subsystems

| Subsystem | Module | Purpose | Real-time? |
|-----------|--------|---------|:----------:|
| **Link Field Search** | `frappe.desk.search` | Autocomplete in link fields | Yes |
| **Global Search** | `frappe.utils.global_search` | Cross-doctype search (desk + web) | No (15min sync) |
| **FullTextSearch** | `frappe.search.full_text_search` | Whoosh-based index (website) | On rebuild |
| **SQLiteSearch** [v15+] | `frappe.search.sqlite_search` | FTS5 with scoring + spelling | Yes (5min queue) |

---

## Decision Tree

```
What search do you need?
│
├─ Link field autocomplete (user types in a Link field)?
│  ├─ Default behavior sufficient → Configure search_fields on DocType
│  └─ Custom logic needed → standard_queries hook or query parameter
│
├─ Cross-doctype search (user searches for anything)?
│  ├─ Desk users → Global Search (auto-enabled)
│  │  └─ Set in_global_search=1 on important fields
│  └─ Website visitors → web_search() or WebsiteSearch (Whoosh)
│
├─ Custom full-text search for your app [v15+]?
│  └─ SQLiteSearch subclass + sqlite_search hook
│     → Spelling correction, recency boost, custom scoring
│
└─ Awesomebar customization?
   └─ Client-side: override build_options or use search dialog
```

---

## Link Field Search

### Configuring search_fields (Most Common Need)

```python
# In DocType JSON or via customize form
{
    "search_fields": "customer_name, customer_group",
    "title_field": "customer_name",
    "show_title_field_in_link": 1
}
```

**ALWAYS set `search_fields`** — Without it, users can only search by `name` (often a code like `CUST-001`).

### How Link Search Works

1. User types in link field → calls `search_link(doctype, txt)`
2. Searches across: `name` + `title_field` + `search_fields`
3. Allowed field types: Data, Text, Small Text, Long Text, Link, Select, Autocomplete, Read Only, Text Editor
4. Prefix matches rank higher than substring matches
5. Respects `enabled`/`disabled` fields automatically

### Custom Link Query

```python
# hooks.py — override search for a specific DocType
standard_queries = {
    "Customer": "my_app.queries.customer_query"
}
```

```python
# my_app/queries.py — MUST be @frappe.whitelist()
@frappe.whitelist()
def customer_query(doctype, txt, searchfield, start, page_length, filters,
                   as_dict=False, reference_doctype=None,
                   ignore_user_permissions=False):
    # Return list of dicts: [{"value": name, "description": label}, ...]
    return frappe.db.sql("""
        SELECT name, customer_name as description
        FROM `tabCustomer`
        WHERE (name LIKE %(txt)s OR customer_name LIKE %(txt)s)
        AND status = 'Active'
        ORDER BY customer_name
        LIMIT %(start)s, %(page_length)s
    """, {"txt": f"%{txt}%", "start": start, "page_length": page_length},
    as_dict=True)
```

### Per-Field Query Override

```javascript
// In Client Script or Form JS
frappe.ui.form.on("Sales Order", {
    setup(frm) {
        frm.set_query("customer", () => ({
            filters: { status: "Active", territory: frm.doc.territory }
        }));
    }
});
```

---

## Global Search

### Enabling

Set `in_global_search = 1` on DocType fields that should be searchable.

### How It Works

- Indexed fields stored in `__global_search` table
- Synced via Redis queue every 15 minutes
- Uses DB-native fulltext: MariaDB `MATCH...AGAINST`, PostgreSQL `TSVECTOR`
- Permission-filtered results

### Rebuilding Index

```python
# Rebuild for specific DocType
from frappe.utils.global_search import rebuild_for_doctype
rebuild_for_doctype("Sales Order")

# Rebuild everything
from frappe.utils.global_search import rebuild
rebuild()
```

### hooks.py Configuration

```python
# Default doctypes for global search
global_search_doctypes = {
    "Default": [
        {"doctype": "Contact"},
        {"doctype": "Customer"},
        {"doctype": "Sales Order"},
    ]
}
```

---

## SQLiteSearch [v15+]

### Creating Custom Search

```python
# my_app/search.py
from frappe.search.sqlite_search import SQLiteSearch

class ProjectSearch(SQLiteSearch):
    INDEX_SCHEMA = {
        "metadata_fields": ["project", "owner", "status"],
        "tokenizer": "unicode61 remove_diacritics 2 tokenchars '-_'",
    }

    INDEXABLE_DOCTYPES = {
        "Task": {
            "fields": ["name", {"title": "subject"}, {"content": "description"},
                       "modified", "project"],
            "filters": {"status": ("!=", "Cancelled")}
        },
        "Project": {
            "fields": ["name", {"title": "project_name"}, {"content": "notes"},
                       "modified", "status"],
        }
    }

    def get_search_filters(self, query, scope=None):
        """Permission filtering — return additional WHERE conditions"""
        return {}
```

### Register in hooks.py

```python
sqlite_search = ['my_app.search.ProjectSearch']
```

### Features (automatic)

- **Spelling correction**: Trigram-based fuzzy matching
- **Recency boosting**: 1.8x (24h) → 1.5x (7d) → 1.2x (30d) → 1.1x (90d)
- **Resumable indexing**: Progress tracked, atomic replacement
- **Auto-scheduling**: Build every 3h, queue every 5min, doc events trigger updates

---

## Anti-Patterns

| NEVER | ALWAYS | Why |
|-------|--------|-----|
| Omit `search_fields` on DocType | Set `search_fields` for user-friendly names | Users can't find records by name codes |
| Custom query without `@frappe.whitelist()` | Decorate with `@frappe.whitelist()` | Silently fails — rejected by security check |
| Raw SQL without params in search | Use parameterized queries (`%(txt)s`) | SQL injection risk |
| Index all fields in global search | Only `in_global_search=1` on key fields | Bloats table, slows 15-min sync |
| Use global search for real-time | Use link field search for real-time | Global search has 15-min sync delay |
| Skip `get_search_filters()` in SQLiteSearch | Implement permission filtering | Returns all results regardless of access |
| Index cancelled/deleted docs | Set `filters` in `INDEXABLE_DOCTYPES` | Stale results confuse users |

---

## Version Differences

| Feature | v14 | v15+ |
|---------|:---:|:----:|
| Link search caching | -- | `@http_cache(max_age=60)` |
| `link_fieldname` param | -- | Added |
| `page_length` default | 20 | 10 |
| SQLiteSearch (FTS5) | -- | Full implementation |
| Spelling correction | -- | Trigram-based |
| Recency boosting | -- | Time-based multipliers |
| `sqlite_search` hook | -- | Available |
| Global search | Yes | Yes |
| Whoosh FullTextSearch | Yes | Yes (legacy) |

---

## Reference Files

- [Link Search API](references/link-search-api.md) — search_link, search_widget, custom queries
- [Global & Website Search](references/global-website-search.md) — Global search, WebsiteSearch, SQLiteSearch
---
name: frappe-core-translation
description: >
  Use when implementing translations/i18n in Frappe v14-v16 apps.
  Covers _() in Python, __() in JavaScript, CSV translation files,
  bench commands, string extraction rules, lazy translation _lt(),
  PO/MO files [v15+], RTL support, and custom app translations.
  Prevents common mistakes with f-strings, concatenation, and template
  literals that break string extraction.
  Keywords: translation, i18n, _(), __(), _lt(), CSV, PO, gettext,, translate my app, multi-language, text not translated, wrong language, how to add translation.
  bench get-untranslated, RTL, localization.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "3.0"
---

# Frappe Translation / i18n

> Deterministic patterns for translating Frappe apps across v14, v15, and v16.

---

## Quick Reference

| Task | Python | JavaScript |
|------|--------|------------|
| Translate string | `_("Hello")` | `__("Hello")` |
| With substitution | `_("Hello {0}").format(name)` | `__("Hello {0}", [name])` |
| With context | `_("Change", context="Coins")` | `__("Change", null, "Coins")` |
| Lazy (module-level) | `_lt("Pending")` [v15+] | N/A |
| Check RTL | `frappe.utils.is_rtl()` | `frappe.utils.is_rtl()` |

---

## Decision Tree

```
Need to translate a string?
├── In Python (.py)?
│   ├── Inside a function/method → _("text {0}").format(val)
│   ├── Module-level constant [v15+] → _lt("text")
│   └── Module-level constant [v14] → define inside function or use lazy
├── In JavaScript (.js)?
│   └── ALWAYS → __("text {0}", [val])
├── In Jinja template (.html)?
│   └── {{ _("text") }}
├── In Vue (.vue)?
│   └── __("text") in <script>, {{ __("text") }} in <template>
└── DocType label/description/option?
    └── Auto-extracted — no _() needed

Where do translations live?
├── v14 → apps/{app}/{app}/translations/{lang}.csv
├── v15+ → apps/{app}/{app}/locale/{lang}/LC_MESSAGES/{app}.po
└── User overrides → Translation DocType (highest priority)

Need to extract untranslated strings?
├── v14 → bench --site {site} get-untranslated {lang} {output}
└── v15+ → bench generate-pot-file --app {app}
```

---

## Translation Priority (Highest First)

| Priority | Source | Scope |
|----------|--------|-------|
| 1 | **Translation DocType** (user overrides) | Per-site |
| 2 | **MO files** (`locale/{lang}/.../{app}.mo`) | Per-app [v15+] |
| 3 | **CSV files** (`translations/{lang}.csv`) | Per-app |
| 4 | **Parent language** (e.g., `pt` for `pt-BR`) | Fallback |

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| `_()` / `__()` | Yes | Yes | Yes |
| `_lt()` lazy translation | No | Yes | Yes |
| CSV translations | Yes | Yes (legacy) | Yes (legacy) |
| PO/MO (gettext) | No | Yes | Yes |
| `bench generate-pot-file` | No | Yes | Yes |
| Babel JS extractor | No | Yes | Yes |
| Type hints on `_()` | No | No | Yes |

---

## Auto-Extracted Strings (No _() Needed)

These are extracted automatically by the framework:

- DocType **labels** and **descriptions**
- Select field **options** (each option line)
- Workflow **states** and **actions**
- Print Format **labels**
- Report **column labels**
- Notification **subjects** (not body)
- Dashboard chart **labels**

---

## String Extraction Rules

| File Type | Extractor | What It Finds |
|-----------|-----------|---------------|
| `.py` | Babel (AST) | `_("...")`, `_lt("...")` calls |
| `.js` | Babel tokenizer [v15+] / regex [v14] | `__("...")` calls |
| `.html` | Regex | `{{ _("...") }}` in Jinja |
| `.vue` | Same as JS | `__("...")` in script/template |
| `.json` | DocType parser | Labels, descriptions, options |

**CRITICAL**: Extractors work on the AST/tokens. They CANNOT extract dynamically constructed strings. See [Anti-Patterns](references/anti-patterns.md).

---

## Anti-Patterns (NEVER Do These)

| Pattern | Why It Breaks | Correct Form |
|---------|---------------|--------------|
| `_(f"Hello {name}")` | f-string not extractable | `_("Hello {0}").format(name)` |
| `_("Hello " + name)` | Concatenation fragments | `_("Hello {0}").format(name)` |
| `_("Welcome %s") % name` | Old-style not extractable | `_("Welcome {0}").format(name)` |
| `` __(`Hello ${name}`) `` | Template literal not extractable | `__("Hello {0}", [name])` |
| `_(" Hello ")` | Leading/trailing spaces trimmed | `_("Hello")` |
| `_("item" if x else "items")` | Ternary inside _() | `_("item") if x else _("items")` |
| `_(variable)` | Variable not extractable | `_("Known String")` |

> Full anti-pattern catalog with code examples: [references/anti-patterns.md](references/anti-patterns.md)

---

## CSV Translation File Format

**Location**: `apps/{app}/{app}/translations/{lang}.csv`

```csv
"source","translation","context"
"Hello","Hallo",""
"Change","Wisselgeld","Coins"
"Change","Wijziging","Amendment"
```

- ALWAYS use UTF-8 encoding (no BOM)
- ALWAYS quote all fields with double quotes
- Context column is optional but MUST be present (empty string if unused)
- No hooks registration needed — auto-discovered from `translations/` directory

---

## PO/MO Files [v15+]

**Location**: `apps/{app}/{app}/locale/{lang}/LC_MESSAGES/{app}.po`

```bash
# Generate POT template
bench generate-pot-file --app {app}

# Migrate existing CSV to PO
bench migrate-csv-to-po --app {app}

# Compile PO to MO (required for runtime)
bench compile-po-to-mo --app {app}
```

PO files follow standard GNU gettext format. Use any PO editor (Poedit, Weblate, Transifex).

---

## Bench Commands

| Command | Version | Purpose |
|---------|---------|---------|
| `bench --site {site} get-untranslated {lang} {output.csv}` | All | Export untranslated strings |
| `bench update-translations {lang} {untranslated.csv} {translated.csv}` | All | Import translations |
| `bench generate-pot-file --app {app}` | v15+ | Generate .pot template |
| `bench migrate-csv-to-po --app {app}` | v15+ | Convert CSV to PO format |
| `bench compile-po-to-mo --app {app}` | v15+ | Compile PO to binary MO |

---

## RTL Support

**Hardcoded RTL languages**: `ar` (Arabic), `he` (Hebrew), `fa` (Persian/Farsi), `ps` (Pashto)

```python
# Python
if frappe.utils.is_rtl():
    # Apply RTL-specific logic
```

```javascript
// JavaScript
if (frappe.utils.is_rtl()) {
    // Apply RTL-specific logic
}
```

- Frappe auto-applies `dir="rtl"` to the `<html>` element
- ALWAYS use logical CSS properties (`margin-inline-start` not `margin-left`) for RTL compatibility
- Bootstrap RTL stylesheet is auto-loaded when RTL language is active

---

## Custom App Translation Workflow

### Adding translations to your custom app:

1. **Write translatable strings** using `_()` / `__()` with positional placeholders
2. **Extract untranslated strings**:
   - v14: `bench --site {site} get-untranslated {lang} untranslated.csv`
   - v15+: `bench generate-pot-file --app {app}`
3. **Translate** the extracted strings (manually or via PO editor)
4. **Place translations**:
   - CSV: `apps/{app}/{app}/translations/{lang}.csv`
   - PO: `apps/{app}/{app}/locale/{lang}/LC_MESSAGES/{app}.po`
5. **Compile** (v15+ PO only): `bench compile-po-to-mo --app {app}`
6. **Clear cache**: `bench --site {site} clear-cache`

---

## Reference Files

| File | Contents |
|------|----------|
| [references/api-reference.md](references/api-reference.md) | Full Python _() and JS __() API with all signatures and edge cases |
| [references/csv-and-bench.md](references/csv-and-bench.md) | CSV format spec, bench commands, PO/MO workflow, custom app setup |
| [references/anti-patterns.md](references/anti-patterns.md) | Complete anti-pattern catalog with failing and corrected examples |
---
name: frappe-core-utils
description: >
  Use when working with utility functions in Frappe v14-v16. Covers
  frappe.utils.* for date/time, number/money, string, validation, and
  file path operations. Prevents reinventing stdlib alternatives that
  break timezone awareness, locale formatting, or multi-tenancy.
  Keywords: frappe.utils, nowdate, flt, cint, fmt_money, getdate,, date calculation, format number, money format, validate email, how to calculate days between.
  add_days, date_diff, validate_email, pretty_date, get_files_path.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "3.0"
---

# Frappe Utility Functions

## Quick Reference: Python

| Need | Function | Returns |
|------|----------|---------|
| Current date | `nowdate()` / `today()` | `datetime.date` |
| Current datetime | `now_datetime()` | `datetime.datetime` |
| Parse date string | `getdate(str)` | `datetime.date` |
| Parse datetime string | `get_datetime(str)` | `datetime.datetime` |
| Add days | `add_days(date, n)` | `datetime.date` |
| Add months | `add_months(date, n)` | `datetime.date` |
| Date difference | `date_diff(end, start)` | `int` (days) |
| Format for user | `format_date(dt)` | `str` (user locale) |
| Relative time | `pretty_date(dt)` | `str` ("2 hours ago") |
| Safe float | `flt(val, precision)` | `float` |
| Safe int | `cint(val)` | `int` |
| Safe string | `cstr(val)` | `str` |
| Safe bool | `sbool(val)` | `bool` |
| Safe division | `safe_div(a, b)` | `float` [v15+] |
| Money format | `fmt_money(amt, currency)` | `str` |
| Money in words | `money_in_words(amt, cur)` | `str` |
| Strip HTML | `strip_html(text)` | `str` |
| List to prose | `comma_and(items)` | `str` ("a, b, and c") |
| Validate email | `validate_email_address(e)` | `str` or `""` |
| Validate URL | `validate_url(url)` | `bool` |
| Parse JSON | `parse_json(s)` | `Any` |
| Files path | `get_files_path(is_private)` | `str` |
| Site path | `get_site_path(*parts)` | `str` |
| Unique list | `unique(seq)` | `list` |
| Hash | `generate_hash(s, length)` | `str` |

> **ALL imports**: `from frappe.utils import nowdate, flt, ...` in controllers/whitelisted methods.
> In **Server Scripts**: Use `frappe.utils.nowdate()` directly — NO import statements allowed.

---

## Decision Tree: "Which function do I use?"

```
Need a date/time value?
├─ Current date → nowdate() or today()
├─ Current datetime → now_datetime()
├─ Parse a string → getdate() or get_datetime()
├─ Add/subtract time → add_days(), add_months(), add_to_date()
├─ Difference → date_diff() (days), month_diff(), time_diff_in_seconds()
├─ Period boundary → get_first_day(), get_last_day(), get_quarter_start()
└─ Display to user → format_date(), format_datetime(), pretty_date()

Need a number?
├─ Convert safely → flt(), cint(), cstr(), sbool()
├─ Round → rounded() (banker's rounding)
├─ Safe divide → safe_div(a, b, default=0) [v15+]
├─ Format money → fmt_money(amount, currency)
└─ Money to words → money_in_words(amount, currency)

Need string processing?
├─ HTML → strip_html(), escape_html(), is_html()
├─ Join list → comma_and(), comma_or(), comma_sep()
├─ Markdown ↔ HTML → to_markdown(), md_to_html()
└─ Mask sensitive → mask_string(input, show_first=4) [v16+]

Need validation?
├─ Email → validate_email_address(email, throw=False)
├─ URL → validate_url(url, valid_schemes=["https"])
├─ Phone → validate_phone_number(phone, throw=False)
├─ JSON → validate_json_string(s)
└─ IBAN → validate_iban(iban) [v16+]

Need file/path?
├─ Public files → get_files_path()
├─ Private files → get_files_path(is_private=True)
├─ Site directory → get_site_path("private", "backups")
├─ Bench root → get_bench_path()
└─ File size → get_file_size(path, format=True)
```

---

## Critical Anti-Patterns

### NEVER use Python stdlib when frappe.utils exists

| NEVER (stdlib) | ALWAYS (frappe.utils) | Why |
|----------------|----------------------|-----|
| `datetime.datetime.now()` | `now_datetime()` | Ignores system timezone |
| `datetime.date.today()` | `nowdate()` | Ignores system timezone |
| `float(val)` | `flt(val, precision)` | Crashes on None/empty |
| `int(val)` | `cint(val)` | Crashes on None/empty |
| `round(val, 2)` | `rounded(val, 2)` | Inconsistent rounding |
| `val1 / val2` | `safe_div(val1, val2)` | ZeroDivisionError [v15+] |
| `json.loads(s)` | `parse_json(s)` | Crashes on None/empty |
| `json.dumps(obj)` | `frappe.as_json(obj)` | Inconsistent serialization |
| `"{:,.2f}".format(a)` | `fmt_money(a, currency)` | Ignores locale/currency |
| `os.path.join(...)` | `get_site_path(...)` | Breaks multi-tenancy |
| `", ".join(items)` | `comma_and(items)` | No localized "and" |
| `dt.strftime(fmt)` | `format_date(dt)` | Ignores user preference |
| `re.sub(r'<.*?>', '', h)` | `strip_html(h)` | Misses edge cases |

### Server Script Sandbox

```python
# ❌ NEVER in Server Scripts
from frappe.utils import nowdate, flt
import json

# ✅ ALWAYS in Server Scripts (no imports allowed)
today = frappe.utils.nowdate()
amount = frappe.utils.flt(doc.amount, 2)
data = frappe.parse_json(doc.json_field)
```

---

## JavaScript Quick Reference

| Need | Function |
|------|----------|
| Escape HTML | `frappe.utils.escape_html(txt)` |
| HTML to text | `frappe.utils.html2text(html)` |
| Check if HTML | `frappe.utils.is_html(txt)` |
| Parse JSON | `frappe.utils.parse_json(str)` |
| Validate URL | `frappe.utils.is_url(txt)` |
| Title case | `frappe.utils.to_title_case(str)` |
| Join with "and" | `frappe.utils.comma_and(list)` |
| Unique array | `frappe.utils.unique(list)` |
| Copy clipboard | `frappe.utils.copy_to_clipboard(txt)` |
| Scroll to element | `frappe.utils.scroll_to(el)` |
| Is mobile | `frappe.utils.is_mobile()` |
| Throttle | `frappe.utils.throttle(fn, delay)` |
| Debounce | `frappe.utils.debounce(fn, delay)` |
| Format value | `frappe.format(value, df, options, doc)` |
| Duration display | `frappe.utils.get_formatted_duration(secs)` |

---

## Version Differences

| Function | v14 | v15 | v16 |
|----------|:---:|:---:|:---:|
| `safe_div()` | -- | Added | Yes |
| `duration_to_seconds()` | -- | Added | Yes |
| `guess_date_format()` | -- | Added | Yes |
| `validate_duration_format()` | -- | Added | Yes |
| `mask_string()` | -- | -- | Added |
| `validate_iban()` | -- | -- | Added |
| `validate_name()` | -- | -- | Added |
| `safe_json_loads()` | -- | -- | Added |
| `groupby_metric()` | -- | -- | Added |
| Core functions | Yes | Yes | Yes |

---

## Reference Files

- [Date/Time Functions](references/date-time-functions.md) — Complete date/time API with signatures
- [Number & Money Functions](references/number-money-functions.md) — flt, fmt_money, rounding
- [String & Validation Functions](references/string-validation-functions.md) — HTML, join, validate
- [JavaScript Utilities](references/javascript-utilities.md) — Client-side frappe.utils.*
- [Anti-patterns](references/anti-patterns.md) — stdlib vs frappe.utils comparison
---
name: frappe-core-workflow
description: >
  Use when creating or modifying Frappe Workflows, defining states and transitions, adding action conditions, or troubleshooting workflow permission errors.
  Prevents stuck documents from misconfigured transitions, missing state permissions, and circular workflow paths.
  Covers Workflow DocType, workflow states, transitions, actions, conditions (Python expressions), workflow permissions, workflow_state field, Workflow Action DocType.
  Keywords: workflow, states, transitions, actions, conditions, workflow_state, Workflow Action, approval, document workflow, approval process, document stuck, cannot change status, workflow not moving, who can approve..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Workflow Engine

The Frappe Workflow engine is a state machine that controls document lifecycle through configurable states, transitions, and role-based permissions. It governs when and how documents change status, who can perform actions, and what side effects occur on each transition.

## Quick Reference

```
Workflow DocType            → Defines the state machine for a specific DocType
├── states (child table)    → Workflow Document State rows
│   ├── state               → Link to Workflow State
│   ├── doc_status          → 0 (Draft), 1 (Submitted), 2 (Cancelled)
│   ├── allow_edit          → Role that can edit in this state
│   ├── update_field        → Field to update when entering state
│   ├── update_value        → Value to set (literal or expression)
│   └── next_action_email_template → Email Template link
└── transitions (child table) → Workflow Transition rows
    ├── state               → Source state (Link to Workflow State)
    ├── action              → Link to Workflow Action Master
    ├── next_state          → Target state (Link to Workflow State)
    ├── allowed             → Role that can perform this action
    ├── allow_self_approval → Check (default: 1)
    ├── condition           → Python expression (optional)
    └── transition_tasks    → Link to Workflow Transition Tasks
```

### Key Fields on Workflow DocType

| Field | Type | Purpose |
|-------|------|---------|
| `workflow_name` | Data | Unique identifier |
| `document_type` | Link → DocType | Target DocType |
| `is_active` | Check | Only ONE workflow per DocType can be active |
| `workflow_state_field` | Data | Default: `workflow_state` |
| `override_status` | Check | Prevent workflow from overriding list view status |
| `send_email_alert` | Check | Email notifications with next possible actions |

## How the Engine Works

### 1. Activation and Field Creation

When a Workflow is saved with `is_active = 1`:
- All other workflows for the same DocType are deactivated automatically
- A hidden Custom Field (`workflow_state_field`, default `workflow_state`) is created on the target DocType if it does not exist
- The field is type `Link` to `Workflow State`, with `hidden=1`, `allow_on_submit=1`, `no_copy=1`
- Existing documents with empty workflow state get their state set based on their current `docstatus`

### 2. State Resolution

Every document under a workflow has a `workflow_state` field. The engine resolves available transitions by:

1. Reading current `workflow_state` from the document
2. Filtering `workflow.transitions` where `transition.state == current_state`
3. Filtering by user roles: `transition.allowed in frappe.get_roles()`
4. Evaluating `transition.condition` via `frappe.safe_eval()` (if set)
5. Returning matching transitions as available actions

### 3. Applying a Transition

When `apply_workflow(doc, action)` is called:

1. Load document from DB (fresh read)
2. Get available transitions for current user
3. Find transition matching the requested `action`
4. Check self-approval: blocked if `allow_self_approval=0` AND user is document owner
5. Set `workflow_state_field` to `transition.next_state`
6. If `update_field` is set on the target state, update that field
7. Execute transition tasks (sync first, then async via `frappe.enqueue`)
8. Handle docstatus change based on source/target state `doc_status` values
9. Save/Submit/Cancel document accordingly
10. Add workflow comment

## Workflow and DocStatus Interaction

**CRITICAL**: The workflow engine controls docstatus transitions. You NEVER call `doc.submit()` or `doc.cancel()` directly on a workflow-controlled document. The workflow does it.

### DocStatus Transition Rules

| Source doc_status | Target doc_status | Engine Action | Valid? |
|:-:|:-:|---|:-:|
| 0 (Draft) | 0 (Draft) | `doc.save()` | YES |
| 0 (Draft) | 1 (Submitted) | `doc.submit()` | YES |
| 1 (Submitted) | 1 (Submitted) | `doc.save()` | YES |
| 1 (Submitted) | 2 (Cancelled) | `doc.cancel()` | YES |
| 2 (Cancelled) | ANY | BLOCKED | NO |
| 1 (Submitted) | 0 (Draft) | BLOCKED | NO |
| 0 (Draft) | 2 (Cancelled) | BLOCKED | NO |

**ALWAYS** define your states so that docstatus only moves forward: 0→0, 0→1, 1→1, 1→2.
**NEVER** create a transition from a cancelled state or from submitted back to draft.

### Non-Submittable DocTypes

If the target DocType is NOT submittable, ALL states MUST have `doc_status = 0`. The engine validates this and throws an error if any state has `doc_status = 1` or `2` on a non-submittable DocType.

## Workflow States

Workflow State is a separate DocType used as a master list. Each state has:

| Field | Purpose |
|-------|---------|
| `state` | Display name of the state |
| `style` | CSS class for badge display (Primary, Success, Warning, Danger, Info, Inverse) |
| `icon` | Font Awesome icon class |

### State Row Fields (Workflow Document State)

| Field | Purpose |
|-------|---------|
| `state` | Link to Workflow State |
| `doc_status` | Select: 0, 1, or 2 |
| `allow_edit` | Link to Role — ONLY this role can edit the document in this state |
| `update_field` | Field to update when document enters this state |
| `update_value` | Value to set (string or Python expression if `evaluate_as_expression=1`) |
| `is_optional_state` | Check — optional states are skipped in `get_next_possible_transitions` |
| `send_email` | Check (default 1) — send email notification on entering this state |
| `next_action_email_template` | Link to Email Template |
| `message` | Text message for the email notification |

## Workflow Transitions

Each transition row defines one possible action:

| Field | Purpose |
|-------|---------|
| `state` | Source state (MUST exist in states table) |
| `action` | Link to Workflow Action Master (e.g., "Approve", "Reject", "Review") |
| `next_state` | Target state (MUST exist in states table) |
| `allowed` | Link to Role — ONLY users with this role see this action |
| `allow_self_approval` | Check (default 1) — if 0, document owner cannot perform this action |
| `condition` | Python expression evaluated with `frappe.safe_eval()` |
| `transition_tasks` | Link to Workflow Transition Tasks (v15+) |

### Condition Expressions

Conditions are Python expressions evaluated in a sandboxed environment. Available globals:

```python
# Available in condition expressions:
frappe.db.get_value(doctype, name, fieldname)
frappe.db.get_list(doctype, filters, fields)
frappe.session.user
frappe.session.roles  # NOT available — use frappe.get_roles() outside conditions
frappe.utils.now_datetime()
frappe.utils.add_to_date(date, **kwargs)
frappe.utils.get_datetime(datetime_str)
frappe.utils.now()
doc.fieldname  # Access any field on the document (as dict)
```

Example conditions:
```python
doc.grand_total > 50000
doc.department == "HR"
doc.grand_total > 50000 and doc.department != "Finance"
```

## Workflow Actions

### Workflow Action Master

Simple DocType with just a `workflow_action_name` field. Common actions: Approve, Reject, Review, Send Back, Cancel. Create these first before defining transitions.

### Workflow Action DocType

Tracks pending actions for users. Created automatically when a document enters a state with outgoing transitions.

| Field | Purpose |
|-------|---------|
| `status` | Open or Completed |
| `reference_doctype` | The DocType of the document |
| `reference_name` | The document name |
| `workflow_state` | Current workflow state |
| `user` | Assigned user |
| `permitted_roles` | Table MultiSelect of roles that can act |
| `completed_by` | User who completed the action |
| `completed_by_role` | Role used to complete |

Workflow Actions appear in the user's "Workflow Action" list and can be acted on via email links.

## Self-Approval Control

```python
def has_approval_access(user, doc, transition):
    return (user == "Administrator"
            or transition.get("allow_self_approval")
            or user != doc.get("owner"))
```

- **Administrator** ALWAYS has approval access regardless of settings
- If `allow_self_approval = 1` (default): document owner CAN approve
- If `allow_self_approval = 0`: document owner CANNOT approve their own document

## Decision Tree

```
Need workflow on a DocType?
├── Is DocType submittable?
│   ├── YES → States can use doc_status 0, 1, 2
│   └── NO  → ALL states MUST have doc_status = 0
├── Define states → Create Workflow State records first
├── Define transitions → Need Workflow Action Master records first
├── Who can edit in each state? → Set allow_edit per state
├── Need conditional transitions?
│   └── Use Python expressions with doc.field access
├── Need to block self-approval?
│   └── Set allow_self_approval = 0 on specific transitions
└── Need email notifications?
    └── Set send_email_alert on Workflow + email templates on states
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `WorkflowStateError` | Document has no workflow_state set | Ensure workflow sets initial state on creation |
| `WorkflowTransitionError` | Action not valid for current state/role | Verify transitions table covers all needed paths |
| `WorkflowPermissionError` | User lacks role for transition, or self-approval blocked | Check `allowed` role and `allow_self_approval` |
| "Illegal Document Status" | Invalid docstatus transition (e.g., 0→2) | Fix state `doc_status` values |
| "Cannot cancel before submitting" | Transition from draft (0) to cancelled (2) | Add intermediate submitted (1) state |

## See Also

- [API Reference](references/api-reference.md) — Complete workflow Python API
- [Examples](references/examples.md) — Workflow configuration examples
- [Anti-Patterns](references/anti-patterns.md) — Common mistakes and how to avoid them
- `frappe-impl-workflow` — Step-by-step implementation guide
---
name: frappe-errors-api
description: >
  Use when debugging or handling API errors in Frappe/ERPNext v14/v15/v16.
  Prevents silent failures and wrong HTTP status codes in REST endpoints.
  Covers 401 Unauthorized (wrong token format, expired OAuth), 403 Forbidden
  (missing @whitelist, allow_guest needed), 404 Not Found (wrong endpoint URL),
  417 Expectation Failed (validation via frappe.throw), 500 Internal Server
  Error, CORS issues, CSRF token missing/invalid, rate limit exceeded (429),
  file upload failures, JSON parse errors in request/response, webhook delivery
  failures, and timeout on long operations.
  Keywords: API error, 401, 403, 404, 417, 429, 500, CSRF, CORS, REST,, API call fails, 403 forbidden, CORS error, token expired, endpoint not found, webhook not received.
  whitelist, webhook, rate limit, file upload, authentication token.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# API Error Handling

For API implementation patterns see `frappe-core-api`. For permission errors see `frappe-errors-permissions`.

---

## HTTP Status Code Map: Error -> Cause -> Fix

| Code | Frappe Exception | When It Happens | Fix |
|------|-----------------|-----------------|-----|
| 200 | — | Success | — |
| 401 | `AuthenticationError` | Bad/expired token, wrong format | Check `Authorization: token key:secret` or `Bearer access_token` |
| 403 | `PermissionError` | Missing `@whitelist`, no role, no `allow_guest` | Add decorator or grant permission |
| 404 | `DoesNotExistError` | Wrong URL, doc not found, typo in endpoint path | Verify `/api/resource/:doctype/:name` or `/api/method/dotted.path` |
| 409 | `DuplicateEntryError` | Unique constraint violated | Check existing records before insert |
| 417 | `ValidationError` | `frappe.throw()` called | Fix validation logic or input data |
| 429 | `RateLimitExceededError` | Too many requests | Respect `Retry-After` header; throttle requests |
| 500 | `Exception` (unhandled) | Unhandled server error | Check Error Log; wrap in try/except |
| 503 | — | Server overloaded / maintenance | Retry with exponential backoff |

---

## Authentication Errors (401)

### Wrong Token Format

```
Error:  HTTP 401 Unauthorized
Cause:  Using "Bearer api_key:api_secret" instead of "token api_key:api_secret"
```

**Frappe uses TWO authentication formats — NEVER mix them:**

| Method | Header Format | When to Use |
|--------|--------------|-------------|
| API Key/Secret | `Authorization: token api_key:api_secret` | Server-to-server, scripts |
| OAuth Bearer | `Authorization: Bearer access_token` | OAuth 2.0 flows |
| Session Cookie | Cookie from `/api/method/login` | Browser-based apps |

```python
# WRONG — Bearer with API key:secret
headers = {"Authorization": f"Bearer {api_key}:{api_secret}"}

# CORRECT — token keyword for API key:secret
headers = {"Authorization": f"token {api_key}:{api_secret}"}

# CORRECT — Bearer for OAuth access tokens only
headers = {"Authorization": f"Bearer {oauth_access_token}"}
```

### Expired OAuth Token

```
Error:  HTTP 401 after token was working
Cause:  OAuth access_token expired
Fix:    Use refresh_token to get new access_token
```

```python
def get_fresh_token(settings):
    """ALWAYS implement token refresh for OAuth integrations."""
    if is_token_expired(settings.token_expiry):
        response = requests.post(f"{settings.base_url}/api/method/frappe.integrations.oauth2.get_token", data={
            "grant_type": "refresh_token",
            "refresh_token": settings.get_password("refresh_token"),
            "client_id": settings.client_id,
        })
        if response.status_code == 200:
            data = response.json()
            settings.access_token = data["access_token"]
            settings.token_expiry = frappe.utils.add_to_date(None, seconds=data["expires_in"])
            settings.save(ignore_permissions=True)
        else:
            frappe.throw(_("OAuth token refresh failed"), exc=frappe.AuthenticationError)
    return settings.access_token
```

---

## Forbidden Errors (403)

### Missing @frappe.whitelist()

```
Error:  HTTP 403 on /api/method/myapp.api.my_function
Cause:  Function exists but lacks @frappe.whitelist() decorator
Fix:    Add decorator — without it, NO external call is allowed
```

```python
# WRONG — Callable internally but returns 403 via REST
def my_function(name):
    return frappe.get_doc("Item", name)

# CORRECT — Exposed to authenticated users
@frappe.whitelist()
def my_function(name):
    return frappe.get_doc("Item", name)

# CORRECT — Exposed to everyone including unauthenticated
@frappe.whitelist(allow_guest=True)
def public_function():
    return {"status": "ok"}
```

### Missing allow_guest for Public Endpoints

```
Error:  HTTP 403 for unauthenticated requests
Cause:  @frappe.whitelist() without allow_guest=True
Fix:    Add allow_guest=True — but ALWAYS validate inputs
```

**NEVER use `allow_guest=True` without input validation** — these endpoints are exposed to the internet.

---

## Not Found Errors (404)

### Common URL Mistakes

| Wrong URL | Correct URL | Issue |
|-----------|-------------|-------|
| `/api/resource/SalesOrder/SO-001` | `/api/resource/Sales Order/SO-001` | Space in DocType name |
| `/api/method/myapp.my_function` | `/api/method/myapp.api.my_function` | Missing module path |
| `/api/resource/sales_order` | `/api/resource/Sales Order` | Wrong case / underscore |
| `/api/v2/document/Item/ITEM-001` [v14] | `/api/resource/Item/ITEM-001` | v2 API only in v15+ |

```python
# ALWAYS URL-encode DocType names with spaces
import urllib.parse
url = f"/api/resource/{urllib.parse.quote('Sales Order')}/{name}"
```

---

## Validation Errors (417)

Every `frappe.throw()` call returns HTTP 417 by default (unless a specific exception class is provided).

```python
# Returns 417 — generic validation error
frappe.throw(_("Amount must be positive"))

# Returns 417 — with explicit ValidationError type
frappe.throw(_("Amount must be positive"), exc=frappe.ValidationError)

# Returns 403 — PermissionError overrides to 403
frappe.throw(_("Access denied"), exc=frappe.PermissionError)

# Returns 404 — DoesNotExistError overrides to 404
frappe.throw(_("Not found"), exc=frappe.DoesNotExistError)
```

**ALWAYS use the specific exception class** so clients can handle error types correctly:
```python
# WRONG — all errors look the same to the client
frappe.throw(_("Customer not found"))  # 417, generic

# CORRECT — client can distinguish 404 from validation error
frappe.throw(_("Customer not found"), exc=frappe.DoesNotExistError)  # 404
```

---

## CSRF Token Errors

```
Error:  HTTP 403 "CSRF token missing or invalid"
Cause:  POST/PUT/DELETE request without X-Frappe-CSRF-Token header
```

**Rules:**
- ALWAYS include `X-Frappe-CSRF-Token` header for session-based (cookie) auth.
- Token-based auth (`Authorization: token ...`) does NOT require CSRF token.
- OAuth Bearer auth does NOT require CSRF token.
- The CSRF token is available in `frappe.csrf_token` in JavaScript or embedded as `window.CSRF_TOKEN`.

```javascript
// Browser-side: ALWAYS include CSRF for session-based requests
fetch("/api/method/myapp.api.update", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-Frappe-CSRF-Token": frappe.csrf_token
    },
    body: JSON.stringify({data: "value"})
});
```

---

## CORS Errors

```
Error:  "Access-Control-Allow-Origin" header missing
Cause:  Cross-origin request not configured in site_config.json
```

```json
// site_config.json — NEVER use "*" in production
{
    "allow_cors": "https://your-frontend.example.com"
}
```

**For multiple origins [v15+]:**
```json
{
    "allow_cors": ["https://app1.example.com", "https://app2.example.com"]
}
```

---

## Rate Limit Errors (429)

```
Error:  HTTP 429 Too Many Requests
Cause:  Exceeded rate limit configured in site_config.json or hooks.py
```

```python
# hooks.py — rate limiting on whitelisted methods [v14+]
rate_limit = {"myapp.api.heavy_endpoint": {"limit": 10, "seconds": 60}}
```

**ALWAYS handle 429 in external API calls:**
```python
def call_with_rate_limit(url, data):
    response = requests.post(url, json=data, timeout=30)
    if response.status_code == 429:
        wait = int(response.headers.get("Retry-After", 60))
        time.sleep(min(wait, 120))  # Cap at 2 minutes
        response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()
    return response.json()
```

---

## File Upload Errors

```
Error:  HTTP 500 on /api/method/upload_file
Cause:  Wrong content type, file too large, or missing file field
```

```python
# CORRECT file upload via REST API
import requests

response = requests.post(
    f"{base_url}/api/method/upload_file",
    headers={"Authorization": f"token {api_key}:{api_secret}"},
    files={"file": ("document.pdf", open("document.pdf", "rb"), "application/pdf")},
    data={
        "doctype": "Sales Invoice",
        "docname": "SINV-001",
        "is_private": 1  # 1 = private, 0 = public
    },
    timeout=60  # ALWAYS set timeout for uploads
)
```

**Common upload failures:**
- `Content-Type` must be `multipart/form-data` (set automatically by `files=` param)
- NEVER set `Content-Type: application/json` for file uploads
- Check `max_file_size` in site_config.json (default 10MB)
- [v15+] `allowed_file_extensions` restricts file types

---

## JSON Parse Errors

```
Error:  "Failed to decode JSON" or unexpected behavior
Cause:  API arguments sent as JSON string instead of parsed object
```

```python
@frappe.whitelist()
def update_items(items):
    # ALWAYS handle both string and parsed input
    if isinstance(items, str):
        try:
            items = frappe.parse_json(items)
        except Exception:
            frappe.throw(_("Invalid JSON format"), exc=frappe.ValidationError)

    if not isinstance(items, (list, dict)):
        frappe.throw(_("Expected list or dict"), exc=frappe.ValidationError)
```

---

## Webhook Delivery Failures

```
Error:  Webhook not firing or returning errors
Cause:  Target URL unreachable, wrong format, or timeout
```

**Debug checklist:**
1. Check Error Log for webhook delivery errors
2. Verify target URL is reachable from server
3. Check webhook condition — is it filtering out the event?
4. [v15+] Check Webhook Request Log for delivery status

```python
# Custom webhook with error handling
@frappe.whitelist(allow_guest=True)
def incoming_webhook():
    """Handle incoming webhook with validation."""
    payload = frappe.request.data
    signature = frappe.request.headers.get("X-Webhook-Signature")

    if not verify_signature(payload, signature):
        frappe.local.response["http_status_code"] = 401
        return {"error": "Invalid signature"}

    try:
        data = frappe.parse_json(payload)
    except Exception:
        frappe.local.response["http_status_code"] = 400
        return {"error": "Invalid JSON payload"}

    # ALWAYS return 200 quickly to prevent sender retries
    frappe.enqueue(process_webhook_data, data=data, queue="short")
    return {"status": "accepted"}
```

---

## Timeout on Long Operations

```
Error:  HTTP 504 Gateway Timeout or connection reset
Cause:  Operation takes longer than proxy/server timeout (typically 60s)
```

**Fix: Use background jobs for long operations:**
```python
@frappe.whitelist()
def start_long_operation(filters):
    """NEVER run long operations synchronously in API calls."""
    job_id = frappe.generate_hash(length=10)

    frappe.enqueue(
        "myapp.tasks.run_long_operation",
        queue="long",
        timeout=600,
        job_id=job_id,
        filters=filters
    )

    return {"status": "queued", "job_id": job_id}

@frappe.whitelist()
def check_job_status(job_id):
    """Poll for job completion."""
    from frappe.utils.background_jobs import get_info
    jobs = get_info()
    for job in jobs:
        if job.get("job_id") == job_id:
            return {"status": job.get("status", "unknown")}
    return {"status": "completed"}
```

---

## Server-Side Error Pattern (Standard)

```python
@frappe.whitelist()
def safe_api_endpoint(docname, action):
    """ALWAYS follow: validate -> check permission -> execute -> handle errors."""

    # 1. Validate input
    if not docname:
        frappe.throw(_("Document name required"), exc=frappe.ValidationError)

    # 2. Check existence
    if not frappe.db.exists("My DocType", docname):
        frappe.throw(_("Document not found"), exc=frappe.DoesNotExistError)

    # 3. Check permission
    frappe.has_permission("My DocType", "write", docname, throw=True)

    # 4. Execute with error handling
    try:
        doc = frappe.get_doc("My DocType", docname)
        result = doc.run_method(action)
        return {"status": "success", "data": result}

    except frappe.ValidationError:
        raise  # Let Frappe handle — returns 417
    except frappe.PermissionError:
        raise  # Let Frappe handle — returns 403
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"API Error: {docname}")
        frappe.throw(_("Operation failed. Please try again."))
```

---

## Client-Side Error Handling

```javascript
// ALWAYS handle errors in frappe.call
frappe.call({
    method: "myapp.api.safe_api_endpoint",
    args: {docname: "DOC-001", action: "approve"},
    freeze: true,
    freeze_message: __("Processing..."),
    callback: function(r) {
        if (r.message && r.message.status === "success") {
            frappe.show_alert({message: __("Done"), indicator: "green"});
        }
    },
    error: function(r) {
        // ALWAYS check exc_type for specific handling
        if (r.exc_type === "PermissionError") {
            frappe.msgprint(__("You lack permission for this action."));
        } else if (r.exc_type === "DoesNotExistError") {
            frappe.msgprint(__("Record not found."));
        } else if (!r.status) {
            frappe.msgprint(__("Network error. Check your connection."));
        }
    }
});
```

---

## Critical Rules

### ALWAYS
1. **Use specific exception classes** in `frappe.throw()` — enables correct HTTP status codes
2. **Set timeout on all external requests** — `requests.get(url, timeout=30)`
3. **Validate ALL inputs** before processing — whitelisted methods are callable by any logged-in user
4. **Log errors before throwing** — `frappe.log_error()` then `frappe.throw()`
5. **Handle error callback** in every `frappe.call()` — silent failures confuse users
6. **Use background jobs** for operations exceeding 30 seconds
7. **Return 200 quickly** from incoming webhooks then process asynchronously

### NEVER
1. **Expose internal errors to users** — log traceback, show friendly message
2. **Mix token formats** — `token key:secret` vs `Bearer oauth_token`
3. **Retry 4xx errors** (except 429) — they indicate client bugs, not transient failures
4. **Skip CSRF token** for session-based POST requests — results in 403
5. **Set Content-Type: application/json** for file uploads — must be multipart/form-data
6. **Catch exceptions without logging** — makes production debugging impossible
7. **Hardcode API credentials** — use `settings.get_password("field")` from a DocType

---

## Reference Files

| File | Contents |
|------|----------|
| `references/patterns.md` | Complete whitelisted method, webhook, external API patterns |
| `references/examples.md` | Full working API module, client integration, external API client |
| `references/anti-patterns.md` | 15 common API error handling mistakes |

---

## See Also

- `frappe-core-api` — API implementation patterns
- `frappe-errors-permissions` — Permission error handling (403 deep dive)
- `frappe-syntax-whitelisted` — Whitelisted method syntax
- `frappe-errors-serverscripts` — Server Script error handling
---
name: frappe-errors-clientscripts
description: >
  Use when debugging or preventing errors in Frappe Client Scripts.
  Prevents TypeError, frappe.call failures, async/await mistakes,
  cur_frm vs frm confusion, field not found, child table access errors,
  timing issues, CSRF token errors, and permission denied on frappe.call.
  Covers error diagnosis flowchart and debug tools for v14/v15/v16.
  Keywords: client script error, TypeError, frappe.call, async await,, Cannot read properties of undefined, TypeError, browser console error, script not running, form not updating.
  cur_frm, field not found, child table, CSRF, permission denied.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Client Script Errors — Diagnosis and Resolution

Cross-refs: `frappe-syntax-clientscripts` (syntax), `frappe-impl-clientscripts` (workflows), `frappe-errors-serverscripts` (server-side).

---

## Error Diagnosis Flowchart

```
ERROR IN CLIENT SCRIPT
│
├─► TypeError: Cannot read properties of undefined
│   ├─► "frm.doc.fieldname" → Field does not exist on DocType
│   ├─► "r.message.value" → Server returned null/error
│   └─► "row.fieldname" in child table → Row not fetched correctly
│
├─► frappe.call fails silently
│   ├─► Missing error callback → Add error handler
│   ├─► 403 Forbidden → Method not whitelisted (@frappe.whitelist)
│   ├─► 417 Expectation Failed → Server-side frappe.throw()
│   └─► 401 Unauthorized → Session expired or CSRF token invalid
│
├─► Uncaught (in promise) → Missing try/catch on async frappe.call
│
├─► Field appears blank after set_value → Timing issue (setup vs refresh)
│
├─► cur_frm is undefined → Using cur_frm in list/report context
│
└─► frappe.throw() does not prevent save → Used outside validate event
```

---

## Error Message → Cause → Fix Table

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `TypeError: Cannot read properties of undefined (reading 'fieldname')` | Field does not exist on DocType or doc not loaded | ALWAYS check `frm.doc` exists before accessing fields |
| `TypeError: frm.set_value is not a function` | Using `cur_frm` shortcut that is undefined | ALWAYS use the `frm` parameter from event handler |
| `Uncaught (in promise)` | Unhandled async rejection from frappe.call | ALWAYS wrap async calls in try/catch |
| `CSRFTokenError` / `403 with CSRF` | Token mismatch after session timeout | ALWAYS use `frappe.call()` (handles CSRF automatically) |
| `Not permitted` / 403 on frappe.call | Server method missing `@frappe.whitelist()` | ALWAYS add `@frappe.whitelist()` decorator to API methods |
| `frappe.throw() not preventing save` | `frappe.throw()` used outside `validate` event | ALWAYS use `frappe.throw()` only in `validate` |
| `field not found: xyz` in set_query | Fieldname typo or field not in child table | Verify exact fieldname against DocType definition |
| `row.item_code is undefined` | Accessing child row wrong — `locals` not synced | Use `frappe.get_doc(cdt, cdn)` in child table events |
| `frm.set_value not working` | Called in `setup` before form fully loaded | Move field-setting logic to `refresh` event |
| `Maximum call stack exceeded` | Circular trigger — field change fires own handler | Use `frm.flags` guard to break recursion |

---

## Critical Error Patterns

### 1. cur_frm vs frm: The #1 Beginner Mistake

```javascript
// ❌ WRONG — cur_frm is undefined in many contexts
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        cur_frm.set_value('territory', 'Default');  // BREAKS in list view
    }
});

// ✅ CORRECT — ALWAYS use the frm parameter
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        frm.set_value('territory', 'Default');
    }
});
```

**Rule**: NEVER use `cur_frm`. ALWAYS use the `frm` parameter passed to every event handler.

### 2. Async/Await: Silent Failure Without try/catch

```javascript
// ❌ WRONG — Unhandled rejection crashes silently
frappe.ui.form.on('Sales Order', {
    async customer(frm) {
        let r = await frappe.call({
            method: 'myapp.api.get_data',
            args: { customer: frm.doc.customer }
        });
        frm.set_value('credit_limit', r.message.limit);  // r.message may be null
    }
});

// ✅ CORRECT — try/catch with null check
frappe.ui.form.on('Sales Order', {
    async customer(frm) {
        if (!frm.doc.customer) return;
        try {
            let r = await frappe.call({
                method: 'myapp.api.get_data',
                args: { customer: frm.doc.customer }
            });
            if (r.message) {
                frm.set_value('credit_limit', r.message.limit || 0);
            }
        } catch (error) {
            console.error('Customer fetch failed:', error);
            frappe.show_alert({
                message: __('Could not load customer details'),
                indicator: 'red'
            }, 5);
        }
    }
});
```

### 3. Child Table Access: Wrong Pattern

```javascript
// ❌ WRONG — frm.doc.items[0] may not reflect latest state
frappe.ui.form.on('Sales Order Item', {
    item_code(frm, cdt, cdn) {
        let row = frm.doc.items.find(r => r.name === cdn);  // fragile
        row.rate = 100;  // Does not trigger UI refresh
    }
});

// ✅ CORRECT — Use frappe.get_doc and frappe.model.set_value
frappe.ui.form.on('Sales Order Item', {
    item_code(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (!row.item_code) return;
        frappe.model.set_value(cdt, cdn, 'rate', 100);  // Triggers refresh
    }
});
```

### 4. Timing: setup vs refresh

```javascript
// ❌ WRONG — set_value in setup, form not ready
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        frm.set_value('company', 'My Company');  // May not work
    }
});

// ✅ CORRECT — set_query in setup, set_value in refresh/onload
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        // Filters belong in setup
        frm.set_query('customer', () => ({ filters: { disabled: 0 } }));
    },
    refresh(frm) {
        // Value changes belong in refresh (or onload for new docs)
        if (frm.is_new()) {
            frm.set_value('company', 'My Company');
        }
    }
});
```

### 5. frappe.throw() Scope: Only Works in validate

```javascript
// ❌ WRONG — throw in customer change does NOT prevent save
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        if (!frm.doc.customer) {
            frappe.throw(__('Customer required'));  // Stops script, NOT save
        }
    }
});

// ✅ CORRECT — throw in validate prevents save
frappe.ui.form.on('Sales Order', {
    customer(frm) {
        if (!frm.doc.customer) {
            frappe.msgprint({ message: __('Customer required'), indicator: 'orange' });
        }
    },
    validate(frm) {
        if (!frm.doc.customer) {
            frappe.throw(__('Customer is required'));  // Prevents save
        }
    }
});
```

### 6. Recursion Guard with Flags

```javascript
// ❌ WRONG — discount change triggers amount recalc, which triggers discount...
frappe.ui.form.on('Sales Order', {
    discount_percent(frm) {
        frm.set_value('grand_total', calculate(frm));  // Fires on_change loop
    }
});

// ✅ CORRECT — Use flags to break the cycle
frappe.ui.form.on('Sales Order', {
    discount_percent(frm) {
        if (frm.flags.skip_recalc) return;
        frm.flags.skip_recalc = true;
        frm.set_value('grand_total', calculate(frm));
        frm.flags.skip_recalc = false;
    }
});
```

---

## Debug Tools

| Tool | How to Use | When |
|------|-----------|------|
| Browser Console (F12) | `console.log(frm.doc)` | Inspect form state |
| `console.table()` | `console.table(frm.doc.items)` | View child table rows |
| `JSON.parse(JSON.stringify(frm.doc))` | Deep-clone for snapshot | Avoid circular refs in console |
| `frappe.boot.developer_mode` | Check if dev mode on | Conditional debug logging |
| `frappe.ui.toolbar.clear_cache()` | Clear client cache | After deploying script changes |
| Network tab (F12) | Filter XHR requests | Inspect frappe.call payloads |
| `frappe.show_alert({message: 'debug', indicator: 'blue'}, 5)` | Visual debug in UI | Quick feedback without console |

---

## ALWAYS / NEVER Rules

### ALWAYS

1. **Use the `frm` parameter** — NEVER use `cur_frm` [v14+]
2. **Wrap async frappe.call in try/catch** — Unhandled rejections fail silently
3. **Use `__()` for all user-facing strings** — Required for translation
4. **Collect multiple validation errors** before calling `frappe.throw()`
5. **Use `frappe.get_doc(cdt, cdn)`** to access child table rows in events
6. **Put `frappe.throw()` only in `validate`** to prevent save
7. **Check `r.message` for null** before accessing server response properties
8. **Use `frappe.model.set_value(cdt, cdn, field, value)`** in child table events

### NEVER

1. **NEVER use `alert()`, `confirm()`, or `prompt()`** — Use frappe.msgprint / frappe.confirm
2. **NEVER expose stack traces to users** — Log to console, show friendly message
3. **NEVER use `cur_frm`** — It is unreliable and undefined in many contexts
4. **NEVER leave `console.log` in production** — Use conditional `frappe.boot.developer_mode` check
5. **NEVER mix `.then()` and `await`** in the same function — Pick one pattern
6. **NEVER call `frm.set_value` in `setup`** — Form is not ready; use `refresh` or `onload`
7. **NEVER ignore the `error` callback** on `frappe.call` when using callback style

---

## Reference Files

| File | Contents |
|------|----------|
| `references/examples.md` | Real error scenarios with diagnosis |
| `references/anti-patterns.md` | Common mistakes with before/after fixes |
| `references/patterns.md` | Defensive error handling patterns |
---
name: frappe-errors-controllers
description: >
  Use when debugging or preventing errors in Frappe Document Controllers.
  Prevents autoname failures, validate loops, on_submit without is_submittable,
  wrong lifecycle hook choice, get_list permission errors, NestedSet errors,
  extend_doctype_class conflicts, missing super() calls, and recursion without
  flags. Covers error diagnosis by lifecycle phase for v14/v15/v16.
  Keywords: controller error, autoname, validate loop, on_submit, is_submittable,, save fails, validate error, on_submit not working, autoname broken, controller crash.
  get_list, NestedSet, extend_doctype_class, super, flags, recursion guard.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Controller Errors — Diagnosis and Resolution

Cross-refs: `frappe-syntax-controllers` (syntax), `frappe-impl-controllers` (workflows), `frappe-errors-serverscripts` (server scripts).

---

## Error Diagnosis by Lifecycle Phase

```
CONTROLLER ERROR
│
├─► NAMING PHASE (autoname / before_naming)
│   ├─► NamingSeries not set → Add naming_series field or autoname property
│   ├─► DuplicateEntryError → Name collision, check uniqueness
│   └─► "name cannot be set directly" → Use autoname method, not self.name = x
│
├─► VALIDATION PHASE (before_validate / validate / before_save)
│   ├─► Infinite recursion → doc.save() called inside validate
│   ├─► Validation skipped → Missing super().validate() in override
│   └─► Wrong error timing → Use validate, not on_update, to block save
│
├─► SAVE PHASE (before_save / on_update / after_insert)
│   ├─► Changes lost in on_update → Use db_set(), not self.field = x
│   ├─► Infinite loop → self.save() in on_update triggers on_update again
│   └─► Transaction broken → frappe.db.commit() in controller (DON'T)
│
├─► SUBMIT PHASE (before_submit / on_submit)
│   ├─► "Not allowed to submit" → DocType missing is_submittable = 1
│   ├─► Partial state → Validation in on_submit (too late, already submitted)
│   └─► Stock/GL failures → Entries fail but docstatus already = 1
│
├─► CANCEL PHASE (before_cancel / on_cancel)
│   ├─► "Cannot cancel: linked docs" → Check and handle linked documents
│   └─► Partial cleanup → One reversal fails, rest skipped
│
└─► PERMISSION PHASE (has_permission / get_list)
    ├─► "Not permitted" → has_permission returns None (should be True/False)
    ├─► get_list returns nothing → permission_query_conditions SQL error
    └─► SQL injection → User input in conditions without escape
```

---

## Error Message → Cause → Fix Table

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `NamingSeries is not set` | DocType uses naming_series but field is missing | Add `naming_series` field to DocType or set `autoname` in controller |
| `DuplicateEntryError` | `autoname` generated non-unique name | Use `naming_series` with counter, or add hash suffix |
| `Maximum recursion depth exceeded` | `self.save()` called in validate/on_update | NEVER call `self.save()` in hooks; use `self.db_set()` in on_update |
| `Not allowed to submit` | DocType lacks `is_submittable = 1` | Enable "Is Submittable" in DocType settings |
| `Cannot cancel: linked docs exist` | Submitted linked documents block cancellation | Cancel linked docs first, or use `before_cancel` to check |
| `AttributeError: super()` | Missing `super()` call in overridden hook | ALWAYS call `super().method_name()` first in overrides |
| `Value missing for: field` | Controller validate skipped parent logic | Ensure `super().validate()` is called |
| `frappe.db.commit() breaks transactions` | Manual commit in controller hook | NEVER call `frappe.db.commit()` in controllers |
| `Changes lost in on_update` | Set `self.field = x` instead of `self.db_set()` | Use `self.db_set("field", value)` after save hooks |
| `NestedSet: root cannot be child` | Parent set to itself or circular reference | Validate parent != self in validate, check `lft`/`rgt` |
| `extend_doctype_class conflict` [v16+] | Multiple apps extend same class with conflicting methods | Use MRO-aware design, check method resolution order |
| `has_permission returns wrong result` | Function returns None instead of True/False | ALWAYS return explicit True or False |
| `permission_query_conditions SQL error` | Malformed WHERE clause fragment | Test conditions string independently, use `frappe.db.escape()` |

---

## Critical Error Patterns

### 1. Autoname Failures

```python
# ❌ WRONG — Setting name directly fails
class CustomDoc(Document):
    def autoname(self):
        self.name = f"DOC-{self.customer}"  # May cause DuplicateEntryError

# ✅ CORRECT — Use naming utilities
class CustomDoc(Document):
    def autoname(self):
        # Option 1: Naming series
        from frappe.model.naming import set_name_by_naming_series
        set_name_by_naming_series(self)

        # Option 2: Safe format with counter
        self.name = frappe.model.naming.make_autoname(
            f"DOC-.{self.customer}.-.####"
        )

        # Option 3: Hash for guaranteed uniqueness
        # Set autoname = "hash" in DocType JSON instead
```

**Autoname options**: `naming_series`, `field:fieldname`, `format:PREFIX-{fieldname}-.####`, `hash`, `Prompt`, or custom `autoname()` method.

### 2. Validate Loop: self.save() in Hooks

```python
# ❌ WRONG — Infinite recursion
class SalesOrder(Document):
    def validate(self):
        self.calculate_totals()
        self.save()  # Triggers validate again → infinite loop!

    def on_update(self):
        self.status = "Updated"
        self.save()  # Triggers on_update again → infinite loop!

# ✅ CORRECT — Framework handles save; use db_set after save
class SalesOrder(Document):
    def validate(self):
        self.calculate_totals()
        # No save() — framework saves after validate completes

    def on_update(self):
        self.db_set("status", "Updated")  # Direct DB write, no trigger
```

### 3. on_submit Without is_submittable

```python
# ❌ ERROR — "Not allowed to submit"
class MyDoc(Document):
    def on_submit(self):
        self.create_entries()
# This fails if DocType JSON lacks: "is_submittable": 1

# ✅ FIX — Enable in DocType definition
# In my_doc.json:
# { "is_submittable": 1 }
# Then before_submit and on_submit hooks work
```

### 4. Wrong Lifecycle Hook: Error Timing

```python
# ❌ WRONG — Validation in on_submit (document already submitted!)
class SalesOrder(Document):
    def on_submit(self):
        if not self.has_stock():
            frappe.throw(_("Insufficient stock"))  # docstatus already = 1!

# ✅ CORRECT — ALWAYS validate in before_submit
class SalesOrder(Document):
    def before_submit(self):
        if not self.has_stock():
            frappe.throw(_("Insufficient stock"))  # Clean abort, stays Draft

    def on_submit(self):
        self.create_stock_entries()  # Only post-submit actions here
```

**Transaction Rollback Rules by Hook:**

| Hook | `frappe.throw()` Effect |
|------|------------------------|
| `validate` / `before_save` | Full rollback — document NOT saved |
| `before_submit` | Full rollback — stays Draft |
| `before_cancel` | Full rollback — stays Submitted |
| `on_update` / `after_insert` | Document IS saved — error shown but doc persists |
| `on_submit` | docstatus = 1 — error shown but ALREADY submitted |
| `on_cancel` | docstatus = 2 — error shown but ALREADY cancelled |

### 5. Missing super() in Overrides

```python
# ❌ WRONG — Parent validation completely skipped
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

class CustomSalesOrder(SalesOrder):
    def validate(self):
        # Parent validate() never runs! All ERPNext validations bypassed!
        self.custom_check()

# ✅ CORRECT — ALWAYS call super() first
class CustomSalesOrder(SalesOrder):
    def validate(self):
        super().validate()  # Run all parent validations first
        self.custom_check()  # Then add custom logic
```

### 6. extend_doctype_class [v16+]

```python
# In hooks.py — v16+ preferred approach
extend_doctype_class = {
    "Sales Order": ["myapp.overrides.sales_order.SalesOrderMixin"]
}

# myapp/overrides/sales_order.py
class SalesOrderMixin:
    """Mixin class — extends, does not replace."""
    def validate(self):
        super().validate()  # ALWAYS call super — runs original + other mixins
        self.custom_validation()
```

**Resolution order**: `class ExtendedSalesOrder(Mixin2, Mixin1, OriginalSalesOrder)` — last mixin listed has highest priority.

### 7. Flags for Recursion Guard

```python
# ❌ WRONG — on_update of linked doc triggers this doc's on_update
class SalesOrder(Document):
    def on_update(self):
        self.update_quotation()  # Quotation.on_update triggers back here

# ✅ CORRECT — Use flags to prevent recursion
class SalesOrder(Document):
    def on_update(self):
        if self.flags.get("skip_linked_update"):
            return
        self.flags.skip_linked_update = True
        self.update_quotation()

    def update_quotation(self):
        if self.quotation:
            q = frappe.get_doc("Quotation", self.quotation)
            q.flags.skip_linked_update = True  # Prevent back-trigger
            q.db_set("status", "Ordered")
```

### 8. get_list Permission Errors

```python
# ❌ WRONG — permission_query_conditions returns None (fallback to no filter)
def get_permission_query(user):
    pass  # Returns None — shows ALL records!

# ❌ WRONG — SQL injection
def get_permission_query(user):
    dept = frappe.db.get_value("User", user, "department")
    return f"department = '{dept}'"  # INJECTION RISK

# ✅ CORRECT — Explicit conditions with escape
def get_permission_query(user):
    if "System Manager" in frappe.get_roles(user):
        return ""  # No filter — full access
    dept = frappe.db.get_value("User", user, "department")
    if dept:
        return f"department = {frappe.db.escape(dept)}"
    return "owner = {0}".format(frappe.db.escape(user))
```

**Note**: `permission_query_conditions` affects `frappe.db.get_list()` only, NOT `frappe.db.get_all()`.

### 9. NestedSet Errors

```python
# ❌ WRONG — Circular reference causes lft/rgt corruption
class Territory(NestedSet):
    def validate(self):
        # No parent validation!
        pass

# ✅ CORRECT — Validate parent chain
class Territory(NestedSet):
    def validate(self):
        super().validate()
        if self.parent_territory == self.name:
            frappe.throw(_("Territory cannot be its own parent"))
        # NestedSet.validate() checks circular refs automatically
        # but explicit check gives better error message
```

---

## on_cancel: Isolate Cleanup Operations

```python
# ❌ WRONG — First failure stops all cleanup
def on_cancel(self):
    self.reverse_stock()     # If this fails...
    self.reverse_gl()        # ...this never runs
    self.update_linked()     # ...neither does this

# ✅ CORRECT — Isolate each reversal
def on_cancel(self):
    errors = []
    for operation, label in [
        (self.reverse_stock, "Stock reversal"),
        (self.reverse_gl, "GL reversal"),
        (self.update_linked, "Linked docs"),
    ]:
        try:
            operation()
        except Exception as e:
            errors.append(f"{label}: {str(e)}")
            frappe.log_error(frappe.get_traceback(), f"{label} Error")

    if errors:
        frappe.msgprint(
            _("Cancelled with errors:<br>{0}").format("<br>".join(errors)),
            indicator="orange"
        )
```

---

## ALWAYS / NEVER Rules

### ALWAYS

1. **Call `super().method()` in overridden hooks** — Preserve parent logic
2. **Validate in `before_submit`** not `on_submit` — Last clean abort point
3. **Use `self.db_set()` in `on_update`** — Direct `self.field = x` is lost
4. **Use `self.flags` for recursion guards** — Prevent circular hook triggers
5. **Isolate cleanup operations in `on_cancel`** — Don't let one failure stop all
6. **Use `frappe.db.escape()` in permission queries** — Prevent SQL injection
7. **Return explicit True/False from `has_permission`** — None falls back to default
8. **Use `frappe.log_error()` for unexpected exceptions** — Never swallow silently
9. **Use `_()` wrapper for all user-facing error messages** — Enable translation

### NEVER

1. **NEVER call `self.save()` in validate/on_update** — Causes infinite recursion
2. **NEVER call `frappe.db.commit()` in controllers** — Framework manages transactions
3. **NEVER put blocking validation in `on_submit`** — Document already submitted
4. **NEVER skip `super()` in overridden methods** — Breaks parent class logic
5. **NEVER return None from `has_permission`** — Returns unpredictable results
6. **NEVER swallow exceptions with bare `except: pass`** — Always log errors
7. **NEVER use `override_doctype_class` when `extend_doctype_class` works** [v16+]
8. **NEVER put heavy operations in `validate`** — Use `frappe.enqueue()` from `on_update`

---

## Reference Files

| File | Contents |
|------|----------|
| `references/examples.md` | Real controller error scenarios with diagnosis |
| `references/anti-patterns.md` | Common controller mistakes with fixes |
| `references/patterns.md` | Defensive error handling patterns by lifecycle hook |
---
name: frappe-errors-database
description: >
  Use when handling database errors in Frappe/ERPNext. Covers
  DuplicateEntryError, LinkValidationError, MandatoryError,
  TimestampMismatchError, CharacterLengthExceededError, InReadOnlyMode,
  QueryTimeoutError, SQL injection errors, frappe.db.sql parameter format
  (% vs %s), get_value returning None, transaction deadlocks, MariaDB gone
  away, too many connections. Error-to-fix mapping for v14/v15/v16.
  Keywords: database error, DuplicateEntryError, TimestampMismatchError,, MariaDB error, MySQL error, column not found, table missing, duplicate entry, database crash.
  SQL injection, deadlock, MariaDB gone away, query timeout.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Database Error Diagnosis & Resolution

Cross-ref: `frappe-core-database` (API syntax), `frappe-errors-controllers` (controller errors).

---

## Error-to-Fix Mapping Table

| Error / Exception | HTTP | Cause | Fix |
|-------------------|------|-------|-----|
| `DuplicateEntryError` | 409 | Unique constraint violation on insert/rename | Check existence first OR catch and return existing |
| `DoesNotExistError` | 404 | `get_doc()` on missing record | Use `frappe.db.exists()` first OR catch exception |
| `LinkValidationError` | 417 | Link field points to non-existent record | Validate link target exists before save |
| `LinkExistsError` | N/A | Delete blocked by linked documents | Show linked docs to user; use `force=True` carefully |
| `MandatoryError` | 417 | Required field is empty on save | Set all mandatory fields before insert/save |
| `TimestampMismatchError` | N/A | Concurrent edit detected (`modified` changed) | Reload doc and retry, or inform user to refresh |
| `CharacterLengthExceededError` | 417 | String exceeds field maxlength / DB column size | Truncate input or increase field length |
| `DataTooLongException` | 417 | Value exceeds DB column storage capacity | Same as CharacterLengthExceededError |
| `InReadOnlyMode` | 503 | Write attempted during read-only mode | Check `frappe.flags.in_import` or site config |
| `QueryTimeoutError` | N/A | Query exceeded time limit [v15+] | Add indexes, reduce result set, paginate |
| `QueryDeadlockError` | N/A | Two transactions waiting on each other | Retry with backoff; reduce transaction scope |
| `TooManyWritesError` | N/A | Excessive writes in single request | Batch operations; use background jobs |
| `InternalError` (gone away) | N/A | MariaDB connection dropped | Reconnect with `frappe.db.connect()` |
| `InternalError` (too many) | N/A | Connection pool exhausted | Check `max_connections`; close idle connections |
| `ValidationError` | 417 | General validation failure in save | Read error message; fix field values |
| SQL syntax error | N/A | Wrong `frappe.db.sql()` parameter format | Use `%(name)s` with dict, NOT `%s` with tuple |

---

## Exception Hierarchy

```
Exception
├── frappe.ValidationError (HTTP 417)
│   ├── frappe.MandatoryError
│   ├── frappe.LinkValidationError
│   ├── frappe.CharacterLengthExceededError
│   ├── frappe.DataTooLongException
│   ├── frappe.UniqueValidationError
│   ├── frappe.UpdateAfterSubmitError
│   └── frappe.DataError
├── frappe.DoesNotExistError (HTTP 404)
├── frappe.DuplicateEntryError (HTTP 409)  ← inherits NameError
├── frappe.TimestampMismatchError
├── frappe.LinkExistsError
├── frappe.QueryTimeoutError
├── frappe.QueryDeadlockError
├── frappe.TooManyWritesError
├── frappe.InReadOnlyMode (HTTP 503)
└── frappe.db.InternalError  ← MariaDB/Postgres driver error
```

---

## frappe.db.sql() Parameter Format

```python
# ❌ WRONG — %s with positional tuple (works but fragile)
frappe.db.sql("SELECT * FROM `tabItem` WHERE name = %s", ("ITEM-001",))

# ❌ WRONG — f-string or .format() — SQL INJECTION!
frappe.db.sql(f"SELECT * FROM `tabItem` WHERE name = '{item_name}'")
frappe.db.sql("SELECT * FROM `tabItem` WHERE name = '{}'".format(item_name))

# ❌ WRONG — bare % operator
frappe.db.sql("SELECT * FROM `tabItem` WHERE name = '%s'" % item_name)

# ✅ CORRECT — named parameters with dict (ALWAYS use this)
frappe.db.sql(
    "SELECT * FROM `tabItem` WHERE name = %(name)s AND warehouse = %(wh)s",
    {"name": item_name, "wh": warehouse},
    as_dict=True
)

# ✅ CORRECT — frappe.qb (query builder, no injection risk)
Item = frappe.qb.DocType("Item")
result = (
    frappe.qb.from_(Item)
    .select(Item.name, Item.item_name)
    .where(Item.warehouse == warehouse)
    .run(as_dict=True)
)
```

**Rule**: ALWAYS use `%(name)s` with a dict parameter. NEVER use string formatting for SQL values.

---

## get_value Returns None: Not an Exception

```python
# ❌ DANGEROUS — get_value returns None, not raises
credit = frappe.db.get_value("Customer", "CUST-001", "credit_limit")
if credit > 1000:  # TypeError: '>' not supported between NoneType and int
    pass

# ✅ CORRECT — handle None explicitly
credit = frappe.db.get_value("Customer", "CUST-001", "credit_limit")
if credit is None:
    frappe.throw(_("Customer not found"))
credit = credit or 0  # Default to 0 if field is empty

# ✅ CORRECT — get_value with as_dict for multiple fields
data = frappe.db.get_value("Customer", "CUST-001",
    ["credit_limit", "disabled"], as_dict=True)
if not data:  # None when record not found
    frappe.throw(_("Customer not found"))
if data.disabled:
    frappe.throw(_("Customer is disabled"))
```

**Key behavior by method**:
| Method | Record Not Found | Empty Field |
|--------|-----------------|-------------|
| `get_doc()` | Raises `DoesNotExistError` | Returns field default |
| `get_value()` | Returns `None` | Returns `None` or `""` |
| `get_all()` | Returns `[]` | Included in result |
| `exists()` | Returns `False` | N/A |
| `set_value()` | Silently does nothing | N/A |
| `db.sql()` | Returns `[]` or `()` | Included in result |

---

## Handling Each Exception Type

### DuplicateEntryError

```python
# Pattern: Insert with duplicate handling
def create_or_get(doctype, data):
    try:
        doc = frappe.get_doc({"doctype": doctype, **data})
        doc.insert()
        return doc
    except frappe.DuplicateEntryError:
        # Race condition safe: someone else created it
        name = frappe.db.get_value(doctype, data, "name")
        return frappe.get_doc(doctype, name)
```

### TimestampMismatchError

```python
# Pattern: Concurrent edit detection
try:
    doc = frappe.get_doc("Sales Invoice", name)
    doc.update(updates)
    doc.save()
except frappe.TimestampMismatchError:
    frappe.throw(
        _("Document modified by another user. Please refresh and try again."),
        title=_("Concurrent Edit")
    )
```

### LinkValidationError & MandatoryError

```python
# Pattern: Pre-validate before save
def safe_create_invoice(data):
    errors = []

    # Check mandatory fields
    if not data.get("customer"):
        errors.append(_("Customer is required"))
    if not data.get("items"):
        errors.append(_("At least one item is required"))

    # Check link validity
    if data.get("customer"):
        if not frappe.db.exists("Customer", data["customer"]):
            errors.append(_("Customer '{0}' not found").format(data["customer"]))

    if errors:
        frappe.throw("<br>".join(errors))

    doc = frappe.get_doc({"doctype": "Sales Invoice", **data})
    doc.insert()
    return doc
```

### CharacterLengthExceededError

```python
# Pattern: Truncate before save
def safe_set_description(doc, description):
    max_len = 140  # Match field length in DocType
    if len(description) > max_len:
        description = description[:max_len - 3] + "..."
        frappe.msgprint(_("Description truncated to {0} characters").format(max_len))
    doc.description = description
```

### QueryTimeoutError [v15+]

```python
# Pattern: Paginated query to avoid timeout
def get_large_report(filters):
    try:
        return frappe.db.sql(query, filters, as_dict=True)
    except frappe.QueryTimeoutError:
        frappe.log_error(frappe.get_traceback(), "Report Query Timeout")
        frappe.throw(
            _("Report too large. Please narrow your date range or add filters."),
            title=_("Query Timeout")
        )
```

### InReadOnlyMode

```python
# Pattern: Check before write
def safe_write(doctype, name, field, value):
    if frappe.flags.in_import:
        frappe.db.set_value(doctype, name, field, value)
        return
    try:
        frappe.db.set_value(doctype, name, field, value)
    except frappe.InReadOnlyMode:
        frappe.log_error(f"Write blocked: {doctype}/{name}", "Read-Only Mode")
        frappe.throw(_("System is in read-only mode. Please try again later."))
```

---

## Transaction Deadlocks

```python
# ❌ CAUSES DEADLOCKS — long transaction with many writes
def process_all():
    for inv in frappe.get_all("Sales Invoice", limit=10000):
        doc = frappe.get_doc("Sales Invoice", inv.name)
        doc.custom_field = "value"
        doc.save()  # Each save locks rows; other processes wait

# ✅ CORRECT — batch with commits to release locks
def process_all():
    invoices = frappe.get_all("Sales Invoice", limit=10000)
    BATCH = 100
    for i in range(0, len(invoices), BATCH):
        for inv in invoices[i:i + BATCH]:
            frappe.db.set_value("Sales Invoice", inv.name, "custom_field", "value")
        frappe.db.commit()  # Release locks after each batch

# ✅ CORRECT — retry on deadlock
import time
def with_deadlock_retry(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except frappe.QueryDeadlockError:
            if attempt < max_retries - 1:
                frappe.db.rollback()
                time.sleep(0.5 * (attempt + 1))
            else:
                raise
```

---

## MariaDB Gone Away / Too Many Connections

```python
# Pattern: Connection recovery
def reliable_operation():
    try:
        return frappe.db.sql("SELECT 1")
    except frappe.db.InternalError as e:
        msg = str(e).lower()
        if "gone away" in msg or "lost connection" in msg:
            frappe.db.connect()  # Reconnect
            return frappe.db.sql("SELECT 1")
        if "too many connections" in msg:
            frappe.log_error("Too many DB connections", "Connection Pool")
            frappe.throw(_("Server busy. Please try again in a moment."))
        raise  # Unknown InternalError — re-raise
```

**Prevention**:
- Set `wait_timeout` in MariaDB config (default 28800s)
- Check `max_connections` setting matches your workload
- Use connection pooling in production (Gunicorn workers)

---

## Transaction Rules

### When to Commit

| Context | Auto-Commit? | Manual Commit? |
|---------|:------------:|:--------------:|
| Web request (POST/PUT) | YES | NEVER |
| Controller hooks (validate, on_update) | YES | NEVER |
| doc_events hooks | YES | NEVER |
| Scheduler tasks | NO | ALWAYS |
| Background jobs (frappe.enqueue) | NO | ALWAYS |
| bench execute | NO | ALWAYS |

### Savepoints for Partial Rollback

```python
def complex_operation():
    frappe.db.savepoint("before_risky")
    try:
        risky_database_operation()
    except Exception:
        frappe.db.rollback(save_point="before_risky")
        safe_alternative()  # Continue with fallback

# Transaction hooks [v15+]
frappe.db.after_commit.add(lambda: send_notification())
frappe.db.after_rollback.add(lambda: cleanup_files())
```

---

## SQL Injection Prevention

```python
# ❌ INJECTION VULNERABLE — all of these
frappe.db.sql(f"SELECT * FROM `tabItem` WHERE name = '{user_input}'")
frappe.db.sql("SELECT * FROM `tabItem` WHERE name = '%s'" % user_input)
frappe.db.sql("SELECT * FROM `tabItem` WHERE name = '{}'".format(user_input))

# ❌ ALSO VULNERABLE — in permission_query_conditions
def query_conditions(user):
    return f"owner = '{user}'"  # Unescaped!

# ✅ SAFE — parameterized query
frappe.db.sql("SELECT * FROM `tabItem` WHERE name = %(name)s", {"name": user_input})

# ✅ SAFE — frappe.db.escape() for dynamic SQL (permission hooks)
def query_conditions(user):
    return f"owner = {frappe.db.escape(user)}"

# ✅ SAFE — query builder
Item = frappe.qb.DocType("Item")
frappe.qb.from_(Item).where(Item.name == user_input).run()

# ✅ SAFE — ORM methods
frappe.get_all("Item", filters={"name": user_input})
frappe.db.get_value("Item", user_input, "item_name")
```

---

## db.set_value Silent Failure

```python
# ❌ DANGEROUS — no error if record doesn't exist
frappe.db.set_value("Customer", "NONEXISTENT", "status", "Active")
# Returns without error! No rows updated.

# ✅ ALWAYS verify existence before set_value
if not frappe.db.exists("Customer", customer_name):
    frappe.throw(_("Customer '{0}' not found").format(customer_name))
frappe.db.set_value("Customer", customer_name, "status", "Active")

# Note: set_value skips validate/on_update hooks
# Use doc.save() when you need validation to run
```

---

## Critical Rules

### ALWAYS
1. Use `%(name)s` dict params in `frappe.db.sql()` — NEVER string formatting
2. Check `frappe.db.exists()` before `get_doc()` — or catch `DoesNotExistError`
3. Handle `DuplicateEntryError` on every `insert()` call
4. Handle `TimestampMismatchError` on every `save()` in APIs
5. Call `frappe.db.commit()` in scheduler and background jobs
6. Paginate large queries — use `limit` parameter
7. Check `get_value()` result for `None` before using it
8. Use `frappe.db.escape()` in dynamic SQL strings

### NEVER
1. Use string formatting (`f""`, `.format()`, `%`) for SQL values
2. Call `frappe.db.commit()` in controller hooks or doc_events
3. Catch bare `Exception` and `pass` — log or re-raise specific types
4. Assume `db.set_value()` succeeded — it fails silently on missing records
5. Expose raw database error messages to users — log details, show generic message
6. Run unbounded queries without `limit` — memory/timeout risk

---

## Quick Reference: Exception Handling

```python
try:
    doc = frappe.get_doc("Customer", name)
except frappe.DoesNotExistError:
    frappe.throw(_("Not found"))

try:
    doc.insert()
except frappe.DuplicateEntryError:
    existing = frappe.db.get_value("Customer", filters, "name")
except frappe.MandatoryError as e:
    frappe.throw(_("Missing required field: {0}").format(e))

try:
    doc.save()
except frappe.TimestampMismatchError:
    frappe.throw(_("Document modified. Please refresh."))
except frappe.CharacterLengthExceededError:
    frappe.throw(_("Text too long for field"))

try:
    frappe.delete_doc("Customer", name)
except frappe.LinkExistsError:
    frappe.throw(_("Cannot delete — linked documents exist"))

try:
    frappe.db.sql(query, values)
except frappe.QueryTimeoutError:          # [v15+]
    frappe.throw(_("Query too slow. Add filters."))
except frappe.QueryDeadlockError:
    frappe.db.rollback()                   # Retry with backoff
except frappe.db.InternalError as e:
    frappe.log_error(frappe.get_traceback(), "DB Error")
```

---

## Reference Files

| File | Contents |
|------|----------|
| `references/patterns.md` | Complete error handling patterns for all DB operations |
| `references/examples.md` | Full working examples with error handling |
| `references/anti-patterns.md` | Common mistakes with wrong/correct pairs |

---

## See Also

- `frappe-core-database` — Database API syntax and query builder
- `frappe-errors-controllers` — Controller error handling
- `frappe-errors-hooks` — Hook error handling
- `frappe-core-permissions` — Permission patterns
---
name: frappe-errors-hooks
description: >
  Use when debugging hooks.py errors in Frappe/ERPNext. Covers hook not firing
  (typo, wrong dict structure), circular imports, app_include_js path errors,
  scheduler_events not running, doc_events on wrong DocType,
  permission_query_conditions SQL errors, override_doctype_class import
  failures, extend_doctype_class [v16+] conflicts, fixtures not loading.
  Error diagnosis by hook type for v14/v15/v16.
  Keywords: hooks.py error, hook not firing, scheduler not running,, hook not working, scheduler not running, app_include not loading, override not applied.
  doc_events error, circular import, fixtures error, override class error.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Hooks Error Diagnosis & Resolution

Cross-ref: `frappe-syntax-hooks` (syntax), `frappe-impl-hooks` (workflows), `frappe-errors-controllers` (controller errors).

---

## Error-to-Fix Mapping Table

| Error / Symptom | Cause | Fix |
|-----------------|-------|-----|
| Hook not firing at all | Typo in dotted path | Verify module path matches actual file location |
| `ImportError` on bench start | Wrong module path or circular import | Fix import path; break circular dependency |
| `AttributeError: module has no attribute` | Function name typo in hooks.py | Match function name exactly to Python definition |
| `app_include_js` not loading | Path missing `assets/` prefix or wrong extension | Use `"assets/myapp/js/file.js"` format |
| scheduler_events not running | Scheduler disabled or workers down | `bench scheduler enable`, check `bench doctor` |
| doc_events handler never called | DocType name misspelled in dict key | Use exact DocType name with spaces: `"Sales Invoice"` |
| `permission_query_conditions` breaks list view | SQL syntax error or frappe.throw() in handler | Return valid SQL string; NEVER throw |
| `override_doctype_class` import failure | Parent class import path changed between versions | Pin import to correct module path for target version |
| `extend_doctype_class` [v16+] method conflict | Two extensions define same method name | Rename conflicting methods; check hook resolution order |
| Fixtures not loading on install | Wrong `dt` key or DocType doesn't exist on target | Verify DocType exists before export; check filter syntax |
| `extend_bootinfo` breaks login | Unhandled exception in boot handler | Wrap ALL bootinfo code in try/except |
| Wildcard `"*"` handler breaks all saves | Unhandled exception in wildcard doc_events | ALWAYS wrap wildcard handlers in try/except |
| Hook fires but changes lost | Missing `frappe.db.commit()` in scheduler | Add explicit commit in scheduler/background tasks |
| Multiple handler chain broken | First handler throws, others never run | Isolate non-critical ops in try/except |

---

## Hook Registration Errors

### Hook Not Firing: Diagnosis Checklist

```
IS YOUR HOOK NOT FIRING?
│
├─► Check 1: Is the dotted path correct?
│   hooks.py: "myapp.events.sales.validate"
│   File:     myapp/events/sales.py → def validate(doc, method=None):
│   COMMON MISTAKE: "myapp.events.sales_invoice.validate" when file is sales.py
│
├─► Check 2: Is the dict structure correct?
│   doc_events uses NESTED dict: {"Sales Invoice": {"validate": "path"}}
│   scheduler_events uses LIST: {"daily": ["path1", "path2"]}
│   permission_query uses FLAT dict: {"Sales Invoice": "path"}
│
├─► Check 3: Is bench restarted after hooks.py change?
│   ALWAYS run: bench restart (or bench clear-cache for dev)
│
├─► Check 4: Is the DocType name exact?
│   "Sales Invoice" NOT "SalesInvoice" NOT "sales_invoice"
│   Use exact DocType name as shown in Frappe UI
│
└─► Check 5: Is the app installed on the site?
    bench --site mysite list-apps
```

### Circular Import Errors

```python
# ❌ CAUSES ImportError — circular dependency
# myapp/hooks.py imports from myapp.events
# myapp/events/sales.py imports from myapp.hooks

# ✅ CORRECT — break the cycle
# Move shared constants to myapp/constants.py
# Import from constants in both hooks.py and events/
```

**Rule**: NEVER import from hooks.py in your event handlers. hooks.py is read by the framework, not imported by your code.

### Wrong Dict Structure by Hook Type

```python
# ❌ WRONG — doc_events needs nested dict, not flat
doc_events = {
    "Sales Invoice": "myapp.events.validate"  # WRONG: string, not dict
}

# ✅ CORRECT
doc_events = {
    "Sales Invoice": {
        "validate": "myapp.events.sales.validate"
    }
}

# ❌ WRONG — scheduler_events daily needs list
scheduler_events = {
    "daily": "myapp.tasks.daily_sync"  # WRONG: string, not list
}

# ✅ CORRECT
scheduler_events = {
    "daily": ["myapp.tasks.daily_sync"]
}

# ❌ WRONG — cron needs nested dict with list values
scheduler_events = {
    "cron": ["0 9 * * *", "myapp.tasks.morning"]  # WRONG structure
}

# ✅ CORRECT
scheduler_events = {
    "cron": {
        "0 9 * * 1-5": ["myapp.tasks.morning_report"]
    }
}
```

---

## app_include_js / app_include_css Errors

```python
# ❌ WRONG — missing assets/ prefix
app_include_js = "js/myapp.js"

# ❌ WRONG — using Python module path instead of file path
app_include_js = "myapp.public.js.myapp"

# ✅ CORRECT — full asset path
app_include_js = "assets/myapp/js/myapp.js"

# ✅ CORRECT — multiple files as list
app_include_js = ["assets/myapp/js/app.js", "assets/myapp/js/utils.js"]
app_include_css = "assets/myapp/css/myapp.css"
```

**Diagnosis**: If JS/CSS not loading, check browser DevTools Network tab for 404. Run `bench build` after adding new files. ALWAYS verify the file exists at `myapp/public/js/myapp.js`.

---

## scheduler_events Not Running

### Diagnosis Steps

```bash
# Step 1: Is scheduler enabled?
bench scheduler status
# If disabled: bench scheduler enable

# Step 2: Are workers running?
bench doctor
# Look for: "Workers online: X"
# If 0: bench start (dev) or supervisorctl restart all (prod)

# Step 3: Check Scheduled Job Log
# In Frappe UI: /api/method/frappe.client.get_list?doctype=Scheduled Job Log&limit=5

# Step 4: Check Error Log for task failures
# In Frappe UI: /app/error-log

# Step 5: Is the task registered?
bench execute frappe.utils.scheduler.get_all_tasks
```

### Common Scheduler Failures

```python
# ❌ PROBLEM: Task runs but changes not persisted
def daily_sync():
    for item in frappe.get_all("Item", limit=100):
        frappe.db.set_value("Item", item.name, "synced", 1)
    # MISSING: frappe.db.commit() — ALL changes lost!

# ✅ FIX: ALWAYS commit in scheduler tasks
def daily_sync():
    for item in frappe.get_all("Item", limit=100):
        frappe.db.set_value("Item", item.name, "synced", 1)
    frappe.db.commit()

# ❌ PROBLEM: Task fails silently — no debugging possible
def daily_task():
    try:
        process_records()
    except Exception:
        pass  # Silent death

# ✅ FIX: ALWAYS log errors in scheduler
def daily_task():
    try:
        process_records()
        frappe.db.commit()
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Daily Task Error")
```

---

## doc_events Errors

### Error Handling by Event Phase

| Event | Throw Effect | Transaction | Pattern |
|-------|-------------|-------------|---------|
| `validate` | Prevents save, full rollback | Pre-write | Collect errors, throw once |
| `before_save` | Prevents save, full rollback | Pre-write | Same as validate |
| `on_update` | Doc already saved, error shown | Post-write | Isolate non-critical ops |
| `after_insert` | Doc already saved, error shown | Post-write | Isolate non-critical ops |
| `on_submit` | Doc already submitted | Post-write | Isolate non-critical ops |
| `on_cancel` | Doc already cancelled | Post-write | Isolate non-critical ops |

### Multiple Handler Chain Problem

```python
# If App A and App B both register validate for Sales Invoice:
# App A's handler throws → App B's handler NEVER runs

# ✅ ALWAYS be aware: your handler is not alone
def validate(doc, method=None):
    """Collect errors, throw once at end."""
    errors = []
    if doc.grand_total < 0:
        errors.append(_("Total cannot be negative"))
    if errors:
        frappe.throw("<br>".join(errors))

# ✅ For on_update: isolate independent operations
def on_update(doc, method=None):
    try:
        send_notification(doc)
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"Notify error: {doc.name}")
    try:
        sync_external(doc)
    except Exception:
        frappe.log_error(frappe.get_traceback(), f"Sync error: {doc.name}")
```

### NEVER Commit in doc_events

```python
# ❌ BREAKS transaction management
def on_update(doc, method=None):
    frappe.db.set_value("Counter", "main", "count", 100)
    frappe.db.commit()  # Partial commit — dangerous!

# ✅ Framework handles commits automatically
def on_update(doc, method=None):
    frappe.db.set_value("Counter", "main", "count", 100)
```

---

## Permission Hook Errors

### permission_query_conditions: NEVER Throw

```python
# ❌ BREAKS list view entirely
def query_conditions(user):
    if "Sales User" not in frappe.get_roles(user):
        frappe.throw("Access denied")  # LIST VIEW CRASHES
    return f"owner = '{user}'"  # Also: SQL injection!

# ✅ CORRECT — safe fallback, escaped values
def query_conditions(user):
    try:
        user = user or frappe.session.user
        if "System Manager" in frappe.get_roles(user):
            return ""
        return f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Query Conditions Error")
        return f"`tabSales Invoice`.owner = {frappe.db.escape(frappe.session.user)}"
```

**Note**: permission_query_conditions only affects `frappe.db.get_list()`, NOT `frappe.db.get_all()`.

### has_permission: NEVER Throw

```python
# ❌ BREAKS document access
def has_permission(doc, user=None, permission_type=None):
    if doc.status == "Locked":
        frappe.throw("Locked")  # DOCUMENT INACCESSIBLE

# ✅ Return False to deny, None to defer
def has_permission(doc, user=None, permission_type=None):
    try:
        user = user or frappe.session.user
        if doc.status == "Locked" and permission_type == "write":
            return False
        return None  # Defer to default permission system
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Permission Error")
        return None
```

---

## Override & Extend Errors

### override_doctype_class: Import Failures

```python
# ❌ COMMON: Import path changes between ERPNext versions
# v14 path:
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.CustomSI"
}
# myapp/overrides.py:
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
# This path may change in v15/v16!

# ✅ ALWAYS call super(), re-raise validation errors
class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        try:
            super().validate()
        except frappe.ValidationError:
            raise  # ALWAYS re-raise validation errors
        except Exception:
            frappe.log_error(frappe.get_traceback(), "Parent validate error")
            raise
        self.custom_validation()
```

**Warning**: Only ONE app's override_doctype_class is active per DocType ("last writer wins"). Use extend_doctype_class [v16+] for multi-app compatibility.

### extend_doctype_class [v16+]: Conflicts

```python
# hooks.py
extend_doctype_class = {
    "Sales Invoice": ["myapp.extensions.si.SalesInvoiceMixin"]
}

# ❌ CONFLICT: Two extensions define same method
# App A: class Mixin: def custom_calc(self): ...
# App B: class Mixin: def custom_calc(self): ...
# Result: Last app's method wins silently

# ✅ ALWAYS prefix method names with app name
class SalesInvoiceMixin:
    def myapp_custom_calc(self):
        """Prefixed to avoid conflicts with other extensions."""
        pass
```

---

## extend_bootinfo Errors

```python
# ❌ BREAKS LOGIN — unhandled error prevents desk from loading
def extend_boot(bootinfo):
    settings = frappe.get_single("My Settings")  # DoesNotExistError!
    bootinfo.config = settings.config

# ✅ ALWAYS wrap in try/except with safe defaults
def extend_boot(bootinfo):
    bootinfo.myapp_config = {}
    try:
        if frappe.db.exists("My Settings", "My Settings"):
            settings = frappe.get_single("My Settings")
            bootinfo.myapp_config = {"feature": settings.feature or False}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Bootinfo Error")
```

---

## Fixtures Not Loading

```python
# ❌ WRONG — dt key misspelled
fixtures = [{"doctype": "Custom Field", "filters": [...]}]  # "doctype" not "dt"!

# ✅ CORRECT — use "dt" key
fixtures = [{"dt": "Custom Field", "filters": [["module", "=", "My App"]]}]

# ❌ PROBLEM: DocType doesn't exist on target site
fixtures = [{"dt": "My Custom DocType"}]  # If not created yet → install fails

# ✅ FIX: Ensure DocType is created before fixtures are imported
# Order: DocType JSON → fixtures JSON (install order matters)
```

**Export command**: `bench --site mysite export-fixtures`
**Import**: Automatic during `bench --site mysite install-app myapp`

---

## Critical Rules

### ALWAYS
1. Restart bench after changing hooks.py
2. Use try/except in scheduler tasks — no user sees errors
3. Call `frappe.db.commit()` in scheduler — no auto-commit
4. Return safe fallbacks in permission hooks — NEVER throw
5. Call `super()` in override classes — re-raise ValidationError
6. Wrap `extend_bootinfo` in try/except — errors break login
7. Wrap wildcard `"*"` doc_events in try/except — errors break ALL saves
8. Prefix extend_doctype_class [v16+] methods with app name

### NEVER
1. Throw in `permission_query_conditions` — breaks list views
2. Throw in `has_permission` — breaks document access
3. Commit in doc_events — breaks transaction management
4. Import from hooks.py in event handlers — causes circular imports
5. Assume single handler — multiple apps register doc_events
6. Use string formatting in permission SQL — SQL injection risk
7. Ignore scheduler errors — they fail completely silently

---

## Quick Reference: Error Handling by Hook Type

| Hook Type | Can Throw? | Commit? | Error Strategy |
|-----------|:----------:|:-------:|----------------|
| doc_events (validate) | YES | NEVER | Collect errors, throw once |
| doc_events (on_update+) | Careful | NEVER | Isolate non-critical ops |
| scheduler_events | Pointless | ALWAYS | try/except + log_error |
| permission_query_conditions | NEVER | NEVER | Return "" or owner filter |
| has_permission | NEVER | NEVER | Return None on error |
| extend_bootinfo | NEVER | NEVER | try/except + safe defaults |
| override_doctype_class | YES | NEVER | super() + re-raise |
| extend_doctype_class [v16+] | YES | NEVER | Prefix methods, avoid conflicts |
| fixtures | N/A | N/A | Verify dt key and DocType existence |
| app_include_js/css | N/A | N/A | Check assets/ prefix, run bench build |

---

## Reference Files

| File | Contents |
|------|----------|
| `references/patterns.md` | Complete error handling patterns by hook type |
| `references/examples.md` | Full working examples with error handling |
| `references/anti-patterns.md` | Common mistakes with wrong/correct pairs |

---

## See Also

- `frappe-syntax-hooks` — Hook syntax and dict structures
- `frappe-impl-hooks` — Implementation workflows
- `frappe-errors-controllers` — Controller error handling
- `frappe-errors-database` — Database error handling
- `frappe-errors-serverscripts` — Server Script error handling
---
name: frappe-errors-permissions
description: >
  Use when debugging or handling permission errors in Frappe/ERPNext.
  Prevents broken document access from throwing in permission hooks.
  Covers PermissionError (403), has_permission hook failures, User Permission
  restricting too much or too little, perm_level blocking field access,
  System Manager bypass not working, Guest access denied, sharing permissions
  not applying, permission_query_conditions breaking get_list, owner-based
  permissions confusion, Apply User Permission checkbox behavior, and the
  permission debug workflow using frappe.permissions.get_doc_permissions.
  Keywords: PermissionError, has_permission, permission_query_conditions,, permission denied, cannot access, user blocked, sharing not working, role not enough.
  User Permission, perm_level, sharing, guest access, owner permission.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Permission Error Handling

For permission system overview see `frappe-core-permissions`. For hook syntax see `frappe-syntax-hooks`.

---

## Quick Diagnostic: Error Message -> Cause -> Fix

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `frappe.exceptions.PermissionError` | User lacks role or doc-level access | Add role in Role Permissions Manager or grant User Permission |
| "Not permitted" on document open | `has_permission` hook returns False or role missing read | Check `frappe.permissions.get_doc_permissions(doc, user)` output |
| List view shows 0 records | `permission_query_conditions` returns overly restrictive SQL | Debug the SQL condition; check User Permissions for the Link field |
| "Not allowed to access ... for Guest" | Endpoint missing `allow_guest=True` or DocType lacks Guest read | Add `allow_guest=True` to `@frappe.whitelist()` |
| Field invisible despite role having read | `perm_level` > 0 on field and role lacks that level | Add role permission row for the specific `perm_level` |
| "User Permission restriction" blocking | User Permission on a Link field auto-filters documents | Uncheck "Apply User Permissions" on that role row or add matching User Permission |
| Sharing not granting access | Sharing adds access but never overrides role absence | User MUST have base role permission; sharing only adds doc-level grants |
| `ignore_permissions` has no effect | Flag set after `get_doc` already checked permissions | Set `flags.ignore_permissions = True` BEFORE calling `save()` or `insert()` |
| System Manager cannot access | Custom `has_permission` hook denies without checking role | ALWAYS check for System Manager / Administrator in hook |

---

## Decision Tree: Where Is the Error?

```
Permission error occurred
├── Document-level (single doc access)?
│   ├── has_permission hook returning False?
│   │   └── Debug: frappe.permissions.get_doc_permissions(doc, user)
│   ├── User Permission restricting Link field?
│   │   └── Check: frappe.get_all("User Permission", filters={"user": user})
│   ├── perm_level blocking field?
│   │   └── Check: role has permission row for that perm_level
│   └── Sharing not applying?
│       └── Check: user has base role + sharing record exists
├── List-level (0 records in list view)?
│   ├── permission_query_conditions returning bad SQL?
│   │   └── Debug: run condition manually in MariaDB console
│   ├── User Permission auto-filtering?
│   │   └── Check "Apply User Permissions" checkbox on role row
│   └── get_all vs get_list confusion?
│       └── ALWAYS use get_list for user-facing queries
├── API endpoint (403 response)?
│   ├── Missing @frappe.whitelist()?
│   │   └── Add decorator to Python method
│   ├── Missing allow_guest=True?
│   │   └── Add allow_guest parameter for public endpoints
│   └── frappe.only_for() blocking?
│       └── Check user has required role
└── System Manager bypass failing?
    └── Custom hook does not check for System Manager role
```

---

## Permission Hook Errors

### has_permission Hook: NEVER Throw

```python
# hooks.py
has_permission = {
    "Sales Order": "myapp.permissions.sales_order_has_permission",
}
```

```python
# WRONG — Breaks ALL document access
def sales_order_has_permission(doc, user, permission_type):
    if doc.status == "Locked":
        frappe.throw("Locked")  # NEVER do this

# CORRECT — Return False to deny, None to defer
def sales_order_has_permission(doc, user, permission_type):
    """
    ALWAYS wrap in try/except. NEVER throw. NEVER return True.
    Returns: False (deny) or None (defer to standard system).
    """
    try:
        user = user or frappe.session.user
        if user == "Administrator":
            return None

        # ALWAYS check System Manager early
        if "System Manager" in frappe.get_roles(user):
            return None

        # Deny write on locked docs (but allow read)
        if permission_type in ("write", "delete", "cancel"):
            if doc.get("status") == "Locked":
                return False

        return None  # Defer to standard permission system

    except Exception:
        frappe.log_error(frappe.get_traceback(),
            f"has_permission error: {getattr(doc, 'name', 'unknown')}")
        return None  # Safe fallback — defer
```

**Critical rules for has_permission hooks:**
- ALWAYS return `None` to defer, `False` to deny. NEVER return `True` — hooks can only restrict, not grant.
- ALWAYS wrap the entire function in `try/except`. An unhandled exception breaks ALL access to that DocType.
- ALWAYS check for `Administrator` and `System Manager` at the top.
- NEVER call `frappe.throw()` inside this hook.

### permission_query_conditions: NEVER Throw

```python
# hooks.py
permission_query_conditions = {
    "Sales Order": "myapp.permissions.sales_order_query",
}
```

```python
# WRONG — Breaks list view for all users
def sales_order_query(user):
    if not user:
        frappe.throw("User required")  # NEVER do this
    return f"owner = '{user}'"  # SQL injection!

# CORRECT — Return SQL string or empty string
def sales_order_query(user):
    """
    ALWAYS return a string. Empty string = no restriction.
    ALWAYS use frappe.db.escape(). ALWAYS wrap in try/except.
    """
    try:
        user = user or frappe.session.user
        if user == "Administrator":
            return ""
        if "System Manager" in frappe.get_roles(user):
            return ""

        return f"`tabSales Order`.owner = {frappe.db.escape(user)}"

    except Exception:
        frappe.log_error(frappe.get_traceback(), "Query conditions error")
        # SAFE FALLBACK: most restrictive
        return f"`tabSales Order`.owner = {frappe.db.escape(frappe.session.user)}"
```

**Critical rules for permission_query_conditions:**
- NEVER throw errors — return `"1=0"` to deny all or a restrictive SQL string.
- ALWAYS use `frappe.db.escape()` for every user-supplied value.
- This hook ONLY affects `frappe.get_list()` / `frappe.db.get_list()`. It does NOT affect `frappe.get_all()` / `frappe.db.get_all()`.

---

## User Permission Errors

### Too Restrictive: Records Disappear

```
Error: User can't see any Sales Orders despite having Sales User role.
Cause: A User Permission for "Company" exists, and "Apply User Permissions"
       is checked on the Sales Order role row. Sales Order has a Company
       Link field, so ALL Sales Orders are filtered by that Company value.
```

**Debug steps:**
```python
# Step 1: Check what User Permissions exist
frappe.get_all("User Permission",
    filters={"user": "john@example.com"},
    fields=["allow", "for_value", "applicable_for"])

# Step 2: Check if Apply User Permissions is checked
frappe.get_all("DocPerm",
    filters={"parent": "Sales Order", "role": "Sales User"},
    fields=["role", "permlevel", "apply_user_permissions"])  # [v14]

# Step 3: Check effective permissions on a specific doc
from frappe.permissions import get_doc_permissions
perms = get_doc_permissions(frappe.get_doc("Sales Order", "SO-001"), "john@example.com")
```

**Fix patterns:**
- Remove overly broad User Permissions that filter unintended DocTypes.
- Use the `applicable_for` field [v14+] to limit which DocType a User Permission applies to.
- Uncheck "Apply User Permissions" on the role permission row if blanket filtering is unwanted.

### Too Permissive: User Sees Everything

```
Error: User Permission set for Territory = "North" but user sees all territories.
Cause: "Apply User Permissions" is NOT checked on the role permission row,
       or the DocType has no Link field for Territory.
```

**Fix:** Ensure the role permission row has "Apply User Permissions" checked AND the DocType has a Link field to the restricted DocType.

---

## perm_level Errors

```
Error: Field "cost_center" is invisible despite user having read permission.
Cause: Field has permlevel=1 but role only has permission for permlevel=0.
```

```python
# Check which perm_levels a role has access to
frappe.get_all("DocPerm",
    filters={"parent": "Sales Invoice", "role": "Accounts User"},
    fields=["permlevel", "read", "write"])
```

**Fix:** Add a new row in the DocType's Permission table for the role at the required `permlevel`.

---

## Sharing Permission Errors

```
Error: Document shared with user but user still gets PermissionError.
Cause: User has NO base role permission on the DocType. Sharing only
       supplements — it never replaces role-based permissions.
```

```python
# Share a document (user MUST already have a role with at least read)
frappe.share.add("Sales Order", "SO-001", "john@example.com",
    read=1, write=1, share=1)

# Check if sharing grants access
frappe.share.get_sharing_permissions("Sales Order", "SO-001", "john@example.com")
```

**Rules:**
- ALWAYS ensure the user has at least one role with read permission on the DocType before sharing.
- Sharing adds document-level grants on top of role permissions.
- [v15+] `frappe.share.add` accepts `notify=1` to send email notification.

---

## Guest Access Errors

```
Error: "Not permitted" for unauthenticated users.
Cause: DocType has no Guest read permission, or API missing allow_guest.
```

**Fix for web pages / portal:**
```python
# Add Guest read permission in DocType Permission table
# Role: Guest, Level: 0, Read: checked
```

**Fix for API endpoints:**
```python
@frappe.whitelist(allow_guest=True)
def public_endpoint():
    # ALWAYS validate input — guest endpoints are exposed to the internet
    pass
```

**NEVER grant Guest write/create/delete permissions** unless the DocType is specifically designed for public submission (e.g., Web Form backend).

---

## Debug Workflow: frappe.permissions

```python
import frappe
from frappe.permissions import get_doc_permissions

# Get all effective permissions for a user on a document
doc = frappe.get_doc("Sales Order", "SO-001")
perms = get_doc_permissions(doc, user="john@example.com")
# Returns dict: {"read": 1, "write": 0, "create": 0, ...}

# Check specific permission with full context
frappe.has_permission("Sales Order", ptype="write",
    doc="SO-001", user="john@example.com", throw=False)

# List all roles for a user
frappe.get_roles("john@example.com")

# Check User Permissions
frappe.get_all("User Permission",
    filters={"user": "john@example.com"},
    fields=["allow", "for_value", "applicable_for", "is_default"])
```

---

## Critical Rules

### ALWAYS
1. **Wrap permission hooks in try/except** — unhandled errors break all access
2. **Return None (not True) in has_permission** — hooks can only deny
3. **Use frappe.db.escape() in query conditions** — prevent SQL injection
4. **Check System Manager / Administrator first** in custom hooks
5. **Use frappe.has_permission(throw=True)** for endpoint permission checks
6. **Use get_list (not get_all)** for user-facing queries — get_all bypasses permissions
7. **Log permission denials** for security audit with `frappe.log_error()`

### NEVER
1. **Throw in has_permission or permission_query_conditions** — breaks access entirely
2. **Return True in has_permission** — has no effect, hooks can only restrict
3. **Use string formatting for SQL** — use `frappe.db.escape()` to prevent injection
4. **Grant Guest write/delete permissions** — security risk
5. **Use ignore_permissions without documenting why** — creates audit gaps
6. **Assume sharing replaces role permissions** — sharing only supplements

---

## Reference Files

| File | Contents |
|------|----------|
| `references/patterns.md` | Complete hook patterns, query conditions, API endpoints |
| `references/examples.md` | Full working examples with hooks.py configuration |
| `references/anti-patterns.md` | 15 common mistakes with wrong/correct comparisons |

---

## See Also

- `frappe-core-permissions` — Permission system architecture
- `frappe-errors-api` — API error handling (401/403/404)
- `frappe-errors-hooks` — Hook error handling patterns
- `frappe-syntax-hooks` — Hook registration syntax
---
name: frappe-errors-serverscripts
description: >
  Use when debugging or preventing errors in Frappe Server Scripts.
  Prevents ImportError (the #1 error), NameError for restricted builtins,
  sandbox violations, doc_events not firing, wrong script type selection,
  SQL injection, permission denied in scheduled scripts, infinite loops,
  and API scripts not returning JSON. Covers error message mapping table.
  Keywords: server script error, ImportError, NameError, sandbox,, ImportError in server script, script not running, sandbox error, restricted function.
  restricted, frappe.throw, doc_events, scheduler, API script, SQL injection.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Server Script Errors — Diagnosis and Resolution

Cross-refs: `frappe-syntax-serverscripts` (syntax), `frappe-impl-serverscripts` (workflows), `frappe-errors-clientscripts` (client-side).

---

## CRITICAL: Server Scripts Disabled by Default [v15+]

Starting from Frappe v15, Server Scripts are **disabled by default**. You MUST enable them:

```python
# In site_config.json
{ "server_script_enabled": 1 }
```

On Frappe Cloud: Server Scripts are ONLY available on **private benches**, NOT on shared benches.

---

## Error Diagnosis Flowchart

```
ERROR IN SERVER SCRIPT
│
├─► ImportError / NameError
│   ├─► "import json" → BLOCKED. Use frappe.parse_json()
│   ├─► "import datetime" → BLOCKED. Use frappe.utils
│   ├─► "import os/sys/subprocess" → BLOCKED. Security restriction
│   └─► "NameError: name 'dict' is not defined" → Some builtins restricted
│
├─► SyntaxError: not allowed
│   ├─► "try/except" → BLOCKED by RestrictedPython [v14-v15]
│   ├─► "raise ValueError" → BLOCKED. Use frappe.throw()
│   └─► "exec/eval" → BLOCKED. Security restriction
│
├─► Script runs but nothing happens
│   ├─► Wrong Script Type selected → Check Document Event vs API vs Scheduler
│   ├─► Wrong DocType selected → Verify exact DocType name
│   ├─► Wrong Event selected → Before Save ≠ After Save
│   └─► Script disabled → Check "Enabled" checkbox
│
├─► 403 Permission Denied
│   ├─► Scheduler script → Runs as Administrator, check role permissions
│   ├─► API script → Check Allow Guest setting
│   └─► doc_event → User lacks DocType permission
│
├─► Data not saved in Scheduler
│   └─► Missing frappe.db.commit() → REQUIRED in scheduler scripts
│
└─► API script returns empty/wrong response
    └─► Not setting frappe.response["message"] → ALWAYS set response
```

---

## Error Message → Cause → Fix Table

| Error Message | Cause | Fix |
|---------------|-------|-----|
| `ImportError: import not allowed` | Any `import` statement in sandbox | Use `frappe.utils`, `frappe.parse_json()`, etc. |
| `NameError: name 'dict' is not defined` | Some Python builtins blocked by RestrictedPython | Use `frappe._dict()` or literal `{}` |
| `SyntaxError: try/except not allowed` | RestrictedPython blocks exception handling [v14-v15] | Use conditional checks (`if/else`) instead |
| `SyntaxError: raise not allowed` | RestrictedPython blocks `raise` | Use `frappe.throw()` |
| `Script not executing` | Wrong Script Type or Event selected | Verify type matches: Document Event, API, or Scheduler |
| `doc is not defined` | Using `doc` in API or Scheduler script (no document context) | `doc` is only available in Document Event scripts |
| `PermissionError` in Scheduler | Scheduler runs as Administrator but script accesses restricted resource | Use `ignore_permissions=True` where appropriate |
| `Changes not saved` in Scheduler | Missing `frappe.db.commit()` | ALWAYS call `frappe.db.commit()` in Scheduler scripts |
| `API returns empty response` | Forgot to set `frappe.response["message"]` | ALWAYS set `frappe.response["message"] = result` |
| `Timeout / killed` | Infinite loop or processing too many records | ALWAYS add `limit` to queries, ALWAYS use batch processing |
| `ValidationError: qty is required` | `doc.save()` called in Before Save (recursion) | NEVER call `doc.save()` in Before Save; just set values |
| `SQL injection via string format` | User input in SQL without escaping | ALWAYS use `frappe.db.escape()` or parameterized queries |

---

## The #1 Error: ImportError

**Every beginner hits this.** The Server Script sandbox blocks ALL imports except `json`.

```python
# ❌ BLOCKED — These ALL fail with ImportError
import json                    # Use frappe.parse_json() / frappe.as_json()
from datetime import datetime  # Use frappe.utils.now(), frappe.utils.today()
import re                      # Not available in sandbox
import os                      # Security: blocked
import requests                # Use frappe.make_get_request(), frappe.make_post_request()

# ✅ CORRECT — Sandbox equivalents
data = frappe.parse_json(doc.json_field)         # Instead of json.loads()
today = frappe.utils.today()                      # Instead of datetime.date.today()
now = frappe.utils.now()                          # Instead of datetime.now()
diff = frappe.utils.date_diff(date1, date2)       # Instead of timedelta
resp = frappe.make_get_request("https://api.com") # Instead of requests.get()
resp = frappe.make_post_request("https://api.com", data=payload)
```

### Available Sandbox API (Complete Reference)

| Category | Available Methods |
|----------|-------------------|
| **Document** | `frappe.get_doc()`, `frappe.new_doc()`, `frappe.get_last_doc()`, `frappe.get_cached_doc()`, `frappe.get_mapped_doc()`, `frappe.rename_doc()`, `frappe.delete_doc()` |
| **Database** | `frappe.db.get_list()`, `frappe.db.get_all()`, `frappe.db.get_value()`, `frappe.db.get_single_value()`, `frappe.db.set_value()`, `frappe.db.exists()`, `frappe.db.sql()`, `frappe.db.commit()`, `frappe.db.rollback()`, `frappe.db.escape()` |
| **Query Builder** | `frappe.qb` (full query builder) |
| **HTTP** | `frappe.make_get_request()`, `frappe.make_post_request()`, `frappe.make_put_request()` |
| **Utility** | `frappe.utils.*` (all utility functions), `frappe.parse_json()`, `frappe.as_json()` |
| **User/Session** | `frappe.session.user`, `frappe.get_roles()`, `frappe.has_permission()` |
| **Messages** | `frappe.throw()`, `frappe.msgprint()`, `frappe.log_error()`, `frappe.sendmail()` |
| **Module** | `json` (the ONLY importable module) |

---

## Script Type Selection Errors

ALWAYS verify you selected the correct Script Type:

| Script Type | Trigger | Has `doc`? | Has `frappe.form_dict`? | Auto-commit? |
|-------------|---------|:----------:|:-----------------------:|:------------:|
| Document Event | DocType lifecycle (Before Save, After Save, etc.) | YES | NO | YES |
| API | HTTP request to `/api/method/{method_name}` | NO | YES | YES |
| Scheduler Event | Cron schedule | NO | NO | NO — MUST call `frappe.db.commit()` |
| Permission Query | Every list query on the DocType | NO | NO (has `user`) | N/A |

### Common Mistake: Wrong Event

```python
# ❌ WRONG — "After Save" cannot prevent save
# Script Type: Document Event, Event: After Save
if not doc.customer:
    frappe.throw("Customer is required")  # Document already saved!

# ✅ CORRECT — Use "Before Save" or "Before Validate"
# Script Type: Document Event, Event: Before Save
if not doc.customer:
    frappe.throw("Customer is required")  # Prevents save
```

---

## Sandbox Workarounds

### try/except Is Blocked: Use Conditional Checks

```python
# ❌ BLOCKED in sandbox
try:
    customer = frappe.get_doc("Customer", doc.customer)
except Exception:
    frappe.throw("Customer not found")

# ✅ CORRECT — Check first, then access
if not frappe.db.exists("Customer", doc.customer):
    frappe.throw(f"Customer '{doc.customer}' not found")
customer = frappe.get_doc("Customer", doc.customer)
```

### raise Is Blocked: Use frappe.throw()

```python
# ❌ BLOCKED
if amount < 0:
    raise ValueError("Amount cannot be negative")

# ✅ CORRECT
if amount < 0:
    frappe.throw("Amount cannot be negative")
```

### frappe.throw() Exception Types for API Scripts

| Exception | HTTP Code | Use When |
|-----------|:---------:|----------|
| `frappe.ValidationError` | 417 | Input validation failure |
| `frappe.PermissionError` | 403 | Access denied |
| `frappe.DoesNotExistError` | 404 | Record not found |
| `frappe.AuthenticationError` | 401 | Not logged in |
| (default, no exc) | 417 | General validation error |

```python
# API Script — Correct exception types
if not customer:
    frappe.throw("Customer param required", exc=frappe.ValidationError)  # 417
if not frappe.db.exists("Customer", customer):
    frappe.throw("Customer not found", exc=frappe.DoesNotExistError)    # 404
if not frappe.has_permission("Customer", "read", customer):
    frappe.throw("Access denied", exc=frappe.PermissionError)           # 403
```

---

## Scheduler Script: Critical Mistakes

```python
# ❌ WRONG — No limit, no commit, no error logging
invoices = frappe.get_all("Sales Invoice", filters={"status": "Unpaid"})
for inv in invoices:
    frappe.db.set_value("Sales Invoice", inv.name, "reminder_sent", 1)

# ✅ CORRECT — Limit, batch commit, error logging
BATCH_SIZE = 50
invoices = frappe.get_all(
    "Sales Invoice",
    filters={"status": "Unpaid", "docstatus": 1},
    fields=["name", "customer"],
    limit=500  # ALWAYS limit
)

errors = []
for i in range(0, len(invoices), BATCH_SIZE):
    batch = invoices[i:i + BATCH_SIZE]
    for inv in batch:
        if not frappe.db.exists("Customer", inv.customer):
            errors.append(f"{inv.name}: Customer not found")
            continue
        frappe.db.set_value("Sales Invoice", inv.name, "reminder_sent", 1)
    frappe.db.commit()  # REQUIRED

if errors:
    frappe.log_error("\n".join(errors), "Reminder Errors")
frappe.db.commit()
```

---

## SQL Injection Prevention

```python
# ❌ VULNERABLE — String interpolation with user input
territory = frappe.form_dict.get("territory")
conditions = f"`tabCustomer`.territory = '{territory}'"  # SQL INJECTION!

# ✅ SAFE — Use frappe.db.escape()
territory = frappe.form_dict.get("territory")
conditions = f"`tabCustomer`.territory = {frappe.db.escape(territory)}"

# ✅ SAFEST — Use parameterized query or Query Builder
results = frappe.db.get_all("Customer", filters={"territory": territory})
```

---

## ALWAYS / NEVER Rules

### ALWAYS

1. **Use `frappe.utils.*` instead of Python imports** — Only `json` module is importable
2. **Use `frappe.throw()` instead of `raise`** — `raise` is blocked by sandbox
3. **Use conditional checks instead of `try/except`** — Exception handling is blocked [v14-v15]
4. **Call `frappe.db.commit()` in Scheduler scripts** — Changes are NOT auto-committed
5. **Add `limit` to ALL queries in Scheduler scripts** — Prevent memory exhaustion
6. **Set `frappe.response["message"]` in API scripts** — Otherwise response is empty
7. **Use `frappe.db.escape()` for user input in SQL** — Prevent SQL injection
8. **Log errors in Scheduler scripts** with `frappe.log_error()` — No user to see errors
9. **Verify Script Type matches your intent** — Document Event vs API vs Scheduler

### NEVER

1. **NEVER use `import` statements** (except `json`) — Blocked by RestrictedPython
2. **NEVER use `try/except` or `raise`** — Blocked by sandbox [v14-v15]
3. **NEVER call `doc.save()` in Before Save** — Causes infinite recursion
4. **NEVER use string formatting for SQL with user input** — SQL injection risk
5. **NEVER process unlimited records in Scheduler** — Always use `limit`
6. **NEVER assume `doc` exists in API/Scheduler scripts** — Only available in Document Events
7. **NEVER forget `frappe.db.commit()` in Scheduler** — All changes will be lost

---

## Reference Files

| File | Contents |
|------|----------|
| `references/examples.md` | Real error scenarios with diagnosis |
| `references/anti-patterns.md` | Common sandbox mistakes with fixes |
| `references/patterns.md` | Defensive error handling patterns by script type |
---
name: frappe-impl-clientscripts
description: >
  Use when implementing client-side form features in Frappe/ERPNext:
  field visibility, cascading filters, calculated fields, custom buttons,
  server calls, form validation, child table logic, debugging.
  Covers step-by-step workflows from Setup > Client Script through
  migration to custom app JS. Keywords: how to implement client script,
  form logic workflow, dynamic UI, calculate fields, frm.call, frappe.call,
  frappe.xcall, client script testing, field dependency, custom button,
  how to hide field, show field based on value, add button to form, calculate total, dynamic form.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Client Scripts — Implementation Workflows

Step-by-step workflows for building client-side form features. For exact API syntax, see `frappe-syntax-clientscripts`.

**Version**: v14/v15/v16 | **Note**: v13 renamed "Custom Script" to "Client Script"

## Quick Decision: Client or Server?

```
MUST the logic ALWAYS execute (imports, API, Data Import)?
├── YES → Server Script or Controller
└── NO  → What is the goal?
         ├── UI feedback / UX → Client Script
         ├── Show/hide fields → Client Script
         ├── Link filters → Client Script
         ├── Data validation → BOTH (client for UX, server for integrity)
         └── Calculations → Client for display, server for critical
```

**Rule**: ALWAYS use Client Scripts for UX. ALWAYS back critical logic with server-side validation.

## Workflow 1: Create a Client Script via UI

1. Navigate to **Setup > Client Script** (or type "New Client Script" in awesomebar)
2. Select the target **DocType**
3. ALWAYS set **Enabled** checkbox
4. Write script using the `frappe.ui.form.on` pattern
5. Save — script is active immediately (no restart needed)
6. Open target DocType form → test behavior
7. Open browser DevTools Console (F12) for debugging

**When to migrate to custom app**: ALWAYS migrate when the script exceeds 50 lines, needs version control, or must be deployed across environments.

## Workflow 2: Choose the Right Event

```
WHAT DO YOU WANT?
├── Set link filters         → setup (once, earliest lifecycle)
├── Add custom buttons       → refresh (re-added after each render)
├── Show/hide fields         → refresh + {fieldname} (BOTH needed)
├── Validate before save     → validate (frappe.throw stops save)
├── Action after save        → after_save
├── Calculate on change      → {fieldname} handler
├── Child row added          → {tablename}_add
├── Child row removed        → {tablename}_remove
├── Child field changed      → Child DocType: {fieldname}
├── One-time init            → setup or onload
└── After full DOM render    → onload_post_render
```

> See [references/decision-tree.md](references/decision-tree.md) for complete event timing matrix.

## Workflow 3: Field Visibility Toggle

**Goal**: Show "delivery_date" only when "requires_delivery" is checked.

**Step 1**: Implement BOTH refresh and fieldname events:

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        frm.trigger('requires_delivery'); // Set initial state
    },
    requires_delivery(frm) {
        frm.toggle_display('delivery_date', frm.doc.requires_delivery);
        frm.toggle_reqd('delivery_date', frm.doc.requires_delivery);
    }
});
```

**Why both?** `refresh` sets state on form load. `{fieldname}` responds to user interaction. NEVER use only one — the form will show wrong state on load or on change.

## Workflow 4: Cascading Link Filters

**Goal**: Filter "city" based on selected "country".

```javascript
frappe.ui.form.on('Customer', {
    setup(frm) {
        // ALWAYS set filters in setup — ensures consistency
        frm.set_query('city', () => ({
            filters: { country: frm.doc.country || '' }
        }));
    },
    country(frm) {
        frm.set_value('city', ''); // ALWAYS clear dependent field
    }
});
```

**Rule**: ALWAYS put `set_query` in `setup`. ALWAYS clear child fields when parent changes.

## Workflow 5: Calculated Fields (Child Table)

**Goal**: Calculate row amounts and document totals.

```javascript
frappe.ui.form.on('Invoice Item', {
    qty(frm, cdt, cdn) { calculate_row(frm, cdt, cdn); },
    rate(frm, cdt, cdn) { calculate_row(frm, cdt, cdn); },
    amount(frm) { calculate_totals(frm); }
});

frappe.ui.form.on('Invoice', {
    items_remove(frm) { calculate_totals(frm); }
});

function calculate_row(frm, cdt, cdn) {
    let row = frappe.get_doc(cdt, cdn);
    frappe.model.set_value(cdt, cdn, 'amount',
        flt(row.qty) * flt(row.rate));
}

function calculate_totals(frm) {
    let total = (frm.doc.items || []).reduce(
        (sum, row) => sum + flt(row.amount), 0);
    frm.set_value('grand_total', flt(total, 2));
}
```

**Rules**:
- ALWAYS use `flt()` for numeric operations (handles null/undefined)
- ALWAYS handle `items_remove` — totals must recalculate on row deletion
- NEVER call `refresh_field` after `set_value` — it triggers automatically

## Workflow 6: Server Calls: Which Method to Use

```
NEED TO CALL THE SERVER?
├── Fetch a single value?
│   └── frappe.db.get_value(doctype, name, fields)
│       Returns: Promise — lightweight, no whitelist needed
│
├── Call a document's controller method?
│   └── frm.call(method, args)
│       Requires: @frappe.whitelist() on controller method
│       Auto-includes: doctype, docname, doc context
│
├── Call a standalone whitelisted function?
│   └── frappe.call({method: 'dotted.path', args: {}})
│       Requires: @frappe.whitelist() decorator
│       Returns: Promise with r.message
│
└── Need Promise-only (no callback)?
    └── frappe.xcall('dotted.path', args)
        Same as frappe.call but returns clean Promise
```

**Example — frm.call**:
```javascript
frm.call('calculate_taxes').then(r => {
    frm.reload_doc();  // Refresh after server-side changes
});
```

**Example — frappe.xcall**:
```javascript
let result = await frappe.xcall(
    'myapp.api.check_credit', { customer: frm.doc.customer });
```

## Workflow 7: Custom Button Implementation

```javascript
frappe.ui.form.on('Sales Order', {
    refresh(frm) {
        // ALWAYS check conditions before adding buttons
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Invoice'), () => {
                create_invoice(frm);
            }, __('Create'));  // Group label
        }
    }
});
```

**Rules**:
- ALWAYS add buttons in `refresh` — they are cleared on each render
- ALWAYS check `frm.is_new()` — buttons on unsaved docs cause errors
- ALWAYS wrap button labels in `__()` for translation
- NEVER add buttons in `setup` or `onload` — UI not ready

## Workflow 8: Async Validation with Server Check

```javascript
frappe.ui.form.on('Sales Order', {
    async validate(frm) {
        if (!frm.doc.customer || !frm.doc.grand_total) return;

        let r = await frappe.call({
            method: 'myapp.api.check_credit',
            args: {
                customer: frm.doc.customer,
                amount: frm.doc.grand_total
            }
        });

        if (r.message && !r.message.allowed) {
            frappe.throw(__('Credit limit exceeded. Available: {0}',
                [r.message.available]));
        }
    }
});
```

**Rules**:
- ALWAYS use `async/await` for server calls in `validate`
- ALWAYS use `frappe.throw()` to stop save — `msgprint` does NOT stop it
- NEVER put slow server calls in `validate` without user expectation

## Workflow 9: Debugging in Browser

1. Open **F12 DevTools > Console**
2. Add `console.log(frm.doc)` in your event handler
3. Use `cur_frm` in Console to inspect current form state
4. Check **Network** tab for failed `frappe.call` requests
5. Use `frappe.ui.form.handlers` to see registered event handlers

**Debug pattern**:
```javascript
frappe.ui.form.on('MyDocType', {
    my_field(frm) {
        console.log('Field changed:', frm.doc.my_field);
        // ... actual logic
    }
});
```

## Workflow 10: Migrate Client Script to Custom App

1. Create JS file: `myapp/myapp/public/js/sales_order.js`
2. Move script content to the file (keep `frappe.ui.form.on` wrapper)
3. Register in `hooks.py`:
   ```python
   doctype_js = {
       "Sales Order": "public/js/sales_order.js"
   }
   ```
4. Run `bench build` (or `bench watch` for development)
5. Delete the Client Script document from Setup
6. Test on the form — behavior must be identical

**ALWAYS migrate when**: version control needed, multi-environment deployment, script > 50 lines, team collaboration required.

## Performance Rules

| Rule | Why |
|------|-----|
| `set_query` in `setup` only | Prevents re-registration on every refresh |
| Batch `set_value` calls | `frm.set_value({a: 1, b: 2})` — one update, not two |
| Cache server responses | Store in `frm._cache_key` to avoid repeat calls |
| NEVER query in loops | Fetch all data once, build lookup map |
| Use `frappe.db.get_value` | Lighter than `frappe.call` for simple lookups |

## Related Skills

- `frappe-syntax-clientscripts` — Exact API syntax and method signatures
- `frappe-errors-clientscripts` — Error handling and common pitfalls
- `frappe-syntax-whitelisted` — Server methods callable from client
- `frappe-core-database` — `frappe.db.*` client-side API
- `frappe-impl-serverscripts` — When to move logic server-side

> See [references/decision-tree.md](references/decision-tree.md) for event selection.
> See [references/workflows.md](references/workflows.md) for extended patterns.
> See [references/examples.md](references/examples.md) for 10+ complete examples.
---
name: frappe-impl-controllers
description: >
  Use when building Document Controllers in a custom Frappe app:
  file creation, lifecycle hooks, validation, autoname, submittable
  workflows, controller override, child table controllers, flags system,
  migration from hooks.py and Server Scripts. Keywords: how to implement
  controller, which hook to use, validate vs on_update, override controller,
  submittable document, autoname, flags, extend_doctype_class, controller
  testing, child table controller,
  which hook to use, when does validate run, how to override save, document lifecycle.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Document Controllers — Implementation Workflows

Step-by-step workflows for building server-side DocType logic with full Python power. For exact syntax, see `frappe-syntax-controllers`.

**Version**: v14/v15/v16 | **v15+**: Supports auto-generated type annotations

## Quick Decision: Controller vs Server Script?

```
NEED full Python (imports, classes, generators)?     → Controller
NEED external libraries (requests, pandas)?          → Controller
NEED try/except with rollback?                       → Controller
NEED frappe.enqueue() for background jobs?           → Controller
NEED to extend standard ERPNext DocType?             → Controller
Quick validation without custom app?                 → Server Script
Simple auto-fill or notification?                    → Server Script
```

**Rule**: ALWAYS use Controllers when you need a custom app. ALWAYS use Server Scripts for no-code prototyping.

## Workflow 1: Create a New Controller

**Step 1**: Create DocType via Frappe UI or `bench new-doctype`

**Step 2**: File is auto-generated at:
```
apps/myapp/myapp/{module}/doctype/{doctype_name}/{doctype_name}.py
```

**Step 3**: Implement the controller class:

```python
import frappe
from frappe import _
from frappe.model.document import Document

class MyDocType(Document):
    def validate(self):
        self.validate_dates()
        self.calculate_totals()

    def validate_dates(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            frappe.throw(_("From Date cannot be after To Date"))

    def calculate_totals(self):
        self.total = sum(item.amount for item in self.items)
```

**Step 4**: Run `bench restart` (or `bench watch` for hot-reload in dev)

**Naming convention**: DocType "Sales Order" → class `SalesOrder`, file `sales_order.py`

## Workflow 2: Choose the Right Hook

```
WHAT DO YOU WANT?
├── Validate data / calculate fields before save?
│   └── validate — changes to self ARE saved
│
├── Action AFTER save (emails, linked docs, logs)?
│   └── on_update — changes to self NOT saved (use db_set)
│
├── Only for NEW documents?
│   └── after_insert
│
├── Before/after SUBMIT?
│   ├── Check before submit → before_submit
│   └── Ledger entries after → on_submit
│
├── Before/after CANCEL?
│   ├── Prevent cancel → before_cancel
│   └── Reverse entries → on_cancel
│
├── Before DELETE?
│   └── on_trash (throw to prevent)
│
├── Custom document naming?
│   └── autoname
│
└── Detect ANY change (including db_set)?
    └── on_change
```

> See [references/decision-tree.md](references/decision-tree.md) for all hooks with execution order.

## CRITICAL: validate vs on_update

| Aspect | `validate` | `on_update` |
|--------|-----------|-------------|
| When | Before DB write | After DB write |
| `self.x = y` saved? | YES | **NO** — use `db_set` |
| Can abort with throw? | YES | Already saved |
| `get_doc_before_save()` | Available | Available |
| Use for | Validation, calculations | Notifications, linked docs |

```python
# WRONG — changes in on_update are NOT saved
def on_update(self):
    self.status = "Completed"  # LOST!

# CORRECT — use db_set
def on_update(self):
    frappe.db.set_value(self.doctype, self.name, "status", "Completed")
```

## Workflow 3: Validation with Error Collection

```python
def validate(self):
    errors = []
    if not self.items:
        errors.append(_("At least one item is required"))
    for item in self.items:
        if item.qty <= 0:
            errors.append(_("Row {0}: Qty must be positive").format(item.idx))
    if self.from_date > self.to_date:
        errors.append(_("From Date cannot be after To Date"))
    if errors:
        frappe.throw("<br>".join(errors))
```

## Workflow 4: Detect Field Changes

```python
def validate(self):
    old = self.get_doc_before_save()
    if old and old.status != self.status:
        self.flags.status_changed = True
        self.status_changed_on = frappe.utils.now()

def on_update(self):
    if self.flags.get('status_changed'):
        self.notify_status_change()
```

**Rule**: ALWAYS use `self.flags` to pass data between hooks. NEVER rely on external state.

## Workflow 5: Custom Naming (autoname)

```python
from frappe.model.naming import getseries

def autoname(self):
    # Format: PRJ-CUST-2025-001
    code = (self.customer or "GEN")[:4].upper()
    year = frappe.utils.getdate(self.start_date or frappe.utils.today()).year
    prefix = f"PRJ-{code}-{year}-"
    self.name = getseries(prefix, 3)
```

**Alternative — before_naming**:
```python
def before_naming(self):
    if self.is_priority:
        self.naming_series = "PRIORITY-.#####"
    else:
        self.naming_series = "STD-.#####"
```

## Workflow 6: Submittable Document

```
DRAFT (docstatus=0) → submit() → SUBMITTED (docstatus=1) → cancel() → CANCELLED (docstatus=2)

submit():  validate → before_submit → [DB: docstatus=1] → on_update → on_submit
cancel():  before_cancel → [DB: docstatus=2] → on_cancel
```

```python
class PurchaseOrder(Document):
    def validate(self):
        self.validate_items()
        self.calculate_totals()

    def before_submit(self):
        # ONLY submit-specific checks here
        if self.total > 100000 and not self.manager_approval:
            frappe.throw(_("Manager approval required for POs over 100,000"))

    def on_submit(self):
        self.update_ordered_qty()
        self.create_purchase_receipt_draft()

    def before_cancel(self):
        if frappe.db.exists("Purchase Invoice",
                {"purchase_order": self.name, "docstatus": 1}):
            frappe.throw(_("Cancel linked invoices first"))

    def on_cancel(self):
        self.reverse_ordered_qty()
```

**Rule**: NEVER duplicate validation between `validate` and `before_submit`. `validate` ALWAYS runs before `before_submit`.

## Workflow 7: Override Standard ERPNext Controller

### Method A: Full Override (hooks.py)

```python
# hooks.py
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.CustomSalesInvoice"
}

# myapp/overrides.py
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice

class CustomSalesInvoice(SalesInvoice):
    def validate(self):
        super().validate()  # ALWAYS call parent first
        self.custom_validation()
```

### Method B: Event Handler (Safer, no class override)

```python
# hooks.py
doc_events = {
    "Sales Invoice": {
        "validate": "myapp.events.validate_sales_invoice",
    }
}

# myapp/events.py
def validate_sales_invoice(doc, method=None):
    if doc.grand_total < 0:
        frappe.throw(_("Invalid total"))
```

### Method C: extend_doctype_class (v16+)

```python
# hooks.py
extend_doctype_class = {
    "Sales Invoice": "myapp.extends.SalesInvoiceExtend"
}

# myapp/extends.py — Only methods to add/override
class SalesInvoiceExtend:
    def custom_method(self):
        pass
```

**Rule**: ALWAYS call `super().validate()` in override. NEVER skip parent methods — standard ERPNext logic depends on it.

## Workflow 8: Whitelisted Methods (Client-Callable)

```python
class Quotation(Document):
    @frappe.whitelist()
    def apply_discount(self, discount_percent):
        if discount_percent < 0 or discount_percent > 100:
            frappe.throw(_("Discount must be 0-100"))
        self.discount_amount = self.total * (discount_percent / 100)
        self.grand_total = self.total - self.discount_amount
        self.save()
        return {"grand_total": self.grand_total}
```

Client-side call:
```javascript
frm.call('apply_discount', { discount_percent: 10 }).then(r => {
    frm.reload_doc();
});
```

## Workflow 9: Flags System

```python
# Document-level flags (built-in)
doc.flags.ignore_permissions = True    # Bypass permission checks
doc.flags.ignore_validate = True       # Skip validate() hook
doc.flags.ignore_mandatory = True      # Skip required field check

# Custom flags for inter-hook communication
def validate(self):
    if self.is_urgent:
        self.flags.needs_notification = True

def on_update(self):
    if self.flags.get('needs_notification'):
        self.notify_team()
```

## Workflow 10: Testing Controllers

```python
# tests/test_my_doctype.py
import frappe
from frappe.tests.utils import FrappeTestCase

class TestMyDocType(FrappeTestCase):
    def test_validate_dates(self):
        doc = frappe.get_doc({
            "doctype": "My DocType",
            "from_date": "2025-01-10",
            "to_date": "2025-01-01"  # Before from_date
        })
        self.assertRaises(frappe.ValidationError, doc.insert)

    def test_calculate_totals(self):
        doc = frappe.get_doc({
            "doctype": "My DocType",
            "items": [
                {"item": "A", "qty": 2, "rate": 100},
                {"item": "B", "qty": 3, "rate": 50}
            ]
        })
        doc.insert()
        self.assertEqual(doc.total, 350)
```

Run: `bench run-tests --module myapp.module.doctype.my_doctype.test_my_doctype`

## Execution Order Reference

### INSERT
```
before_insert → before_naming → autoname → before_validate →
validate → before_save → [DB INSERT] → after_insert →
on_update → on_change
```

### SAVE (existing)
```
before_validate → validate → before_save → [DB UPDATE] →
on_update → on_change
```

### SUBMIT
```
validate → before_submit → [DB: docstatus=1] →
on_update → on_submit → on_change
```

## Anti-Pattern Quick Check

| Do NOT | Do Instead |
|--------|------------|
| `self.x = y` in on_update | `frappe.db.set_value(...)` |
| `self.save()` in on_update | Causes infinite loop |
| `frappe.db.commit()` in hooks | Let framework handle |
| Heavy ops in validate | Use `frappe.enqueue()` in on_update |
| Skip `super().validate()` | ALWAYS call parent first |
| `frappe.get_doc()` in loops | Use `frappe.get_cached_doc()` |
| Hardcoded thresholds | Use Settings DocType |

> See [references/anti-patterns.md](references/anti-patterns.md) for complete list.

## Related Skills

- `frappe-syntax-controllers` — Exact hook signatures and API
- `frappe-errors-controllers` — Error handling patterns
- `frappe-impl-serverscripts` — When Server Script suffices
- `frappe-syntax-hooks` — hooks.py configuration
- `frappe-core-database` — `frappe.db.*` operations

> See [references/decision-tree.md](references/decision-tree.md) for all hooks.
> See [references/workflows.md](references/workflows.md) for extended patterns.
> See [references/examples.md](references/examples.md) for complete working examples.
---
name: frappe-impl-customapp
description: >
  Use when building a custom Frappe app from scratch. Covers bench new-app
  walkthrough, app structure decisions, adding DocTypes, hooks, patches,
  fixtures management, development workflow (bench migrate, build,
  clear-cache), testing, packaging, installing on another site, version
  management, and app dependencies for v14/v15/v16. Keywords: create custom
  app, new frappe app, bench new-app, app structure, module creation,
  doctype creation, fixtures, patches, deployment, packaging,
  data migration, patch file, patches.txt, migrate data between DocTypes, create new app from scratch.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Custom App - Implementation

Workflow for building a custom Frappe app from scratch. For exact syntax, see `frappe-syntax-customapp`.

**Version**: v14/v15/v16 compatible

---

## Main Decision: Do You Need a Custom App?

```
WHAT CHANGES DO YOU NEED?
|
+-- Add fields to existing DocType?
|   +-- NO APP NEEDED: Custom Field + Property Setter
|
+-- Simple automation/validation (<50 lines)?
|   +-- NO APP NEEDED: Server Script or Client Script
|
+-- Complex business logic, new DocTypes, or Python code?
|   +-- YES: Create custom app
|
+-- Integration with external system (needs imports)?
|   +-- YES: Custom app REQUIRED (Server Scripts block imports)
|
+-- Custom reports with complex queries?
|   +-- Script Report (no app) vs Query Report (app optional)
```

**Rule**: ALWAYS start with the simplest solution. Server Scripts + Custom Fields solve 70% of needs without a custom app.

---

## Step 1: Create App Structure

```bash
cd ~/frappe-bench
bench new-app my_app
# Prompts: Title, Description, Publisher, Email, License
```

ALWAYS verify immediately:
```python
# my_app/my_app/__init__.py MUST have:
__version__ = "0.0.1"
```

---

## Step 2: Configure pyproject.toml (v15+)

```toml
[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "my_app"
authors = [{ name = "Your Company", email = "dev@example.com" }]
description = "Your app description"
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]
dependencies = [
    "requests>=2.28.0"   # Only PyPI packages here
]

[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
# erpnext = ">=15.0.0,<16.0.0"  # Only if needed
```

**Rule**: NEVER put frappe or erpnext in `[project].dependencies` -- they are NOT on PyPI.

---

## Step 3: Configure hooks.py

```python
app_name = "my_app"
app_title = "My App"
app_publisher = "Your Company"
app_description = "Description"
app_email = "dev@example.com"
app_license = "MIT"

required_apps = ["frappe"]  # Or ["frappe", "erpnext"]

fixtures = []  # Configured later
```

**Rule**: ALWAYS declare `required_apps` with all dependencies.

---

## Step 4: Define Modules

```text
# my_app/my_app/modules.txt
My App
```

| App Size | Module Strategy |
|----------|----------------|
| 1-5 DocTypes | ONE module with app name |
| 6-15 DocTypes | 2-4 modules by functional area |
| 15+ DocTypes | Modules by business domain |

**Rule**: Each DocType belongs to EXACTLY one module. Module name in `modules.txt` maps to directory: `My Custom App` --> `my_custom_app/`.

### Adding a Module
```bash
mkdir -p my_app/my_app/new_module/doctype
touch my_app/my_app/new_module/__init__.py
# Add "New Module" to modules.txt
bench --site mysite migrate
```

---

## Step 5: Install and Create DocTypes

```bash
# Install app on site
bench --site mysite install-app my_app

# Create DocType (via UI recommended, or CLI)
bench --site mysite new-doctype "My Document" --module "My App"
```

This creates:
```
my_app/my_app/doctype/my_document/
+-- my_document.json    # DocType definition
+-- my_document.py      # Controller
+-- my_document.js      # Client script
+-- test_my_document.py # Tests
```

---

## Step 6: Add Hooks

### doc_events (v14/v15/v16)
```python
doc_events = {
    "Sales Invoice": {
        "validate": "my_app.events.sales_invoice.validate",
        "on_submit": "my_app.events.sales_invoice.on_submit"
    }
}
```

### extend_doctype_class (v16 ONLY -- preferred)
```python
extend_doctype_class = {
    "Sales Invoice": "my_app.overrides.sales_invoice.CustomSalesInvoice"
}
```

**Rule**: ALWAYS call `super().method()` when overriding lifecycle methods in v16.

### Scheduler Events
```python
scheduler_events = {
    "daily": ["my_app.tasks.daily_cleanup"],
    "cron": {"0 9 * * 1-5": ["my_app.tasks.morning_report"]}
}
```

See `frappe-impl-hooks` and `frappe-impl-scheduler` for complete patterns.

---

## Step 7: Add Patches

### Create Patch File
```bash
mkdir -p my_app/my_app/patches/v1_0
touch my_app/my_app/patches/__init__.py
touch my_app/my_app/patches/v1_0/__init__.py
```

```python
# my_app/my_app/patches/v1_0/populate_defaults.py
import frappe

def execute():
    if not frappe.db.has_column("My DocType", "target_field"):
        return  # Skip if not applicable

    batch_size = 1000
    offset = 0
    while True:
        records = frappe.get_all("My DocType",
            limit_page_length=batch_size, limit_start=offset)
        if not records:
            break
        for r in records:
            frappe.db.set_value("My DocType", r.name,
                "target_field", "default", update_modified=False)
        frappe.db.commit()
        offset += batch_size
```

### Register in patches.txt
```ini
[pre_model_sync]
# Patches that run BEFORE schema changes (backup data from deleted fields)

[post_model_sync]
# Patches that run AFTER schema changes (populate new fields)
my_app.patches.v1_0.populate_defaults
```

**Rules**:
- ALWAYS check if patch is needed (guard clause)
- ALWAYS batch process 1000+ records
- ALWAYS commit after each batch
- NEVER run untested patches on production

---

## Step 8: Fixtures Management

### Configure in hooks.py
```python
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "My App"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "My App"]]},
    {"dt": "Role", "filters": [["name", "in", ["My App User", "My App Manager"]]]},
    {"dt": "Workflow", "filters": [["document_type", "=", "My DocType"]]},
    "My Category",  # All records of your own config DocType
]
```

### Export and Verify
```bash
bench --site mysite export-fixtures --app my_app
ls my_app/my_app/fixtures/
# custom_field.json, property_setter.json, etc.
```

**Rules**:
- ALWAYS filter fixtures to YOUR app's customizations
- NEVER include transactional data (invoices, orders)
- NEVER export without filters for shared DocTypes (Custom Field, Workflow)
- Fixtures auto-import during `bench migrate`

---

## Step 9: Development Workflow

### Essential Commands
```bash
# After schema changes (DocType fields, hooks.py, patches)
bench --site mysite migrate

# After JS/CSS changes
bench build --app my_app

# After Python changes (controllers, events)
bench --site mysite clear-cache

# Full restart (production)
bench restart

# Watch mode (development)
bench watch  # Auto-rebuilds on file changes
```

### Development Cycle
```
1. Edit code/DocType
2. bench --site mysite migrate (if schema changed)
3. bench build --app my_app (if JS/CSS changed)
4. bench --site mysite clear-cache (if Python changed)
5. Test in browser
6. Repeat
```

---

## Step 10: Testing the App

```bash
# Run all tests
bench --site mysite run-tests --app my_app

# Run specific test
bench --site mysite run-tests --module my_app.my_module.doctype.my_doctype.test_my_doctype

# Run with verbose output
bench --site mysite run-tests --app my_app -v
```

See `frappe-testing-unit` for writing test cases.

---

## Step 11: Packaging for Distribution

### Via Git (standard method)
```bash
cd apps/my_app
git init && git add . && git commit -m "Initial commit"
git remote add origin https://github.com/org/my_app.git
git push -u origin main
```

### Install on Another Site
```bash
# On target bench
bench get-app https://github.com/org/my_app.git
bench --site target-site install-app my_app
bench --site target-site migrate
```

### Version Management
```python
# my_app/my_app/__init__.py
__version__ = "1.0.0"  # Semantic versioning: MAJOR.MINOR.PATCH
```

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Breaking changes | MAJOR | 1.x -> 2.0.0 |
| New features | MINOR | 1.1.x -> 1.2.0 |
| Bug fixes | PATCH | 1.2.0 -> 1.2.1 |

---

## Step 12: App Dependencies

### Frappe/ERPNext Dependencies
```python
# hooks.py
required_apps = ["frappe", "erpnext"]  # Install order matters
```

```toml
# pyproject.toml
[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"
```

### Python Package Dependencies
```toml
[project]
dependencies = ["requests>=2.28.0", "pandas>=1.5.0"]
```

**Rule**: NEVER create circular dependencies between apps.

---

## Version-Specific Considerations

| Aspect | v14 | v15 | v16 |
|--------|-----|-----|-----|
| Build config | setup.py | pyproject.toml | pyproject.toml |
| DocType extension | doc_events | doc_events | `extend_doctype_class` preferred |
| Python minimum | 3.10 | 3.10 | 3.11 |
| Patch format | INI sections | INI sections | INI sections |

### v16 Breaking Changes to Know
- `extend_doctype_class` hook: Cleaner extension via mixins
- Data masking: Field-level privacy configuration
- UUID naming: New naming rule option
- Chrome PDF: wkhtmltopdf deprecated

---

## Critical Rules Summary

### ALWAYS
1. Start with `bench new-app` - NEVER create structure manually
2. Define `__version__` in `__init__.py`
3. Use `dynamic = ["version"]` in pyproject.toml
4. Test patches on database copy before production
5. Filter fixtures to your app's customizations only
6. Version your patches (v1_0, v2_0 directories)
7. Test installation on a fresh site

### NEVER
1. Put frappe/erpnext in `[project].dependencies`
2. Include transactional data in fixtures
3. Hardcode site-specific values (use settings DocTypes)
4. Skip `frappe.db.commit()` in large patches
5. Delete fields without backup patch
6. Modify core ERPNext files directly

---

## Reference Files

| File | Contents |
|------|----------|
| [workflows.md](references/workflows.md) | 8 step-by-step implementation guides |
| [decision-tree.md](references/decision-tree.md) | Complete decision flowcharts |
| [examples.md](references/examples.md) | 5 complete working app examples |
| [anti-patterns.md](references/anti-patterns.md) | Common mistakes to avoid |

## See Also

- `frappe-syntax-customapp` - Exact syntax reference
- `frappe-syntax-hooks` - Hooks configuration syntax
- `frappe-impl-hooks` - Hook implementation patterns
- `frappe-core-database` - Database operations for patches
- `frappe-impl-scheduler` - Scheduled task implementation
- `frappe-ops-bench` - Bench commands reference
- `frappe-ops-app-lifecycle` - App versioning and release management
- `frappe-testing-unit` - Writing tests for your app
- `frappe-testing-cicd` - CI/CD pipeline for app testing
---
name: frappe-impl-hooks
description: >
  Use when implementing hooks.py configurations in a Frappe custom app.
  Covers step-by-step workflows for doc_events, scheduler_events,
  override/extend_doctype_class, permission hooks, extend_bootinfo,
  fixtures, asset injection, website hooks, and doctype_js.
  Prevents broken transactions, missed migrations, and multi-app conflicts.
  Keywords: hooks.py, doc_events, scheduler_events, override doctype,, how to add hook, when to use doc_events, scheduler setup, override existing behavior.
  extend doctype class, permission hook, scheduler job, fixtures,
  doctype_js, extend_bootinfo, website hooks.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Hooks Implementation Workflow

Step-by-step workflows for implementing hooks.py configurations. For API syntax reference, see `frappe-syntax-hooks`.

**Version**: v14/v15/v16 (V16-specific features noted)

---

## Master Decision: What Are You Implementing?

```
WHAT DO YOU WANT TO ACHIEVE?
│
├─► React to document lifecycle events?
│   ├─► On OTHER app's DocTypes → doc_events in hooks.py
│   ├─► On YOUR OWN DocTypes → controller methods (preferred)
│   └─► On ALL DocTypes → doc_events with "*" wildcard
│
├─► Run code on a schedule?
│   └─► scheduler_events (daily, hourly, cron, etc.)
│
├─► Modify an existing DocType's behavior?
│   ├─► V16+: extend_doctype_class (RECOMMENDED)
│   └─► V14/V15: override_doctype_class (last app wins!)
│
├─► Override an existing API endpoint?
│   └─► override_whitelisted_methods
│
├─► Add custom permission logic?
│   ├─► List filtering → permission_query_conditions
│   └─► Document-level → has_permission
│
├─► Send config data to client on page load?
│   └─► extend_bootinfo
│
├─► Export/import configuration?
│   └─► fixtures
│
├─► Add JS/CSS to desk or portal?
│   ├─► Desk-wide → app_include_js / app_include_css
│   ├─► Portal-wide → web_include_js / web_include_css
│   └─► Specific form → doctype_js
│
├─► Customize website/portal behavior?
│   └─► website_context, portal_menu_items, website_route_rules
│
└─► Hook into session/auth lifecycle?
    └─► on_login, on_session_creation, on_logout
```

---

## Workflow 1: Implementing doc_events

### When to Use

Use doc_events when you need to react to document lifecycle events on DocTypes owned by OTHER apps (ERPNext, Frappe core). For YOUR OWN DocTypes, ALWAYS prefer controller methods.

### Step-by-Step

**Step 1: Choose the right event** (see `references/decision-tree.md`)

```
BEFORE save: validate (every save), before_insert (new only)
AFTER save:  after_insert (new only), on_update (every save), on_change (any change)
SUBMIT flow: before_submit → on_submit → on_change
CANCEL flow: before_cancel → on_cancel → on_change
DELETE:      on_trash (before), after_delete (after)
RENAME:      before_rename, after_rename
```

**Step 2: Add to hooks.py**

```python
# myapp/hooks.py
doc_events = {
    "Sales Invoice": {
        "validate": "myapp.events.sales_invoice.validate",
        "on_submit": "myapp.events.sales_invoice.on_submit"
    }
}
```

**Step 3: Create handler module**

```python
# myapp/events/sales_invoice.py
import frappe

def validate(doc, method=None):
    """Changes to doc ARE saved (before-save event)."""
    if doc.grand_total < 0:
        frappe.throw("Total cannot be negative")

def on_submit(doc, method=None):
    """Document already saved. Use db_set_value for changes."""
    frappe.db.set_value("Sales Invoice", doc.name,
                        "custom_external_id", create_external(doc))
```

**Step 4: Deploy**

```bash
bench --site sitename migrate
```

**Step 5: Test**

```bash
bench --site sitename execute myapp.events.sales_invoice.validate --kwargs '{"doc_name": "INV-001"}'
# Or in bench console:
# doc = frappe.get_doc("Sales Invoice", "INV-001"); doc.save()
```

### Critical Rules for doc_events

- **NEVER** call `frappe.db.commit()` inside a doc_event handler — Frappe manages the transaction
- **NEVER** modify `doc` fields in `on_update` — changes are lost; use `frappe.db.set_value()` instead
- **ALWAYS** accept `method=None` as second parameter in handler signature
- **ALWAYS** use rename signature: `def handler(doc, method, old, new, merge)`
- **ALWAYS** run `bench --site sitename migrate` after changing hooks.py

---

## Workflow 2: Implementing scheduler_events

### Step-by-Step

**Step 1: Choose frequency**

| Frequency | Short (< 5 min) | Long (5-25 min) |
|-----------|-----------------|------------------|
| Every tick | `all` | — |
| Hourly | `hourly` | `hourly_long` |
| Daily | `daily` | `daily_long` |
| Weekly | `weekly` | `weekly_long` |
| Monthly | `monthly` | `monthly_long` |
| Custom | `cron` | `cron` (use long queue manually) |

**Step 2: Add to hooks.py**

```python
scheduler_events = {
    "daily": ["myapp.tasks.daily_cleanup"],
    "daily_long": ["myapp.tasks.heavy_sync"],
    "cron": {
        "0 9 * * 1-5": ["myapp.tasks.weekday_report"]
    }
}
```

**Step 3: Implement task (NO arguments)**

```python
# myapp/tasks.py
import frappe

def daily_cleanup():
    """Scheduler calls with NO arguments."""
    frappe.db.delete("Error Log", {
        "creation": ["<", frappe.utils.add_days(None, -30)]
    })
    frappe.db.commit()

def heavy_sync():
    """Long task — commit periodically."""
    records = get_records_to_sync()
    for i, record in enumerate(records):
        process(record)
        if i % 100 == 0:
            frappe.db.commit()
    frappe.db.commit()
```

**Step 4: Deploy and verify**

```bash
bench --site sitename migrate
bench --site sitename scheduler enable
bench --site sitename scheduler status
# Test manually:
bench --site sitename execute myapp.tasks.daily_cleanup
```

### Critical Rules for Scheduler

- **NEVER** add parameters to scheduler task functions — the scheduler passes none
- **ALWAYS** use `_long` variants for tasks exceeding 5 minutes (default queue timeout is 5 min)
- **ALWAYS** commit periodically in long tasks to save progress
- Tasks > 25 minutes: split into chunks or use `frappe.enqueue()`

---

## Workflow 3: Implementing extend_doctype_class (V16+)

### Step-by-Step

**Step 1: Add to hooks.py**

```python
extend_doctype_class = {
    "Sales Invoice": ["myapp.extensions.sales_invoice.SalesInvoiceMixin"]
}
```

**Step 2: Create mixin class**

```python
# myapp/extensions/sales_invoice.py
import frappe
from frappe.model.document import Document

class SalesInvoiceMixin(Document):
    def validate(self):
        super().validate()  # ALWAYS call super() FIRST
        self.custom_validation()

    def custom_validation(self):
        if self.grand_total > 1000000:
            frappe.msgprint("High-value invoice", indicator="orange")
```

**Step 3: Deploy** — `bench --site sitename migrate`

### When to Use extend vs override

- **ALWAYS** prefer `extend_doctype_class` on V16+ — multiple apps can extend safely
- **ONLY** use `override_doctype_class` when you must completely replace controller logic
- On V14/V15, `override_doctype_class` is the only option — last installed app wins

---

## Workflow 4: Implementing Permission Hooks

### Step-by-Step

**Step 1: Add to hooks.py**

```python
permission_query_conditions = {
    "Sales Invoice": "myapp.permissions.si_query"
}
has_permission = {
    "Sales Invoice": "myapp.permissions.si_permission"
}
```

**Step 2: Implement handlers**

```python
# myapp/permissions.py
import frappe

def si_query(user):
    """Returns SQL WHERE clause for list filtering."""
    if not user:
        user = frappe.session.user
    if "Sales Manager" in frappe.get_roles(user):
        return ""  # See all
    return f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"

def si_permission(doc, user=None, permission_type=None):
    """Returns True (allow), False (deny), or None (use default)."""
    if not user:
        user = frappe.session.user
    if permission_type == "write" and doc.status == "Closed":
        return False
    return None
```

### Critical Rules for Permission Hooks

- `permission_query_conditions` **ONLY** works with `get_list`, **NEVER** with `get_all`
- `has_permission` can **ONLY** deny access — returning True does NOT grant additional permissions
- **ALWAYS** handle `user=None` by defaulting to `frappe.session.user`

---

## Workflow 5: Asset Injection and doctype_js

### Adding Global JS/CSS

```python
# hooks.py
app_include_js = "/assets/myapp/js/myapp.min.js"       # Desk
app_include_css = "/assets/myapp/css/myapp.min.css"     # Desk
web_include_js = "/assets/myapp/js/portal.min.js"       # Portal
web_include_css = "/assets/myapp/css/portal.min.css"    # Portal
```

### Extending a Specific Form

```python
# hooks.py
doctype_js = {
    "Sales Invoice": "public/js/sales_invoice.js"
}
```

```javascript
// myapp/public/js/sales_invoice.js
frappe.ui.form.on("Sales Invoice", {
    refresh(frm) {
        if (frm.doc.docstatus === 1) {
            frm.add_custom_button(__("Custom Action"), () => {
                frappe.call({
                    method: "myapp.api.custom_action",
                    args: { invoice: frm.doc.name },
                    freeze: true
                });
            }, __("Actions"));
        }
    }
});
```

**ALWAYS** run `bench build --app myapp` after changing JS/CSS files.

---

## Workflow 6: Fixtures, Boot Info, and Website Hooks

### Fixtures

```python
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "My App"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "My App"]]}
]
```

**NEVER** export fixtures without filters — it captures ALL apps' customizations.

### extend_bootinfo

```python
extend_bootinfo = "myapp.boot.extend_with_config"
```

```python
def extend_with_config(bootinfo):
    bootinfo.my_app = {"feature_enabled": True}
    # NEVER send secrets — bootinfo is visible in browser DevTools
```

### Website Hooks

```python
website_route_rules = [
    {"from_route": "/shop/<category>", "to_route": "shop"}
]
portal_menu_items = [
    {"title": "My Orders", "route": "/my-orders", "role": "Customer"}
]
on_login = "myapp.handlers.on_login"
on_logout = "myapp.handlers.on_logout"
```

---

## Migration: Moving Logic Between Hooks, Controllers, and Server Scripts

| From | To | Steps |
|------|----|-------|
| Server Script → hooks.py | 1. Create Python handler, 2. Add doc_events, 3. Disable Server Script, 4. Migrate |
| hooks.py → Controller | 1. Move logic to doctype .py, 2. Remove doc_events entry, 3. Migrate |
| Controller → hooks.py | 1. Create events module, 2. Add doc_events, 3. Remove from controller, 4. Migrate |

**ALWAYS** migrate after ANY hooks.py change: `bench --site sitename migrate`

---

## Handler Signatures Quick Reference

| Hook | Signature |
|------|-----------|
| doc_events | `def handler(doc, method=None):` |
| rename events | `def handler(doc, method, old, new, merge):` |
| scheduler_events | `def handler():` (no args) |
| extend_bootinfo | `def handler(bootinfo):` |
| permission_query | `def handler(user):` returns SQL string |
| has_permission | `def handler(doc, user=None, permission_type=None):` returns True/False/None |
| on_login | `def handler(login_manager):` |
| on_logout | `def handler():` |

---

## Version Differences

| Feature | V14 | V15 | V16 |
|---------|:---:|:---:|:---:|
| doc_events | Yes | Yes | Yes |
| scheduler_events | Yes | Yes | Yes |
| override_doctype_class | Yes | Yes | Yes |
| **extend_doctype_class** | No | No | **Yes** |
| permission hooks | Yes | Yes | Yes |
| Scheduler tick interval | ~4 min | ~4 min | ~60 sec |
| auth_hooks | No | Yes | Yes |

---

## Reference Files

| File | Contents |
|------|----------|
| [decision-tree.md](references/decision-tree.md) | Complete hook selection flowcharts |
| [workflows.md](references/workflows.md) | Step-by-step implementation patterns |
| [examples.md](references/examples.md) | Working code examples for all hook types |
---
name: frappe-impl-integrations
description: >
  Use when implementing OAuth providers, Connected Apps, Webhooks, Payment Gateways, or Data Import/Export in Frappe.
  Prevents authentication failures from wrong OAuth flow, missed webhook deliveries, and data corruption during bulk imports.
  Covers OAuth2 provider/client, Connected App DocType, Webhook DocType, Payment Gateway integration, Data Import, Data Export, frappe.integrations module.
  Keywords: OAuth, Connected App, Webhook, Payment Gateway, Data Import, Data Export, integration, API key, OAuth2, webhook trigger, connect to external service, OAuth setup, webhook configuration, import data, export data..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Integrations

Step-by-step workflows for OAuth, Webhooks, Payment Gateways, Data Import/Export, and external API calls.

**Version**: v14/v15/v16

---

## Decision Tree: Which Integration Pattern?

```
WHAT ARE YOU INTEGRATING?
│
├─► External service needs to call YOUR Frappe site?
│   ├─► On document events → Webhook (push to external)
│   ├─► External sends data to you → Whitelisted API endpoint
│   └─► External needs user auth → OAuth 2.0 Provider
│
├─► YOUR Frappe site calls an external service?
│   ├─► Needs user-level OAuth consent → Connected App
│   ├─► Server-to-server with API key → make_request / requests
│   └─► Recurring sync → Scheduler + API calls
│
├─► Bulk data in/out?
│   ├─► Import CSV/XLSX → Data Import DocType
│   ├─► Export data → Report Builder / export-csv / API
│   └─► Programmatic bulk → frappe.get_doc().insert()
│
├─► Payment processing?
│   └─► Payment Request + Payment Gateway controller
│
└─► Real-time vs batch?
    ├─► Real-time → Webhook or API endpoint
    ├─► Near real-time → frappe.enqueue() after event
    └─► Batch → Scheduler task (hourly/daily)
```

---

## Workflow 1: OAuth 2.0: Frappe as Provider

Use when external applications need "Sign in with Frappe" or API access on behalf of users.

### Step 1: Configure OAuth Provider Settings

Navigate to **Setup > Integrations > OAuth Provider Settings**:
- **Force**: ALWAYS asks user for confirmation
- **Auto**: Asks only if no active token exists

### Step 2: Create OAuth Client

Navigate to **Setup > Integrations > OAuth Client**:

| Field | Value |
|-------|-------|
| App Name | External app identifier |
| Scopes | Space-separated (e.g., `openid all`) |
| Redirect URIs | Space-separated callback URLs |
| Default Redirect URI | Primary callback URL |
| Grant Type | `Authorization Code` (RECOMMENDED) or `Implicit` |
| Response Type | `Code` (for Auth Code) or `Token` (for Implicit) |
| Skip Authorization | Check for trusted first-party apps only |

### Step 3: Use the Generated Endpoints

| Endpoint | URL |
|----------|-----|
| Authorize | `/api/method/frappe.integrations.oauth2.authorize` |
| Token | `/api/method/frappe.integrations.oauth2.get_token` |
| Profile | `/api/method/frappe.integrations.oauth2.openid_profile` |

### Step 4: Configure External App

```ini
# Example: Grafana generic_oauth config
client_id = <generated_client_id>
client_secret = <generated_client_secret>
auth_url = https://your-frappe.com/api/method/frappe.integrations.oauth2.authorize
token_url = https://your-frappe.com/api/method/frappe.integrations.oauth2.get_token
api_url = https://your-frappe.com/api/method/frappe.integrations.oauth2.openid_profile
scopes = openid all
```

### Critical Rules

- **NEVER** use `Implicit` grant type for server-side apps — use `Authorization Code`
- **ALWAYS** use HTTPS in production for all OAuth endpoints
- **NEVER** expose `client_secret` in client-side JavaScript

---

## Workflow 2: Connected App: Frappe as OAuth Consumer

Use when your Frappe instance needs to access external services (Google, Microsoft, etc.) on behalf of users.

### Step 1: Create Connected App DocType

| Field | Purpose |
|-------|---------|
| Name | Identifier for the connection |
| OpenID Configuration URL | Auto-fetches endpoints (e.g., `/.well-known/openid-configuration`) |
| Authorization URI | Consent screen URL (auto-filled from OpenID) |
| Token URI | Token exchange URL (auto-filled from OpenID) |
| Redirect URI | Auto-generated — copy this to external provider |
| Client ID | From external provider |
| Client Secret | From external provider |
| Scopes | Permissions needed (e.g., `https://mail.google.com/`) |

### Step 2: Register Redirect URI with Provider

Copy the auto-generated Redirect URI and register it in the external provider's OAuth console.

### Step 3: Add Extra Parameters (if needed)

```
access_type=offline    # Google: enables refresh tokens
prompt=consent         # Google: forces re-consent for refresh token
```

### Step 4: Use in Code

```python
import frappe

connected_app = frappe.get_doc("Connected App", "My Google App")
# Initiates OAuth flow — user clicks "Connect to..." button
# After consent, tokens are stored automatically

# Making authenticated calls:
session = connected_app.get_oauth2_session()
response = session.get("https://www.googleapis.com/gmail/v1/users/me/messages")
```

### Critical Rules

- **ALWAYS** add `access_type=offline` for Google APIs to get refresh tokens
- **NEVER** store tokens manually — Connected App manages token lifecycle
- **ALWAYS** handle `TokenExpiredError` — call `session.refresh_token()` or reconnect

---

## Workflow 3: Webhooks: Push Notifications to External Services

### Step 1: Create Webhook DocType

Navigate to **Integrations > Webhook**:

| Field | Value |
|-------|-------|
| DocType | Target document type |
| Doc Event | `on_update`, `after_insert`, `on_submit`, `on_cancel`, `on_trash` |
| Request URL | External endpoint |
| Request Method | POST (default) |
| Conditions | Optional Jinja filter (e.g., `doc.status == "Approved"`) |
| Enabled | Check to activate |

### Step 2: Configure Headers

Add custom headers for authentication:
```
Authorization: Bearer <api_token>
Content-Type: application/json
```

### Step 3: Configure Data: Choose Format

**Form URL-encoded**: Select specific fields from a table.

**JSON**: Use Jinja templates for structured payloads:
```json
{
  "id": "{{ doc.name }}",
  "total": "{{ doc.grand_total }}",
  "items": {{ doc.items | tojson }},
  "event": "{{ event }}"
}
```

### Step 4: Enable Webhook Secret (HMAC Verification)

Set a **Webhook Secret** — Frappe adds `X-Frappe-Webhook-Signature` header with base64-encoded HMAC-SHA256 hash of the payload.

**Receiver verification (Python example):**

```python
import hmac, hashlib, base64

def verify_webhook(payload_body, secret, signature_header):
    expected = base64.b64encode(
        hmac.new(secret.encode(), payload_body, hashlib.sha256).digest()
    ).decode()
    return hmac.compare_digest(expected, signature_header)
```

### Critical Rules

- **ALWAYS** enable Webhook Secret for production webhooks
- **NEVER** rely on webhooks for guaranteed delivery — implement idempotency on the receiver
- **ALWAYS** use `| tojson` filter for child table data in JSON payloads
- Webhook logs are created for every delivery — check **Webhook Request Log** for debugging

---

## Workflow 4: External API Calls from Frappe

### Using frappe.integrations.utils

```python
from frappe.integrations.utils import make_get_request, make_post_request

# GET request
response = make_get_request(
    "https://api.example.com/data",
    headers={"Authorization": "Bearer token123"}
)

# POST request
response = make_post_request(
    "https://api.example.com/submit",
    data={"key": "value"},
    headers={"Content-Type": "application/json"}
)
```

### Using requests Library Directly

```python
import requests
import frappe

def sync_to_external():
    try:
        response = requests.post(
            "https://api.example.com/endpoint",
            json={"data": "value"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        frappe.log_error(f"API call failed: {e}", "Integration Error")
        raise
```

### Critical Rules

- **ALWAYS** set a `timeout` on external requests (30s recommended)
- **ALWAYS** wrap external calls in try/except and log errors with `frappe.log_error()`
- **NEVER** call external APIs inside `validate` or `before_save` — use `on_update` + `frappe.enqueue()`
- **ALWAYS** use `frappe.enqueue()` for slow external calls to avoid blocking the web request

---

## Workflow 5: Data Import

### Via UI (Data Import DocType)

1. Navigate to **Home > Data Import > New**
2. Select DocType and Import Type (`Insert` or `Update`)
3. Download template CSV/XLSX
4. Fill in data following the template format
5. Upload and preview
6. Start Import

### CSV Format Rules

```csv
ID,Item Name,Item Group,Stock UOM
,Widget A,Products,Nos
,Widget B,Raw Material,Kg
```

- First row: field labels or API field names
- Leave `ID`/`name` empty for Insert (auto-generated)
- For Update: `ID` column MUST contain existing document names
- Child tables: repeat parent row data, add child fields as extra columns

### Programmatic Import

```python
import frappe
from frappe.core.doctype.data_import.data_import import DataImport

# Create Data Import document
di = frappe.get_doc({
    "doctype": "Data Import",
    "reference_doctype": "Item",
    "import_type": "Insert New Records",
    "import_file": "/path/to/file.csv"
})
di.insert()
di.start_import()
```

### Critical Rules

- **ALWAYS** download and use the template — column order and names must match exactly
- **NEVER** import more than 5,000 rows at once — split into batches
- **ALWAYS** test with 5-10 rows first before bulk import
- **ALWAYS** check Import Log for row-level errors after import completes

---

## Workflow 6: Data Export

### Via Report Builder

1. Open any DocType list view
2. Apply filters
3. Menu > Export (CSV/Excel)

### Via CLI

```bash
bench --site mysite export-csv "Sales Invoice"
bench --site mysite export-doc "Sales Invoice" "INV-001"
bench --site mysite export-json "Sales Invoice" "INV-001"
bench --site mysite export-fixtures --app myapp
```

### Programmatic Export

```python
import frappe

# Export filtered data
data = frappe.get_all("Sales Invoice",
    filters={"status": "Paid", "posting_date": [">", "2024-01-01"]},
    fields=["name", "customer", "grand_total", "posting_date"],
    order_by="posting_date desc",
    limit_page_length=0  # No limit
)

# Convert to CSV
import csv, io
output = io.StringIO()
writer = csv.DictWriter(output, fieldnames=["name", "customer", "grand_total", "posting_date"])
writer.writeheader()
writer.writerows(data)
csv_content = output.getvalue()
```

---

## Workflow 7: Frappe REST API Authentication

### API Key + Secret (Server-to-Server)

```bash
# Generate via User > API Access > Generate Keys
curl -H "Authorization: token api_key:api_secret" \
  https://your-site.com/api/resource/Sales%20Invoice
```

### OAuth Bearer Token

```bash
curl -H "Authorization: Bearer access_token" \
  https://your-site.com/api/resource/Sales%20Invoice
```

### Session-Based (Login)

```bash
# Login first
curl -X POST https://your-site.com/api/method/login \
  -d "usr=user@example.com&pwd=password"
# Subsequent requests use session cookie
```

---

## Integration Patterns: Sync vs Async

| Pattern | When to Use | Implementation |
|---------|-------------|----------------|
| Synchronous | Response needed immediately | Direct API call in controller |
| Async (enqueue) | External call > 5s | `frappe.enqueue("myapp.api.sync_record", doc_name=doc.name)` |
| Webhook | Push on event | Webhook DocType configuration |
| Scheduled sync | Periodic batch | `scheduler_events` in hooks.py |
| Real-time | Live updates | Socket.IO + `frappe.publish_realtime()` |

### Retry Pattern

```python
import frappe
from frappe.utils.background_jobs import get_jobs

def sync_with_retry(doc_name, retry_count=0, max_retries=3):
    try:
        result = call_external_api(doc_name)
        frappe.db.set_value("Sales Invoice", doc_name, "sync_status", "Success")
        frappe.db.commit()
    except Exception as e:
        if retry_count < max_retries:
            frappe.enqueue(
                "myapp.integrations.sync_with_retry",
                doc_name=doc_name,
                retry_count=retry_count + 1,
                queue="short",
                enqueue_after_commit=True
            )
        else:
            frappe.log_error(f"Sync failed after {max_retries} retries: {e}")
            frappe.db.set_value("Sales Invoice", doc_name, "sync_status", "Failed")
            frappe.db.commit()
```

---

## Version Differences

| Feature | V14 | V15 | V16 |
|---------|:---:|:---:|:---:|
| Webhook DocType | Yes | Yes | Yes |
| Connected App | Yes | Yes | Yes |
| OAuth 2.0 Provider | Yes | Yes | Yes |
| Data Import (new UI) | Yes | Yes | Yes |
| Print Designer | No | **Yes** | Yes |
| `make_get_request` | Yes | Yes | Yes |
| Webhook HMAC | Yes | Yes | Yes |

---

## Reference Files

| File | Contents |
|------|----------|
| [workflows.md](references/workflows.md) | Complete integration workflow patterns |
| [examples.md](references/examples.md) | Working code examples for all integration types |
| [anti-patterns.md](references/anti-patterns.md) | Common integration mistakes and fixes |
| [decision-tree.md](references/decision-tree.md) | Extended decision trees for integration choice |
---
name: frappe-impl-jinja
description: >
  Use when building Jinja templates in Frappe: Print Formats, Email
  Templates, Notification templates, Portal Pages, and custom Jinja
  methods. Covers template creation workflows, child table handling,
  conditional sections, styling, multi-language support, and debugging.
  Prevents N+1 queries, wrong formatting, and Report Print confusion.
  Keywords: create print format, email template, portal page, pdf, create print format, invoice template, email template, PDF layout, custom print.
  template, invoice template, jinja methods, notification template,
  web page template, print format styling.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Jinja Templates Implementation Workflow

Step-by-step workflows for building Jinja templates. For syntax reference, see `frappe-syntax-jinja`.

**Version**: v14/v15/v16 (V16 Chrome PDF noted)

---

## Master Decision: What Are You Creating?

```
WHAT IS YOUR OUTPUT?
│
├─► Printable PDF (invoice, PO, report)?
│   ├─► Standard DocType → Print Format (Jinja)
│   └─► Query/Script Report → Report Print Format (JAVASCRIPT!)
│       ⚠️ Uses {%= %} NOT {{ }}
│
├─► Automated email with dynamic content?
│   └─► Email Template (Jinja, linked to DocType)
│
├─► System notification?
│   └─► Notification (Setup > Notification, uses Jinja)
│
├─► Customer-facing web page?
│   └─► Portal Page (myapp/www/*.html + *.py)
│
└─► Reusable template functions/filters?
    └─► Custom jenv methods in hooks.py
```

---

## Workflow 1: Create a Print Format

### Step 1: Create via UI

```
Setup > Printing > Print Format > New
- Name: My Invoice Format
- DocType: Sales Invoice
- Module: Accounts
- Standard: No (custom)
- Print Format Type: Jinja
```

### Step 2: Write the Template

```jinja
<style>
    .print-format { font-family: Arial, sans-serif; font-size: 11px; }
    .header { margin-bottom: 20px; }
    .table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    .table th, .table td { border: 1px solid #ddd; padding: 8px; }
    .table th { background: #f0f0f0; }
    .text-right { text-align: right; }
</style>

<div class="header">
    <h1>{{ doc.select_print_heading or _("Invoice") }}</h1>
    <p><strong>{{ doc.name }}</strong> |
       {{ doc.get_formatted("posting_date") }}</p>
</div>

<p><strong>{{ doc.customer_name }}</strong></p>
{% if doc.address_display %}
    <p>{{ doc.address_display | safe }}</p>
{% endif %}

<table class="table">
    <thead>
        <tr>
            <th>#</th>
            <th>{{ _("Item") }}</th>
            <th class="text-right">{{ _("Qty") }}</th>
            <th class="text-right">{{ _("Rate") }}</th>
            <th class="text-right">{{ _("Amount") }}</th>
        </tr>
    </thead>
    <tbody>
        {% for row in doc.items %}
        <tr>
            <td>{{ row.idx }}</td>
            <td>{{ row.item_name }}</td>
            <td class="text-right">{{ row.qty }}</td>
            <td class="text-right">{{ row.get_formatted("rate", doc) }}</td>
            <td class="text-right">{{ row.get_formatted("amount", doc) }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

{% for tax in doc.taxes %}
<p class="text-right">{{ tax.description }}: {{ tax.get_formatted("tax_amount", doc) }}</p>
{% endfor %}

<p class="text-right">
    <strong>{{ _("Grand Total") }}: {{ doc.get_formatted("grand_total") }}</strong>
</p>

{% if doc.terms %}
<div style="margin-top: 30px; border-top: 1px solid #ddd; padding-top: 10px;">
    <strong>{{ _("Terms and Conditions") }}</strong>
    {{ doc.terms | safe }}
</div>
{% endif %}
```

### Step 3: Test

1. Open a Sales Invoice
2. Menu > Print > Select "My Invoice Format"
3. Verify layout and formatting
4. **ALWAYS** test PDF download — wkhtmltopdf renders differently from browser

### Critical Rules for Print Formats

- **ALWAYS** use `doc.get_formatted("field")` for currency, dates, numbers
- **ALWAYS** pass parent doc for child rows: `row.get_formatted("rate", doc)`
- **ALWAYS** wrap user-facing text with `_("text")` for translation
- **ALWAYS** put CSS in a `<style>` block at the top (not external files)
- **NEVER** use flexbox in v14/v15 (wkhtmltopdf does not support it) — V16 Chrome PDF does
- **NEVER** use `| safe` on user-supplied input — only on trusted system HTML

---

## Workflow 2: Create an Email Template

### Step 1: Create via UI

```
Setup > Email > Email Template > New
- Name: Payment Reminder
- Subject: Invoice {{ doc.name }} - Payment Reminder
- DocType: Sales Invoice
```

### Step 2: Write Email Content

**ALWAYS** use inline styles for emails — most clients strip `<style>` blocks.

```jinja
<div style="font-family: Arial, sans-serif; max-width: 600px;">
    <p>{{ _("Dear") }} {{ doc.customer_name }},</p>

    <p>{{ _("Invoice") }} <strong>{{ doc.name }}</strong>
    {{ _("for") }} {{ doc.get_formatted("grand_total") }}
    {{ _("is due for payment.") }}</p>

    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr style="background: #f5f5f5;">
            <td style="padding: 10px; border: 1px solid #ddd;">
                <strong>{{ _("Due Date") }}</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd;">
                {{ frappe.format_date(doc.due_date) }}</td>
        </tr>
        <tr>
            <td style="padding: 10px; border: 1px solid #ddd;">
                <strong>{{ _("Outstanding") }}</strong></td>
            <td style="padding: 10px; border: 1px solid #ddd; color: #c00;">
                {{ doc.get_formatted("outstanding_amount") }}</td>
        </tr>
    </table>

    {% if doc.items %}
    <p><strong>{{ _("Items") }}:</strong></p>
    <ul>
    {% for item in doc.items[:5] %}
        <li>{{ item.item_name }} ({{ item.qty }})</li>
    {% endfor %}
    {% if doc.items | length > 5 %}
        <li style="color: #666;">{{ _("and {0} more...").format(doc.items|length - 5) }}</li>
    {% endif %}
    </ul>
    {% endif %}

    <p>{{ _("Best regards") }},<br>
    {{ frappe.db.get_value("Company", doc.company, "company_name") }}</p>
</div>
```

### Step 3: Use in Notification or Code

**Option A: Auto-triggered Notification**

```
Setup > Notification > New
- Channel: Email
- Document Type: Sales Invoice
- Send Alert On: Days After (7 days after due_date)
- Condition: doc.outstanding_amount > 0
- Email Template: Payment Reminder
```

**Option B: Send from code**

```python
template = frappe.get_doc("Email Template", "Payment Reminder")
frappe.sendmail(
    recipients=[doc.contact_email],
    subject=frappe.render_template(template.subject, {"doc": doc}),
    message=frappe.render_template(template.response, {"doc": doc}),
    reference_doctype=doc.doctype,
    reference_name=doc.name
)
```

---

## Workflow 3: Create a Notification Template

### Step 1: Create via UI

```
Setup > Notification > New
- Name: Low Stock Alert
- Channel: Email (or Slack, System Notification)
- Document Type: Stock Ledger Entry
- Send Alert On: Method (on change)
- Condition: doc.actual_qty < 10
```

### Step 2: Write Message (Jinja)

```jinja
<h3>{{ _("Low Stock Alert") }}</h3>
<p>{{ _("Item") }}: <strong>{{ doc.item_code }}</strong></p>
<p>{{ _("Warehouse") }}: {{ doc.warehouse }}</p>
<p>{{ _("Current Stock") }}: {{ doc.actual_qty }}</p>
<p>{{ _("Please reorder.") }}</p>
```

---

## Workflow 4: Create a Portal Page

### Step 1: Create directory structure

```
myapp/
└── www/
    └── my-orders/
        ├── index.html    # Jinja template
        └── index.py      # Python context
```

### Step 2: Create context (index.py)

```python
import frappe

def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    context.title = "My Orders"
    context.no_cache = True

    customer = frappe.db.get_value("Contact",
        {"user": frappe.session.user}, "link_name")

    context.orders = frappe.get_all("Sales Order",
        filters={"customer": customer, "docstatus": ["!=", 2]},
        fields=["name", "transaction_date", "grand_total", "status"],
        order_by="transaction_date desc",
        limit=50
    ) if customer else []

    return context
```

### Step 3: Create template (index.html)

```jinja
{% extends "templates/web.html" %}

{% block title %}{{ _("My Orders") }}{% endblock %}

{% block page_content %}
<div class="container my-4">
    <h1>{{ _("My Orders") }}</h1>

    {% if orders %}
    <table class="table table-hover">
        <thead>
            <tr>
                <th>{{ _("Order") }}</th>
                <th>{{ _("Date") }}</th>
                <th>{{ _("Status") }}</th>
                <th class="text-right">{{ _("Total") }}</th>
            </tr>
        </thead>
        <tbody>
            {% for order in orders %}
            <tr>
                <td><a href="/orders/{{ order.name }}">{{ order.name }}</a></td>
                <td>{{ frappe.format_date(order.transaction_date) }}</td>
                <td>{{ order.status }}</td>
                <td class="text-right">
                    {{ frappe.format(order.grand_total, {"fieldtype": "Currency"}) }}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% else %}
    <p class="text-muted">{{ _("No orders found.") }}</p>
    {% endif %}
</div>
{% endblock %}
```

### Step 4: Test at `https://yoursite.com/my-orders`

---

## Workflow 5: Register Custom Jinja Methods

### Step 1: Add to hooks.py

```python
jenv = {
    "methods": ["myapp.jinja_utils.methods"],
    "filters": ["myapp.jinja_utils.filters"]
}
```

### Step 2: Create methods module

```python
# myapp/jinja_utils/methods.py
import frappe

def get_company_logo(company):
    """Usage: {{ get_company_logo(doc.company) }}"""
    return frappe.db.get_value("Company", company, "company_logo") or ""

def format_address(address_name):
    """Usage: {{ format_address(doc.customer_address) | safe }}"""
    if not address_name:
        return ""
    return frappe.get_doc("Address", address_name).get_display()
```

### Step 3: Create filters module

```python
# myapp/jinja_utils/filters.py
def phone_format(value):
    """Usage: {{ doc.phone | phone_format }}"""
    if not value:
        return ""
    digits = ''.join(c for c in str(value) if c.isdigit())
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return value
```

### Step 4: Deploy

```bash
bench --site sitename migrate
bench --site sitename clear-cache
```

### Critical Rules for Custom Jinja Methods

- Custom methods should be **READ-ONLY** — **NEVER** write to database or commit
- **ALWAYS** handle None/empty input gracefully (return empty string)
- **NEVER** call slow external APIs — templates must render fast

---

## Workflow 6: Debug a Template

### Template Not Rendering?

```jinja
<!-- Step 1: Check if doc is available -->
<!-- DEBUG: {{ doc.name if doc else 'NO DOC' }} -->

<!-- Step 2: Check child table -->
<!-- DEBUG: items count = {{ doc.items | length if doc.items else 0 }} -->

<!-- Step 3: Check specific field -->
<!-- DEBUG: grand_total = {{ doc.grand_total }} -->
```

### Common Debugging Steps

1. Check **Error Log** (Setup > Error Log) for template exceptions
2. Use `frappe.render_template(template_string, {"doc": doc})` in bench console
3. For Print Formats: Menu > Print > check browser console for errors
4. For Portal Pages: check Python context — add `frappe.logger().info(context)` in `get_context`

### Common Pitfalls

| Symptom | Cause | Fix |
|---------|-------|-----|
| Blank output | Wrong template type (Jinja in Report) | Reports use JS: `{%= %}` |
| "None" displayed | Field is null | Use `\| default('')` |
| Wrong currency format | Missing parent doc context | Use `row.get_formatted("rate", doc)` |
| HTML showing as text | Auto-escaping | Add `\| safe` (trusted content only) |
| Translations not working | Missing `_()` wrapper | Wrap all strings: `{{ _("text") }}` |

---

## Quick Patterns: Child Tables, Conditionals, Translation

```jinja
{# Child tables — ALWAYS pass parent doc for formatting context #}
{% for row in doc.items %}
  {{ row.get_formatted("rate", doc) }}  {# Correct: has currency context #}
{% endfor %}

{# Conditional sections #}
{% if doc.shipping_address_name %}
  {{ doc.shipping_address | safe }}
{% endif %}

{# Translation — ALWAYS wrap user-facing text #}
{{ _("Invoice") }}
{{ _("Page {0} of {1}").format(page, total_pages) }}
{{ doc.get_formatted("grand_total") }}  {# Auto-formats per locale #}
```

---

## Styling/CSS in Print Formats

```css
@page { margin: 1.5cm; }
.avoid-break { page-break-inside: avoid; }
thead { display: table-header-group; }   /* Repeat header on pages */
.page-break { page-break-before: always; }
/* V14/V15: NO flexbox (wkhtmltopdf). V16 Chrome PDF: flexbox OK */
.layout { display: table; width: 100%; }
.col { display: table-cell; vertical-align: top; }
```

---

## Context Variables Quick Reference

| Template Type | Available Objects |
|---------------|-------------------|
| Print Format | `doc`, `frappe`, `_()`, `frappe.format()` |
| Email Template | `doc`, `frappe` (limited), `_()` |
| Notification | `doc`, `frappe`, event data |
| Portal Page | `frappe.session`, `frappe.form_dict`, custom context |

---

## Version Differences

| Feature | V14 | V15 | V16 |
|---------|:---:|:---:|:---:|
| Jinja templates | Yes | Yes | Yes |
| get_formatted() | Yes | Yes | Yes |
| jenv hooks | Yes | Yes | Yes |
| wkhtmltopdf PDF | Yes | Yes | Deprecated |
| **Chrome PDF** | No | No | **Yes** |

> V16 Chrome PDF supports modern CSS (flexbox, grid, CSS variables). See `frappe-syntax-jinja` for details.

---

## Reference Files

| File | Contents |
|------|----------|
| [decision-tree.md](references/decision-tree.md) | Complete template type selection flowcharts |
| [print-format-decision.md](references/print-format-decision.md) | Jinja vs Print Designer vs JS Microtemplate decision tree |
| [workflows.md](references/workflows.md) | Step-by-step patterns for all template types |
| [examples.md](references/examples.md) | Production-ready templates (invoice, email, portal) |
---
name: frappe-impl-reports
description: >
  Use when building Script Reports, Query Reports, dashboard charts, or Number Cards in ERPNext.
  Prevents empty report output from wrong column definitions, broken filters, and unoptimized SQL in large datasets.
  Covers Report Builder, Script Report (Python + JS), Query Report, Report filters, dashboard Chart DocType, Number Card, report permissions.
  Keywords: report, Script Report, Query Report, dashboard, chart, Number Card, filters, columns, execute, get_data, create report, custom report, dashboard chart, report empty, no data showing..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Report Building

## Quick Reference

| Report Type | Best For | Access | Files |
|---|---|---|---|
| Query Report | Simple SQL queries | System Manager only | SQL in DocType or `.py` |
| Script Report | Complex logic, charts | Administrator + Dev Mode | `.py` + `.js` |
| Report Builder | End-user ad-hoc reports | Any permitted user | UI only |
| Prepared Report | Large datasets (>100k rows) | Same as source report | Background job |

## Decision Tree: Which Report Type?

```
Need a report?
├─ End user builds it themselves? → Report Builder
├─ Simple SQL with no Python logic? → Query Report
├─ Complex logic / charts / summary? → Script Report
│   └─ Dataset > 100k rows or timeout? → Add prepared_report = True
└─ Real-time KPI on workspace? → Number Card or Dashboard Chart
```

## 1. Creating a Script Report

### File Structure

```
my_app/my_module/report/sales_summary/
├── sales_summary.json    # Report DocType definition
├── sales_summary.py      # Python: execute() function
└── sales_summary.js      # JavaScript: filters + config
```

ALWAYS create via Desk: Report > New > Script Report > set "Is Standard = Yes" in Developer Mode.

### Python: The execute() Function

```python
# sales_summary.py
import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart(data)
    report_summary = get_summary(data)
    return columns, data, None, chart, report_summary

def get_columns():
    return [
        {"fieldname": "customer", "label": _("Customer"), "fieldtype": "Link",
         "options": "Customer", "width": 200},
        {"fieldname": "total", "label": _("Total"), "fieldtype": "Currency",
         "options": "currency", "width": 120},
        {"fieldname": "qty", "label": _("Qty"), "fieldtype": "Int", "width": 80},
        {"fieldname": "posting_date", "label": _("Date"), "fieldtype": "Date", "width": 100},
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    return frappe.db.sql("""
        SELECT
            si.customer, SUM(si.grand_total) as total,
            SUM(si.total_qty) as qty, si.posting_date
        FROM `tabSales Invoice` si
        WHERE si.docstatus = 1 {conditions}
        GROUP BY si.customer
        ORDER BY total DESC
    """.format(conditions=conditions), filters, as_dict=True)

def get_conditions(filters):
    conditions = ""
    if filters.get("from_date"):
        conditions += " AND si.posting_date >= %(from_date)s"
    if filters.get("to_date"):
        conditions += " AND si.posting_date <= %(to_date)s"
    if filters.get("company"):
        conditions += " AND si.company = %(company)s"
    return conditions
```

**Return value order** (positional — ALWAYS maintain this order):

| Position | Name | Type | Required |
|---|---|---|---|
| 1 | `columns` | list[dict] | YES |
| 2 | `data` | list[dict] or list[list] | YES |
| 3 | `message` | str or None | NO |
| 4 | `chart` | dict or None | NO |
| 5 | `report_summary` | list[dict] or None | NO |
| 6 | `skip_total_rows` | bool | NO |

### JavaScript: Filters

```javascript
// sales_summary.js
frappe.query_reports["Sales Summary"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("company"),
            reqd: 1
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            reqd: 1
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 1
        },
        {
            fieldname: "customer_group",
            label: __("Customer Group"),
            fieldtype: "Link",
            options: "Customer Group",
            depends_on: "eval:doc.company"
        }
    ],
    formatter: function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        if (column.fieldname === "total" && data.total > 100000) {
            value = "<span style='color:green;font-weight:bold'>" + value + "</span>";
        }
        return value;
    }
};
```

## 2. Creating a Query Report

Query Reports use raw SQL. ALWAYS use the legacy column format in SQL aliases:

```sql
SELECT
    `tabWork Order`.name AS "Work Order:Link/Work Order:200",
    `tabWork Order`.creation AS "Date:Date:120",
    `tabWork Order`.company AS "Company:Link/Company:150",
    `tabWork Order`.qty AS "Qty:Int:80",
    `tabWork Order`.grand_total AS "Total:Currency:120"
FROM `tabWork Order`
WHERE `tabWork Order`.docstatus = 1
ORDER BY `tabWork Order`.creation DESC
```

**Column format**: `"Label:Fieldtype/Options:Width"`

Use `%(filter_name)s` for filter variables in WHERE clauses.

## 3. Adding Charts to Reports

Return a chart dict as the 4th element from `execute()`:

```python
def get_chart(data):
    labels = [d.customer for d in data[:10]]
    values = [d.total for d in data[:10]]
    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": _("Revenue"), "values": values}]
        },
        "type": "bar",            # bar | line | pie | donut | percentage
        "colors": ["#7cd6fd"],
        "barOptions": {"stacked": False},  # for bar charts
        "height": 300
    }
```

**Chart types**: `bar`, `line`, `pie`, `donut`, `percentage`.

For multi-dataset charts (e.g., comparing periods):
```python
"datasets": [
    {"name": "2024", "values": [10, 20, 30]},
    {"name": "2025", "values": [15, 25, 35]}
]
```

## 4. Adding Report Summary

Return a list of summary dicts as the 5th element:

```python
def get_summary(data):
    total_revenue = sum(d.total for d in data)
    total_qty = sum(d.qty for d in data)
    return [
        {"value": total_revenue, "label": _("Total Revenue"),
         "datatype": "Currency", "currency": "USD",
         "indicator": "Green" if total_revenue > 0 else "Red"},
        {"value": total_qty, "label": _("Total Qty"),
         "datatype": "Int", "indicator": "Blue"},
        {"value": len(data), "label": _("Customers"),
         "datatype": "Int", "indicator": "Grey"}
    ]
```

**Indicator colors**: `Green`, `Blue`, `Orange`, `Red`, `Grey`.

## 5. Prepared Reports

For reports that timeout on large datasets, add to the `.js` file:

```javascript
frappe.query_reports["Heavy Report"] = {
    filters: [ /* ... */ ],
    prepared_report: true    // enables background generation
};
```

When `prepared_report: true`, Frappe queues the report via background job. Users see cached results and can regenerate on demand.

## 6. Number Cards

Three types of Number Cards for workspace dashboards:

| Type | Source | Use Case |
|---|---|---|
| Document Type | DocType aggregate | Count/sum of documents |
| Report | Script/Query Report | KPI from report data |
| Custom | Whitelisted method | Any computed value |

### Document Type Number Card
Create via Desk > Number Card. Set DocType, aggregate function (Count/Sum/Avg), and filters.

### Report-Based Number Card
Point to an existing report. The card displays the first row's first numeric column.

### Custom Method Number Card
```python
# In your app, create a whitelisted method:
@frappe.whitelist()
def get_open_tickets():
    count = frappe.db.count("Issue", {"status": "Open"})
    return {"value": count, "fieldtype": "Int", "route_options": {"status": "Open"},
            "route": ["query-report", "Open Issues"]}
```

## 7. Dashboard Charts

Create via Desk > Dashboard Chart or programmatically in fixtures:

```python
# hooks.py
fixtures = [
    {"dt": "Dashboard Chart", "filters": [["module", "=", "My Module"]]}
]
```

**Source types**: Report, Group By, Custom (whitelisted method).

### Group By Chart
```json
{
    "chart_name": "Invoices by Status",
    "chart_type": "Group By",
    "document_type": "Sales Invoice",
    "group_by_type": "Count",
    "group_by_based_on": "status",
    "type": "Donut",
    "filters_json": "{\"docstatus\": 1}"
}
```

## 8. Building a Dashboard

Dashboards combine multiple charts and Number Cards:

```json
{
    "name": "Sales Dashboard",
    "module": "Selling",
    "charts": [
        {"chart": "Monthly Revenue", "width": "Full"},
        {"chart": "Invoices by Status", "width": "Half"},
        {"chart": "Top Customers", "width": "Half"}
    ],
    "cards": [
        {"card": "Total Revenue"},
        {"card": "Open Orders"}
    ]
}
```

## 9. Performance Optimization

- ALWAYS add indexes on columns used in WHERE/GROUP BY (`frappe.model.utils.add_index`)
- ALWAYS use `as_dict=True` in `frappe.db.sql()` — matches column fieldnames
- NEVER use `SELECT *` — specify exact columns
- NEVER load full documents (`frappe.get_doc`) inside report loops — use SQL
- Use `frappe.qb` (query builder) for parameterized queries in v14+
- For reports > 50k rows, ALWAYS enable `prepared_report: true`
- ALWAYS filter by `docstatus` to exclude draft/cancelled documents

## 10. Common Patterns

### Date Range Filter Pattern
```python
if filters.get("from_date") and filters.get("to_date"):
    conditions += " AND posting_date BETWEEN %(from_date)s AND %(to_date)s"
```

### Multi-Currency Pattern
```python
{"fieldname": "amount", "label": _("Amount"), "fieldtype": "Currency",
 "options": "currency", "width": 120}
# "options": "currency" means use the row's "currency" field for formatting
```

### Group By with Totals Pattern
```python
data = frappe.db.sql("""
    SELECT customer, COUNT(*) as count, SUM(grand_total) as total
    FROM `tabSales Invoice`
    WHERE docstatus = 1 {conditions}
    GROUP BY customer WITH ROLLUP
""".format(conditions=conditions), filters, as_dict=True)
```

## See Also

- [references/examples.md](references/examples.md) — Complete report examples
- [references/anti-patterns.md](references/anti-patterns.md) — Common mistakes
- [references/workflows.md](references/workflows.md) — Step-by-step workflows
- `frappe-syntax-api` — Frappe Python API reference
- `frappe-core-database` — Database query patterns
---
name: frappe-impl-scheduler
description: >
  Use when implementing scheduled tasks and background jobs in Frappe
  v14/v15/v16. Covers hooks.py scheduler_events, frappe.enqueue, queue
  selection, job deduplication, testing with bench execute/scheduler,
  monitoring via Scheduled Job Log and RQ Dashboard, error handling,
  long-running job patterns, email digest, data cleanup, and report
  generation. Keywords: schedule task, background job, cron job, async
  processing, queue selection, job deduplication, scheduler implementation,
  run task automatically, background process, scheduled task not running, async task.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Scheduler & Background Jobs - Implementation

Workflow for implementing scheduled tasks and background jobs. For exact syntax, see `frappe-syntax-scheduler`.

**Version**: v14/v15/v16 compatible

---

## Main Decision: scheduler_events vs frappe.enqueue

```
WHAT ARE YOU BUILDING?
|
+-- Runs at fixed intervals/times?
|   +-- YES --> scheduler_events (hooks.py)
|   |           Task receives NO arguments
|   |           See: Workflow 1-2
|   |
|   +-- NO --> Triggered by user action or code?
|              +-- YES --> frappe.enqueue()
|              |           Pass any serializable data
|              |           See: Workflow 3-4
|              |
|              +-- NO --> Reconsider requirements
```

| Aspect | scheduler_events | frappe.enqueue |
|--------|------------------|----------------|
| Triggered by | Time/interval | Code execution |
| Defined in | hooks.py | Python code |
| Arguments | NONE (must be parameterless) | Any serializable data |
| Use case | Daily cleanup, hourly sync | User-triggered long task |
| Queue control | Event suffix (_long) | queue= parameter |
| Restart behavior | Runs on schedule | Lost if worker restarts |

---

## Which Scheduler Event Type?

| Need | Event Key | Queue |
|------|-----------|-------|
| Every scheduler tick | `all` | short (NEVER >60s) |
| Hourly (<5 min) | `hourly` | short |
| Hourly (5-25 min) | `hourly_long` | long |
| Daily (<5 min) | `daily` | short |
| Daily (5-25 min) | `daily_long` | long |
| Weekly (<5 min) | `weekly` | short |
| Weekly (5-25 min) | `weekly_long` | long |
| Monthly (<5 min) | `monthly` | short |
| Monthly (5-25 min) | `monthly_long` | long |
| Custom schedule | `cron["expr"]` | short |

**Rule**: ALWAYS use `*_long` suffix for tasks exceeding 5 minutes.

---

## Which Queue for frappe.enqueue?

| Queue | Default Timeout | Use For |
|-------|-----------------|---------|
| `short` | 300s (5 min) | Quick operations (<1 min) |
| `default` | 300s (5 min) | Standard tasks (1-5 min) |
| `long` | 1500s (25 min) | Heavy processing (>5 min) |

**Rule**: ALWAYS specify `queue=` explicitly. NEVER rely on the default.

---

## Implementation Step 1: Scheduler Event

```python
# myapp/tasks.py
import frappe

def daily_cleanup():
    """Daily cleanup - NO parameters allowed."""
    cutoff = frappe.utils.add_days(frappe.utils.nowdate(), -30)
    frappe.db.delete("Error Log", {"creation": ("<", cutoff)})
    frappe.db.commit()
```

```python
# hooks.py
scheduler_events = {
    "daily": ["myapp.tasks.daily_cleanup"]
}
```

**After editing hooks.py**: ALWAYS run `bench migrate`.

---

## Implementation Step 2: Background Job (frappe.enqueue)

```python
# myapp/api.py
import frappe
from frappe.utils.background_jobs import is_job_enqueued

@frappe.whitelist()
def process_documents(doctype, filters):
    job_id = f"process_{doctype}_{frappe.session.user}"

    if is_job_enqueued(job_id):
        return {"message": "Already in progress"}

    frappe.enqueue(
        "myapp.tasks.process_batch",
        queue="long",
        timeout=1800,
        job_id=job_id,
        enqueue_after_commit=True,
        doctype=doctype,
        filters=filters
    )
    return {"status": "queued"}
```

---

## Testing Scheduled Tasks

### Method 1: bench execute (direct)
```bash
# Run the function directly (no queue involved)
bench --site mysite execute myapp.tasks.daily_cleanup
```

### Method 2: bench scheduler (full scheduler test)
```bash
# Check scheduler status
bench --site mysite scheduler status

# Enable scheduler
bench --site mysite scheduler enable

# Trigger all pending scheduler events NOW
bench --site mysite scheduler trigger

# Run specific event type
bench --site mysite execute frappe.utils.scheduler.trigger --args "['daily']"
```

### Method 3: bench console (interactive)
```python
bench --site mysite console
>>> frappe.enqueue("myapp.tasks.my_task", queue="short", now=True)
# now=True executes synchronously for testing
```

### Method 4: Check Scheduled Job Type
```
1. Go to: Setup > Scheduled Job Type
2. Find: myapp.tasks.daily_cleanup
3. Verify: Frequency correct, Stopped = No
4. Click "Run Now" to trigger manually
```

---

## Monitoring

### Scheduled Job Log (UI)
```
Setup > Scheduled Job Log
- Shows every scheduler run with status
- Filter by: status (Success/Failed), creation date
- Check execution time to detect slow tasks
```

### RQ Dashboard
```bash
# Start RQ monitor (development)
bench --site mysite rq-dashboard
# Opens at http://localhost:9181

# Show background job status
bench --site mysite show-pending-jobs
bench --site mysite show-failed-jobs
```

### Programmatic Health Check
```python
def scheduler_health_check():
    failed = frappe.db.count("Scheduled Job Log", {
        "status": "Failed",
        "creation": [">=", frappe.utils.add_to_date(None, hours=-1)]
    })
    if failed > 5:
        frappe.sendmail(
            recipients=["admin@example.com"],
            subject="Scheduler Alert: Many failures",
            message=f"{failed} scheduler jobs failed in last hour"
        )
```

---

## Error Handling in Scheduled Tasks

### Per-Record Error Isolation
```python
def sync_all_orders():
    orders = get_pending_orders()
    success, errors = 0, 0

    for order in orders:
        try:
            sync_to_external(order)
            success += 1
        except Exception as e:
            errors += 1
            frappe.db.rollback()
            frappe.log_error(
                f"Sync failed for {order}: {e}",
                "Order Sync Error"
            )
    frappe.db.commit()
    frappe.logger("sync").info(f"{success} ok, {errors} errors")
```

**Rule**: ALWAYS wrap per-record processing in try-except. NEVER let one failure stop the entire batch.

---

## Long-Running Job Patterns

### Self-Chaining Pattern (>25 min tasks)
```python
def process_batch(offset=0, batch_size=500, total=None):
    if total is None:
        total = frappe.db.count("Sales Invoice", {"custom_processed": 0})

    records = frappe.get_all("Sales Invoice",
        filters={"custom_processed": 0},
        pluck="name", limit=batch_size)

    if not records:
        return  # Done

    for name in records:
        process_single(name)
    frappe.db.commit()

    remaining = frappe.db.count("Sales Invoice", {"custom_processed": 0})
    if remaining > 0:
        frappe.enqueue(
            "myapp.tasks.process_batch",
            queue="long",
            offset=offset + batch_size,
            batch_size=batch_size,
            total=total
        )
```

**Rule**: ALWAYS split tasks >25 min into self-chaining batches.

---

## Common Implementation Patterns

### Email Digest (weekly summary)
```python
# hooks.py
scheduler_events = {
    "cron": {
        "0 8 * * 1": ["myapp.newsletter.send_weekly_digest"]
    }
}
```
See `references/examples.md` Example 4 for complete implementation.

### Data Cleanup (daily maintenance)
```python
scheduler_events = {
    "daily_long": ["myapp.maintenance.daily_database_maintenance"]
}
```
See `references/examples.md` Example 1 for batch deletion pattern.

### Report Generation (user-triggered)
```python
frappe.enqueue(
    "myapp.tasks.generate_report",
    queue="long",
    timeout=3600,
    job_id=f"report::{frappe.session.user}",
    user=frappe.session.user
)
```
See `references/workflows.md` Workflow 6 for progress reporting.

---

## Critical Rules

1. **Scheduler tasks receive NO arguments** - Use settings or hardcoded values
2. **ALWAYS `bench migrate` after hooks.py changes** - Required to register events
3. **Jobs run as Administrator** - ALWAYS commit explicitly
4. **Commit in batches** - NEVER per-record (every 100-500 records)
5. **ALWAYS use `job_id` for user-triggered jobs** - Prevents duplicates
6. **Use `enqueue_after_commit=True`** from document events - Ensures data exists
7. **Scheduler events should be thin** - Enqueue heavy work to background

## Version Differences

| Aspect | v14 | v15 | v16 |
|--------|-----|-----|-----|
| Tick interval | 240s | 60s | 60s |
| Job dedup param | `job_name` | `job_id` | `job_id` |
| `enqueue_doc()` | Yes | Yes | Yes |
| Custom queues | No | Yes | Yes |

---

## Reference Files

| File | Contents |
|------|----------|
| [workflows.md](references/workflows.md) | 8 step-by-step implementation patterns |
| [decision-tree.md](references/decision-tree.md) | Detailed decision flowcharts |
| [examples.md](references/examples.md) | 5 complete working examples |
| [anti-patterns.md](references/anti-patterns.md) | 14 common mistakes to avoid |

## See Also

- `frappe-syntax-scheduler` - Exact syntax reference for hooks and enqueue
- `frappe-errors-serverscripts` - Error handling patterns
- `frappe-impl-hooks` - Hook configuration patterns
- `frappe-ops-bench` - Bench commands for scheduler management
- `frappe-ops-performance` - Performance tuning for background jobs
- `frappe-testing-unit` - Testing scheduled task logic
---
name: frappe-impl-serverscripts
description: >
  Use when implementing server-side features via Setup > Server Script:
  document validation, auto-fill, API endpoints, scheduled tasks,
  permission queries. Covers sandbox-safe coding, script type selection,
  testing, migration to controllers. Keywords: how to implement server
  script, which script type, sandbox limitation, Document Event, API
  script, Scheduler Event, Permission Query, migrate to controller,
  no-code automation, run code on save, auto-fill field, server-side validation, scheduled script.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Server Scripts — Implementation Workflows

Step-by-step workflows for building server-side features without a custom app. For exact syntax, see `frappe-syntax-serverscripts`.

**Version**: v14/v15/v16 | **v15+ Note**: Server Scripts disabled by default — enable with `bench set-config server_script_enabled true`

## CRITICAL: Sandbox Limitations

```
ALL IMPORTS BLOCKED — RestrictedPython sandbox
  import json          → ImportError: __import__ not found
  from frappe.utils    → ImportError
  import requests      → ImportError

SOLUTION: Use pre-loaded namespace:
  frappe.utils.nowdate()        frappe.utils.flt()
  frappe.parse_json(data)       json.loads() (json IS available)
  frappe.as_json(obj)           json.dumps()
  frappe.make_get_request(url)  (replaces requests.get)
```

**Rule**: If you need `import` statements beyond `json`, ALWAYS use a Controller instead.

## Workflow 1: Create a Server Script

1. Enable server scripts: `bench set-config server_script_enabled true`
2. Navigate to **Setup > Server Script** (or awesomebar: "New Server Script")
3. Select **Script Type** (see decision tree below)
4. Configure type-specific settings (DocType, event, API method, cron)
5. Write script in the editor
6. Save — script is active immediately
7. Test by triggering the configured event
8. Use "Compare Versions" button to diff changes

## Workflow 2: Choose the Script Type

```
WHAT DO YOU NEED?
│
├── React to document save/submit/cancel?
│   └── Document Event
│       └── Select DocType + Event (Before Save, After Save, etc.)
│
├── Create a REST API endpoint?
│   └── API
│       └── Set method name + guest access setting
│       └── Endpoint: /api/method/{method_name}
│
├── Run task on schedule (daily/hourly/cron)?
│   └── Scheduler Event
│       └── Set cron pattern or frequency
│
└── Filter list views per user/role?
    └── Permission Query
        └── Select DocType — set `conditions` variable
```

> See [references/decision-tree.md](references/decision-tree.md) for complete decision tree.

## Workflow 3: Document Event: Validation

**Goal**: Validate Sales Order before save.

**Step 1**: Choose event — "Before Save" maps to `validate` hook.

**Step 2**: Write sandbox-safe script:

```python
# Type: Document Event | Event: Before Save | DocType: Sales Order

errors = []

if not doc.customer:
    errors.append("Customer is required")

if doc.delivery_date and doc.delivery_date < frappe.utils.today():
    errors.append("Delivery date cannot be in the past")

for item in doc.items:
    if item.qty <= 0:
        errors.append(f"Row {item.idx}: Quantity must be positive")

if errors:
    frappe.throw("<br>".join(errors), title="Validation Error")
```

**Rules**:
- ALWAYS collect errors and throw once (better UX than multiple throws)
- NEVER call `doc.save()` in Before Save — framework handles it
- ALWAYS use `frappe.throw()` — `msgprint` does NOT stop save

## Workflow 4: Document Event: Auto-Calculate

**Goal**: Auto-calculate totals and set derived fields.

```python
# Type: Document Event | Event: Before Save | DocType: Purchase Order

doc.total_qty = sum(item.qty or 0 for item in doc.items)
doc.total_amount = sum((item.qty or 0) * (item.rate or 0) for item in doc.items)

if doc.total_amount > 50000:
    doc.requires_approval = 1
    doc.approval_status = "Pending"

if doc.supplier and not doc.supplier_name:
    doc.supplier_name = frappe.db.get_value("Supplier", doc.supplier, "supplier_name")
```

**Rule**: ALWAYS modify `doc` fields directly in Before Save — they are automatically persisted.

## Workflow 5: Document Event: Create Related Document

**Goal**: Create a ToDo when a new Lead is inserted.

```python
# Type: Document Event | Event: After Insert | DocType: Lead

frappe.get_doc({
    "doctype": "ToDo",
    "allocated_to": doc.lead_owner or doc.owner,
    "reference_type": "Lead",
    "reference_name": doc.name,
    "description": f"Follow up with new lead: {doc.lead_name}",
    "date": frappe.utils.add_days(frappe.utils.today(), 1),
    "priority": "High" if doc.status == "Hot" else "Medium"
}).insert(ignore_permissions=True)
```

**Rules**:
- ALWAYS use After Insert or After Save for creating related docs
- NEVER create documents in Before Save — `doc.name` may not exist yet
- ALWAYS use `ignore_permissions=True` for system-generated documents

## Workflow 6: API Endpoint

**Goal**: Create authenticated REST API returning customer data.

```python
# Type: API | Method: get_customer_dashboard | Allow Guest: No
# Endpoint: /api/method/get_customer_dashboard

customer = frappe.form_dict.get("customer")
if not customer:
    frappe.throw("Parameter 'customer' is required")

# ALWAYS check permissions
if not frappe.has_permission("Customer", "read", customer):
    frappe.throw("Access denied", frappe.PermissionError)

orders = frappe.db.count("Sales Order", {"customer": customer, "docstatus": 1})
revenue = frappe.db.get_value("Sales Invoice",
    filters={"customer": customer, "docstatus": 1},
    fieldname="sum(grand_total)") or 0

frappe.response["message"] = {
    "customer": customer,
    "total_orders": orders,
    "total_revenue": revenue
}
```

**Rules**:
- ALWAYS validate input parameters
- ALWAYS check permissions (even with Allow Guest: No)
- ALWAYS cap query limits: `min(frappe.utils.cint(limit), 100)`
- NEVER expose full documents — return only needed fields

## Workflow 7: Scheduler Event

**Goal**: Daily reminder for overdue invoices.

```python
# Type: Scheduler Event | Cron: 0 9 * * * (daily at 9:00)

BATCH_SIZE = 50
today = frappe.utils.today()

overdue = frappe.get_all("Sales Invoice",
    filters={
        "status": "Unpaid",
        "due_date": ["<", today],
        "docstatus": 1
    },
    fields=["name", "customer", "owner", "due_date", "grand_total"],
    limit=BATCH_SIZE
)

for inv in overdue:
    days = frappe.utils.date_diff(today, inv.due_date)
    if not frappe.db.exists("ToDo", {
        "reference_type": "Sales Invoice",
        "reference_name": inv.name,
        "status": "Open"
    }):
        frappe.get_doc({
            "doctype": "ToDo",
            "allocated_to": inv.owner,
            "reference_type": "Sales Invoice",
            "reference_name": inv.name,
            "description": f"Invoice {inv.name} is {days} days overdue"
        }).insert(ignore_permissions=True)

frappe.db.commit()  # REQUIRED in scheduler scripts
```

**Rules**:
- ALWAYS add `frappe.db.commit()` at end of scheduler scripts
- ALWAYS add `limit` to queries — prevent memory exhaustion
- ALWAYS use `try/except` + `frappe.log_error()` in loops
- NEVER run scheduler scripts that process unlimited records

## Workflow 8: Permission Query

**Goal**: Users see only their territory's customers.

```python
# Type: Permission Query | DocType: Customer

user_territory = frappe.db.get_value("User", user, "territory")
user_roles = frappe.get_roles(user)

if "System Manager" in user_roles:
    conditions = ""  # Full access
elif user_territory:
    conditions = f"`tabCustomer`.territory = {frappe.db.escape(user_territory)}"
else:
    conditions = f"`tabCustomer`.owner = {frappe.db.escape(user)}"
```

**Rules**:
- ALWAYS give System Manager full access (`conditions = ""`)
- ALWAYS use `frappe.db.escape()` for user input in SQL
- ALWAYS set `conditions` variable — it is the output
- Permission Query only affects `frappe.db.get_list`, NOT `frappe.db.get_all`

## Event Name Mapping

| UI Name | Internal Hook | Best For |
|---------|---------------|----------|
| Before Validate | `before_validate` | Pre-validation defaults |
| **Before Save** | **`validate`** | Validation + calculations (MOST COMMON) |
| After Save | `on_update` | Notifications, audit logs |
| After Insert | `after_insert` | Create related docs (new only) |
| Before Submit | `before_submit` | Submit-time validation |
| After Submit | `on_submit` | Post-submit automation |
| Before Cancel | `before_cancel` | Cancel prevention |
| After Cancel | `on_cancel` | Cleanup after cancel |
| Before Delete | `on_trash` | Delete prevention |

## Sandbox-Safe API Quick Reference

| Need | Use (NOT import) |
|------|-------------------|
| Parse JSON | `frappe.parse_json()` or `json.loads()` |
| Serialize JSON | `frappe.as_json()` or `json.dumps()` |
| Today's date | `frappe.utils.today()` |
| Now (datetime) | `frappe.utils.now()` |
| Add days | `frappe.utils.add_days(date, n)` |
| Date diff | `frappe.utils.date_diff(d1, d2)` |
| Float conversion | `frappe.utils.flt(val)` |
| Int conversion | `frappe.utils.cint(val)` |
| HTTP GET | `frappe.make_get_request(url)` |
| HTTP POST | `frappe.make_post_request(url, data)` |
| Render template | `frappe.render_template(tmpl, ctx)` |
| Log error | `frappe.log_error(msg, title)` |
| Send email | `frappe.sendmail(recipients, subject, message)` |

## When to Migrate to Controller

ALWAYS migrate to a Document Controller when:
- You need `import` statements (beyond `json`)
- Script exceeds 100 lines
- You need try/except with rollback
- You need `frappe.enqueue()` for background jobs
- You need to extend an existing ERPNext DocType
- Multiple scripts on same DocType become hard to manage

**Migration path**: See `frappe-impl-controllers` for controller implementation.

## Related Skills

- `frappe-syntax-serverscripts` — Exact sandbox API reference
- `frappe-errors-serverscripts` — Error handling and anti-patterns
- `frappe-core-database` — `frappe.db.*` operations
- `frappe-core-permissions` — Permission system details
- `frappe-impl-controllers` — When to migrate from Server Script

> See [references/decision-tree.md](references/decision-tree.md) for complete decision trees.
> See [references/workflows.md](references/workflows.md) for extended patterns.
> See [references/examples.md](references/examples.md) for 10+ complete examples.
---
name: frappe-impl-ui-components
description: >
  Use when building custom dialogs, extending List View, creating Page controllers, or adding Kanban/Calendar views and realtime updates.
  Prevents UI freezes from synchronous calls, broken dialogs from wrong field definitions, and missed socket events.
  Covers frappe.ui.Dialog, frappe.ui.form.MultiSelectDialog, List View customization, frappe.pages, Kanban Board, Calendar View, frappe.realtime, socket.io publish/subscribe.
  Keywords: Dialog, List View, Page, Kanban, Calendar, realtime, socket.io, frappe.ui, MultiSelectDialog, publish_realtime, popup dialog, custom dialog, list view customize, realtime update, live data, kanban setup..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe UI Components & Realtime — Implementation Workflows

Step-by-step workflows for building client-side UI. For form scripting see `frappe-impl-clientscripts`. For server-side API see `frappe-syntax-serverscripts`.

**Version**: v14/v15/v16 | **Note**: v15+ uses Bootstrap 5; Dialog API is stable across all versions.

## Quick Decision: Which UI Component?

```
WHAT do you need?
├── Prompt user for input         → frappe.prompt (simple) or frappe.ui.Dialog (complex)
├── Show a message/alert          → frappe.msgprint / frappe.show_alert / frappe.throw
├── Confirm an action             → frappe.confirm
├── Multi-field data entry popup  → frappe.ui.Dialog with fields
├── Select from a list of records → frappe.ui.form.MultiSelectDialog
├── Full custom page (not a form) → frappe.ui.Page
├── Customize list columns/colors → frappe.listview_settings
├── Visual board for workflow     → Kanban Board (Select field based)
├── Date-based record view        → Calendar View ({doctype}_calendar.js)
├── Hierarchical data display     → Tree View (is_tree DocType)
├── Live updates without refresh  → frappe.publish_realtime + frappe.realtime.on
├── Show background job progress  → frappe.publish_progress
├── Scan barcode/QR code          → frappe.ui.Scanner
└── Custom cell formatting        → formatters in listview_settings or form
```

See `references/decision-tree.md` for the complete decision tree.

## Workflow 1: Dialogs (frappe.ui.Dialog)

### Simple Dialog

```javascript
let d = new frappe.ui.Dialog({
    title: "Enter Details",
    fields: [
        { label: "Full Name", fieldname: "full_name", fieldtype: "Data", reqd: 1 },
        { label: "Email", fieldname: "email", fieldtype: "Data", options: "Email" },
        { label: "Role", fieldname: "role", fieldtype: "Select",
          options: "Developer\nManager\nDesigner" },
    ],
    size: "small",  // "small", "large", or "extra-large"
    primary_action_label: "Create",
    primary_action(values) {
        frappe.call({
            method: "myapp.api.create_user",
            args: values,
            callback(r) {
                if (!r.exc) {
                    frappe.show_alert({ message: "User created", indicator: "green" });
                    d.hide();
                }
            }
        });
    }
});
d.show();
```

**Rule**: ALWAYS call `d.hide()` inside the callback, NEVER before the async call completes.

### Dialog with Table Field

```javascript
let d = new frappe.ui.Dialog({
    title: "Add Items",
    fields: [
        { label: "Customer", fieldname: "customer", fieldtype: "Link",
          options: "Customer", reqd: 1 },
        { fieldtype: "Section Break" },
        { label: "Items", fieldname: "items", fieldtype: "Table",
          in_place_edit: true, reqd: 1,
          fields: [
              { fieldname: "item", label: "Item", fieldtype: "Link",
                options: "Item", in_list_view: 1, reqd: 1 },
              { fieldname: "qty", label: "Qty", fieldtype: "Int",
                in_list_view: 1, default: 1 },
              { fieldname: "rate", label: "Rate", fieldtype: "Currency",
                in_list_view: 1 },
          ],
        },
    ],
    primary_action_label: "Submit",
    primary_action(values) {
        console.log(values);  // { customer: "...", items: [{item, qty, rate}] }
        d.hide();
    }
});
d.show();
```

**Rule**: ALWAYS set `in_list_view: 1` on table child fields you want visible. Fields without it are hidden in the grid.

### Multi-Step Dialog

```javascript
let d = new frappe.ui.Dialog({
    title: "Setup Wizard",
    fields: [
        // Page 1
        { fieldtype: "Section Break", label: "Step 1: Basic Info",
          collapsible: 0 },
        { label: "Name", fieldname: "name", fieldtype: "Data", reqd: 1 },
        // Page 2
        { fieldtype: "Section Break", label: "Step 2: Configuration",
          collapsible: 0 },
        { label: "Option", fieldname: "option", fieldtype: "Select",
          options: "A\nB\nC" },
    ],
    primary_action_label: "Finish",
    primary_action(values) {
        d.hide();
    }
});
d.show();
```

### Key Dialog Methods

| Method | Purpose |
|--------|---------|
| `d.show()` | Display the dialog |
| `d.hide()` | Close the dialog |
| `d.get_values()` | Get all field values as object |
| `d.set_values({field: val})` | Set field values |
| `d.get_field("name")` | Get a specific field control |
| `d.set_df_property("name", "hidden", 1)` | Show/hide fields dynamically |
| `d.disable_primary_action()` | Grey out submit button |
| `d.enable_primary_action()` | Re-enable submit button |

## Workflow 2: Messages & Alerts

### frappe.msgprint: Modal Message

```javascript
// Simple message
frappe.msgprint("Record saved successfully");

// With options
frappe.msgprint({
    title: "Warning",
    message: "This action cannot be undone",
    indicator: "orange",     // green, blue, orange, red
    primary_action: {
        label: "Proceed",
        action() { do_something(); }
    }
});

// List of messages
frappe.msgprint({
    title: "Validation Errors",
    message: "Please fix the following:",
    as_list: true,
    indicator: "red",
});
```

### frappe.throw: Error with Exception

```javascript
// Client-side: shows msgprint and stops execution
frappe.throw("Amount cannot be negative");
```

```python
# Server-side: raises ValidationError, shown as red msgprint
frappe.throw("Amount cannot be negative")
frappe.throw("Not Permitted", frappe.PermissionError)  # specific exception
```

**Rule**: ALWAYS use `frappe.throw` for validation errors. NEVER use `frappe.msgprint` for errors — it does not stop execution.

### frappe.confirm: Yes/No Dialog

```javascript
frappe.confirm(
    "Are you sure you want to delete this record?",
    () => { /* Yes callback */ delete_record(); },
    () => { /* No callback (optional) */ }
);
```

### frappe.prompt: Quick Single-Field Input

```javascript
frappe.prompt(
    { label: "Reason", fieldname: "reason", fieldtype: "Small Text", reqd: 1 },
    (values) => {
        console.log(values.reason);
    },
    "Enter Reason",    // dialog title
    "Submit"           // primary action label
);

// Multiple fields
frappe.prompt([
    { label: "Reason", fieldname: "reason", fieldtype: "Small Text", reqd: 1 },
    { label: "Priority", fieldname: "priority", fieldtype: "Select",
      options: "Low\nMedium\nHigh" },
], (values) => { console.log(values); }, "Details");
```

### frappe.show_alert: Toast Notification

```javascript
// Simple
frappe.show_alert("Saved");

// With indicator and duration
frappe.show_alert({ message: "Email sent", indicator: "green" }, 5);
// Duration in seconds (default: 7)
```

**Rule**: Use `frappe.show_alert` for non-blocking success messages. Use `frappe.msgprint` when the user MUST acknowledge.

## Workflow 3: List View Customization

Create `{doctype_name}_list.js` in the DocType directory:

```javascript
// myapp/doctype/task/task_list.js
frappe.listview_settings["Task"] = {
    // Extra fields to fetch (beyond standard)
    add_fields: ["priority", "status", "assigned_to"],

    // Hide the name column
    hide_name_column: true,

    // Row indicator (colored dot)
    get_indicator(doc) {
        // MUST return [label, color, comma-separated-filter]
        if (doc.status === "Completed") return ["Completed", "green", "status,=,Completed"];
        if (doc.status === "Overdue") return ["Overdue", "red", "status,=,Overdue"];
        return ["Open", "orange", "status,=,Open"];
    },

    // Custom column formatters
    formatters: {
        priority(val) {
            const colors = { High: "red", Medium: "orange", Low: "green" };
            return `<span class="indicator-pill ${colors[val] || ""}">${val}</span>`;
        }
    },

    // Row action button
    button: {
        show(doc) { return doc.status === "Open"; },
        get_label() { return __("Complete"); },
        get_description(doc) { return __("Mark {0} as complete", [doc.name]); },
        action(doc) {
            frappe.xcall("myapp.api.complete_task", { task: doc.name })
                .then(() => cur_list.refresh());
        }
    },

    // Lifecycle hooks
    onload(listview) {
        listview.page.add_inner_button("Export", () => export_tasks());
    },

    refresh(listview) {
        // Runs on every list refresh
    },

    // Default filters
    filters: [["status", "!=", "Cancelled"]],
};
```

**Rule**: ALWAYS return a 3-element array from `get_indicator`. The third element is the filter string for click-to-filter.

## Workflow 4: Custom Page (frappe.ui.Page)

### Step 1: Register in hooks.py

```python
# hooks.py
page_js = { "my-custom-page": "public/js/my_custom_page.js" }
```

### Step 2: Create page definition

```javascript
// myapp/myapp/my_custom_page/my_custom_page.js
frappe.pages["my-custom-page"].on_page_load = function(wrapper) {
    let page = frappe.ui.make_app_page({
        parent: wrapper,
        title: "My Custom Page",
        single_column: true,
    });

    // Primary action button
    page.set_primary_action("Create", () => create_new(), "octicon octicon-plus");

    // Secondary action
    page.set_secondary_action("Refresh", () => refresh_data());

    // Dropdown menu
    page.add_menu_item("Export CSV", () => export_csv());
    page.add_menu_item("Settings", () => frappe.set_route("Form", "My Settings"));

    // Inner toolbar buttons
    page.add_inner_button("Update All", () => update_all());
    page.add_inner_button("New Post", () => new_post(), "Make");  // grouped

    // Toolbar filter fields
    let status_field = page.add_field({
        label: "Status",
        fieldtype: "Select",
        fieldname: "status",
        options: ["", "Open", "Closed", "Cancelled"],
        change() { refresh_data(); }
    });

    // Status indicator
    page.set_indicator("Active", "green");

    // Content area
    $(page.body).html(`<div class="my-page-content"></div>`);

    // Load initial data
    refresh_data();
};
```

### Key Page Methods

| Method | Purpose |
|--------|---------|
| `page.set_title(title)` | Set page heading |
| `page.set_indicator(label, color)` | Status badge (green/red/orange/blue) |
| `page.set_primary_action(label, fn, icon)` | Main action button |
| `page.set_secondary_action(label, fn)` | Secondary button |
| `page.add_menu_item(label, fn)` | Dropdown menu entry |
| `page.add_inner_button(label, fn, group)` | Toolbar button (optional group) |
| `page.add_field({...})` | Add filter/input to toolbar |
| `page.get_form_values()` | Get all toolbar field values |
| `page.clear_fields()` | Remove all toolbar fields |
| `page.clear_primary_action()` | Remove primary button |

## Workflow 5: Calendar View

Create `{doctype}_calendar.js` in the DocType directory:

```javascript
// myapp/doctype/event/event_calendar.js
frappe.views.calendar["Event"] = {
    field_map: {
        start: "starts_on",
        end: "ends_on",
        id: "name",
        title: "subject",
        allDay: "all_day",
        color: "color",
    },
    gantt: true,  // Enable Gantt view toggle
    get_events_method: "myapp.api.get_events",  // Optional custom event source
    filters: [
        { fieldtype: "Link", fieldname: "event_type", label: "Type",
          options: "Event Type" }
    ],
};
```

**Rule**: ALWAYS map `start` and `end` to actual Date or Datetime fields on the DocType. Missing mappings cause blank calendars.

## Workflow 6: Kanban Board

Kanban boards work on any DocType with a **Select** field. No code needed:

1. Open List View → sidebar → **Kanban** → **New Kanban Board**
2. Select the **Select field** (e.g., `status`) — options become columns
3. Save — cards are draggable between columns

**Rule**: NEVER create Kanban boards for DocTypes without a Select field. See `references/examples.md` for programmatic configuration.

## Workflow 7: Realtime Updates (Socket.IO)

### Server: Publish Events

```python
# Broadcast to all users
frappe.publish_realtime("task_updated", {"task": task.name, "status": "Done"})

# Send to specific user
frappe.publish_realtime("notification", {"msg": "Your report is ready"},
    user="admin@example.com")

# Send to users viewing a specific document
frappe.publish_realtime("doc_updated", {"field": "status"},
    doctype="Task", docname="TASK-001")

# ALWAYS use after_commit=True in document events
frappe.publish_realtime("order_created", message, after_commit=True)
```

### Client: Subscribe to Events

```javascript
// Listen for events
frappe.realtime.on("task_updated", (data) => {
    frappe.show_alert({ message: `Task ${data.task}: ${data.status}`, indicator: "green" });
    cur_list && cur_list.refresh();
});

// Stop listening
frappe.realtime.off("task_updated");
```

### Progress Indicator

```python
# Server: publish progress during long operations
def process_items(items):
    total = len(items)
    for i, item in enumerate(items):
        process(item)
        frappe.publish_progress(
            percent=(i + 1) / total * 100,
            title="Processing Items",
            description=f"Processing {item.name}",
        )
```

**Rule**: ALWAYS use `after_commit=True` when publishing from document events. Without it, the event fires even if the transaction rolls back.

### Realtime Rooms

| Room | Audience | Use Case |
|------|----------|----------|
| (default) | All System Users | Global notifications |
| `user:{email}` | Single user | Personal alerts |
| `doctype:{dt}` | Users viewing list | List refresh triggers |
| `doc:{dt}/{name}` | Users viewing document | Document change alerts |
| `website` | All users including guests | Public announcements |

## Workflow 8: Scanner API (Barcode/QR)

```javascript
// Single scan — closes after first scan
new frappe.ui.Scanner({
    dialog: true, multiple: false,
    on_scan(data) {
        frappe.set_route("Form", "Item", data.decodedText);
    }
});

// Continuous scanning — stays open for multiple scans
let scanner = new frappe.ui.Scanner({
    dialog: true, multiple: true,
    on_scan(data) { add_item_to_list(data.decodedText); }
});
// Stop: scanner.stop_scan() or close the dialog
```

**Rule**: ALWAYS set `multiple: false` for single-item lookups. See `references/examples.md` for a full barcode-in-Stock-Entry example.

## Anti-Patterns Summary

| Anti-Pattern | Correct Approach |
|---|---|
| `frappe.msgprint` for errors | Use `frappe.throw` — it stops execution |
| Hiding dialog before async completes | Hide in the callback: `callback() { d.hide(); }` |
| Synchronous API calls in dialogs | ALWAYS use `frappe.call` / `frappe.xcall` (async) |
| Missing `in_list_view` on table fields | Set `in_list_view: 1` on visible columns |
| `publish_realtime` without `after_commit` | ALWAYS use `after_commit=True` in doc events |
| Kanban on DocType without Select field | Kanban requires a Select field for columns |
| Missing start/end in calendar field_map | ALWAYS map both `start` and `end` fields |
| 2-element array from get_indicator | ALWAYS return 3 elements: [label, color, filter] |

## Reference Files

- `references/controls-api.md` — Standalone controls via `frappe.ui.form.make_control()`, full control type reference, control methods and events
- `references/tree-view.md` — Tree DocType configuration, `frappe.views.TreeView` API, `frappe.ui.Tree` low-level API, tree node operations
- `references/workflows.md` — Extended workflow walkthroughs
- `references/examples.md` — Complete code examples
- `references/decision-tree.md` — Full UI component decision tree
- `references/anti-patterns.md` — Expanded anti-patterns with code examples

## See Also

- `frappe-impl-clientscripts` — Form-level client scripts
- `frappe-syntax-clientscripts` — Client-side API syntax reference
- `frappe-impl-hooks` — Hook registration for pages and routes
---
name: frappe-impl-website
description: >
  Use when building portal pages, Web Forms, website routes, or configuring themes and SEO in Frappe.
  Prevents 404 errors from wrong route resolution, broken Web Form submissions, and missing meta tags for SEO.
  Covers Web Page, Web Form, Portal Settings, Website Settings, website routes, Jinja templates, Blog, Web Template, has_web_view, meta tags, sitemap.
  Keywords: website, portal, Web Form, Web Page, route, theme, SEO, meta tags, has_web_view, Blog, Web Template, sitemap, customer portal, self-service, public form, web page, website not showing, 404 on portal..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Website & Portals — Implementation Workflows

Step-by-step workflows for building websites, portals, and public-facing pages. For hooks syntax see `frappe-impl-hooks`. For Jinja templating see `frappe-impl-jinja`.

**Version**: v14/v15/v16 | **Note**: v15+ uses Bootstrap 5; v14 uses Bootstrap 4.

## Quick Decision: Which Page Type?

```
WHAT do you need?
├── Static content page (About, Terms)     → Web Page DocType or www/ HTML
├── Data entry by external users           → Web Form
├── List of records visible on website     → has_web_view on DocType
├── Blog / news articles                   → Blog Post + Blog Category
├── Custom app with sidebar/toolbar        → Custom Portal Page (www/)
└── Dynamic route with parameters          → website_route_rules in hooks.py
```

See `references/decision-tree.md` for the complete decision tree.

## Workflow 1: Create a Portal Page (www/)

Portal pages live in your app's `www/` directory. The file name becomes the URL route.

1. Create `myapp/www/custom_page.html`:

```html
{% extends "templates/web.html" %}
{% block page_content %}
<h1>{{ title }}</h1>
<div>{{ content }}</div>
{% endblock %}
```

2. Create matching controller `myapp/www/custom_page.py`:

```python
import frappe

def get_context(context):
    context.title = "My Custom Page"
    context.content = "Hello World"
    context.no_cache = 1  # ALWAYS set for dynamic content
```

3. Result: page available at `/custom_page`

**File types auto-loaded**: `.html` (template), `.py` (controller), `.css` (styles), `.js` (scripts).

**Subdirectory pattern** — for nested routes:
```
myapp/www/
├── services/
│   ├── index.html        → /services
│   ├── index.py
│   ├── consulting.html   → /services/consulting
│   └── consulting.py
```

### Context Variables Reference

| Key | Type | Effect |
|-----|------|--------|
| `title` | str | Page title and browser tab |
| `no_cache` | bool | Disable page caching |
| `no_header` | bool | Hide the page header |
| `no_breadcrumbs` | bool | Remove breadcrumbs |
| `add_breadcrumbs` | bool | Auto-generate from folder structure |
| `show_sidebar` | bool | Display web sidebar |
| `sitemap` | int | 0 = exclude from sitemap, 1 = include |
| `metatags` | dict | SEO meta tags (see Workflow 7) |

**Rule**: ALWAYS set `no_cache = 1` for pages with user-specific or frequently changing content.

## Workflow 2: Create a Web Form

Web Forms let external users submit data that creates Frappe documents.

1. Navigate to **Web Form** list → **New Web Form**
2. Set **Title**, select target **DocType**, set **Route** (URL slug)
3. Add fields — ALWAYS match `fieldname` to the target DocType field names
4. Configure access:
   - **Login Required**: uncheck for guest submissions
   - **Allow Edit**: let users edit their submissions
   - **Allow Multiple**: let users submit more than once
5. Save and publish

### Guest Submissions

```
ALLOWING guest submissions?
├── YES → Uncheck "Login Required"
│        → Set "Guest Title" for the submission form
│        → ALWAYS add rate limiting in site_config:
│           "rate_limit": {"web_form": "5/hour"}
│        → ALWAYS validate server-side (guests can bypass JS)
└── NO  → Keep "Login Required" checked (default)
```

### Web Form Custom Script (Client)

```javascript
frappe.web_form.on("after_load", function() {
    // Runs after form loads in browser
});

frappe.web_form.on("before_submit", function() {
    // Validate before submission — return false to cancel
    let val = frappe.web_form.get_value("email");
    if (!val) {
        frappe.throw("Email is required");
        return false;
    }
});

frappe.web_form.on("after_submit", function() {
    // Redirect or show message after success
    window.location.href = "/thank-you";
});
```

### Web Form Custom Script (Server: Python)

In the Web Form document, add a Python script:

```python
def get_context(context):
    # Add custom context variables for the template
    context.categories = frappe.get_all("Category", fields=["name", "title"])
```

**Rule**: NEVER trust client-side validation alone for Web Forms. ALWAYS validate in the target DocType's controller or server script.

## Workflow 3: Enable has_web_view on a DocType

This makes individual documents accessible as web pages (e.g., `/articles/my-article`).

1. Open DocType → check **Has Web View** and **Allow Guest to View**
2. Set the **Route** field prefix (e.g., `articles`)
3. ALWAYS add these fields to the DocType:
   - `route` (Data, hidden) — auto-generated URL slug
   - `published` (Check) — controls visibility
4. Create templates in the DocType directory:
   - `{doctype_name}.html` — single record template
   - `{doctype_name}_row.html` — list item template
5. In `hooks.py`, register as website generator:

```python
website_generators = ["Article"]
```

6. In the controller, implement `get_context`:

```python
class Article(WebsiteGenerator):
    website = frappe._dict(
        template="templates/generators/article.html",
        condition_field="published",
        page_title_field="title",
    )

    def get_context(self, context):
        context.related = frappe.get_all(
            "Article",
            filters={"published": 1, "name": ("!=", self.name)},
            fields=["title", "route"],
            limit=5,
        )
```

**Rule**: ALWAYS include a `published` check field. NEVER expose unpublished documents to guests.

## Workflow 4: Website Route Rules (hooks.py)

Route rules map URL patterns to controllers or pages.

```python
# hooks.py
website_route_rules = [
    # Map parameterized URL to a page
    {"from_route": "/projects/<name>", "to_route": "projects/project"},
    # Map URL prefix to DocType
    {"from_route": "/kb/<path:name>", "to_route": "knowledge-base"},
]

# Redirects (301/304)
website_redirects = [
    {"source": "/old-page", "target": "/new-page"},
    {"source": r"/docs(/.*)?", "target": r"https://docs.example.com\1"},
]

# Homepage for logged-in users (role-based)
role_home_page = {
    "Customer": "orders",
    "Supplier": "rfqs",
}

# Dynamic homepage
get_website_user_home_page = "myapp.utils.get_home_page"
```

**Priority order** for homepage: `get_website_user_home_page` > `role_home_page` > Portal Settings > Website Settings.

## Workflow 5: Blog Setup

1. Create **Blog Category** documents (e.g., "News", "Updates")
2. Create **Blog Post** documents:
   - Select category, write content (Markdown or Rich Text)
   - Set **Published** and **Published On** date
   - Blog route auto-generates as `/blog/{slug}`
3. Configure in **Website Settings**:
   - Set blog title
   - Enable/disable comments

**Rule**: ALWAYS set `Published On` date — posts without a date NEVER appear in RSS feeds.

## Workflow 6: Website Theme & Custom CSS

### Via Website Theme DocType

1. Navigate to **Website Theme** → New
2. Configure: fonts, colors, navbar style, button radius
3. Add custom CSS in the **Custom CSS** field
4. Set as active theme in **Website Settings**

### Via hooks.py

```python
# Inject CSS/JS on all web pages
website_context = {
    "favicon": "/assets/myapp/images/favicon.png",
}

update_website_context = "myapp.overrides.website_context"

# Override base template
base_template = "myapp/templates/custom_base.html"
```

## Workflow 7: SEO: Meta Tags, Open Graph & Sitemap

### In portal pages (frontmatter or context)

```python
def get_context(context):
    context.metatags = {
        "title": "My Page Title",
        "description": "Page description for search engines",
        "image": "/assets/myapp/images/og-image.png",
        "og:type": "website",
        "twitter:card": "summary_large_image",
    }
```

### In Web Page DocType

Set meta fields directly: **Meta Title**, **Meta Description**, **Meta Image**.

### Sitemap

- Frappe auto-generates `/sitemap.xml` from published Web Pages and has_web_view documents
- Exclude pages: set `sitemap = 0` in context or frontmatter
- Custom robots.txt: set `robots_txt` path in `site_config.json`

**Rule**: ALWAYS set `meta description` on public pages. NEVER leave it empty — search engines penalize pages without descriptions.

## Workflow 8: Guest Access & Security

```python
# site_config.json — rate limiting
{
    "rate_limit": {
        "web_form": "5/hour",
        "api": "100/hour"
    },
    "allowed_referrers": ["https://mysite.com"],
    "allow_cors": "https://mysite.com"
}
```

**Security rules**:
- ALWAYS enable CSRF protection (default). NEVER set `ignore_csrf` in production
- ALWAYS rate-limit guest-accessible endpoints
- ALWAYS sanitize user input in Web Forms (Frappe does this by default for standard fields)
- NEVER expose internal DocType names in guest-facing URLs without access control

## Anti-Patterns

| Anti-Pattern | Correct Approach |
|---|---|
| Hard-coding HTML in `get_context` | Use Jinja templates with context variables |
| Skipping `no_cache` on dynamic pages | ALWAYS set `no_cache = 1` for user-specific content |
| Guest Web Form without rate limiting | ALWAYS configure rate limits for guest forms |
| Missing `published` field on has_web_view | ALWAYS add published check to prevent data leaks |
| Using `website_route_rules` for simple redirects | Use `website_redirects` instead |
| Putting business logic in www/ controllers | Keep in DocType controllers; www/ is for presentation |

See `references/anti-patterns.md` for expanded anti-patterns with examples.

## See Also

- `frappe-impl-hooks` — Website hooks in detail
- `frappe-impl-jinja` — Jinja templating patterns
- `frappe-impl-controllers` — DocType controllers (WebsiteGenerator)
- `frappe-syntax-clientscripts` — Client-side API for Web Forms
- `references/generators.md` — Portal generators, blog system, custom routing patterns
- `references/workflows.md` — Extended workflow walkthroughs
- `references/examples.md` — Complete code examples
- `references/decision-tree.md` — Full decision tree for page types
---
name: frappe-impl-whitelisted
description: >
  Use when building API endpoints with @frappe.whitelist() in Frappe.
  Covers endpoint design, permission patterns, error handling, client
  integration, file uploads, background jobs, rate limiting, REST API
  testing, and migration from Server Scripts to whitelisted methods.
  Prevents permission bypasses, SQL injection, and data exposure.
  Keywords: how to create API, build REST endpoint, frappe.call,, create API endpoint, call from frontend, custom API, REST endpoint, how to call python from JS.
  frappe.whitelist, API permission, guest API, secure endpoint,
  rate limiting, curl testing, frm.call.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Whitelisted Methods Implementation Workflow

Step-by-step workflows for building API endpoints. For decorator syntax, see `frappe-syntax-whitelisted`.

**Version**: v14/v15/v16 (version-specific features noted)

---

## Master Decision: What Type of Endpoint?

```
WHAT ARE YOU BUILDING?
│
├─► Public API (no login required)?
│   └─► allow_guest=True + STRICT input validation + rate limiting
│
├─► Authenticated API for logged-in users?
│   └─► Default @frappe.whitelist() + document permission checks
│
├─► Admin-only API?
│   └─► frappe.only_for("System Manager")
│
├─► Document-specific method (called from form)?
│   └─► Controller method + frm.call() from JS
│
├─► Standalone utility API?
│   └─► Separate api.py + frappe.call() from JS
│
├─► External webhook receiver?
│   └─► allow_guest=True + signature verification
│
└─► Background job trigger?
    └─► Authenticated API that calls frappe.enqueue()
```

---

## Workflow 1: Design the Endpoint

### Step 1: Choose Location

```
WHERE SHOULD THE CODE LIVE?
│
├─► Related to a DocType, called from its form?
│   └─► doctype/xxx/xxx.py (controller method)
│       Client: frm.call('method_name', args)
│
├─► Related to a DocType, standalone?
│   └─► doctype/xxx/xxx_api.py or myapp/api/module.py
│       Client: frappe.call('myapp.api.module.method')
│
├─► General app utility?
│   └─► myapp/api.py (small app) or myapp/api/module.py (large app)
│
└─► External integration?
    └─► myapp/integrations/service_name.py
```

### Step 2: Choose Permission Model

```
WHO CAN CALL THIS API?
│
├─► Anyone (public) → allow_guest=True
│   ⚠️ MUST validate ALL input, sanitize for XSS, rate limit
│
├─► Any logged-in user → Default (no allow_guest)
│   Still check document permissions per record!
│
├─► Specific role(s) → frappe.only_for("Role")
│
└─► Document-level → frappe.has_permission(doctype, ptype, doc)
```

### Step 3: Choose HTTP Method

```
WHAT DOES THE API DO?
│
├─► Read-only → methods=["GET"]
├─► Creates/modifies data → methods=["POST"]
└─► Both or default → omit methods parameter (all allowed)
```

---

## Workflow 2: Implement an Authenticated API

### Step-by-Step

**Step 1: Create the function**

```python
# myapp/api.py
import frappe
from frappe import _

@frappe.whitelist()
def get_customer_balance(customer):
    """Get outstanding balance for a customer."""
    # 1. Permission check
    if not frappe.has_permission("Customer", "read", customer):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    # 2. Validate input
    if not customer or not frappe.db.exists("Customer", customer):
        frappe.throw(_("Customer not found"), frappe.DoesNotExistError)

    # 3. Fetch and return
    balance = frappe.db.sql("""
        SELECT COALESCE(SUM(outstanding_amount), 0)
        FROM `tabSales Invoice`
        WHERE customer = %s AND docstatus = 1
    """, customer)[0][0]

    return {"customer": customer, "balance": balance}
```

**Step 2: Call from Client Script**

```javascript
frappe.call({
    method: 'myapp.api.get_customer_balance',
    args: { customer: 'CUST-00001' },
    callback(r) {
        if (r.message) console.log(r.message.balance);
    }
});
```

**Step 3: Test with curl**

```bash
# Authenticate first
curl -X POST https://site.com/api/method/login \
  -d 'usr=admin&pwd=password'

# Call the API
curl -X POST https://site.com/api/method/myapp.api.get_customer_balance \
  -H "Content-Type: application/json" \
  -d '{"customer": "CUST-00001"}' \
  --cookie cookies.txt

# Or use token auth
curl -X POST https://site.com/api/method/myapp.api.get_customer_balance \
  -H "Authorization: token api_key:api_secret" \
  -H "Content-Type: application/json" \
  -d '{"customer": "CUST-00001"}'
```

---

## Workflow 3: Implement a Public (Guest) API

### Step-by-Step

**Step 1: Create with strict validation**

```python
@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_inquiry(name, email, phone=None, message=None):
    """Public contact form — strict validation required."""
    # 1. Validate required fields
    if not all([name, email]):
        frappe.throw(_("Name and email are required"))

    # 2. Validate email format
    if not frappe.utils.validate_email_address(email):
        frappe.throw(_("Invalid email address"))

    # 3. Sanitize ALL input
    name = frappe.utils.strip_html(name)[:100]
    email = email.strip().lower()[:200]
    phone = frappe.utils.strip_html(phone)[:20] if phone else None
    message = frappe.utils.strip_html(message)[:2000] if message else None

    # 4. Create record with ignore_permissions
    lead = frappe.get_doc({
        "doctype": "Lead",
        "lead_name": name, "email_id": email,
        "phone": phone, "notes": message, "source": "Website"
    })
    lead.insert(ignore_permissions=True)

    return {"success": True, "message": _("Thank you")}
```

**Step 2: Add rate limiting (v15+)**

```python
from frappe.rate_limiter import rate_limit

@frappe.whitelist(allow_guest=True, methods=["POST"])
@rate_limit(limit=5, seconds=60)  # 5 calls per minute
def submit_inquiry(name, email, phone=None, message=None):
    ...
```

### Critical Rules for Guest APIs

- **ALWAYS** validate and sanitize every input parameter
- **ALWAYS** use `methods=["POST"]` for data-writing endpoints
- **ALWAYS** add rate limiting (v15+ decorator or manual cache-based throttle on v14)
- **NEVER** expose internal error details — log with `frappe.log_error()`, show generic message
- **NEVER** return sensitive data (internal IDs, file paths, stack traces)
- **NEVER** pass raw user input to `frappe.get_doc()` — use explicit field mapping

---

## Workflow 4: Implement a Controller Method

### Step-by-Step

**Step 1: Add method to DocType controller**

```python
# myapp/doctype/sales_order/sales_order.py
class SalesOrder(Document):
    @frappe.whitelist()
    def calculate_shipping(self, carrier):
        """Called from form via frm.call()."""
        if not self.shipping_address:
            frappe.throw(_("Shipping address required"))
        rate = get_shipping_rate(self.shipping_address, carrier)
        return {"carrier": carrier, "rate": rate}
```

**Step 2: Call from form JS**

```javascript
frm.call('calculate_shipping', {
    carrier: 'FedEx'
}).then(r => {
    frm.set_value('shipping_amount', r.message.rate);
});
```

**Key difference**: Frappe automatically checks document permissions for controller methods called via `frm.call()`. No manual permission check needed for the document itself.

---

## Workflow 5: Implement Error Handling

### Standard Pattern

```python
@frappe.whitelist()
def process_payment(invoice, amount):
    try:
        # Validate
        if not invoice:
            frappe.throw(_("Invoice required"), frappe.ValidationError)
        if not frappe.has_permission("Sales Invoice", "write", invoice):
            frappe.throw(_("Not permitted"), frappe.PermissionError)

        # Process
        result = do_payment(invoice, float(amount))
        return {"success": True, "data": result}

    except (frappe.ValidationError, frappe.PermissionError):
        raise  # Let Frappe handle (417 / 403)
    except frappe.DoesNotExistError:
        frappe.throw(_("Not found"), frappe.DoesNotExistError)  # 404
    except Exception:
        frappe.log_error(frappe.get_traceback(), "Payment Error")
        frappe.local.response["http_status_code"] = 500
        return {"success": False, "error": _("Internal error")}
```

### HTTP Status Code Reference

| Code | Frappe Exception | When |
|------|-----------------|------|
| 200 | — | Success |
| 403 | PermissionError | Access denied |
| 404 | DoesNotExistError | Not found |
| 409 | DuplicateEntryError | Duplicate |
| 417 | ValidationError | Validation failed |
| 429 | — | Rate limit exceeded (v15+) |
| 500 | Exception | Server error |

---

## Workflow 6: File Upload Endpoint

```python
@frappe.whitelist()
def upload_attachment(doctype, docname):
    """Handle file upload attached to a document."""
    if not frappe.has_permission(doctype, "write", docname):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    file = frappe.request.files.get('file')
    if not file:
        frappe.throw(_("No file provided"))

    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_name": file.filename,
        "attached_to_doctype": doctype,
        "attached_to_name": docname,
        "content": file.read(),
        "is_private": 1
    })
    file_doc.insert(ignore_permissions=True)
    return {"file_url": file_doc.file_url}
```

---

## Workflow 7: Background Job Endpoint

```python
@frappe.whitelist()
def start_heavy_export(doctype, filters=None):
    """Trigger a background job — returns immediately."""
    frappe.only_for("System Manager")

    frappe.enqueue(
        "myapp.tasks.export_data",
        queue="long",
        timeout=1500,
        doctype=doctype,
        filters=filters,
        user=frappe.session.user
    )
    return {"status": "queued", "message": _("Export started")}
```

---

## Client Integration Patterns

### frappe.call() with Options

```javascript
frappe.call({
    method: 'myapp.api.my_method',
    args: { param: 'value' },
    freeze: true,
    freeze_message: __('Processing...'),
    callback(r) { console.log(r.message); },
    error(r) { frappe.msgprint(__('Error')); }
});
```

### Async/Await Pattern

```javascript
const r = await frappe.call({
    method: 'myapp.api.get_data',
    args: { id: 123 }
});
console.log(r.message);
```

### REST API from External System

```bash
# Token auth (recommended for integrations)
curl -H "Authorization: token api_key:api_secret" \
  https://site.com/api/method/myapp.api.method

# Bearer auth (OAuth)
curl -H "Authorization: Bearer access_token" \
  https://site.com/api/method/myapp.api.method
```

---

## Security Rules (ALWAYS/NEVER)

1. **ALWAYS** check permissions before accessing any document
2. **ALWAYS** use parameterized queries — **NEVER** use f-strings in SQL
3. **ALWAYS** validate and sanitize input for guest APIs
4. **ALWAYS** check role with `frappe.only_for()` before using `ignore_permissions=True`
5. **NEVER** expose internal errors — log details, return generic message
6. **NEVER** use `methods=["GET"]` for endpoints that modify data
7. **NEVER** trust `data` dicts from guest APIs — use explicit parameter names
8. **ALWAYS** include `X-Frappe-CSRF-Token` header in fetch() calls from browser

---

## Migration: Server Script API to Whitelisted Method

| Step | Action |
|------|--------|
| 1 | Copy Server Script logic to `myapp/api/module.py` |
| 2 | Add `@frappe.whitelist()` decorator with same permission model |
| 3 | Update all `frappe.call()` references to new dotted path |
| 4 | Disable or delete the Server Script |
| 5 | Run `bench --site sitename migrate` |

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---------|:---:|:---:|:---:|
| @frappe.whitelist() | Yes | Yes | Yes |
| allow_guest | Yes | Yes | Yes |
| methods parameter | Yes | Yes | Yes |
| Type annotation validation | No | **Yes** | Yes |
| @rate_limit decorator | No | **Yes** | Yes |
| API v2 endpoints | No | **Yes** | Yes |

### v15+ Type Validation

```python
@frappe.whitelist()
def typed_api(customer: str, limit: int = 10) -> dict:
    """v15+ validates types from annotations automatically."""
    return {"customer": customer, "limit": limit}
```

---

## Reference Files

| File | Contents |
|------|----------|
| [decision-tree.md](references/decision-tree.md) | Complete API type and permission selection guide |
| [workflows.md](references/workflows.md) | Step-by-step implementation patterns (10+ workflows) |
| [examples.md](references/examples.md) | Production-ready code examples |
---
name: frappe-impl-workflow
description: >
  Use when implementing document Workflows, approval chains, or state-based transitions in Frappe.
  Prevents stuck documents from missing transitions, broken approval chains, and permission errors on workflow actions.
  Covers Workflow DocType, Workflow State, Workflow Action, transition rules, allowed roles, conditions, workflow_state field, apply_workflow.
  Keywords: workflow, approval, transition, Workflow State, Workflow Action, state machine, approval chain, workflow_state, approval chain, document approval, multi-step approval, workflow stuck, status transitions..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Workflow Implementation

Step-by-step guide for implementing document workflows in Frappe. Covers design, setup, testing, and common approval chain patterns.

## Quick Reference: Implementation Checklist

```
1. □ Design states and transitions on paper/diagram first
2. □ Create Workflow State records (master list)
3. □ Create Workflow Action Master records (Approve, Reject, etc.)
4. □ Create the Workflow DocType record
5. □ Add states with correct doc_status values
6. □ Add transitions with roles, actions, and conditions
7. □ Set allow_edit roles per state
8. □ Configure email notifications (optional)
9. □ Test every transition path with test users
10. □ Verify self-approval blocking works as expected
```

## Step 1: Design Your Workflow

Before touching the UI, map out your workflow on paper.

### Identify States

**ALWAYS** start by listing every distinct document stage:

```
Example — Purchase Order Approval:
  Draft → Pending Review → Pending Approval → Approved → Submitted → Cancelled
```

### Map DocStatus to States

For submittable DocTypes, ALWAYS assign `doc_status` correctly:

| Stage | doc_status | Meaning |
|-------|:-:|---------|
| All "in-progress" states | 0 | Document is Draft, editable |
| Final approved/active state | 1 | Document is Submitted, locked |
| Cancelled state | 2 | Document is Cancelled |

**NEVER** assign `doc_status = 1` to intermediate approval states. A submitted document cannot return to draft. Once submitted, the only forward path is another submitted state or cancellation.

### Map Transitions

For each state, define: What actions are possible? Who can perform them? Any conditions?

```
Draft         →[Submit for Review / Creator]→     Pending Review
Pending Review →[Approve / Reviewer]→              Pending Approval
Pending Review →[Reject / Reviewer]→               Draft
Pending Approval →[Approve / Manager]→             Approved
Pending Approval →[Reject / Manager]→              Draft
Approved      →[Submit / Manager]→                 Submitted (doc_status=1)
Submitted     →[Cancel / Manager]→                 Cancelled (doc_status=2)
```

## Step 2: Create Prerequisite Records

### 2a. Create Workflow States

Navigate to **Workflow State** list or create via API:

```python
# Create states with appropriate styles
states = [
    {"workflow_state_name": "Draft", "style": ""},
    {"workflow_state_name": "Pending Review", "style": "Primary"},
    {"workflow_state_name": "Pending Approval", "style": "Warning"},
    {"workflow_state_name": "Approved", "style": "Success"},
    {"workflow_state_name": "Submitted", "style": "Info"},
    {"workflow_state_name": "Rejected", "style": "Danger"},
    {"workflow_state_name": "Cancelled", "style": "Inverse"},
]
for s in states:
    if not frappe.db.exists("Workflow State", s["workflow_state_name"]):
        frappe.get_doc({"doctype": "Workflow State", **s}).insert()
```

Available styles: `Primary`, `Success`, `Warning`, `Danger`, `Info`, `Inverse` (or empty for default).

### 2b. Create Workflow Action Masters

```python
actions = ["Submit for Review", "Approve", "Reject", "Send Back", "Cancel"]
for action in actions:
    if not frappe.db.exists("Workflow Action Master", action):
        frappe.get_doc({
            "doctype": "Workflow Action Master",
            "workflow_action_name": action
        }).insert()
```

## Step 3: Create the Workflow

### Via UI

Navigate to **Setup > Workflow > New Workflow**:

1. Set **Workflow Name** (e.g., "Purchase Order Approval")
2. Set **Document Type** (e.g., "Purchase Order")
3. Check **Is Active**
4. Add states in the **States** table
5. Add transitions in the **Transitions** table

### Via Python

```python
workflow = frappe.get_doc({
    "doctype": "Workflow",
    "workflow_name": "Purchase Order Approval",
    "document_type": "Purchase Order",
    "is_active": 1,
    "send_email_alert": 1,
    "states": [
        {"state": "Draft", "doc_status": "0", "allow_edit": "Purchase User"},
        {"state": "Pending Approval", "doc_status": "0", "allow_edit": "Purchase Manager"},
        {"state": "Approved", "doc_status": "1", "allow_edit": "Purchase Manager"},
        {"state": "Rejected", "doc_status": "0", "allow_edit": "Purchase User"},
        {"state": "Cancelled", "doc_status": "2"},
    ],
    "transitions": [
        {
            "state": "Draft",
            "action": "Submit for Review",
            "next_state": "Pending Approval",
            "allowed": "Purchase User",
            "allow_self_approval": 1,
        },
        {
            "state": "Pending Approval",
            "action": "Approve",
            "next_state": "Approved",
            "allowed": "Purchase Manager",
            "allow_self_approval": 0,
        },
        {
            "state": "Pending Approval",
            "action": "Reject",
            "next_state": "Rejected",
            "allowed": "Purchase Manager",
        },
        {
            "state": "Rejected",
            "action": "Submit for Review",
            "next_state": "Pending Approval",
            "allowed": "Purchase User",
        },
        {
            "state": "Approved",
            "action": "Cancel",
            "next_state": "Cancelled",
            "allowed": "Purchase Manager",
        },
    ],
})
workflow.insert()
```

## Step 4: Configure Advanced Features

### Conditional Transitions

Add Python conditions to show transitions only when criteria are met:

```python
# Only allow approval for orders above 50000 by Senior Manager
{
    "state": "Pending Approval",
    "action": "Approve",
    "next_state": "Approved",
    "allowed": "Senior Manager",
    "condition": "doc.grand_total > 50000",
}

# Standard approval for orders up to 50000
{
    "state": "Pending Approval",
    "action": "Approve",
    "next_state": "Approved",
    "allowed": "Purchase Manager",
    "condition": "doc.grand_total <= 50000",
}
```

**ALWAYS** use `doc.fieldname` syntax in conditions (the document is exposed as a dict).

Available in conditions: `frappe.db.get_value()`, `frappe.db.get_list()`, `frappe.session.user`, `frappe.utils.now_datetime()`, `frappe.utils.add_to_date()`, `frappe.utils.get_datetime()`.

### Self-Approval Blocking

Set `allow_self_approval = 0` on approval transitions. This means:
- The document **owner** (creator) CANNOT perform this action
- Administrator is ALWAYS exempt from this restriction
- Other users with the required role CAN perform the action

### Email Notifications

1. Set `send_email_alert = 1` on the Workflow
2. On each state row, set `send_email = 1` (default)
3. Optionally link an `Email Template` via `next_action_email_template`
4. Add a custom `message` on the state row for inline notification text

### Update Fields on State Change

Use `update_field` and `update_value` on state rows to automatically set document fields:

```python
# Set approval_status when entering "Approved" state
{"state": "Approved", "doc_status": "1",
 "update_field": "approval_status", "update_value": "Approved"}

# Use expression to set approval date dynamically
{"state": "Approved", "doc_status": "1",
 "update_field": "custom_approved_on", "update_value": "frappe.utils.now()",
 "evaluate_as_expression": 1}
```

## Step 5: Test Your Workflow

### Manual Testing Checklist

1. **Create a test document** — verify it starts in the first state (Draft)
2. **Check available actions** — only roles with transitions from Draft should see buttons
3. **Perform each transition** — verify state changes correctly
4. **Test rejection paths** — verify documents return to correct state
5. **Test self-approval** — log in as document owner, verify blocked transitions
6. **Test conditions** — create documents that meet/fail conditions, verify button visibility
7. **Test email notifications** — verify emails sent on state changes
8. **Test with non-submittable DocType** — verify all doc_status = 0

### Programmatic Testing

```python
# Get available transitions for a document
from frappe.model.workflow import get_transitions, apply_workflow

doc = frappe.get_doc("Purchase Order", "PO-00001")
transitions = get_transitions(doc)
# Returns list of dicts with action, next_state, allowed, etc.

# Apply a workflow action
updated_doc = apply_workflow(doc, "Approve")
# Returns the updated document after state change
```

## Common Workflow Patterns

### Pattern 1: Sequential Approval Chain

```
Draft → Level 1 Review → Level 2 Review → Approved → Submitted
```

Each level has its own role. Document moves linearly through approvals.

### Pattern 2: Conditional Routing by Amount

```
Draft → Pending Approval
  ├─[amount <= 10000 / Team Lead]─→ Approved
  ├─[amount <= 50000 / Manager]──→ Approved
  └─[amount > 50000 / Director]──→ Approved
```

Use `condition` on each transition to route based on document values.

### Pattern 3: Review with Rejection Loop

```
Draft ←──[Reject]── Pending Review ──[Approve]──→ Approved
  └──[Submit for Review]──→ Pending Review
```

Rejected documents return to Draft for revision. Creator resubmits. This is the most common approval pattern.

### Pattern 4: Leave Approval

```
Applied (doc_status=0, allow_edit=Employee)
  └─[Approve / Leave Approver]─→ Approved (doc_status=1)
  └─[Reject / Leave Approver]─→ Rejected (doc_status=0)
Approved
  └─[Cancel / HR Manager]─→ Cancelled (doc_status=2)
```

### Pattern 5: Document Review (Non-Submittable)

For non-submittable DocTypes, ALL states MUST have `doc_status = 0`:

```
Draft → Under Review → Reviewed → Published
(all doc_status = 0)
```

## Migrating from Manual DocStatus to Workflow

If your DocType currently uses manual Submit/Cancel buttons and you want to add a workflow:

1. **Map existing documents** — The workflow engine auto-maps existing documents to states based on their `docstatus` when the workflow is created
2. **Define a state for each docstatus** — ALWAYS have at least one state per docstatus value your documents currently use
3. **Test with existing data** — Verify that existing submitted documents show the correct workflow state
4. **Update list views** — If using `override_status`, the workflow state replaces the Status column

**NEVER** activate a workflow without a state for docstatus=0. New documents would have no valid initial state.

## Decision Tree

```
Starting a new workflow implementation?
│
├── What type of DocType?
│   ├── Submittable → can use doc_status 0, 1, 2
│   └── Non-submittable → ALL states must be doc_status = 0
│
├── How many approval levels?
│   ├── Single → Two-state: Draft → Approved
│   ├── Sequential → Chain: Draft → L1 → L2 → Approved
│   └── Conditional → Route by field values using conditions
│
├── Need self-approval blocking?
│   └── Set allow_self_approval = 0 on approval transitions
│
├── Need rejection/revision loop?
│   └── Add Reject transition back to Draft or previous state
│
├── Need email notifications?
│   ├── Enable send_email_alert on Workflow
│   └── Link Email Template on each state
│
└── Need automated field updates?
    └── Use update_field + update_value on target state
```

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| No action buttons visible | User lacks required role | Add role to user OR add transition for user's role |
| "Self approval is not allowed" | User is doc owner + `allow_self_approval=0` | Have different user approve, or set flag to 1 |
| "Workflow State not set" | Document created before workflow activation | Run `update_default_workflow_status` or manually set state |
| Document stuck in state | No outgoing transition defined for current state + user role | Add missing transition |
| "Cannot cancel before submitting" | Transition goes from doc_status=0 to doc_status=2 | Add intermediate submitted state |
| Actions show for wrong users | Role assignment too broad | Use more specific roles or add conditions |

## See Also

- [Workflow Patterns](references/workflows.md) — Detailed step-by-step workflow examples
- [Decision Tree](references/decision-tree.md) — Extended decision tree for workflow design
- [Examples](references/examples.md) — Code examples for common scenarios
- [Anti-Patterns](references/anti-patterns.md) — Mistakes to avoid
- `frappe-core-workflow` — Workflow engine internals and API reference
---
name: frappe-impl-workspace
description: >
  Use when creating or customizing Workspace pages in Frappe v14-v16.
  Covers Workspace DocType structure, shortcuts, number cards, dashboard
  charts, custom HTML blocks, JSON content format, shipping workspaces
  with custom apps, and role-based access control.
  Prevents common mistakes with content/child-table desync and missing fixtures.
  Keywords: workspace, desk, dashboard, number card, chart, shortcut,, customize desk, dashboard setup, add shortcut, module page, sidebar customize.
  workspace builder, module, fixtures, sidebar.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "3.0"
---

# Frappe Workspace Implementation Workflow

Step-by-step workflows for creating and customizing Workspace pages. Workspaces are the block-based dashboard/navigation pages in Frappe Desk.

**Version**: v14/v15/v16 (version-specific features noted)

---

## Quick Reference

| Concept | Description |
|---------|-------------|
| Workspace | Block-based page with 12-column grid layout |
| Public Workspace | Visible to all permitted users; requires Workspace Manager role to edit |
| Private Workspace | Per-user dashboard under "My Workspaces"; any Desk User can create |
| Content field | JSON array storing the block layout |
| Child tables | 6 tables: charts, shortcuts, links, quick_lists, number_cards, custom_blocks |
| Module association | Primary access control mechanism |

---

## Master Decision: What Do You Need?

```
NEED A WORKSPACE?
│
├─► Default DocType landing page?
│   └─► NO workspace needed — Frappe auto-generates list views
│
├─► Custom dashboard for a module?
│   └─► Create PUBLIC Workspace (Workspace Manager role required)
│
├─► Personal dashboard for a user?
│   └─► Create PRIVATE Workspace (appears under "My Workspaces")
│
└─► Navigation link in sidebar?
    └─► type="Link" (internal) or type="URL" (external)

ADDING COMPONENTS?
│
├─► Key metrics (counts, sums) → Number Cards
├─► Trend / time-series data  → Dashboard Charts
├─► Quick navigation links    → Shortcuts
├─► Grouped link categories   → Link Cards (Card Break + Links)
├─► Custom HTML/JS content    → Custom HTML Blocks
└─► Recent record lists       → Quick Lists
```

---

## Workspace DocType Structure

### Key Fields

| Field | Type | Purpose |
|-------|------|---------|
| `label` | Data | Display name in sidebar |
| `title` | Data | Page title (defaults to label) |
| `module` | Link → Module Def | Associates workspace with a module for access control |
| `parent_page` | Link → Workspace | Nesting under another workspace in sidebar |
| `icon` | Data | Sidebar icon (e.g., `"chart-line"`) |
| `type` | Select | `Workspace` / `Link` / `URL` (v15+) |
| `sequence_id` | Int | Sidebar ordering |
| `content` | JSON | Block layout as JSON array |
| `for_user` | Data | If set, workspace is private to that user |
| `roles` | Table → Has Role | Role-based access restrictions |
| `app` | Data | Owning app identifier (v15+) |
| `indicator_color` | Color | Sidebar indicator dot (v15+) |

### Child Tables (6 total)

| Child Table | DocType | Purpose |
|-------------|---------|---------|
| `charts` | Workspace Chart | Dashboard Chart references |
| `shortcuts` | Workspace Shortcut | DocType/Report/Page/URL shortcuts |
| `links` | Workspace Link | Grouped navigation links |
| `quick_lists` | Workspace Quick List | Recent record lists |
| `number_cards` | Workspace Number Card | Metric card references |
| `custom_blocks` | Workspace Custom Block | HTML block references |

> **CRITICAL**: The `content` JSON and the child tables MUST stay in sync. ALWAYS use the Workspace Builder UI or programmatic API — NEVER manually edit the `content` JSON without updating child tables. See `references/anti-patterns.md`.

---

## Content JSON Format

The `content` field is a JSON array. Each element represents a block in the 12-column grid:

```json
[
  {
    "id": "unique-block-id",
    "type": "header",
    "data": {"text": "Overview", "level": 4, "col": 12}
  },
  {
    "id": "unique-block-id-2",
    "type": "chart",
    "data": {
      "chart_name": "Sales Trends",
      "col": 12
    }
  },
  {
    "id": "unique-block-id-3",
    "type": "number_card",
    "data": {
      "number_card_name": "Open Orders",
      "col": 4
    }
  },
  {
    "id": "unique-block-id-4",
    "type": "shortcut",
    "data": {
      "shortcut_name": "New Sales Order",
      "col": 4
    }
  },
  {
    "id": "unique-block-id-5",
    "type": "spacer",
    "data": {"col": 12}
  }
]
```

### Block Types

| Type | `data` fields | Description |
|------|---------------|-------------|
| `header` | `text`, `level`, `col` | Section heading (h3/h4/h5) |
| `chart` | `chart_name`, `col` | References a Dashboard Chart doc |
| `number_card` | `number_card_name`, `col` | References a Number Card doc |
| `shortcut` | `shortcut_name`, `col` | References a Workspace Shortcut child |
| `card` | `card_name`, `col` | Card break for grouped links |
| `quick_list` | `quick_list_name`, `col` | Recent records for a DocType |
| `custom_block` | `custom_block_name`, `col` | References a Custom HTML Block doc |
| `text` | `body`, `col` | Rich text / Markdown block |
| `spacer` | `col` | Empty vertical space |
| `onboarding` | `onboarding_name`, `col` | Module onboarding widget |

> `col` values MUST be 1-12 and represent grid column width. Blocks in the same row MUST sum to ≤ 12.

---

## Implementation Workflows

### Workflow 1: Create a Public Workspace via UI

1. Navigate to `/app/workspace` → click **+ New Workspace**
2. Set **Label** (appears in sidebar), **Module**, **Icon**
3. Use the Workspace Builder to drag-and-drop blocks
4. Add components: Charts, Number Cards, Shortcuts, Links
5. Click **Save** → workspace appears in sidebar for permitted users
6. In developer mode: JSON auto-exports to your app directory

### Workflow 2: Create a Workspace Programmatically

```python
import frappe
import json

workspace = frappe.new_doc("Workspace")
workspace.label = "Project Dashboard"
workspace.module = "Projects"
workspace.icon = "project"
workspace.type = "Workspace"
workspace.sequence_id = 10

# Build content blocks
workspace.content = json.dumps([
    {
        "id": frappe.generate_hash(length=10),
        "type": "header",
        "data": {"text": "Project Overview", "level": 4, "col": 12}
    },
    {
        "id": frappe.generate_hash(length=10),
        "type": "number_card",
        "data": {"number_card_name": "Active Projects", "col": 4}
    },
    {
        "id": frappe.generate_hash(length=10),
        "type": "chart",
        "data": {"chart_name": "Project Status", "col": 12}
    }
])

# Add child table entries (MUST match content JSON)
workspace.append("number_cards", {
    "number_card_name": "Active Projects"
})
workspace.append("charts", {
    "chart_name": "Project Status"
})

# Role restrictions (optional)
workspace.append("roles", {"role": "Projects Manager"})

workspace.insert(ignore_permissions=True)
frappe.db.commit()
```

> **ALWAYS** add corresponding child-table rows when setting `content` JSON programmatically.

### Workflow 3: Create Supporting Documents First

Before adding components to a workspace, create the referenced documents:

**Number Card:**
```python
card = frappe.new_doc("Number Card")
card.label = "Active Projects"
card.document_type = "Project"
card.function = "Count"
card.filters_json = json.dumps([["Project", "status", "=", "Open"]])
card.is_public = 1
card.insert(ignore_permissions=True)
```

**Dashboard Chart:**
```python
chart = frappe.new_doc("Dashboard Chart")
chart.chart_name = "Project Status"
chart.chart_type = "Group By"
chart.document_type = "Project"
chart.group_by_type = "Count"
chart.group_by_based_on = "status"
chart.type = "Donut"
chart.is_public = 1
chart.insert(ignore_permissions=True)
```

**Shortcut:**
Shortcuts are child-table entries on the Workspace, not standalone docs:
```python
workspace.append("shortcuts", {
    "label": "New Project",
    "type": "DocType",
    "link_to": "Project",
    "color": "Blue",
    "format": "{} Active",
    "stats_filter": json.dumps([["Project", "status", "=", "Open"]])
})
```

See `references/workspace-components.md` for complete component reference.

---

## Permission Model

### Three Layers of Access Control

```
Layer 1: Module Access (PRIMARY)
└─► User must have access to the workspace's module
    └─► Controlled via "Module Def" and user's "Block Modules" list

Layer 2: Role Restrictions (OPTIONAL)
└─► workspace.roles child table
    └─► If populated: ONLY users with listed roles see the workspace
    └─► If empty: ALL users with module access see it

Layer 3: Workspace Manager Role
└─► Required to create/edit PUBLIC workspaces
└─► NOT required for private workspaces
```

### Rules

- ALWAYS set `module` on public workspaces — without it, the workspace is visible to ALL Desk users
- ALWAYS add role restrictions for sensitive dashboards (financial, HR)
- NEVER set `for_user` on workspaces shipped with an app — it creates a private workspace

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| Workspace Builder UI | Basic | Redesigned (drag-drop grid) | Incremental fixes |
| `type` field (Workspace/Link/URL) | Not available | Added | Available |
| `app` field | Not available | Added | Available |
| `indicator_color` | Not available | Added | Available |
| Name collision protection | Manual | Manual | Auto-deduplicate |
| Welcome header config | Not available | Not available | Added |
| Content JSON format | Same | Same | Same |

### Migration Notes

- v14 → v15: Workspace Builder UI changed significantly; existing JSON content remains compatible
- v15 → v16: Minor field additions; no breaking changes to workspace structure
- ALWAYS test workspace rendering after major version upgrades

---

## Shipping Workspaces with a Custom App

### Directory Structure

```
myapp/
└── mymodule/
    └── workspace/
        └── my_workspace/
            └── my_workspace.json
```

### Export Process

1. Enable **Developer Mode** (`frappe.conf.developer_mode = 1`)
2. Create/edit workspace via Workspace Builder UI
3. On save, Frappe auto-exports to the app directory above
4. Commit the JSON file to version control

### CRITICAL: Ship Dependencies Too

A workspace JSON alone is NOT sufficient. You MUST also ship:

| Component | How to Ship |
|-----------|-------------|
| Number Cards | fixtures in hooks.py OR `myapp/fixtures/` |
| Dashboard Charts | fixtures in hooks.py OR `myapp/fixtures/` |
| Custom HTML Blocks | fixtures in hooks.py OR `myapp/fixtures/` |
| Linked Reports | Already shipped via report directory structure |
| Linked Pages | Already shipped via page directory structure |

```python
# hooks.py
fixtures = [
    {"dt": "Number Card", "filters": [["module", "=", "My Module"]]},
    {"dt": "Dashboard Chart", "filters": [["module", "=", "My Module"]]},
    {"dt": "Custom HTML Block", "filters": [["name", "in", ["My Block"]]]},
]
```

See `references/shipping-with-app.md` for complete shipping guide.

---

## Common Patterns

### Pattern 1: Module Dashboard with KPIs

```
[Header: "Key Metrics"]
[Number Card: Open Orders (col=3)] [Number Card: Revenue (col=3)]
[Number Card: Pending (col=3)]     [Number Card: Overdue (col=3)]
[Spacer]
[Header: "Trends"]
[Chart: Monthly Revenue (col=12)]
[Header: "Quick Access"]
[Shortcut: New Order (col=4)] [Shortcut: Reports (col=4)] [Shortcut: Settings (col=4)]
```

### Pattern 2: Role-Based Workspace

```python
# Sales Manager sees full dashboard; Sales User sees limited view
# Option A: Two separate workspaces with different role restrictions
# Option B: One workspace — use Number Card/Chart permissions to filter

# Option A implementation:
ws_manager = frappe.get_doc({"doctype": "Workspace", "label": "Sales Management", ...})
ws_manager.append("roles", {"role": "Sales Manager"})

ws_user = frappe.get_doc({"doctype": "Workspace", "label": "Sales Overview", ...})
ws_user.append("roles", {"role": "Sales User"})
```

### Pattern 3: Sidebar Hierarchy

```python
# Parent workspace
parent = frappe.get_doc({"doctype": "Workspace", "label": "CRM", "module": "CRM"})

# Child workspaces (nested in sidebar)
child = frappe.get_doc({
    "doctype": "Workspace",
    "label": "Lead Pipeline",
    "module": "CRM",
    "parent_page": "CRM"  # References parent workspace label
})
```

---

## Reference Files

| File | Content |
|------|---------|
| `references/workspace-components.md` | Number Cards, Dashboard Charts, Shortcuts, Custom Blocks — full API |
| `references/shipping-with-app.md` | JSON format, fixtures, module structure, install hooks |
| `references/anti-patterns.md` | Common workspace mistakes and how to avoid them |
---
name: frappe-ops-app-lifecycle
description: >
  Use when scaffolding a new Frappe app, configuring app settings, building assets, running tests, deploying, updating, or publishing to marketplace.
  Prevents broken app structure from incorrect scaffolding, missing setup.py fields, and failed builds.
  Covers bench new-app, app directory structure, setup.py/pyproject.toml, hooks.py config, bench build, bench run-tests, app publishing.
  Keywords: app lifecycle, new-app, scaffolding, setup.py, pyproject.toml, hooks.py, bench build, app publishing, marketplace, create app, publish app, app structure, how to start new app, app directory layout..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# App Lifecycle Management

## Quick Reference

| Command | Purpose | When to Use |
|---|---|---|
| `bench new-app` | Scaffold new app | Starting a new project |
| `bench get-app URL` | Clone from Git | Installing existing app |
| `bench --site SITE install-app` | Install on site | After get-app or new-app |
| `bench --site SITE remove-app` | Uninstall from site | Removing app from site |
| `bench remove-app` | Remove from bench | Removing app entirely |
| `bench --site SITE migrate` | Run patches + sync | After code changes |
| `bench build` | Compile assets | After JS/CSS changes |
| `bench --site SITE console` | Python REPL | Debugging |
| `bench start` | Start dev server | Development |
| `bench setup production` | Configure nginx+supervisor | Deploying to production |

## 1. Scaffolding: bench new-app

```bash
bench new-app my_custom_app
```

Interactive prompts:
- App Title → Human-readable name
- App Description → One-line summary
- App Publisher → Company/author name
- App Email → Contact email
- App Icon → Default: `octicon octicon-file-directory`
- App Color → Default: `grey`
- App License → Default: `MIT`

### Generated Directory Structure

```
apps/my_custom_app/
├── MANIFEST.in              # Files included in Python package
├── README.md                # Project readme
├── license.txt              # License file
├── requirements.txt         # Python dependencies
├── dev-requirements.txt     # Dev-only Python deps (v15+)
├── package.json             # Node.js dependencies
├── setup.py                 # Python package config (v14)
├── pyproject.toml           # Python package config (v15+)
├── my_custom_app/
│   ├── __init__.py          # App version string
│   ├── hooks.py             # Framework integration hooks
│   ├── modules.txt          # List of app modules
│   ├── patches.txt          # Migration patches list
│   ├── config/
│   │   ├── __init__.py
│   │   ├── desktop.py       # Desktop/workspace config
│   │   └── docs.py          # Documentation config
│   ├── public/              # Static assets → /assets/my_custom_app/
│   │   ├── css/
│   │   └── js/
│   ├── templates/           # Jinja templates
│   └── www/                 # Portal pages (URL = path)
```

### What Each Core File Does

| File | Purpose | NEVER Forget |
|---|---|---|
| `__init__.py` | Defines `__version__` | ALWAYS update before release |
| `hooks.py` | ALL framework integration | Entry point for everything |
| `modules.txt` | Declares app modules | ALWAYS add new modules here |
| `patches.txt` | Migration patch registry | ALWAYS add patches in order |
| `requirements.txt` | Python deps installed on setup | Add pip packages here |
| `public/` | Static files served by nginx | Accessible at `/assets/app_name/` |
| `www/` | Portal pages | Filename = URL path |

## 2. Development Cycle

```
Code → Migrate → Build → Test → Commit
```

### Step-by-Step

```bash
# 1. Make code changes (DocTypes, reports, APIs, etc.)

# 2. Migrate — sync DocType schema + run patches
bench --site mysite migrate

# 3. Build — compile JS/CSS assets
bench build --app my_custom_app

# 4. Test — run Python tests
bench --site mysite run-tests --app my_custom_app

# 5. Commit
git -C apps/my_custom_app add -A && git -C apps/my_custom_app commit -m "feat: add feature"
```

ALWAYS run `bench migrate` after modifying DocType JSON files.
ALWAYS run `bench build` after modifying JS/CSS files.

## 3. Getting Apps from Git

```bash
# Public repo
bench get-app https://github.com/org/my_app

# Specific branch
bench get-app https://github.com/org/my_app --branch develop

# Private repo via SSH
bench get-app git@github.com:org/private_app.git

# Private repo via token (v15+)
bench get-app https://TOKEN@github.com/org/private_app.git
```

After `get-app`, ALWAYS install on the target site:
```bash
bench --site mysite install-app my_app
```

`get-app` clones to `apps/` and adds to `apps.txt`.
`install-app` creates database tables and runs `after_install` hooks.

## 4. Installing and Removing Apps

### Installation Order Matters
Apps are installed in order listed in `apps.txt`. If App B depends on App A, App A MUST be listed first.

```bash
# Install
bench --site mysite install-app my_app

# Verify
bench --site mysite list-apps
# Output: frappe, erpnext, my_app

# Remove from site (keeps code in apps/)
bench --site mysite remove-app my_app

# Remove from bench entirely (deletes code)
bench remove-app my_app
```

### App Dependencies (v14+)
Declare in `hooks.py`:
```python
required_apps = ["frappe", "erpnext"]
```

Frappe ALWAYS checks `required_apps` during installation and blocks if dependencies are missing.

## 5. Debugging with bench console

```bash
bench --site mysite console
```

Opens an IPython REPL with Frappe context:

```python
# Query data
frappe.db.sql("SELECT name, status FROM `tabSales Invoice` LIMIT 5", as_dict=True)

# Get a document
doc = frappe.get_doc("Sales Invoice", "SINV-00001")
print(doc.grand_total)

# Test a whitelisted method
from my_app.api import my_function
result = my_function(param="value")

# Check configuration
frappe.get_site_config()

# Auto-reload on code changes (v15+)
# Start with: bench --site mysite console --autoreload
```

ALWAYS use `bench console` for debugging — NEVER modify production data with raw SQL.

## 6. Development Mode vs Production Mode

### Development Mode
```bash
# Enable
bench set-config -g developer_mode 1

# Start dev server (Procfile: web + worker + redis + socketio)
bench start
```

Development mode enables:
- DocType editing in Desk
- "Is Standard" option for reports/scripts
- Auto-reload on Python file changes
- Detailed error tracebacks in browser
- `dev-requirements.txt` dependencies installed

### Production Mode
```bash
# Disable developer mode
bench set-config -g developer_mode 0

# Setup production (nginx + supervisor)
sudo bench setup production USERNAME

# Restart
sudo supervisorctl restart all
# or
sudo systemctl restart supervisor
```

Production mode:
- Serves via nginx (port 80/443)
- Background workers via supervisor
- Static files served directly by nginx
- Errors logged to files, not browser
- NEVER enable `developer_mode` on production sites

## 7. Asset Building

### v15+ (esbuild)
```bash
# Build all apps
bench build

# Build specific app
bench build --app my_custom_app

# Watch mode (auto-rebuild on changes)
bench watch
```

### v14 (build.json)
v14 uses `build.json` in the app root to map source files to bundles:
```json
{
    "css/my_app.css": [
        "public/css/style.css"
    ],
    "js/my_app.js": [
        "public/js/main.js"
    ]
}
```

### Asset Include in hooks.py
```python
# Desk (backend UI)
app_include_js = "my_app.bundle.js"      # v15+ bundle syntax
app_include_css = "my_app.bundle.css"

# Portal (website)
web_include_js = "my_app_web.bundle.js"
web_include_css = "my_app_web.bundle.css"

# v14 legacy syntax
app_include_js = "/assets/my_app/js/my_app.js"
app_include_css = "/assets/my_app/css/my_app.css"
```

ALWAYS run `bench build` after changing JS/CSS files.
ALWAYS run `bench clear-cache` if assets are not updating.

## 8. App Versioning

### Version String in __init__.py
```python
# my_custom_app/__init__.py
__version__ = "1.2.0"
```

ALWAYS use semantic versioning: `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

The version is read by `bench version`, displayed in Desk, and used by the Marketplace.

### Checking Versions
```bash
bench version
# frappe 15.23.0
# erpnext 15.18.0
# my_custom_app 1.2.0
```

## 9. Patches: Data Migrations

### Writing a Patch

```python
# my_app/patches/v1_2/update_customer_status.py
import frappe

def execute():
    frappe.reload_doc("module_name", "doctype", "customer_extension")

    frappe.db.sql("""
        UPDATE `tabCustomer Extension`
        SET status = 'Active'
        WHERE status IS NULL
    """)
    frappe.db.commit()
```

### Registering in patches.txt

```
# patches.txt — v14+ supports sections

[pre_model_sync]
my_app.patches.v1_1.fix_old_data
my_app.patches.v1_2.rename_field_before_schema

[post_model_sync]
my_app.patches.v1_2.update_customer_status
my_app.patches.v1_2.migrate_settings
```

**Section timing** (v14+):
- `[pre_model_sync]` — Runs BEFORE DocType schema changes are applied
- `[post_model_sync]` — Runs AFTER schema changes (new fields available)
- No section header — Runs in `[pre_model_sync]` by default

### Patch Rules
- ALWAYS add new patches at the END of their section
- Patches run ONCE — tracked in `tabPatch Log`
- To re-run a patch, append a comment: `my_app.patches.v1_2.fix #2025-03-20`
- ALWAYS call `frappe.reload_doc()` before accessing new/modified DocTypes
- ALWAYS use `[post_model_sync]` for patches that need new fields
- One-liner patches: `execute:frappe.delete_doc("Page", "old-page", ignore_missing=True)`

### Testing a Patch
```bash
# Run all pending patches
bench --site mysite migrate

# Run a specific patch manually in console
bench --site mysite console
>>> from my_app.patches.v1_2.update_customer_status import execute
>>> execute()
>>> frappe.db.commit()
```

## 10. Publishing to Frappe Marketplace

### Prerequisites Checklist
1. App hosted on public GitHub repository
2. `setup.py` or `pyproject.toml` with correct metadata
3. Valid `__version__` in `__init__.py`
4. README.md with installation instructions
5. All tests passing

### setup.py (v14)
```python
from setuptools import setup, find_packages

setup(
    name="my_custom_app",
    version="1.0.0",
    description="My Custom App for ERPNext",
    author="Your Name",
    author_email="you@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=["frappe"],
)
```

### pyproject.toml (v15+)
```toml
[project]
name = "my_custom_app"
dynamic = ["version"]
requires-python = ">=3.10,<3.13"
dependencies = ["frappe"]

[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core:buildapi"
```

### Publishing Steps
1. Create account at https://frappecloud.com/marketplace
2. Add your GitHub repository
3. Configure supported versions (v14, v15)
4. Submit for review
5. After approval, app appears in Marketplace

## 11. App Update Lifecycle on Client Sites

```bash
# Pull latest code
bench update --pull

# Or update specific app
cd apps/my_custom_app && git pull origin main && cd ../..

# Then migrate (runs patches + syncs schema)
bench --site mysite migrate

# Rebuild assets
bench build --app my_custom_app

# Restart workers
bench restart
```

The `bench update` command wraps: backup → pull → requirements → migrate → build → restart.

ALWAYS take a backup before running `bench update` on production.
ALWAYS test updates on staging before applying to production.

## See Also

- [references/examples.md](references/examples.md) — Complete app scaffolding examples
- [references/anti-patterns.md](references/anti-patterns.md) — Common mistakes
- [references/workflows.md](references/workflows.md) — Step-by-step workflows
- [references/module-workspace-shipping.md](references/module-workspace-shipping.md) — Module Def, modules.txt, and workspace shipping
- `frappe-syntax-hooks` — Complete hooks.py reference
- `frappe-core-database` — Database and migration patterns
- `frappe-impl-workspace` — Workspace builder, components, and customization
---
name: frappe-ops-backup
description: >
  Use when configuring backups, restoring sites, encrypting backup files, scheduling automated backups, or planning disaster recovery.
  Prevents data loss from missing backups, failed restores, and unencrypted sensitive data.
  Covers bench backup, bench restore, backup encryption, S3/remote storage, scheduled backups, disaster recovery procedures.
  Keywords: backup, restore, encryption, S3, scheduled backup, disaster recovery, bench backup, bench restore, how to backup, restore database, backup failed, data recovery, automated backup..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Backup & Disaster Recovery

Frappe provides built-in backup and restore commands via bench. ALWAYS back up before updates, migrations, or any destructive operation. A backup that has never been test-restored is NOT a backup.

## Quick Reference

```bash
# Database-only backup (default)
bench backup

# Full backup with public + private files
bench backup --with-files

# Backup specific site
bench --site mysite.com backup --with-files

# Backup with compression (.tgz instead of .tar)
bench backup --with-files --compress

# Backup only specific DocTypes
bench backup --only "Sales Invoice,Purchase Invoice"

# Backup excluding specific DocTypes
bench backup --exclude "Error Log,Activity Log"

# Custom backup path
bench backup --backup-path /mnt/backups/

# Restore from backup
bench --site mysite.com restore /path/to/backup.sql.gz

# Restore with files
bench --site mysite.com restore /path/to/backup.sql.gz \
    --with-public-files /path/to/files.tar \
    --with-private-files /path/to/private-files.tar

# Setup automated backups (cron)
bench setup backups
```

### What Gets Backed Up

| Component | Default | With --with-files | Location |
|---|---|---|---|
| Database (SQL dump) | YES | YES | `sites/{site}/private/backups/` |
| Site config | YES | YES | `sites/{site}/private/backups/` |
| Public files | NO | YES | `sites/{site}/public/files/` |
| Private files | NO | YES | `sites/{site}/private/files/` |

**Backup file naming**: `{datetime}_{hash}_{site}-database.sql.gz`

---

## Backup Decision Tree

```
What do you need to back up?
|
+-- Quick database snapshot before a change?
|   +-- bench backup (database only, fast)
|
+-- Full backup before upgrade or migration?
|   +-- bench backup --with-files --compress
|
+-- Automated daily backups?
|   +-- bench setup backups (cron-based)
|   +-- OR S3 Backup Settings (cloud storage)
|
+-- Offsite / cloud backup?
|   +-- S3 Backup Settings DocType (built-in)
|   +-- OR custom script with rclone/aws-cli
|
+-- Partial backup (specific DocTypes)?
|   +-- bench backup --only "DocType1,DocType2"
|
+-- Disaster recovery?
|   +-- Full backup + files + tested restore procedure
|   +-- See Disaster Recovery section below
```

---

## bench backup: All Options

```bash
bench backup [OPTIONS]

# Path options
--backup-path PATH              # Save all backup files to this directory
--backup-path-db PATH           # Custom path for database dump
--backup-path-conf PATH         # Custom path for site config backup
--backup-path-files PATH        # Custom path for public files archive
--backup-path-private-files PATH # Custom path for private files archive

# Filter options
--only, --include, -i DOCTYPES  # Include ONLY these DocTypes (comma-separated)
--exclude, -e DOCTYPES          # Exclude these DocTypes (comma-separated)
--ignore-backup-conf            # Ignore include/exclude from site config

# Flags
--with-files                    # Include public and private files
--compress                      # Use .tgz format (gzip compressed tar)
--verbose                       # Show detailed output
```

**Safety feature**: If backup fails (any exception), partial files are automatically deleted to avoid consuming disk space with incomplete backups.

---

## bench restore: All Options

```bash
bench --site [site-name] restore [OPTIONS] SQL_FILE_PATH

# SQL_FILE_PATH: path to .sql or .sql.gz file
# Can be relative to sites/ directory or absolute path

# Options
--db-root-username USERNAME     # MariaDB/PostgreSQL root username
--db-root-password PASSWORD     # MariaDB/PostgreSQL root password
--db-name NAME                  # Use custom database name
--admin-password PASSWORD       # Set administrator password after restore
--install-app APP_NAME          # Install app after restore
--with-public-files PATH        # Restore public files (.tar or .tgz)
--with-private-files PATH       # Restore private files (.tar or .tgz)

# Flags
--force                         # Bypass downgrade warnings (NOT recommended)
```

**CRITICAL**: Downgrades are NOT supported. Restoring a backup from a newer version onto an older version triggers a warning. NEVER use `--force` to bypass this unless you understand the consequences.

---

## Automated Backups

### Cron-Based (bench setup backups)

```bash
# Sets up daily backup cron job
bench setup backups

# This adds to crontab:
# 0 */6 * * * cd /home/frappe/frappe-bench && bench backup --with-files
```

### S3 Backup Settings (Built-in DocType)

Configure in ERPNext: **Settings > S3 Backup Settings**

| Field | Description |
|---|---|
| Enable | Toggle automated S3 backups |
| S3 Bucket Name | Target bucket |
| AWS Access Key ID | IAM credentials |
| AWS Secret Access Key | IAM secret |
| Region | AWS region (e.g., eu-west-1) |
| Frequency | Daily, Weekly |
| Backup Files | Include public/private files |

```python
# Programmatic S3 backup trigger
from frappe.integrations.offsite_backup_utils import send_email
import frappe

# The S3 backup runs via scheduled job when enabled
# To trigger manually:
from frappe.integrations.doctype.s3_backup_settings.s3_backup_settings import take_backups_s3
take_backups_s3()
```

### Custom Backup Script

```bash
#!/bin/bash
# custom-backup.sh — Daily backup with rotation and offsite copy
set -e

BENCH_DIR="/home/frappe/frappe-bench"
BACKUP_DIR="/mnt/backups/frappe"
RETENTION_DAYS=30
S3_BUCKET="s3://my-frappe-backups"
DATE=$(date +%Y-%m-%d_%H%M)

cd $BENCH_DIR

# Create backup
bench backup --with-files --compress --backup-path "$BACKUP_DIR/$DATE/"

# Sync to S3
aws s3 sync "$BACKUP_DIR/$DATE/" "$S3_BUCKET/$DATE/"

# Remove local backups older than retention period
find "$BACKUP_DIR" -type d -mtime +$RETENTION_DAYS -exec rm -rf {} +

# Verify latest backup exists on S3
aws s3 ls "$S3_BUCKET/$DATE/" || echo "WARNING: S3 sync failed!"
```

---

## Backup Encryption

### Encrypt Backups at Rest

```bash
# Encrypt backup with GPG (symmetric)
bench backup --with-files --compress
gpg --symmetric --cipher-algo AES256 \
    sites/mysite/private/backups/latest-database.sql.gz

# Decrypt for restore
gpg --decrypt backup.sql.gz.gpg > backup.sql.gz
bench --site mysite.com restore backup.sql.gz
```

### Encrypt with OpenSSL

```bash
# Encrypt
openssl enc -aes-256-cbc -salt -pbkdf2 \
    -in backup.sql.gz -out backup.sql.gz.enc

# Decrypt
openssl enc -d -aes-256-cbc -pbkdf2 \
    -in backup.sql.gz.enc -out backup.sql.gz
```

ALWAYS store encryption keys/passwords separately from backups. NEVER store the decryption key in the same location as the encrypted backup.

---

## Restore Procedures

### Full Site Restore

```bash
# 1. Stop services (traditional deployment)
sudo supervisorctl stop all

# 2. Restore database
bench --site mysite.com restore \
    /path/to/20240115_backup-database.sql.gz \
    --db-root-password YOUR_DB_ROOT_PASSWORD \
    --admin-password NEW_ADMIN_PASSWORD

# 3. Restore files
bench --site mysite.com restore \
    /path/to/20240115_backup-database.sql.gz \
    --with-public-files /path/to/20240115_backup-files.tar \
    --with-private-files /path/to/20240115_backup-private-files.tar

# 4. Run migrations (if version differs)
bench --site mysite.com migrate

# 5. Clear cache
bench --site mysite.com clear-cache

# 6. Restart services
sudo supervisorctl start all
```

### Restore to New Site

```bash
# Create new site from backup (useful for staging/testing)
bench new-site staging.example.com \
    --db-root-password YOUR_DB_ROOT_PASSWORD \
    --admin-password STAGING_PASSWORD

bench --site staging.example.com restore \
    /path/to/production-backup.sql.gz \
    --with-public-files /path/to/files.tar \
    --with-private-files /path/to/private-files.tar

bench --site staging.example.com migrate
```

### Docker Restore

```bash
# Copy backup into container
docker cp backup.sql.gz frappe-backend:/tmp/

# Restore
docker compose exec backend \
    bench --site mysite.com restore /tmp/backup.sql.gz \
    --db-root-password $DB_ROOT_PASSWORD

# Cleanup
docker compose exec backend rm /tmp/backup.sql.gz
```

---

## Backup Verification

ALWAYS test restores regularly. A backup is only valid if it can be successfully restored.

```bash
#!/bin/bash
# verify-backup.sh — Test restore to verify backup integrity
set -e

BACKUP_SQL="/mnt/backups/frappe/latest/database.sql.gz"
TEST_SITE="backup-test.localhost"
BENCH_DIR="/home/frappe/frappe-bench"

cd $BENCH_DIR

# Create temporary test site
bench new-site $TEST_SITE --db-root-password $DB_ROOT_PASSWORD --admin-password test

# Restore backup
bench --site $TEST_SITE restore $BACKUP_SQL --db-root-password $DB_ROOT_PASSWORD

# Run basic verification
bench --site $TEST_SITE migrate
bench --site $TEST_SITE console <<'EOF'
import frappe
count = frappe.db.count("User")
print(f"User count: {count}")
assert count > 0, "No users found — backup may be corrupt"
print("Backup verification PASSED")
EOF

# Cleanup test site
bench drop-site $TEST_SITE --db-root-password $DB_ROOT_PASSWORD --force

echo "Backup verification complete"
```

---

## Multi-Site Backup Strategy

```bash
#!/bin/bash
# backup-all-sites.sh — Backup every site in the bench
set -e

BENCH_DIR="/home/frappe/frappe-bench"
cd $BENCH_DIR

for site in $(bench --site all list-apps 2>/dev/null | grep -oP '^\S+'); do
    echo "Backing up $site..."
    bench --site "$site" backup --with-files --compress
done
```

---

## Disaster Recovery Plan Template

```
1. PREVENTION
   - Automated daily backups (bench setup backups OR S3)
   - Offsite copies (S3, GCS, or remote server)
   - Encrypted backups for sensitive data
   - Backup retention: minimum 30 days

2. DETECTION
   - Monitor backup cron job (check /var/log/syslog)
   - Verify backup file sizes (alert if < expected)
   - Weekly automated restore test

3. RECOVERY (RTO target: < 4 hours)
   a. Provision new server (or use standby)
   b. Install Frappe/ERPNext (same version as backup)
   c. Restore from latest verified backup
   d. Run migrations
   e. Update DNS to point to new server
   f. Verify functionality

4. DOCUMENTATION
   - Backup locations and credentials
   - Encryption key storage (separate from backups)
   - Step-by-step restore procedure
   - Contact list for escalation
```

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---|---|---|---|
| `--compress` flag | Yes | Yes | Yes |
| `--only` / `--exclude` | Yes | Yes | Yes |
| S3 Backup Settings | Yes | Yes | Yes |
| Site-level logs | v13+ | Yes | Yes |
| `partial-restore` command | No | Yes | Yes |

---

## Reference Files

| File | Contents |
|---|---|
| [examples.md](references/examples.md) | Complete backup/restore scripts |
| [anti-patterns.md](references/anti-patterns.md) | Common backup mistakes |
| [workflows.md](references/workflows.md) | Step-by-step backup workflows |

## Related Skills

- `frappe-ops-deployment` — Production deployment (includes backup in update workflow)
- `frappe-ops-performance` — Performance tuning
- `frappe-ops-bench` — Bench CLI reference
- `frappe-ops-upgrades` — Version upgrade procedures (backup required)
---
name: frappe-ops-bench
description: >
  Use when running bench commands, managing sites, configuring multi-tenancy, or setting up domains.
  Prevents misconfigured bench environments, broken site routing, and DNS mismatches.
  Covers bench CLI commands, site creation, bench init, multi-tenancy setup, DNS-based routing, common-site-config.
  Keywords: bench, site, multi-tenancy, domains, bench init, bench new-site, bench setup, common_site_config, bench command not working, site setup, multi-tenant, domain routing, new site..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Bench CLI Complete Reference

Complete bench CLI reference for site management, app lifecycle, configuration, and multi-tenancy.

**Version**: v14/v15/v16

---

## Quick Reference: Essential Commands

| Task | Command |
|------|---------|
| Create bench | `bench init myproject --frappe-branch version-15` |
| Create site | `bench new-site mysite.localhost --admin-password admin` |
| Set default site | `bench use mysite.localhost` |
| Get app | `bench get-app erpnext --branch version-15` |
| Install app | `bench --site mysite install-app erpnext` |
| Start dev server | `bench start` |
| Run migrations | `bench --site mysite migrate` |
| Build assets | `bench build --app myapp` |
| Backup site | `bench --site mysite backup` |
| Restore backup | `bench --site mysite restore /path/to/backup.sql.gz` |
| Open console | `bench --site mysite console` |
| Open DB shell | `bench --site mysite mariadb` |
| Check scheduler | `bench doctor` |
| View pending jobs | `bench show-pending-jobs` |
| Update everything | `bench update` |
| Drop site | `bench drop-site mysite --force` |

---

## Workflow 1: Creating a New Bench

```bash
# Initialize bench with specific Frappe version
bench init myproject --frappe-branch version-15

# With Python version
bench init myproject --frappe-branch version-15 --python python3.11

# Enter bench directory (REQUIRED for all subsequent commands)
cd myproject
```

**What `bench init` creates:**

```
myproject/
├── apps/           # Installed Frappe apps (frappe is default)
├── sites/          # All sites and shared config
│   └── common_site_config.json
├── config/         # Redis, Procfile, supervisor configs
├── env/            # Python virtual environment
├── logs/           # Log files
└── Procfile        # Process definitions for bench start
```

### Critical Rules

- **ALWAYS** specify `--frappe-branch` to pin Frappe version
- **ALWAYS** run commands from inside the bench directory
- **NEVER** run bench commands as root — use a dedicated frappe user

---

## Workflow 2: Site Management

### Creating Sites

```bash
# Basic site creation
bench new-site mysite.localhost --admin-password admin

# With specific database
bench new-site mysite.localhost --db-name mysite_db --admin-password admin

# With MariaDB root password
bench new-site mysite.localhost --mariadb-root-password rootpass --admin-password admin

# Install apps during creation
bench new-site mysite.localhost --admin-password admin --install-app erpnext
```

### Setting Default Site

```bash
bench use mysite.localhost
# OR set environment variable for current session:
export FRAPPE_SITE=mysite.localhost
```

### Dropping a Site

```bash
bench drop-site mysite.localhost --force
# Deletes database and archives site directory
```

### Site Directory Structure

```
sites/mysite.localhost/
├── site_config.json     # Site-specific config (db credentials)
├── private/             # Auth-required files, backups
├── public/              # Publicly accessible files
├── locks/               # Scheduler lock files
└── task-logs/           # Scheduler task logs
```

---

## Workflow 3: App Management

```bash
# Download app from GitHub
bench get-app erpnext --branch version-15
bench get-app https://github.com/org/custom-app.git --branch main

# Install app on a site
bench --site mysite install-app erpnext

# List installed apps
bench --site mysite list-apps

# Remove app from site (creates backup first)
bench --site mysite uninstall-app custom_app

# Remove app from bench entirely
bench remove-app custom_app

# Switch app branch
bench switch-to-branch version-15 erpnext frappe

# Exclude app from updates
bench exclude-app custom_app

# Re-include app in updates
bench include-app custom_app
```

### Critical Rules

- **ALWAYS** `get-app` before `install-app` — get downloads, install activates
- **ALWAYS** backup before `uninstall-app` — it deletes app-related data
- **NEVER** manually delete app folders — use `bench remove-app`

---

## Workflow 4: bench update: What It Does

```bash
# Full update (pull + migrate + build + restart)
bench update

# Update specific app only
bench update --pull --app erpnext

# Skip build step
bench update --no-build

# Skip backup
bench update --no-backup

# Reset to upstream (DESTROYS local changes)
bench update --reset
```

**`bench update` executes these steps in order:**
1. Backup all sites
2. Pull latest code for all apps (`git pull`)
3. Install Python/Node requirements
4. Build static assets (`bench build`)
5. Run migrations on all sites (`bench migrate`)
6. Restart bench processes

### Critical Rules

- **ALWAYS** run `bench update` in a screen/tmux session — it takes time
- **NEVER** use `--reset` in production without understanding it does `git reset --hard`
- **ALWAYS** test updates on staging first

---

## Workflow 5: bench migrate

```bash
# Migrate specific site
bench --site mysite migrate

# Migrate all sites
bench --site all migrate

# Check if safe to migrate (no pending jobs)
bench --site mysite ready-for-migration
```

**What `bench migrate` does:**
1. Runs schema sync (DocType changes → database)
2. Runs patches (data migrations)
3. Rebuilds search index
4. Syncs translations
5. Rebuilds Dashboard cache

### When to Migrate

- After `bench update` (done automatically)
- After changing hooks.py
- After adding/modifying DocTypes
- After pulling code changes
- **NEVER** skip migrate after code changes — leads to schema mismatches

---

## Workflow 6: bench build

```bash
# Build all apps
bench build

# Build specific app
bench build --app myapp

# Build with bundle analyzer
bench build --app myapp --production

# Watch mode (auto-rebuild on file changes)
bench watch
```

### When to Build

- After changing JS/CSS files
- After `bench get-app` (done automatically)
- After modifying `package.json`
- **ALWAYS** build after modifying client-side assets

---

## Workflow 7: Console and Database Access

```bash
# IPython console (with Frappe loaded)
bench --site mysite console
# In console:
# >>> frappe.get_doc("Sales Invoice", "INV-001")
# >>> frappe.db.sql("SELECT name FROM `tabUser` LIMIT 5")

# Auto-reload on code changes
bench --site mysite console --autoreload

# MariaDB shell
bench --site mysite mariadb
# >>> SELECT name, email FROM tabUser LIMIT 5;

# PostgreSQL shell
bench --site mysite postgres

# Execute a method directly
bench --site mysite execute myapp.tasks.daily_cleanup
bench --site mysite execute myapp.api.process --kwargs '{"name": "INV-001"}'

# Make authenticated request as Administrator
bench --site mysite request GET /api/resource/User
```

---

## Workflow 8: Backup and Restore

```bash
# Backup (database + files)
bench --site mysite backup
# Creates: sites/mysite/private/backups/
#   YYYY-MM-DD_HHMMSS-mysite-database.sql.gz
#   YYYY-MM-DD_HHMMSS-mysite-files.tar
#   YYYY-MM-DD_HHMMSS-mysite-private-files.tar

# Backup all sites
bench backup-all-sites

# Backup with encryption
bench --site mysite backup --backup-encryption-key mykey

# Restore from backup
bench --site mysite restore /path/to/database.sql.gz

# Restore with files
bench --site mysite restore /path/to/database.sql.gz \
  --with-public-files /path/to/files.tar \
  --with-private-files /path/to/private-files.tar

# Partial restore
bench --site mysite partial-restore /path/to/database.sql.gz
```

### Critical Rules

- **ALWAYS** backup before `bench update`, `uninstall-app`, or `drop-site`
- Backups older than 24 hours auto-deleted by default — configure `keep_backups_for_hours`
- **ALWAYS** test restore on a staging site before relying on a backup

---

## Workflow 9: Scheduler and Background Jobs

```bash
# Enable/disable scheduler
bench --site mysite scheduler enable
bench --site mysite scheduler disable
bench --site mysite scheduler pause
bench --site mysite scheduler resume

# Check scheduler health
bench doctor

# View queued jobs
bench show-pending-jobs

# Purge pending jobs
bench --site mysite purge-jobs

# Manually trigger scheduler event
bench --site mysite trigger-scheduler-event hourly

# Start worker manually (for debugging)
bench worker --queue short
```

---

## Workflow 10: Multi-Tenancy

### DNS-Based Routing (Recommended)

```bash
# Enable DNS multi-tenancy
bench config dns_multitenant on

# Create sites with proper hostnames
bench new-site site1.example.com --admin-password admin
bench new-site site2.example.com --admin-password admin

# Regenerate nginx config
bench setup nginx

# Reload nginx
sudo service nginx reload
```

Requests are routed by matching the `Host` header to site names.

### Port-Based Routing (Alternative)

```bash
bench config dns_multitenant off
bench new-site site2.localhost --admin-password admin
bench set-nginx-port site2.localhost 8082
bench setup nginx
sudo service nginx reload
```

### Custom Domain Mapping

```bash
# Add domain to site
bench setup add-domain site1.example.com --site mysite
bench setup nginx
sudo service nginx reload
```

---

## Configuration: common_site_config.json

Located at `sites/common_site_config.json` — applies to ALL sites.

### Essential Keys

| Key | Default | Purpose |
|-----|---------|---------|
| `background_workers` | 1 | Number of background job workers |
| `developer_mode` | false | Auto-sync DocType changes to files |
| `dns_multitenant` | false | Enable DNS-based multi-tenancy |
| `gunicorn_workers` | 2 | Web server worker count (min: 2) |
| `maintenance_mode` | 0 | Take all sites offline |
| `pause_scheduler` | 0 | Pause job scheduler |
| `serve_default_site` | — | Default site when host not matched |
| `server_script_enabled` | false | Enable Server Scripts |
| `scheduler_tick_interval` | 60 | Seconds between scheduler checks |
| `webserver_port` | 8000 | Development server port |
| `socketio_port` | 9000 | Socket.IO port |
| `live_reload` | false | Auto-reload on asset rebuild |

### Redis Configuration

| Key | Default |
|-----|---------|
| `redis_cache` | `redis://localhost:13000` |
| `redis_queue` | `redis://localhost:11000` |
| `redis_socketio` | `redis://localhost:13000` |

### Setting Config Values

```bash
# Set common config (all sites)
bench config set-common-config -c background_workers 4
bench config set-common-config -c developer_mode 1

# Set site-specific config
bench --site mysite set-config developer_mode 1
bench --site mysite set-config maintenance_mode 1

# View current config
bench --site mysite show-config
```

---

## Configuration: site_config.json

Per-site config at `sites/<sitename>/site_config.json`.

### Mandatory Keys

| Key | Purpose |
|-----|---------|
| `db_type` | `mariadb` or `postgres` |
| `db_name` | Database name |
| `db_password` | Database password |

### Important Optional Keys

| Key | Purpose |
|-----|---------|
| `admin_password` | Administrator initial password |
| `host_name` | Full site URL (with protocol) |
| `install_apps` | Apps to install on restore/reinstall |
| `allow_cors` | CORS origins (`"*"`, URL, or array) |
| `max_file_size` | Upload limit (default: 10MB) |
| `mute_emails` | Disable all outgoing email |
| `logging` | Debug level (0-2, level 2 shows SQL queries) |

### Environment Variable Overrides

Environment variables override config files. Key mappings: `FRAPPE_REDIS_QUEUE`, `FRAPPE_REDIS_CACHE`, `FRAPPE_DB_HOST`, `FRAPPE_DB_PORT`, `FRAPPE_DB_NAME`, `FRAPPE_DB_PASSWORD`.

**Priority**: Environment Variable > site_config.json > common_site_config.json > Default

---

## Production Setup

```bash
sudo bench setup production frappe-user   # nginx + supervisor + fail2ban
bench setup lets-encrypt mysite.example.com  # SSL
sudo bench restart                          # Restart services
bench disable-production                    # Back to development
```

---

## Version Differences

| Feature | V14 | V15 | V16 |
|---------|:---:|:---:|:---:|
| bench init | Yes | Yes | Yes |
| Scheduler tick interval | ~240s | ~240s | **60s** |
| `db_user` config (separate) | No | No | **Yes** |
| `console --autoreload` | No | Yes | Yes |
| `trim-tables` command | No | Yes | Yes |
| `trim-database` command | No | Yes | Yes |
| `request` command | No | Yes | Yes |
| Gettext translations | No | No | **Yes** |

---

## Reference Files

| File | Contents |
|------|----------|
| [commands.md](references/commands.md) | Full command reference with all options |
| [examples.md](references/examples.md) | Common workflow examples |
| [custom-commands.md](references/custom-commands.md) | Creating custom bench CLI commands with Click |
| [anti-patterns.md](references/anti-patterns.md) | Common bench mistakes and fixes |
---
name: frappe-ops-cloud
description: >
  Use when working with Frappe Cloud, Press API, provisioning sites, or managing benches on Frappe Cloud infrastructure.
  Prevents failed deployments from misconfigured cloud settings and API misuse.
  Covers Frappe Cloud dashboard, Press API, site provisioning, bench management, environment variables, cloud-specific limitations.
  Keywords: Frappe Cloud, Press, cloud API, site provisioning, bench management, FC, frappecloud, Frappe Cloud deploy, FC hosting, cloud setup, managed hosting..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Cloud & Press

Complete reference for Frappe Cloud managed hosting and Press self-hosted alternative.

---

## Quick Reference: Frappe Cloud Concepts

| Concept | Description |
|---------|-------------|
| **Site** | A single Frappe instance with its own database, domain, and apps |
| **Bench** | A shared runtime environment hosting one or more sites with the same app versions |
| **Server** | The underlying infrastructure (VM) running one or more benches |
| **Private Bench** | A dedicated bench for a single customer with full control |
| **Shared Bench** | A Frappe-managed bench shared across multiple sites |
| **Press** | The open-source platform (AGPL-3.0) that powers Frappe Cloud |
| **Agent** | Flask application on each server enabling Press-to-site communication |

---

## Decision Tree: Frappe Cloud vs Self-Hosted

```
Choosing hosting strategy:
├── Small team, want zero ops overhead?
│   └── Frappe Cloud (Shared Bench) — fastest time to production
├── Need custom server configuration?
│   ├── Budget for managed infra? → Frappe Cloud (Private Bench)
│   └── Want full control? → Self-hosted with bench
├── Need to host Frappe for multiple clients?
│   ├── Want managed platform? → Frappe Cloud
│   └── Want own platform? → Self-hosted Press
├── Regulatory/compliance — data must stay on-premises?
│   └── Self-hosted (bench or Press)
└── Development/testing environment?
    ├── Quick prototype → Frappe Cloud (free trial)
    └── Long-term dev → Local bench installation
```

---

## Frappe Cloud Overview

Frappe Cloud is a fully managed hosting platform for the Frappe stack. It handles server provisioning, backups, updates, monitoring, and scaling.

### Core Features

| Feature | Details |
|---------|---------|
| **Automated backups** | Scheduled daily backups with retention policies |
| **Automatic updates** | Managed update cycles for Frappe apps |
| **Scaling** | Horizontal and vertical scaling without downtime |
| **Multi-tenancy** | Multiple independent sites per bench |
| **SSL/TLS** | Automatic certificate provisioning and renewal |
| **Monitoring** | Real-time server and site monitoring |
| **Role-based access** | Granular permissions for team members |
| **Billing** | Daily/monthly subscriptions, wallet credits, multiple payment methods |

### Infrastructure Options

| Option | Use Case |
|--------|----------|
| **Shared Bench** | Cost-effective for small sites; Frappe manages the bench |
| **Private Bench** | Dedicated environment; custom app versions and update schedules |
| **Dedicated Server** | Full server for high-traffic or compliance requirements |

---

## Frappe Cloud Dashboard

### Site Management

The dashboard provides centralized control for all site operations:

- **Create sites** — Provision new sites on shared or private benches
- **Install/remove apps** — Add or remove Frappe apps from sites
- **Backups** — Manual and scheduled backups, restore from backup
- **Domain management** — Add custom domains with automatic SSL
- **Site config** — Edit `site_config.json` via the dashboard
- **Monitoring** — View CPU, memory, disk usage, and request logs
- **Site actions** — Migrate, update, suspend, archive, or transfer sites

### Bench Management

- **Create benches** — Set up shared or private benches
- **App management** — Select apps and their versions/branches
- **Update scheduling** — Control when benches receive updates
- **Environment variables** — Set custom environment variables
- **SSH access** — Connect to bench via SSH for debugging
- **Log browser** — View application and error logs
- **Database access** — Query the database via the dashboard

### Server Management

- **Provision servers** — Create servers across multiple cloud providers
- **Scale resources** — Upgrade CPU, memory, and storage
- **Storage add-ons** — Attach additional storage volumes
- **Server snapshots** — Create and restore server snapshots

---

## Deploying Apps on Frappe Cloud

### Adding a Custom App

1. Navigate to **Apps** in the Frappe Cloud dashboard
2. Click **Add App** and provide the GitHub repository URL
3. Select the branch to deploy
4. Configure build settings if needed
5. The app becomes available for installation on sites within compatible benches

### App Marketplace

Frappe Cloud includes a marketplace where developers can:

- List apps with descriptions and pricing
- Set compatibility requirements (Frappe version, dependencies)
- Configure pricing models (free, one-time, subscription)
- Manage payouts for commercial apps
- Track installations and usage analytics

### Deployment Workflow

```
Developer pushes code → Frappe Cloud detects update →
  Bench rebuild triggered → Assets compiled →
    Sites migrated → New version live
```

**For Private Benches**: Updates are controlled by the bench owner — NEVER auto-deployed without approval.

**For Shared Benches**: Frappe manages the update schedule.

---

## Site Provisioning Workflow

### Creating a New Site

1. **Select bench** — Choose shared or private bench
2. **Choose plan** — Select resource allocation (CPU, memory, storage)
3. **Configure apps** — Select which apps to install
4. **Set domain** — Use `*.frappe.cloud` subdomain or custom domain
5. **Create** — Frappe Cloud provisions the site (typically under 5 minutes)

### Custom Domain Setup

1. Navigate to site **Domains** in the dashboard
2. Add your custom domain (e.g., `erp.example.com`)
3. Configure DNS: Add a **CNAME** record pointing to the Frappe Cloud proxy
4. Frappe Cloud verifies DNS and provisions SSL certificate automatically
5. **ALWAYS** wait for DNS propagation before expecting SSL to work (up to 48 hours)

### Critical Rules

- **ALWAYS** use CNAME records for custom domains (not A records)
- **NEVER** transfer DNS to Frappe Cloud — only add CNAME records
- **ALWAYS** verify SSL is active before switching production traffic
- Custom domain SSL uses Let's Encrypt — auto-renews before expiry

---

## Frappe Cloud vs Self-Hosted Comparison

| Aspect | Frappe Cloud | Self-Hosted (bench) | Self-Hosted (Press) |
|--------|:------------:|:-------------------:|:-------------------:|
| **Setup time** | Minutes | Hours | Days |
| **Server management** | Managed | You manage | You manage |
| **Backups** | Automatic | Manual/cron | Automatic |
| **Updates** | Managed schedule | `bench update` | Managed via Press |
| **SSL certificates** | Automatic | Manual/certbot | Automatic |
| **Scaling** | Dashboard button | Manual | Dashboard |
| **Multi-tenancy** | Built-in | DNS multi-tenant | Built-in |
| **Cost** | Subscription | Infrastructure only | Infrastructure only |
| **Custom server config** | Limited | Full control | Full control |
| **Data sovereignty** | Frappe's infra | Your infra | Your infra |
| **SSH access** | Private bench only | Full | Full |
| **Monitoring** | Built-in | Set up yourself | Built-in |
| **Support** | Included | Community only | Community only |

---

## Press: Self-Hosted Frappe Cloud

### What Is Press?

Press is the open-source platform (AGPL-3.0) that powers Frappe Cloud. Organizations can self-host Press to create their own managed hosting platform for Frappe applications.

**GitHub**: `https://github.com/frappe/press`

### Architecture

| Component | Technology | Role |
|-----------|-----------|------|
| Press | Frappe Framework | Platform management, billing, dashboard |
| Agent | Flask | Server-to-site communication |
| Docker | Container runtime | App packaging and deployment |
| Ansible | Automation | Server provisioning and configuration |
| Frappe UI | Vue.js | Dashboard frontend |

### Key Capabilities

- **Multi-server management** — Provision and manage multiple servers
- **Site lifecycle** — Create, update, migrate, backup, restore, archive sites
- **Bench management** — Deploy benches with specific app versions
- **Billing system** — Subscriptions, invoicing, wallet credits, ERP integration
- **Marketplace** — App listing, pricing, payouts
- **Role-based access** — Granular permissions per team and resource
- **Monitoring** — Real-time metrics and alerting

### When to Self-Host Press

- You need to host Frappe for multiple clients/tenants
- You want a managed platform but on your own infrastructure
- You need full data sovereignty and regulatory compliance
- You want to offer Frappe hosting as a service

### When NOT to Self-Host Press

- **NEVER** self-host Press for a single site — use bench directly
- **NEVER** self-host Press without dedicated DevOps capacity
- **NEVER** underestimate the operational overhead — Press itself requires maintenance

### Self-Hosting Requirements

- Dedicated servers (bare metal or VMs) with Ubuntu
- DNS management for wildcard domains
- Object storage for backups (S3-compatible)
- SMTP service for transactional email
- Familiarity with Ansible, Docker, and Frappe Framework

---

## Frappe Cloud Limitations

### What You CANNOT Do on Frappe Cloud

- Install system-level packages (no root access on shared benches)
- Modify Nginx/Supervisor configuration directly
- Access raw database files (only SQL access via dashboard)
- Run long-running background processes outside Frappe's job queue
- Use non-standard ports or protocols

### Shared Bench Limitations

- No SSH access
- No custom environment variables (use site_config.json instead)
- Shared resources with other sites — performance may vary
- Update schedule controlled by Frappe (not the site owner)

### Private Bench Advantages Over Shared

- SSH access for debugging
- Custom environment variables
- Controlled update schedule
- Dedicated resources
- Custom app versions and branches

---

## Frappe Cloud Best Practices

### Site Configuration

- **ALWAYS** set `maintenance_mode` before large data imports
- **ALWAYS** use the dashboard for site config changes (not direct file edits)
- **NEVER** disable scheduler on Frappe Cloud — use `pause_scheduler` instead
- **ALWAYS** test app updates on a staging site before production

### Backup Strategy

- Frappe Cloud creates automatic daily backups
- **ALWAYS** create a manual backup before major changes
- **ALWAYS** download and store backups off-platform periodically
- **NEVER** rely solely on Frappe Cloud backups — maintain your own copies

### Performance

- Monitor site usage via the dashboard — upgrade plan before hitting limits
- Use background jobs for heavy operations (not synchronous API calls)
- Enable Redis caching for frequently accessed data
- Review slow query logs via the database analyzer tool

---

## Frappe Cloud DevOps Tools

| Tool | Purpose |
|------|---------|
| **Log Browser** | View application logs, error logs, scheduler logs |
| **Database Analyzer** | Run SQL queries, view slow queries, analyze indexes |
| **Binlog Browser** | View database change logs (binary log events) |
| **SSH Access** | Terminal access to private benches for debugging |
| **Process Status** | View running workers, scheduler status, job queue |

### Analytics Integrations

Frappe Cloud sites can connect to external analytics tools:
- Frappe Insights (native)
- Power BI (via API)
- Metabase (via database connection)
- Custom dashboards (via Frappe API)

---

## Reference Files

| File | Contents |
|------|----------|
| [examples.md](references/examples.md) | Cloud deployment workflow examples |
| [anti-patterns.md](references/anti-patterns.md) | Common Frappe Cloud mistakes and fixes |
---
name: frappe-ops-deployment
description: >
  Use when deploying Frappe/ERPNext to production, configuring Nginx or Supervisor, setting up Docker, enabling SSL, or hardening security.
  Prevents insecure deployments, missing reverse proxy config, and broken process management.
  Covers production setup, Nginx configuration, Supervisor/systemd, Docker Compose, Let's Encrypt SSL, firewall rules, security hardening.
  Keywords: deployment, production, nginx, supervisor, docker, ssl, letsencrypt, security, gunicorn, systemd, go live, production setup, HTTPS setup, server config, deploy to VPS, Docker setup..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Production Deployment

Deploy Frappe/ERPNext to production using either traditional (bench + Nginx + Supervisor) or Docker (frappe_docker + Compose). Frappe officially recommends Docker for new deployments.

## Quick Reference

```bash
# Traditional production setup (one command)
sudo bench setup production [frappe-user]

# What it configures:
# 1. Supervisor — process management (gunicorn, workers, Redis, socketio)
# 2. Nginx — reverse proxy, static files, websocket proxy
# 3. Sudoers — allows frappe-user to restart services

# Individual setup commands
bench setup supervisor          # Generate supervisor config
bench setup nginx               # Generate nginx config
bench setup sudoers $(whoami)   # Allow service restarts without password

# Symlink configs into system directories
sudo ln -s $(pwd)/config/supervisor.conf /etc/supervisor/conf.d/frappe-bench.conf
sudo ln -s $(pwd)/config/nginx.conf /etc/nginx/conf.d/frappe-bench.conf

# SSL setup
sudo -H bench setup lets-encrypt [site-name]
sudo -H bench setup lets-encrypt [site-name] --custom-domain [domain]

# DNS multitenancy (multiple sites on port 80/443)
bench config dns_multitenant on
bench setup nginx
sudo service nginx reload
```

---

## Deployment Decision Tree

```
Which deployment method?
|
+-- New server, minimal ops experience?
|   +-- Docker (frappe_docker) — recommended by Frappe
|
+-- Existing server with bench already installed?
|   +-- Traditional (bench setup production)
|
+-- Need custom Frappe apps or complex build?
|   +-- Docker with custom image build
|
+-- Cloud hosting (AWS/GCP/Azure)?
|   +-- Docker on VM or Kubernetes
|   +-- OR Frappe Cloud (managed)
|
+-- Single site or multi-site?
|   +-- Single site: standard setup
|   +-- Multi-site: DNS multitenancy required
```

---

## Traditional Deployment

### Process Architecture

```
Internet → Nginx (port 80/443)
               |
               +-- Static files served directly
               +-- /api, /app → Gunicorn (port 8000)
               +-- /socket.io → Node.js socketio (port 9000)

Supervisor manages:
  - frappe-bench-web (gunicorn)
  - frappe-bench-socketio (node)
  - frappe-bench-worker-short
  - frappe-bench-worker-default
  - frappe-bench-worker-long
  - frappe-bench-redis-cache
  - frappe-bench-redis-queue
  - frappe-bench-schedule (scheduler)
```

### Step-by-Step Setup

```bash
# 1. Install bench (as non-root user)
sudo pip3 install frappe-bench
bench init frappe-bench --frappe-branch version-15
cd frappe-bench

# 2. Create site
bench new-site mysite.example.com
bench --site mysite.example.com install-app erpnext

# 3. Production setup (configures nginx + supervisor + sudoers)
sudo bench setup production $(whoami)

# 4. Verify processes are running
sudo supervisorctl status

# 5. Verify nginx config
sudo nginx -t && sudo systemctl reload nginx
```

### Nginx Configuration

`bench setup nginx` generates `config/nginx.conf` with:
- Server block per site (DNS multitenancy)
- Proxy to gunicorn on port 8000
- WebSocket proxy to socketio on port 9000
- Static file serving from `sites/` directory
- Client max body size (default varies by version)

**ALWAYS disable default nginx site** to avoid port 80 conflicts:
```bash
sudo rm /etc/nginx/sites-enabled/default
# OR disable: sudo mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.bak
```

### Supervisor Configuration

`bench setup supervisor` generates `config/supervisor.conf` with:
- `--skip-redis` flag to skip Redis if managed externally

For CentOS/RHEL: use `.ini` extension instead of `.conf` for supervisor configs.

---

## SSL / HTTPS

### Let's Encrypt (Recommended)

```bash
# Automated setup with cron renewal
sudo -H bench setup lets-encrypt mysite.example.com

# For custom domain (site name differs from domain)
sudo -H bench setup lets-encrypt mysite.example.com --custom-domain www.example.com

# Manual renewal
sudo bench renew-lets-encrypt
```

**Prerequisites**:
- DNS multitenancy enabled (`bench config dns_multitenant on`)
- Domain resolves to server IP
- Port 80 open for ACME challenge
- Root/sudo access

**Certificate locations**: `/etc/letsencrypt/live/example.com/`
- `fullchain.pem` — certificate + chain
- `privkey.pem` — private key

Certificates expire every 90 days. The setup command adds a monthly cron for renewal.

### Custom SSL Certificate

```bash
# 1. Place certificate files
sudo mkdir -p /etc/nginx/conf.d/ssl
sudo cp certificate.crt /etc/nginx/conf.d/ssl/
sudo cp private.key /etc/nginx/conf.d/ssl/
sudo chmod 600 /etc/nginx/conf.d/ssl/private.key

# 2. Configure site
bench set-config ssl_certificate "/etc/nginx/conf.d/ssl/certificate.crt"
bench set-config ssl_certificate_key "/etc/nginx/conf.d/ssl/private.key"

# 3. Regenerate and reload
bench setup nginx
sudo systemctl reload nginx
```

All HTTP traffic is automatically redirected to HTTPS after SSL is configured.

---

## DNS Multitenancy (Multi-Site)

```bash
# Enable DNS-based site routing
bench config dns_multitenant on

# Create sites with domain names
bench new-site site1.example.com
bench new-site site2.example.com

# Regenerate nginx (creates server blocks per site)
bench setup nginx
sudo systemctl reload nginx
```

ALWAYS use the actual domain as the site name. Nginx routes requests to the correct site based on the `Host` header.

---

## Docker Deployment

### Architecture (frappe_docker)

```
Docker Compose Services:
  - configurator  — initializes DB/Redis config (runs once)
  - backend       — Frappe/ERPNext application server (gunicorn)
  - frontend      — Nginx reverse proxy
  - websocket     — Node.js Socket.IO server
  - queue-short   — RQ worker for short jobs
  - queue-long    — RQ worker for long jobs
  - (external)    — MariaDB/PostgreSQL + Redis (separate containers or managed)

Shared Volume:
  - sites:/home/frappe/frappe-bench/sites (persistent data)
```

### Production Docker Compose

```bash
# Clone frappe_docker
git clone https://github.com/frappe/frappe_docker.git
cd frappe_docker

# Use compose.yaml for production
# Key environment variables:
#   DB_HOST, DB_PORT — database connection
#   REDIS_CACHE, REDIS_QUEUE — Redis endpoints
#   FRAPPE_SITE_NAME_HEADER — for multi-site routing
#   PROXY_READ_TIMEOUT — upstream timeout
#   CLIENT_MAX_BODY_SIZE — upload limit (default 50m)

docker compose -f compose.yaml up -d
```

### Custom Image Build

```bash
# Build custom image with your apps
export APPS_JSON='[
  {"url":"https://github.com/frappe/erpnext","branch":"version-15"},
  {"url":"https://github.com/your-org/custom-app","branch":"main"}
]'

docker build \
  --build-arg APPS_JSON_BASE64=$(echo $APPS_JSON | base64 -w 0) \
  --tag your-registry/custom-erpnext:latest \
  images/custom/
```

---

## Security Hardening

### Firewall (UFW)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
# NEVER expose ports 8000, 9000, 6379, 3306 to the internet
```

### Fail2Ban

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban

# /etc/fail2ban/jail.local
# [sshd]
# enabled = true
# maxretry = 5
# bantime = 3600
```

### Redis Authentication

```bash
# Secure Redis for multi-bench environments
bench create-rq-users --set-admin-password
# Generates unique passwords per bench for Redis auth
```

### Additional Hardening

- ALWAYS disable root SSH login (`PermitRootLogin no` in `/etc/ssh/sshd_config`)
- ALWAYS use SSH key authentication, disable password auth
- NEVER run bench as root — create a dedicated `frappe` user
- ALWAYS keep system packages updated (`sudo apt update && sudo apt upgrade`)
- ALWAYS set `ALLOW_CORS` only to trusted domains in `site_config.json`

---

## Zero-Downtime Updates

```bash
# Traditional deployment
bench update --pull --patch --build --requirements
# Supervisor auto-restarts workers after update

# Docker deployment
# 1. Pull new image
docker compose pull
# 2. Recreate containers (rolling)
docker compose up -d --no-deps backend websocket queue-short queue-long
# 3. Run migrations
docker compose exec backend bench --site mysite.example.com migrate
```

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---|---|---|---|
| Docker recommended | No | Official recommendation | Yes |
| `create-rq-users` | No | Yes | Yes |
| ARM64 Docker images | No | Yes | Yes |
| Site-level logs | v13+ | Yes | Yes |
| `extend_doctype_class` | No | No | Yes |

---

## Reference Files

| File | Contents |
|---|---|
| [examples.md](references/examples.md) | Complete deployment scripts and configs |
| [anti-patterns.md](references/anti-patterns.md) | Common deployment mistakes |
| [workflows.md](references/workflows.md) | Step-by-step deployment workflows |

## Related Skills

- `frappe-ops-backup` — Backup and disaster recovery
- `frappe-ops-performance` — Performance tuning
- `frappe-ops-bench` — Bench CLI reference
- `frappe-ops-upgrades` — Version upgrade procedures
---
name: frappe-ops-frontend-build
description: >
  Use when configuring frontend asset bundling, migrating from build.json (v14) to esbuild (v15+), or troubleshooting SCSS/CSS compilation.
  Prevents build failures from mixing v14 and v15 build systems and misconfigured asset pipelines.
  Covers esbuild configuration (v15+), build.json (v14), asset bundling, SCSS compilation, bundle.js setup, bench build flags.
  Keywords: esbuild, build.json, frontend build, SCSS, CSS, asset bundling, bench build, bundle.js, webpack, build error, assets not loading, CSS not updating, JS not compiling, bench build fails..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frontend Build System

Complete reference for Frappe's frontend asset bundling pipeline, from build configuration to production optimization.

**Versions**: v14 (build.json) / v15+ (esbuild)

---

## Quick Reference: Build Commands

| Task | Command |
|------|---------|
| Build all apps | `bench build` |
| Build specific app | `bench build --app myapp` |
| Build multiple apps | `bench build --apps frappe,erpnext` |
| Production build (minified) | `bench build --production` |
| Force rebuild | `bench build --force` |
| Watch mode (auto-rebuild) | `bench watch` |
| Hard link assets | `bench build --hard-link` |

---

## Decision Tree: Build System Selection

```
Which build system?
├── Frappe v14?
│   └── build.json — Concatenation-based bundling
├── Frappe v15+?
│   └── esbuild — ES module bundling with *.bundle.* convention
└── Migrating v14 → v15?
    └── Replace build.json with *.bundle.* files in public/
```

---

## Build Pipeline Overview

### v15+ (esbuild): Current System

The v15+ build system uses esbuild for fast ES module bundling. It automatically discovers bundle entry points by scanning the `public/` directory for files matching `*.bundle.{js|ts|css|scss|sass|less|styl}`.

**How it works:**

1. `bench build` scans each app's `public/` directory recursively
2. Files matching `*.bundle.*` are treated as entry points
3. esbuild compiles, bundles, and optionally minifies each entry point
4. Output goes to `assets/dist/[app]/js/` or `assets/dist/[app]/css/`
5. Filenames include content hashes for cache-busting: `main.bundle.HASH.js`

**Supported file types:**
- `.js` — ES6 modules with import/export
- `.ts` — TypeScript
- `.vue` — Vue single-file components
- `.css` — Standard CSS
- `.scss` / `.sass` — SASS/SCSS stylesheets
- `.less` — Less stylesheets
- `.styl` — Stylus stylesheets

### v14 (build.json): Legacy System

The v14 system uses `build.json` in the app root to define concatenation rules.

```json
{
  "js/myapp.min.js": [
    "public/js/file1.js",
    "public/js/file2.js"
  ],
  "css/myapp.min.css": [
    "public/css/style1.css",
    "public/css/style2.css"
  ]
}
```

**NEVER** use `build.json` in v15+ — it is ignored by the esbuild pipeline.

---

## Bundle Entry Points [v15+]

### Creating a Bundle

Place files in your app's `public/` directory with the `.bundle.` naming convention:

```
myapp/
└── public/
    ├── js/
    │   └── myapp.bundle.js       # → dist/myapp/js/myapp.bundle.HASH.js
    ├── css/
    │   └── myapp.bundle.scss     # → dist/myapp/css/myapp.bundle.HASH.css
    └── components/
        └── widget.bundle.js      # → dist/myapp/js/widget.bundle.HASH.js
```

### Bundle File Content

```javascript
// myapp/public/js/myapp.bundle.js
import { createApp } from "vue";
import MyComponent from "./components/MyComponent.vue";

// ES6 imports are resolved by esbuild
import "../css/myapp.bundle.scss";

// npm packages (installed via yarn) can be imported directly
import dayjs from "dayjs";

createApp(MyComponent).mount("#myapp-root");
```

### Output Mapping

| Input | Output |
|-------|--------|
| `public/js/main.bundle.js` | `assets/dist/[app]/js/main.bundle.[hash].js` |
| `public/css/style.bundle.scss` | `assets/dist/[app]/css/style.bundle.[hash].css` |
| `public/deep/nested/file.bundle.ts` | `assets/dist/[app]/js/file.bundle.[hash].js` |

---

## hooks.py Asset Inclusion

### Desk Assets (Backend Interface)

```python
# hooks.py — loads in /app (Desk)
app_include_js = "myapp.bundle.js"
app_include_css = "myapp.bundle.css"

# Multiple files
app_include_js = ["myapp.bundle.js", "extra.bundle.js"]
app_include_css = ["myapp.bundle.css", "extra.bundle.css"]
```

### Portal Assets (Public Website)

```python
# hooks.py — loads on web pages (portal)
web_include_js = "myapp-web.bundle.js"
web_include_css = "myapp-web.bundle.css"
```

### Page-Specific Assets

```python
# hooks.py — loads on specific Desk pages
page_js = {"page_name": "public/js/custom_page.js"}
```

### Web Form Assets (Standard Web Forms Only)

```python
# hooks.py — loads on specific Web Forms
webform_include_js = {"ToDo": "public/js/custom_todo.js"}
webform_include_css = {"ToDo": "public/css/custom_todo.css"}
```

### Critical Rules

- **ALWAYS** use the bundle filename (not the full path) in hooks.py for v15+
- **NEVER** include the hash in hooks.py — Frappe resolves the hashed filename automatically
- **ALWAYS** rebuild after changing hooks.py: `bench build --app myapp`
- Multiple apps can define the same hooks — assets accumulate across all installed apps

---

## Including Assets in Templates

### Jinja Helpers

```html
<!-- Include script with correct hash -->
{{ include_script("myapp.bundle.js") }}

<!-- Include stylesheet with correct hash -->
{{ include_style("myapp.bundle.css") }}

<!-- Get path string only (no HTML tag) -->
<script src="{{ bundled_asset('myapp.bundle.js') }}"></script>
```

### Lazy Loading in Desk

```javascript
// Load asset on demand (returns Promise)
frappe.require("myapp.bundle.js", () => {
    // Asset loaded, initialize component
    myapp.init();
});

// Multiple assets
frappe.require(["widget.bundle.js", "widget.bundle.css"], () => {
    // Both loaded
});
```

---

## SCSS/CSS Compilation

### SCSS Bundle Example

```scss
// myapp/public/css/myapp.bundle.scss

// Import Frappe variables (available in all apps)
@import "frappe/public/scss/variables";

// Import partials (NOT bundles — no .bundle. in name)
@import "./components/header";
@import "./components/sidebar";

.myapp-container {
  padding: var(--padding-lg);
  background: var(--bg-color);
}
```

### Partial Files

Partials (files starting with `_` or without `.bundle.` in the name) are NOT compiled as entry points. They are only included via `@import`:

```
public/css/
├── myapp.bundle.scss        # Entry point — compiled
├── _variables.scss          # Partial — imported only
└── components/
    ├── _header.scss         # Partial — imported only
    └── _sidebar.scss        # Partial — imported only
```

---

## Development Workflow

### Watch Mode [v15+]

```bash
# Auto-rebuild on file changes
bench watch
```

- Watches all apps' `public/` directories for changes
- Rebuilds only affected bundles (incremental)
- Desk auto-reloads when assets change (if `live_reload` is enabled)

### Enabling Live Reload

```bash
# Via config
bench set-config -g live_reload true

# Via environment variable
export LIVE_RELOAD=1
```

### Development vs Production Build

| Feature | Development (`bench build`) | Production (`bench build --production`) |
|---------|---------------------------|---------------------------------------|
| Minification | No | Yes |
| Source maps | Yes | No |
| Bundle size | Larger | Optimized |
| Build speed | Fast | Slower |

---

## Frappe UI (Vue.js) Custom Pages [v15+]

### Setting Up a Vue Page

```javascript
// myapp/public/js/mypage.bundle.js
import { createApp } from "vue";
import { FrappeUI } from "frappe-ui";
import App from "./App.vue";

const app = createApp(App);
app.use(FrappeUI);
app.mount("#myapp-page");
```

### Registering the Page

```python
# Create a Page DocType or use www/ for web pages
# The bundle loads via hooks.py or include_script()
```

### npm Dependencies

```bash
# Install from app directory
cd apps/myapp
yarn add vue frappe-ui dayjs
```

Dependencies are resolved by esbuild from `node_modules/` during build.

---

## Common Build Errors and Fixes

### Error: "Could not resolve module"

```
ERROR: Could not resolve "some-package"
```

**Fix**: Install the missing npm package:
```bash
cd apps/myapp && yarn add some-package
```

### Error: "No bundle entry points found"

**Fix**: Ensure files use the `*.bundle.*` naming convention and are in the `public/` directory.

### Error: Stale Assets After Deployment

**Fix**: Force rebuild with cache clear:
```bash
bench build --force
bench clear-cache
```

### Error: CSS Not Updating

**Fix**: Check that SCSS files import correctly and the entry point has `.bundle.` in the name:
```bash
bench build --app myapp --force
```

### Error: "build.json" Ignored in v15

**Fix**: Migrate to `*.bundle.*` entry points. build.json is a v14-only feature.

---

## Asset Optimization for Production

### Pre-Deployment Checklist

1. **Build with production flag**: `bench build --production`
2. **Verify bundle sizes**: Check `assets/dist/` for unexpectedly large files
3. **Use lazy loading**: Split rarely-used features into separate bundles loaded via `frappe.require()`
4. **Minimize hook includes**: Only include essential assets in `app_include_js/css`
5. **Use CSS variables**: Leverage Frappe's built-in CSS custom properties instead of duplicating styles

### Bundle Splitting Strategy

```
public/
├── js/
│   ├── myapp.bundle.js          # Core — loaded on every page via hooks
│   ├── report-widget.bundle.js  # Lazy — loaded only on report pages
│   └── chart-tools.bundle.js    # Lazy — loaded only when charts needed
└── css/
    ├── myapp.bundle.scss        # Core — loaded on every page via hooks
    └── print.bundle.scss        # Lazy — loaded only for print views
```

---

## Version Differences

| Feature | v14 | v15+ |
|---------|:---:|:----:|
| Build system | build.json | **esbuild** |
| Entry point convention | Defined in JSON | `*.bundle.*` auto-discovery |
| TypeScript support | No | **Yes** |
| Vue SFC support | No | **Yes** |
| SCSS compilation | Via build pipeline | **Via esbuild** |
| Watch mode | `bench watch` | `bench watch` (faster) |
| Live reload | Manual | **Automatic** (configurable) |
| Source maps | Limited | **Full support** |
| Tree shaking | No | **Yes** |
| npm imports | Requires manual bundling | **Direct ES6 imports** |

---

## Reference Files

| File | Contents |
|------|----------|
| [examples.md](references/examples.md) | Complete build configuration examples |
| [anti-patterns.md](references/anti-patterns.md) | Common build mistakes and fixes |
---
name: frappe-ops-performance
description: >
  Use when tuning MariaDB, configuring Redis memory, sizing Gunicorn workers, setting up CDN, or profiling slow queries.
  Prevents performance bottlenecks from default configurations, memory exhaustion, and unoptimized database queries.
  Covers MariaDB tuning, Redis configuration, Gunicorn worker sizing, CDN setup, slow query log analysis, Python profiling, request profiling.
  Keywords: performance, MariaDB, Redis, Gunicorn, CDN, slow query, profiling, tuning, optimization, workers, slow page, loading time, ERPNext slow, why is it slow, page takes long, timeout..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Performance Tuning

Frappe/ERPNext performance depends on four layers: database (MariaDB), cache (Redis), application server (Gunicorn), and background workers (RQ). ALWAYS tune all four layers together — optimizing one while ignoring others creates new bottlenecks.

## Quick Reference

```bash
# Check system health
bench doctor

# Show pending background jobs
bench --site mysite.com show-pending-jobs

# Clear all caches
bench --site mysite.com clear-cache
bench --site mysite.com clear-website-cache

# Purge stuck background jobs
bench purge-jobs

# Enable MariaDB slow query log
# In /etc/mysql/mariadb.conf.d/50-server.cnf:
# slow_query_log = 1
# slow_query_log_file = /var/log/mysql/slow.log
# long_query_time = 1

# Check Gunicorn worker count
# In Procfile or supervisor config: -w [workers]
# Formula: workers = (2 * CPU_CORES) + 1
```

---

## Performance Decision Tree

```
What is slow?
|
+-- Page loads are slow?
|   +-- Check Gunicorn workers (are they saturated?)
|   +-- Check MariaDB slow query log
|   +-- Check Redis memory (is cache evicting?)
|   +-- Enable CDN for static assets
|
+-- Background jobs are delayed?
|   +-- bench doctor (check worker count and pending jobs)
|   +-- Increase RQ worker count
|   +-- Check for long-running jobs blocking queues
|
+-- Database queries are slow?
|   +-- Enable slow query log
|   +-- Run EXPLAIN on slow queries
|   +-- Add indexes on frequently filtered columns
|   +-- Use get_cached_value instead of get_value
|
+-- Server runs out of memory?
|   +-- Reduce Gunicorn workers
|   +-- Set Redis maxmemory
|   +-- Check MariaDB innodb_buffer_pool_size
|   +-- Look for memory leaks in custom code
|
+-- High CPU usage?
|   +-- Profile Python code (cProfile)
|   +-- Check for N+1 query patterns
|   +-- Review custom scheduled jobs
```

---

## MariaDB Tuning

### Critical Settings

```ini
# /etc/mysql/mariadb.conf.d/50-server.cnf
[mysqld]
# InnoDB buffer pool — MOST important setting
# Set to 50-70% of available RAM on dedicated DB server
# Set to 25-40% of RAM on shared server
innodb_buffer_pool_size = 2G

# Buffer pool instances (1 per GB of buffer pool)
innodb_buffer_pool_instances = 2

# Log file size (larger = better write performance, slower recovery)
innodb_log_file_size = 256M

# Flush method — use O_DIRECT to avoid double buffering
innodb_flush_method = O_DIRECT

# Character set (ALWAYS use utf8mb4 for Frappe)
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Key buffer for MyISAM (Frappe uses InnoDB, keep small)
key_buffer_size = 32M

# Query cache (DISABLE for MariaDB 10.4+ / MySQL 8.0+)
query_cache_type = 0
query_cache_size = 0

# Connection limits
max_connections = 200
wait_timeout = 600
interactive_timeout = 600

# Temp tables
tmp_table_size = 64M
max_heap_table_size = 64M

# Slow query log
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 1
```

### Slow Query Analysis

```bash
# Enable slow query log (runtime, no restart needed)
SET GLOBAL slow_query_log = 1;
SET GLOBAL long_query_time = 1;

# Analyze slow queries with mysqldumpslow
mysqldumpslow -t 10 -s c /var/log/mysql/slow.log
# -t 10: top 10 queries
# -s c: sort by count (use -s t for total time)

# Use EXPLAIN to analyze specific queries
EXPLAIN SELECT * FROM `tabSales Invoice` WHERE customer = 'ABC';
# Look for: type=ALL (full table scan), rows > 10000, Using filesort
```

### Index Optimization

```sql
-- Check for missing indexes on frequently filtered columns
SHOW INDEX FROM `tabSales Invoice`;

-- Add index for common filter patterns
ALTER TABLE `tabSales Invoice` ADD INDEX idx_customer_date (customer, posting_date);

-- Frappe way: add index via DocType definition
-- In doctype JSON: set "in_list_view" or "search_index" on fields
-- OR use hooks.py:
-- after_migrate = ["myapp.patches.add_custom_indexes"]
```

---

## Redis Configuration

### Memory Management

```conf
# /etc/redis/redis.conf (or bench config/redis_cache.conf)

# Set maximum memory — NEVER let Redis use all available RAM
maxmemory 512mb

# Eviction policy — allkeys-lru is best for cache use
maxmemory-policy allkeys-lru

# Disable persistence for cache Redis (performance boost)
save ""
appendonly no
```

### Frappe Redis Architecture

Frappe uses THREE Redis instances:

| Instance | Default Port | Purpose | Memory Guide |
|---|---|---|---|
| redis-cache | 13000 | Document cache, session data | 256MB-1GB |
| redis-queue | 11000 | RQ job queues | 128MB-512MB |
| redis-socketio | 12000 | Real-time events | 64MB-256MB |

ALWAYS set `maxmemory` on redis-cache. Without it, Redis grows unbounded and can trigger OOM killer.

### Frappe Caching API

```python
import frappe

# Basic Redis cache
frappe.cache.set_value("my_key", {"data": "value"})
result = frappe.cache.get_value("my_key")

# get_cached_value — cached database lookup (ALWAYS prefer over get_value for reads)
value = frappe.db.get_cached_value("Customer", "CUST-001", "customer_name")
# Equivalent to get_value but caches in Redis — dramatically faster for repeated reads

# Hashed cache (group related values)
frappe.cache.hset("settings", "key1", "value1")
frappe.cache.hget("settings", "key1")

# Clear specific cache
frappe.cache.delete_value("my_key")
frappe.cache.delete_keys("prefix*")

# Clear all cache (use sparingly)
# bench --site mysite.com clear-cache
```

---

## Gunicorn Workers

### Worker Count Formula

```
workers = (2 * CPU_CORES) + 1

Examples:
  2 CPU cores  →  5 workers
  4 CPU cores  →  9 workers
  8 CPU cores  → 17 workers
```

### Configuration

```bash
# Traditional: edit Procfile or supervisor config
# In supervisor.conf:
command=/home/frappe/frappe-bench/env/bin/gunicorn \
    -b 127.0.0.1:8000 \
    -w 9 \                    # Worker count
    --timeout 120 \           # Request timeout (seconds)
    --graceful-timeout 30 \   # Graceful shutdown timeout
    --max-requests 5000 \     # Restart worker after N requests (prevents memory leaks)
    --max-requests-jitter 500 \
    frappe.app:application

# Docker: set via environment variable or command override
```

### Memory Calculation

Each Gunicorn worker consumes 150-300MB RAM. ALWAYS verify total memory fits:

```
Required RAM = workers * 300MB + MariaDB buffer pool + Redis + OS overhead

Example (4 CPU, 8GB RAM server):
  9 workers * 300MB = 2.7GB (Gunicorn)
  + 2GB (MariaDB innodb_buffer_pool_size)
  + 1GB (Redis total)
  + 1.5GB (OS + other)
  = 7.2GB — fits in 8GB
```

NEVER set more workers than your RAM allows. Swapping kills performance.

---

## Background Workers (RQ)

### Worker Queues

| Queue | Purpose | Default Workers |
|---|---|---|
| short | Quick tasks (< 5 min) | 1 |
| default | Standard tasks | 1 |
| long | Heavy tasks (reports, bulk ops) | 1 |

### Tuning Worker Count

```bash
# Supervisor: duplicate worker sections with unique names
# For high-volume sites, increase short/default workers:

[program:frappe-bench-frappe-worker-short-1]
command=bench worker --queue short
...

[program:frappe-bench-frappe-worker-short-2]
command=bench worker --queue short
...

# Docker: scale via docker compose
docker compose up -d --scale queue-short=3 --scale queue-long=2
```

### Diagnosing Job Backlogs

```bash
# Check overall health
bench doctor
# Expected: Workers online: N, no pending jobs

# Check specific site queues
bench --site mysite.com show-pending-jobs

# Clear stuck jobs (use when jobs are permanently stuck)
bench purge-jobs
```

---

## CDN Setup for Static Assets

```python
# site_config.json
{
    "cdn_url": "https://cdn.example.com"
}
# All /assets/ URLs will be prefixed with the CDN URL

# ALTERNATIVELY: configure at Nginx level
# location /assets {
#     alias /home/frappe/frappe-bench/sites/assets;
#     expires 1y;
#     add_header Cache-Control "public, immutable";
# }
```

---

## Monitoring

### bench doctor

```bash
bench doctor
# Output:
# -----Checking scheduler------
# mysite.com: scheduler is running
# Workers online: 3
# -----None Jobs-----
```

### Key Log Locations

| Log | Path | Contains |
|---|---|---|
| Frappe web log | `logs/web.log` | HTTP requests, errors |
| Worker log | `logs/worker.log` | Background job output |
| Scheduler log | `logs/scheduler.log` | Scheduled job execution |
| Site-level log | `sites/{site}/logs/` | Per-site errors (v13+) |
| Slow query log | `/var/log/mysql/slow.log` | Slow database queries |

### Scheduled Job Log (DocType)

Check **Setup > Scheduled Job Log** in ERPNext UI for:
- Job execution times
- Failed jobs with error details
- Frequency analysis

### RQ Dashboard (Optional)

```bash
# Install RQ dashboard for web-based job monitoring
pip install rq-dashboard
rq-dashboard --redis-url redis://localhost:11000
# Access at http://localhost:9181
```

---

## Common Bottleneck Diagnosis

| Symptom | Likely Cause | Solution |
|---|---|---|
| Slow page loads, high DB time | Missing indexes, N+1 queries | Add indexes, use `get_list` with filters |
| Worker queue growing | Too few workers, long jobs | Increase workers, optimize job code |
| High memory, OOM kills | Too many Gunicorn workers, Redis unbounded | Reduce workers, set `maxmemory` |
| Intermittent timeouts | Gunicorn timeout too low | Increase `--timeout` (default 120s) |
| Slow after cache clear | Cold cache, no warming | Pre-warm critical caches after deploy |
| Static assets slow | No CDN, no browser caching | Add CDN, set `expires` headers |

---

## Scaling Patterns

```
Vertical Scaling (single server):
  1. Add RAM → increase innodb_buffer_pool_size + Redis maxmemory
  2. Add CPU → increase Gunicorn workers + RQ workers
  3. Use SSD → dramatic improvement for database I/O

Horizontal Scaling (multiple servers):
  1. Separate DB server (MariaDB on dedicated host)
  2. Separate Redis server(s)
  3. Multiple app servers behind load balancer
  4. Read replicas for reporting queries
  5. Kubernetes with frappe_docker for auto-scaling
```

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---|---|---|---|
| Site-level logs | v13+ | Yes | Yes |
| `bench doctor` | Yes | Yes | Yes |
| Scheduled Job Log | Yes | Yes | Yes |
| `get_cached_value` | Yes | Yes | Yes |
| Background workers (RQ) | Yes | Yes | Yes |

---

## Reference Files

| File | Contents |
|---|---|
| [examples.md](references/examples.md) | Complete tuning configs and scripts |
| [anti-patterns.md](references/anti-patterns.md) | Common performance mistakes |
| [workflows.md](references/workflows.md) | Step-by-step tuning workflows |

## Related Skills

- `frappe-ops-deployment` — Production deployment setup
- `frappe-ops-backup` — Backup and disaster recovery
- `frappe-ops-bench` — Bench CLI reference
- `frappe-core-database` — Database API and query patterns
---
name: frappe-ops-upgrades
description: >
  Use when upgrading Frappe/ERPNext between major versions (v14 to v15, v15 to v16), troubleshooting failed migrations, or planning rollback.
  Prevents broken upgrades from skipped patches, incompatible customizations, and missing pre-upgrade checks.
  Covers version upgrade paths, bench update, migrate command, patch troubleshooting, rollback procedures, breaking changes per version.
  Keywords: upgrade, migration, v14, v15, v16, bench update, bench migrate, rollback, patches, breaking changes, update failed, bench update error, migration error, patches failing, rollback after upgrade..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Version Upgrades

Complete guide for upgrading Frappe/ERPNext between major versions, handling failed migrations, and rolling back safely.

**Versions**: v14 → v15 → v16

---

## Quick Reference: Upgrade Commands

| Task | Command |
|------|---------|
| Full update | `bench update` |
| Update specific app | `bench update --pull --app erpnext` |
| Switch branch | `bench switch-to-branch version-15 frappe erpnext` |
| Run migrations only | `bench --site mysite migrate` |
| Check migration readiness | `bench --site mysite ready-for-migration` |
| Backup before upgrade | `bench --site mysite backup` |
| Restore from backup | `bench --site mysite restore /path/to/backup.sql.gz` |
| Re-run failed patch | Add `#YYYY-MM-DD` suffix in patches.txt |

---

## Decision Tree: Upgrade Strategy

```
Need to upgrade?
├── Single minor version bump (e.g., v15.10 → v15.20)?
│   └── YES → Run `bench update` directly
├── Major version jump (e.g., v14 → v15)?
│   ├── Have custom apps?
│   │   ├── YES → Test on staging FIRST, check breaking changes
│   │   └── NO → Follow standard upgrade path
│   └── Multiple major versions (v14 → v16)?
│       └── ALWAYS upgrade one version at a time: v14 → v15 → v16
└── Production environment?
    ├── YES → ALWAYS test on staging clone first
    └── NO → Proceed with standard upgrade
```

---

## Pre-Upgrade Checklist

**ALWAYS** complete these steps before ANY major version upgrade:

1. **Full backup** — `bench --site mysite backup --with-files`
2. **Test on staging** — Clone production to a staging bench and test there first
3. **Check breaking changes** — Review the breaking changes section below
4. **Audit custom apps** — Run custom apps against new version's API changes
5. **Check Python/Node versions** — v15 requires Node 18+; v16 requires Node 24+, Python 3.14+
6. **Disable scheduler** — `bench --site mysite scheduler disable`
7. **Check pending jobs** — `bench --site mysite ready-for-migration`
8. **Read release notes** — Check GitHub release notes for each version

---

## Standard Upgrade Process

### Step-by-Step

```bash
# 1. Backup all sites
bench backup-all-sites

# 2. Switch to target version branch
bench switch-to-branch version-15 frappe erpnext

# 3. Update (pulls code, installs deps, builds, migrates)
bench update

# 4. Verify
bench --site mysite migrate  # if not done by update
bench version                # confirm versions
```

### What `bench update` Executes (In Order)

1. Backup all sites
2. Pull latest code for all apps (`git pull`)
3. Install Python requirements (`pip install`)
4. Install Node requirements (`yarn install`)
5. Build static assets (`bench build`)
6. Run migrations on all sites (`bench migrate`)
7. Restart bench processes

---

## v14 → v15 Breaking Changes

### Environment Requirements

| Requirement | v14 | v15 |
|-------------|-----|-----|
| Node.js | v14+ | **v18+** |
| Python packaging | setup.py | **pyproject.toml** |

### Backend Breaking Changes

- **`db.set()` removed** — Use `doc.db_set()` instead
- **`db.sql()` parameters removed** — `as_utf8` and `formatted` no longer accepted
- **`db.set_value()` for Singles** — Use `frappe.db.set_single_value()` instead
- **`job_name` deprecated** — Use `job_id` parameter in `enqueue()`
- **`frappe.new_doc()` arguments** — `parent_doc`, `parentfield`, `as_dict` MUST be keyword args
- **`frappe.get_installed_apps()`** — No longer accepts `sort` or `frappe_last` args
- **Method override order reversed** — Last override now takes precedence
- **Timezone functions renamed** — `convert_utc_to_user_timezone` → `convert_utc_to_system_timezone`

### Frontend Breaking Changes

- **Vue 2 → Vue 3** — All Vue components MUST be migrated
- **Window globals removed** — `get_today` → `frappe.datetime.get_today`, `user` → `frappe.session.user`
- **`this` in Client Scripts** — Local scope access no longer supported
- **Image lazy loading** — Replace `website-image-lazy` class with native `loading="lazy"`

### Security Changes

- **Server Scripts disabled by default** — Enable: `bench set-config -g server_script_enabled 1`
- **"Desk User" role added** — Replaces "All" role for desk user permissions
- **`currentsite.txt` removed** — Use `bench use sitename` or `FRAPPE_SITE` env var

### Removed Features

- Event Streaming moved to separate app
- Cordova support removed
- `setup.py` removed (use `pyproject.toml`)
- `--make_copy` and `--restore` build flags removed (use `--hard-link`)

See [breaking-changes.md](references/breaking-changes.md) for the complete list.

---

## v15 → v16 Breaking Changes

### Environment Requirements

| Requirement | v15 | v16 |
|-------------|-----|-----|
| Node.js | v18+ | **v24+** |
| Python | 3.10+ | **3.14+** |

### Backend Breaking Changes

- **Default sort order changed** — `creation` instead of `modified` for all list queries
- **`has_permission` hooks** — MUST return explicit `True`; `None` no longer accepted
- **`frappe.get_doc(doctype, name, field=value)`** — No longer updates values
- **DB commits in document hooks** — No longer allowed to prevent data integrity issues
- **`frappe.sendmail(now=True)`** — No longer commits transactions implicitly
- **`db.get_value()` for Singles** — Now returns proper types instead of strings
- **State-changing methods require POST** — `/api/method/logout`, `/api/method/upload_file`, etc.

### Separated Modules (Install Separately)

- Energy Points → `frappe/eps`
- Newsletter → `frappe/newsletter`
- Backup Integrations → `frappe/offsite_backups`
- Blog → `frappe/blog`

### Frontend Breaking Changes

- Report/Dashboard/Page JS evaluated as IIFEs (no global scope pollution)
- Awesome Bar redesigned, moved to sidebar (`Cmd+K`)
- List view right sidebar removed
- `/apps` endpoint deprecated; `/app` reroutes to `/desk`

### Configuration Changes

- Site config cached for up to one minute (changes not immediate)
- Country field requires valid ISO 3166 ALPHA-2 code
- `bench version` output format changed to "plain" (use `-f legacy` for old format)
- `override_doctype` hook classes MUST inherit from the overridden class

See [breaking-changes.md](references/breaking-changes.md) for the complete list.

---

## Patch System

### How Patches Work

Patches are one-off data migration scripts that run during `bench migrate`. They are defined in each app's `patches.txt` file.

### patches.txt Format [v14+]

```ini
[pre_model_sync]
# Runs BEFORE schema sync — use for data prep
myapp.patches.v15_0.prepare_data_for_migration

[post_model_sync]
# Runs AFTER schema sync — use for data that needs new schema
myapp.patches.v15_0.migrate_data_to_new_fields
```

### Patch Execution Rules

- Patches run in the order defined in `patches.txt`
- Each patch runs exactly ONCE — tracked in the `__patches` table
- To re-run a patch, append a date comment: `myapp.patches.v15_0.fix #2025-03-20`
- One-off statements: `execute:frappe.delete_doc('Page', 'old_page', ignore_missing=True)`

### Writing a Patch

```python
# myapp/patches/v15_0/migrate_field_data.py
import frappe

def execute():
    # ALWAYS reload if you need the NEW schema
    frappe.reload_doc("module_name", "doctype", "doctype_name")

    # Perform data migration
    frappe.db.sql("""
        UPDATE `tabSales Invoice`
        SET new_field = old_field
        WHERE old_field IS NOT NULL
    """)
```

### Debugging Stuck Patches

```bash
# Check which patches have run
bench --site mysite console
>>> frappe.db.sql("SELECT * FROM __patches WHERE patch LIKE '%stuck_patch%'")

# Remove a patch record to force re-run
>>> frappe.db.sql("DELETE FROM __patches WHERE patch = 'myapp.patches.v15_0.broken_patch'")
>>> frappe.db.commit()

# Then re-run migrate
bench --site mysite migrate
```

---

## Rollback Procedure

### Immediate Rollback (Within Hours)

```bash
# 1. Stop all processes
bench stop

# 2. Restore database from pre-upgrade backup
bench --site mysite restore /path/to/pre-upgrade-backup.sql.gz \
  --with-public-files /path/to/files.tar \
  --with-private-files /path/to/private-files.tar

# 3. Switch back to previous version branch
bench switch-to-branch version-14 frappe erpnext

# 4. Install old dependencies
bench setup requirements

# 5. Build old assets
bench build

# 6. Start bench
bench start  # or: sudo bench restart (production)
```

### Critical Rules for Rollback

- **ALWAYS** keep pre-upgrade backups for at least 7 days
- **NEVER** run `bench migrate` after restoring to old branch — schema is already correct
- **ALWAYS** restore files alongside database — file references may break otherwise
- **NEVER** attempt rollback after users have created new data on the upgraded version

---

## Frappe Packages: Moving Customizations Between Sites

Frappe Packages (v14+) are lightweight UI-built applications — bundles of Custom Module Defs distributed as `.tar.gz` tarballs. For Custom Fields, Property Setters, and DocPerms on standard DocTypes, use **Fixtures** instead.

### Quick Reference: Package vs Fixtures vs App

| Mechanism | Use When | CLI Command |
|-----------|----------|-------------|
| **Package** | UI-built DocTypes, Scripts, Web Pages | UI only (Package Import/Release) |
| **Fixtures** | Custom Fields, Property Setters, DocPerms | `bench --site mysite export-fixtures` |
| **Frappe App** | Full development workflow, CI/CD, tests | `bench get-app`, `bench install-app` |

### Package Workflow (UI-Based)

1. Create a **Package** document → assign Custom Module Defs to it
2. Create a **Package Release** → exports to `[bench]/sites/[site]/packages/` as `[package]-[version].tar.gz`
3. On target site, create **Package Import** → attach tarball, check **Activate**
4. System migrates data like an app migration; use **Force** to overwrite existing files

### Fixtures Workflow (CLI-Based)

```python
# hooks.py — define what to export
fixtures = [
    "Custom Field",
    "Property Setter",
    {"dt": "Client Script", "filters": [["module", "=", "My Module"]]}
]
```

```bash
# Export fixtures to JSON in your app
bench --site mysite export-fixtures --app myapp

# Fixtures auto-sync on: bench --site mysite migrate
```

**NEVER** use Packages to modify standard/core DocTypes — use a Frappe App with Fixtures.

See [frappe-packages.md](references/frappe-packages.md) for the complete reference including decision trees, limitations, and best practices.

---

## Custom App Compatibility Checks

Before upgrading, audit each custom app:

1. **Check deprecated APIs** — Search for removed functions listed in breaking changes
2. **Check `setup.py`** — Must migrate to `pyproject.toml` for v15+
3. **Check Vue components** — Must be Vue 3 compatible for v15+
4. **Check `patches.txt`** — Ensure patches use `[pre_model_sync]`/`[post_model_sync]` sections [v14+]
5. **Check hooks.py** — Verify no removed hooks are used
6. **Run tests** — `bench --site test_site run-tests --app myapp`

---

## Decision Tree: In-Place vs Fresh Install

```
Choosing upgrade strategy:
├── Small site (< 10 GB database)?
│   └── In-place upgrade is usually fine
├── Large site (> 50 GB database)?
│   ├── Many custom apps? → Fresh install + data migration
│   └── Standard apps only? → In-place with extended downtime window
├── Skipping multiple versions (v13 → v15)?
│   └── ALWAYS fresh install — sequential upgrades are too risky
└── Critical production with zero-downtime requirement?
    └── Fresh install on parallel server + DNS switch
```

---

## Version Differences Summary

| Feature | v14 | v15 | v16 |
|---------|:---:|:---:|:---:|
| Python packaging | setup.py | pyproject.toml | pyproject.toml |
| Vue version | Vue 2 | **Vue 3** | Vue 3 |
| Node.js minimum | v14 | **v18** | **v24** |
| Python minimum | 3.8 | 3.10 | **3.14** |
| Server Scripts | Enabled | **Disabled default** | Disabled default |
| Default sort | modified | modified | **creation** |
| patches.txt sections | Yes | Yes | Yes |
| Workspace sidebar | No | No | **Yes** |
| Separated modules | — | Event Streaming | Blog, Newsletter, EPS |

---

## Reference Files

| File | Contents |
|------|----------|
| [examples.md](references/examples.md) | Complete upgrade workflow examples |
| [anti-patterns.md](references/anti-patterns.md) | Common upgrade mistakes and fixes |
| [breaking-changes.md](references/breaking-changes.md) | Detailed breaking changes per version |
| [frappe-packages.md](references/frappe-packages.md) | Packages, fixtures, and moving customizations between sites |
---
name: frappe-ops-website-deploy
description: >
  Deploy HTML/CSS websites to ERPNext/Frappe (v15/v16) as Web Pages via the REST API.
  Use this skill whenever a user wants to host a website on ERPNext, deploy HTML mockups
  to Frappe, create Web Pages programmatically, configure Website Settings, or integrate
  Frappe's Discussion system as a forum. Also use when the user mentions "website on ERPNext",
  "Web Page API", "Page Builder", "Web Template", or wants to serve custom HTML from Frappe.
  Covers: Web Pages with Page Builder, custom Web Templates, Website Settings (navbar, footer),
  CSS management, Frappe Discussion integration, and deployment scripting.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v15-v16, ERPNext v15-v16."
metadata:
  author: OpenAEC-Foundation
  version: "1.0"
---

# Deploy Websites on ERPNext/Frappe

> Patterns for deploying static HTML/CSS websites to ERPNext v15/v16 using Web Pages, Page Builder, and the REST API.

---

## Critical: ERPNext v16 Does NOT Render main_section

In Frappe v16, the `main_section` field on a Web Page is stored but **not rendered** in the browser — even with `content_type: "HTML"` or `dynamic_template: 1`. The Page Builder (`page_blocks`) is the primary rendering mechanism.

**You must use `page_blocks` with a custom Web Template to render HTML content.**

---

## Decision Tree

```
What do you need?
├── Deploy HTML pages to ERPNext
│   ├── Step 1: Create "Raw HTML Section" Web Template (one-time)
│   ├── Step 2: Create Web Pages with page_blocks
│   └── Step 3: Configure Website Settings
│
├── Add a forum / discussion system
│   └── Use Frappe's built-in Discussion Topic/Reply + Discussions Web Template
│
├── Manage CSS
│   ├── Per-page CSS → Web Page `css` field
│   ├── Global CSS → Website Settings `head_html`
│   └── WARNING: Never stack !important overrides (see CSS Management)
│
└── Configure navigation
    └── Website Settings: top_bar_items, footer_items, brand_html, home_page
```

---

## Step 1: Create the Raw HTML Section Web Template

This is a one-time setup. The template accepts raw HTML and renders it as-is.

```
POST /api/resource/Web%20Template
```

```json
{
  "name": "Raw HTML Section",
  "type": "Section",
  "template": "{{ values.html_content }}",
  "fields": [
    {
      "fieldname": "html_content",
      "fieldtype": "Text",
      "label": "HTML Content"
    }
  ]
}
```

**Important constraints:**
- The `fieldtype` must be `"Text"` — Frappe rejects `"Code"` for Web Template fields
- Allowed fieldtypes: `Attach Image`, `Check`, `Data`, `Int`, `Link`, `Select`, `Small Text`, `Text`, `Markdown Editor`, `Section Break`, `Column Break`, `Table Break`
- The template uses `{{ values.html_content }}` (with `values.` prefix) to access field data

---

## Step 2: Create Web Pages with Page Builder

Each page needs `content_type: "Page Builder"` and its HTML in `page_blocks`.

```
POST /api/resource/Web%20Page
```

```json
{
  "title": "Page Title",
  "route": "my-page",
  "published": 1,
  "show_title": 0,
  "full_width": 1,
  "content_type": "Page Builder",
  "css": "<per-page CSS here>",
  "page_blocks": [
    {
      "web_template": "Raw HTML Section",
      "web_template_values": "{\"html_content\": \"<div>Your HTML here</div>\"}"
    }
  ]
}
```

**Critical: `web_template_values` is a JSON string, not an object.** Serialize it with `json.dumps()` before sending.

### Updating an existing page

```
PUT /api/resource/Web%20Page/{url_encoded_name}
```

To find a page by route:
```
GET /api/resource/Web%20Page?filters=[["route","=","my-page"]]&fields=["name"]
```

---

## Step 3: Configure Website Settings

```
PUT /api/resource/Website%20Settings/Website%20Settings
```

```json
{
  "home_page": "home",
  "brand_html": "<span style=\"...\">NL</span> My Brand",
  "head_html": "<link href=\"fonts.css\" rel=\"stylesheet\">\n<style>/* global CSS */</style>",
  "top_bar_items": [
    {"label": "About", "url": "/about", "right": 0}
  ],
  "footer_items": [
    {"label": "About", "url": "/about"}
  ]
}
```

### head_html: Frappe Wrapper Fixes

Frappe wraps page content in several divs that add unwanted whitespace. Add these fixes to `head_html`:

```html
<style>
.page-header-wrapper { display: none !important; }
.page-breadcrumbs { display: none !important; }
.page-content-wrapper { padding: 0 !important; margin: 0 !important; }
.page_content { padding: 0 !important; margin: 0 !important; }
.webpage-content { padding: 0 !important; margin: 0 !important; }
.web-page-content { padding: 0 !important; margin: 0 !important; max-width: none !important; }
.section.section-padding-top { padding-top: 0 !important; }
.section.section-padding-bottom { padding-bottom: 0 !important; }
.web-template-section { padding: 0 !important; margin: 0 !important; }
main { padding: 0 !important; margin: 0 !important; }
</style>
```

These are the **only** `!important` overrides you should use — they target Frappe's own wrapper elements, not your content.

---

## CSS Management

### The golden rule: keep your mockup CSS intact

Use the original mockup CSS in each page's `css` field. Only add Frappe wrapper fixes in `head_html`. Do not layer `!important` overrides on top of your content CSS — this leads to cascading conflicts and unpredictable layouts.

### Where CSS goes

| CSS Type | Where | Field |
|----------|-------|-------|
| Mockup/page CSS | Per Web Page | `css` |
| Google Fonts, Frappe fixes | Website Settings | `head_html` |
| CSS variables (:root) | Website Settings | `head_html` |

### What NOT to do

Never add broad `!important` overrides for content elements like `.card`, `section`, `h2`, etc. If spacing looks wrong, the cause is almost always a Frappe wrapper div — fix that specifically rather than overriding all your content styles.

---

## Deploying from HTML Mockups

When converting a static HTML mockup to ERPNext Web Pages, follow this process:

### 1. Extract the body content

Strip everything outside the main content area — typically between `</header>` and `<footer>`. Remove the mockup's own nav and footer since Frappe provides its own via Website Settings.

### 2. Rewrite links

Replace `.html` file references with Frappe routes:
```
href="about.html"  →  href="/about"
href="index.html"  →  href="/"
```

### 3. Handle images

Local `img/` references won't work on ERPNext. Options:
- Upload images via Frappe File Manager and use the returned URL
- Use the File API: `POST /api/method/upload_file`
- Reference external image URLs

### 4. Deploy script pattern

See `scripts/deploy.py` for a complete deployment script. The key pattern:

```python
import requests, json

def deploy_page(title, route, html_content, css):
    data = {
        "title": title,
        "route": route,
        "published": 1,
        "show_title": 0,
        "full_width": 1,
        "content_type": "Page Builder",
        "css": css,
        "page_blocks": [{
            "web_template": "Raw HTML Section",
            "web_template_values": json.dumps({"html_content": html_content})
        }]
    }
    # Create or update (check 409 conflict for existing pages)
    resp = requests.post(f"{BASE_URL}/api/resource/Web%20Page",
                         headers=HEADERS, json=data)
    if resp.status_code == 409:
        # Find and update existing
        ...
```

---

## Forum Integration with Frappe Discussions

Frappe has built-in DocTypes for discussions that can be embedded on any Web Page.

### Available DocTypes

- **Discussion Topic** — a thread/topic linked to a reference document
- **Discussion Reply** — a reply within a topic

### Creating a forum page

Use the built-in "Discussions" Web Template as a page block:

```json
{
  "page_blocks": [
    {
      "web_template": "Raw HTML Section",
      "web_template_values": "{\"html_content\": \"<section><div class=\\\"container\\\"><h1>Forum</h1></div></section>\"}"
    },
    {
      "web_template": "Discussions",
      "web_template_values": "{\"title\": \"Discussies\", \"cta_title\": \"Nieuw onderwerp\", \"docname\": \"forum\", \"single_thread\": 0}"
    }
  ]
}
```

### Discussions Web Template fields

| Field | Type | Purpose |
|-------|------|---------|
| `title` | Data | Section heading |
| `cta_title` | Data | Button text for new topic |
| `docname` | Link | Web Page to attach discussions to |
| `single_thread` | Check | 0 = multiple topics, 1 = single thread |

### Managing topics via API

```
POST /api/resource/Discussion%20Topic
{"subject": "My topic", "reference_doctype": "Web Page", "reference_docname": "forum"}

POST /api/resource/Discussion%20Reply
{"topic": "TOPIC0001", "reply": "My reply text"}
```

---

## Authentication

All API calls require authentication via token header:

```
Authorization: token {api_key}:{api_secret}
```

Generate API keys in ERPNext: User Settings → API Access → Generate Keys.

**Never store API keys in skill files, SKILL.md, or commit them to git.** Pass them as environment variables or read from a secure config.

---

## Troubleshooting

### Page is blank / main_section not rendering
You're hitting the v16 Page Builder issue. Switch to `content_type: "Page Builder"` with `page_blocks`. See Step 2.

### White bar above content
Frappe's `.page-header-wrapper` and `.page-breadcrumbs` add empty space. Hide them via `head_html`. See Step 3.

### Web Template creation fails with fieldtype error
Use `"Text"` not `"Code"` for the fieldtype. Frappe Web Templates only allow a subset of fieldtypes.

### CSS looks wrong / spacing is off
Check if Frappe's `.section.section-padding-top` or `.page-content-wrapper` are adding padding. Fix those specifically — don't override your content CSS with `!important`.

### Grid layouts collapse to single column
If your mockup CSS has media queries that override grid columns, those will apply on ERPNext too. Check the rendered CSS for conflicting media query rules.

### Images don't show
Local `img/` paths from mockups won't resolve. Upload files to ERPNext or use absolute URLs.
---
name: frappe-syntax-clientscripts
description: >
  Use when writing client-side JavaScript for ERPNext/Frappe form events,
  field manipulation, server calls, or child table handling in v14/v15/v16.
  Covers exact syntax for frappe.ui.form.on, frm methods, frappe.call,
  and browser-side validation. Keywords: client script, form event, frm,
  frappe.call, frappe.ui.form.on, JavaScript, UI interaction, field validation,
  form event syntax, how to write client script, frm example, frappe.call example.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Client Scripts Syntax

Client Scripts run in the browser and control all UI interactions in Frappe/ERPNext. Create them via **Setup > Client Script** or in custom apps under `public/js/`.

**CRITICAL**: Client Script validations ONLY apply in the browser form view. API calls and System Console bypass them. ALWAYS pair with Server Scripts for security-critical validation.

## Quick Reference

| Action | Code |
|--------|------|
| Set value | `frm.set_value('field', value)` |
| Get value | `frm.doc.fieldname` |
| Hide field | `frm.toggle_display('field', false)` |
| Make mandatory | `frm.toggle_reqd('field', true)` |
| Make read-only | `frm.toggle_enable('field', false)` |
| Set field property | `frm.set_df_property('field', 'options', [...])` |
| Filter Link field | `frm.set_query('field', () => ({filters: {}}))` |
| Call server | `frappe.call({method: 'path.to.fn', args: {}})` |
| Call doc method | `frm.call('method_name', {args})` |
| Prevent save | `frappe.throw(__('Error message'))` |
| Add button | `frm.add_custom_button(__('Label'), callback, group)` |
| Add child row | `frm.add_child('table', {values}); frm.refresh_field('table')` |
| Show alert | `frappe.show_alert({message: __('Done'), indicator: 'green'})` |
| Translate string | `__('Text')` or `__('Hello {0}', [name])` |

## Event Decision Tree

```
What do you need to do?
│
├─ One-time setup (queries, formatters)?
│  └─ ALWAYS use setup — runs once per form instance
│
├─ Show/hide fields, add buttons, update UI?
│  └─ ALWAYS use refresh — fires after every load/reload
│
├─ Validate data before save?
│  └─ ALWAYS use validate — use frappe.throw() to block save
│
├─ Modify data right before server save?
│  └─ Use before_save — last chance to change values
│
├─ Run logic after successful save?
│  └─ Use after_save — document is persisted
│
├─ React to a field value change?
│  └─ Use the fieldname as the event name
│
├─ Intercept workflow state change?
│  └─ Use before_workflow_action / after_workflow_action
│
└─ Manipulate DOM after full render?
   └─ Use onload_post_render — NEVER use jQuery selectors directly
```

> See [references/events.md](references/events.md) for complete event list and execution order.

## Form Event Registration

```javascript
// Parent form events
frappe.ui.form.on('Sales Order', {
    setup(frm) { },           // Once per form instance
    refresh(frm) { },         // After every load/reload
    validate(frm) { },        // Before save — throw to block
    fieldname(frm) { }        // On field value change
});

// Child table events — ALWAYS register on the CHILD doctype
frappe.ui.form.on('Sales Order Item', {
    qty(frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.rate);
    },
    items_add(frm, cdt, cdn) { },     // Row added
    items_remove(frm) { },            // Row removed (no cdt/cdn)
    items_move(frm) { }               // Row reordered
});
```

## Value Manipulation

```javascript
// ALWAYS use frm.set_value() — NEVER assign frm.doc.field directly
frm.set_value('status', 'Approved');                        // Single
frm.set_value({status: 'Approved', priority: 'High'});      // Multiple

// Read values (read-only — NEVER write via frm.doc)
let val = frm.doc.fieldname;
let items = frm.doc.items;  // Child table array
```

## Field Properties

```javascript
// Show/hide (accepts single field or array)
frm.toggle_display(['priority', 'due_date'], frm.doc.status === 'Open');

// Mandatory toggle
frm.toggle_reqd('due_date', true);

// Read-only toggle
frm.toggle_enable('amount', false);  // false = read-only

// Arbitrary property change
frm.set_df_property('status', 'options', ['New', 'Open', 'Closed']);
frm.set_df_property('amount', 'read_only', 1);
frm.set_df_property('notes', 'label', 'Internal Notes');

// Intro message at form top
frm.set_intro('This document is pending review', 'orange');
```

## Link Field Filters

```javascript
// ALWAYS set queries in setup event — NEVER in refresh
frappe.ui.form.on('Sales Order', {
    setup(frm) {
        // Simple filter
        frm.set_query('customer', () => ({
            filters: { disabled: 0 }
        }));

        // Child table filter
        frm.set_query('item_code', 'items', (doc, cdt, cdn) => {
            let row = locals[cdt][cdn];
            return { filters: { is_sales_item: 1 } };
        });

        // Server-side query for complex logic
        frm.set_query('customer', () => ({
            query: 'myapp.queries.get_filtered_customers',
            filters: { region: frm.doc.region }
        }));
    }
});
```

## Server Communication

```javascript
// frappe.call — whitelisted Python method
let r = await frappe.call({
    method: 'myapp.api.process_data',
    args: { customer: frm.doc.customer },
    freeze: true,
    freeze_message: __('Processing...')
});
if (r.message) { /* use r.message */ }

// frm.call — document controller method
let result = await frm.call('calculate_taxes', { include_shipping: true });

// frappe.db shortcuts
let val = await frappe.db.get_value('Customer', name, 'credit_limit');
let list = await frappe.db.get_list('Sales Order', {
    filters: { customer: frm.doc.customer },
    fields: ['name', 'grand_total'],
    order_by: 'creation desc',
    limit: 10
});
```

## Child Table Operations

```javascript
// Add row — ALWAYS call refresh_field after
let row = frm.add_child('items', { item_code: 'ITEM-001', qty: 5 });
frm.refresh_field('items');

// Clear all rows
frm.clear_table('items');
frm.refresh_field('items');

// Modify existing rows — refresh_field ONCE after loop
frm.doc.items.forEach(row => {
    row.discount = row.qty > 10 ? 5 : 0;
});
frm.refresh_field('items');

// Set child row value (inside child event handler)
frappe.model.set_value(cdt, cdn, 'amount', row.qty * row.rate);

// Mark form dirty after programmatic changes
frm.dirty();
```

## Custom Buttons

```javascript
refresh(frm) {
    if (frm.doc.docstatus === 1) {
        // Grouped dropdown
        frm.add_custom_button(__('Invoice'), () => {
            frappe.model.open_mapped_doc({
                method: 'erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice',
                frm: frm
            });
        }, __('Create'));

        // Primary action
        frm.page.set_primary_action(__('Process'), () => {
            frm.call('process').then(() => frm.reload_doc());
        });
    }

    // ALWAYS guard buttons with state checks
    if (!frm.is_new() && frm.doc.docstatus === 0) {
        frm.add_custom_button(__('Validate'), () => { /* ... */ });
    }
}
```

## List View Customization

```javascript
frappe.listview_settings['Task'] = {
    add_fields: ['status', 'priority'],
    filters: [['status', '!=', 'Cancelled']],
    hide_name_column: true,

    get_indicator(doc) {
        // ALWAYS return [label, color, filter_field + ',' + filter_value]
        if (doc.status === 'Open') return [__('Open'), 'orange', 'status,=,Open'];
        if (doc.status === 'Closed') return [__('Closed'), 'green', 'status,=,Closed'];
    },

    button: {
        show(doc) { return doc.status === 'Open'; },
        get_label() { return __('Close'); },
        action(doc) { frappe.call({method: 'myapp.api.close', args: {name: doc.name}}); }
    },

    formatters: {
        priority(val) { return val === 'High' ? `<b>${val}</b>` : val; }
    },

    onload(listview) { /* runs once */ },
    refresh(listview) { /* runs on every refresh */ }
};
```

## Dialogs and Prompts

```javascript
// Quick prompt
frappe.prompt({label: 'Reason', fieldname: 'reason', fieldtype: 'Data'},
    (values) => { console.log(values.reason); },
    __('Enter Reason')
);

// Full dialog
let d = new frappe.ui.Dialog({
    title: __('Enter Details'),
    fields: [
        {label: 'Name', fieldname: 'name', fieldtype: 'Data', reqd: 1},
        {label: 'Date', fieldname: 'date', fieldtype: 'Date'}
    ],
    size: 'small',
    primary_action_label: __('Submit'),
    primary_action(values) { d.hide(); /* use values */ }
});
d.show();

// Progress indicator
frappe.show_progress(__('Importing'), 45, 100, __('Please wait'));
```

## Critical Rules

1. **ALWAYS** call `frm.refresh_field('table')` after ANY child table modification
2. **NEVER** assign `frm.doc.field = value` — ALWAYS use `frm.set_value()`
3. **ALWAYS** use `__('text')` for every user-facing string
4. **ALWAYS** place `set_query` in `setup` — NEVER in `refresh`
5. **NEVER** use `async: false` — it freezes the browser
6. **ALWAYS** check `frm.is_new()` before adding action buttons
7. **NEVER** use direct jQuery selectors for field manipulation — use Frappe API
8. **NEVER** store state in global variables — attach to `frm` object instead
9. **ALWAYS** check `r.message` before using server call responses
10. **ALWAYS** use `frappe.throw()` inside `validate` to block save — NEVER `return false` in async handlers

> See [references/methods.md](references/methods.md) for complete API reference.
> See [references/examples.md](references/examples.md) for real-world patterns.
> See [references/anti-patterns.md](references/anti-patterns.md) for common mistakes.

## Related Skills

- `frappe-impl-clientscripts` — Implementation workflows and decision trees
- `frappe-errors-clientscripts` — Error handling and debugging patterns
- `frappe-syntax-whitelisted` — Server-side methods called from client scripts
- `frappe-syntax-doctypes` — DocType field definitions referenced in scripts
---
name: frappe-syntax-controllers
description: >
  Use when writing Python Document Controllers for ERPNext/Frappe DocTypes.
  Covers lifecycle hooks (validate, on_update, on_submit), controller
  override, submittable documents, autoname patterns, UUID naming (v16),
  and the flags system. Keywords: document controller, lifecycle hook,
  validate, on_update, on_submit, autoname, naming series, flags, v14-v16,
  controller example, lifecycle hook order, when to use validate, Python DocType class.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Syntax: Document Controllers

Document Controllers are Python classes that define all server-side logic for a DocType.
EVERY DocType has exactly one controller file. The controller class extends `frappe.model.document.Document`.

## Quick Reference

```python
import frappe
from frappe import _
from frappe.model.document import Document

class SalesOrder(Document):
    def autoname(self):
        """Custom naming logic. Sets self.name."""
        self.name = f"SO-{self.customer_code}-{frappe.utils.now_datetime().year}"

    def validate(self):
        """MAIN validation — runs on EVERY save (insert and update).
        Changes to self ARE saved to database."""
        if not self.items:
            frappe.throw(_("Items are required"))
        self.total = sum(item.amount for item in self.items)

    def on_update(self):
        """After save — changes to self are NOT saved.
        Use frappe.db.set_value() for post-save field changes."""
        self.notify_linked_docs()

    def on_submit(self):
        """After submit (docstatus 0 -> 1). Create ledger entries here."""
        self.create_gl_entries()

    def on_cancel(self):
        """After cancel (docstatus 1 -> 2). Reverse ledger entries here."""
        self.reverse_gl_entries()

    @frappe.whitelist()
    def recalculate(self):
        """Exposed to client JS via frm.call('recalculate')."""
        self.total = sum(item.amount for item in self.items)
        return {"total": self.total}
```

### File Location and Naming

| DocType Name | Class Name | File Path |
|---|---|---|
| Sales Order | `SalesOrder` | `selling/doctype/sales_order/sales_order.py` |
| My Custom Doc | `MyCustomDoc` | `module/doctype/my_custom_doc/my_custom_doc.py` |

**Rule**: DocType name -> PascalCase class -> snake_case filename. ALWAYS match exactly.

---

## Lifecycle Hook Execution Order

### INSERT (new document)

```
before_insert -> before_naming -> autoname -> before_validate -> validate
-> before_save -> [db_insert] -> after_insert -> on_update -> on_change
```

### SAVE (existing document)

```
before_validate -> validate -> before_save -> [db_update]
-> on_update -> on_change
```

### SUBMIT (docstatus 0 -> 1)

```
before_validate -> validate -> before_submit -> [db_update]
-> on_submit -> on_update -> on_change
```

### CANCEL (docstatus 1 -> 2)

```
before_cancel -> [db_update] -> on_cancel -> on_change
```

### UPDATE AFTER SUBMIT

```
before_update_after_submit -> [db_update]
-> on_update_after_submit -> on_change
```

### DELETE

```
on_trash -> [db_delete] -> after_delete
```

### DISCARD [v15+]

```
before_discard -> [db_set docstatus=2] -> on_discard
```

**Complete hook reference with parameters**: See [lifecycle-methods.md](references/lifecycle-methods.md)

---

## Hook Selection Decision Tree

```
What do you need to do?
|
+-- Validate data or calculate fields?
|   +-- validate (changes to self ARE saved)
|
+-- Action AFTER save (emails, sync, linked docs)?
|   +-- on_update (changes to self are NOT saved)
|
+-- Only for NEW documents?
|   +-- after_insert (runs once on first save only)
|
+-- Custom document name?
|   +-- autoname (set self.name)
|
+-- Before/after SUBMIT?
|   +-- Validate before submit? -> before_submit
|   +-- Create entries after submit? -> on_submit
|
+-- Before/after CANCEL?
|   +-- Check linked docs? -> before_cancel
|   +-- Reverse entries? -> on_cancel
|
+-- Cleanup before delete?
|   +-- on_trash
|
+-- React to ANY value change (including db_set)?
|   +-- on_change (MUST be idempotent)
```

---

## Critical Rules

### 1. Changes after on_update are NOT saved

```python
# WRONG - change is lost after on_update
def on_update(self):
    self.status = "Completed"  # NOT saved to database

# CORRECT - use db_set or frappe.db.set_value
def on_update(self):
    self.db_set("status", "Completed")
```

### 2. NEVER call frappe.db.commit() in controllers

```python
# WRONG - breaks Frappe transaction management
def validate(self):
    frappe.db.commit()  # Can cause partial updates on error

# CORRECT - Frappe commits automatically at end of request
def validate(self):
    self.update_related()  # No commit needed
```

### 3. ALWAYS call super() when overriding

```python
# WRONG - parent validation is skipped entirely
def validate(self):
    self.custom_check()

# CORRECT - parent logic preserved
def validate(self):
    super().validate()
    self.custom_check()
```

### 4. Use flags for recursion prevention

```python
def on_update(self):
    if self.flags.get("from_linked_doc"):
        return
    linked = frappe.get_doc("Linked Doc", self.linked_doc)
    linked.flags.from_linked_doc = True
    linked.save()
```

### 5. NEVER put validation logic in on_update

```python
# WRONG - document is already saved when this throws
def on_update(self):
    if self.total < 0:
        frappe.throw("Invalid total")  # Too late!

# CORRECT - validate BEFORE save
def validate(self):
    if self.total < 0:
        frappe.throw("Invalid total")  # Blocks save
```

---

## Document Naming (autoname)

| Method | Example | Result | Version |
|---|---|---|---|
| `field:fieldname` | `field:customer_name` | `ABC Company` | All |
| `naming_series:` | `naming_series:` | `SO-2024-00001` | All |
| Expression | `PRE-.#####` | `PRE-00001` | All |
| Old-style format | `INV-{YYYY}-{####}` | `INV-2024-0001` | Deprecated v16 |
| `hash` / `random` | `hash` | `a1b2c3d4e5` | All |
| `Prompt` | `Prompt` | User enters name | All |
| `autoincrement` | `autoincrement` | `1`, `2`, `3` | All |
| **`UUID`** | `UUID` | `550e8400-e29b-...` | **v16+** |
| Custom method | `autoname()` in controller | Any pattern | All |

### Custom autoname Method

```python
from frappe.model.naming import getseries

class Project(Document):
    def autoname(self):
        prefix = f"P-{self.customer[:3].upper()}-"
        self.name = getseries(prefix, 3)
        # Result: P-ACM-001, P-ACM-002, etc.
```

### UUID Naming [v16+]

Set `autoname = "UUID"` in DocType definition. Frappe generates UUID v4.

```
When to use UUID:              When to use traditional naming:
- Cross-system sync            - User-facing references (SO-00001)
- Bulk record creation         - Sequential numbering required
- Global uniqueness needed     - Auditing requires readable names
```

---

## Controller Extension Mechanisms

### 1. override_doctype_class (full replacement) [All versions]

```python
# hooks.py
override_doctype_class = {
    "Sales Order": "custom_app.overrides.CustomSalesOrder"
}

# custom_app/overrides.py
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder

class CustomSalesOrder(SalesOrder):
    def validate(self):
        super().validate()  # ALWAYS call super()
        self.custom_validation()
```

**WARNING**: Only ONE app can override a DocType class. Multiple overrides conflict.

### 2. extend_doctype_class (mixin, non-destructive) [v16+]

```python
# hooks.py
extend_doctype_class = {
    "Address": ["custom_app.extensions.address.GeocodingMixin"],
    "Contact": [
        "custom_app.extensions.common.ValidationMixin",
        "custom_app.extensions.contact.PhoneMixin"
    ]
}

# custom_app/extensions/address.py
from frappe.model.document import Document

class GeocodingMixin(Document):
    @property
    def full_address(self):
        return f"{self.address_line1}, {self.city}, {self.country}"

    def validate(self):
        super().validate()
        self.geocode_address()
```

**ALWAYS prefer `extend_doctype_class` over `override_doctype_class` in v16+.**
Multiple apps can safely extend the same DocType.

### 3. doc_events (hook individual events) [All versions]

```python
# hooks.py
doc_events = {
    "Sales Order": {
        "validate": "custom_app.events.validate_sales_order",
        "on_submit": "custom_app.events.on_submit_sales_order"
    },
    "*": {  # ALL DocTypes
        "after_insert": "custom_app.events.log_creation"
    }
}

# custom_app/events.py
def validate_sales_order(doc, method=None):
    if doc.total > 100000:
        doc.requires_approval = 1
```

### When to Use Which

```
Need full class replacement?     -> override_doctype_class [all versions]
Need to add methods/properties?  -> extend_doctype_class [v16+]
Need to hook one or two events?  -> doc_events [all versions]
Need to extend in v14/v15?       -> override_doctype_class or doc_events
```

---

## Whitelisted Methods

Expose controller methods to client-side JavaScript with `@frappe.whitelist()`:

```python
class SalesOrder(Document):
    @frappe.whitelist()
    def send_email(self, recipient):
        """Callable from JS: frm.call('send_email', {recipient: '...'})"""
        frappe.sendmail(recipients=[recipient], message="Order confirmed")
        return {"status": "sent"}
```

```javascript
// Client-side call
frm.call('send_email', { recipient: 'customer@example.com' })
    .then(r => frappe.msgprint(r.message.status));
```

**Rules**:
- ALWAYS add `@frappe.whitelist()` decorator — without it, the method is NOT callable from client
- The method MUST be defined on the controller class (not standalone)
- Permission checks happen automatically (user must have read access to the document)

---

## Submittable Documents

Documents with `is_submittable = 1` follow the docstatus lifecycle:

| docstatus | State | Editable | Transitions |
|---|---|---|---|
| 0 | Draft | Yes | -> 1 (Submit) |
| 1 | Submitted | Only "Allow on Submit" fields | -> 2 (Cancel) |
| 2 | Cancelled | No | None (amend creates new Draft) |

ALWAYS implement both `on_submit` and `on_cancel` as a pair.
ALWAYS reverse in `on_cancel` what `on_submit` created.

---

## Inheritance Patterns

```python
# Standard controller
from frappe.model.document import Document
class MyDoc(Document): pass

# Tree DocType (hierarchical)
from frappe.utils.nestedset import NestedSet
class Department(NestedSet):
    nsm_parent_field = "parent_department"

# Virtual DocType (no database table)
class ExternalData(Document):
    def load_from_db(self): ...
    def db_insert(self, *args, **kwargs): ...
    def db_update(self, *args, **kwargs): ...
    @staticmethod
    def get_list(args): ...
    @staticmethod
    def get_count(args): ...
```

---

## Type Annotations [v15+]

```python
class Person(Document):
    if TYPE_CHECKING:
        from frappe.types import DF
        first_name: DF.Data
        last_name: DF.Data
        birth_date: DF.Date
        company: DF.Link
```

Enable auto-generation in `hooks.py`: `export_python_type_annotations = True`

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---|---|---|---|
| Type annotations | No | Auto-generated | Yes |
| `before_discard` / `on_discard` | No | Yes | Yes |
| `flags.notify_update` | No | Yes | Yes |
| `extend_doctype_class` | No | No | **Yes** |
| UUID autoname | No | No | **Yes** |
| Old-style format naming | Yes | Yes | Deprecated |

---

## Reference Files

| File | Contents |
|---|---|
| [lifecycle-methods.md](references/lifecycle-methods.md) | All hooks with execution order diagrams |
| [document-api-complete.md](references/document-api-complete.md) | **Complete Document API**: all methods by category (CRUD, fields, DB, permissions, flags, child tables, naming) |
| [methods.md](references/methods.md) | Document class method signatures |
| [events.md](references/events.md) | All document events in order |
| [examples.md](references/examples.md) | Complete working controller examples |
| [anti-patterns.md](references/anti-patterns.md) | Common mistakes and corrections |
| [flags.md](references/flags.md) | Flags system (doc.flags, frappe.flags) |
| [hooks.md](references/hooks.md) | Controller interaction with hooks.py |
| [patterns.md](references/patterns.md) | Common controller patterns |
| [syntax.md](references/syntax.md) | Controller class syntax reference |

## Related Skills

- `frappe-syntax-serverscripts` -- Server Scripts (sandbox alternative)
- `frappe-syntax-hooks` -- hooks.py configuration
- `frappe-impl-controllers` -- Implementation workflows
- `frappe-core-permissions` -- Permission system
---
name: frappe-syntax-customapp
description: >
  Use when building Frappe custom apps from scratch. Covers app structure,
  pyproject.toml configuration, module creation, patches, and fixtures
  for v14/v15/v16. Prevents common mistakes with app scaffolding and
  module organization. Keywords: custom app, bench new-app, pyproject.toml,
  patches, fixtures, modules, app structure,
  app boilerplate, bench new-app example, module setup, patch example.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Custom App Syntax

Deterministic syntax reference for building Frappe custom apps — scaffolding, configuration, modules, patches, and fixtures.

## Decision Tree

```
What do you need?
├─ Brand new app from scratch → bench new-app
├─ Extend existing ERPNext behavior → bench new-app + required_apps = ["frappe", "erpnext"]
├─ Install existing app from Git → bench get-app <url>
└─ Add functionality to an installed app
   ├─ New data model → Add module to modules.txt + create DocType
   ├─ New fields on existing DocType → Fixtures (Custom Field)
   ├─ Modify field properties → Fixtures (Property Setter)
   └─ Data migration → Patch in patches.txt

New app vs extend existing?
├─ Independent functionality → New app
├─ Tightly coupled to one app → New app with required_apps dependency
└─ Small customization (fields, properties) → Extend via fixtures in existing custom app
```

## Creating an App

```bash
# Create new app (interactive prompts for title, description, publisher, etc.)
bench new-app my_custom_app

# Install on site
bench --site mysite install-app my_custom_app

# Get existing app from Git
bench get-app https://github.com/org/my_custom_app

# Build frontend assets
bench build --app my_custom_app

# Run migrations (patches + fixtures + schema sync)
bench --site mysite migrate
```

## App Directory Structure

### [v15+] pyproject.toml (Primary)

```
apps/my_custom_app/
├── pyproject.toml                     # Build configuration (flit)
├── README.md
├── my_custom_app/                     # Inner Python package
│   ├── __init__.py                    # MUST contain __version__
│   ├── hooks.py                       # Frappe integration hooks
│   ├── modules.txt                    # Module registration
│   ├── patches.txt                    # Migration scripts
│   ├── patches/                       # Patch files
│   │   └── __init__.py
│   ├── my_custom_app/                 # Default module (same name as app)
│   │   ├── __init__.py
│   │   └── doctype/
│   ├── public/                        # Static assets → /assets/my_custom_app/
│   │   ├── css/
│   │   └── js/
│   ├── templates/                     # Jinja templates
│   │   └── includes/
│   └── www/                           # Portal pages (URL = directory path)
└── .git/
```

### [v14] setup.py (Legacy)

```
apps/my_custom_app/
├── setup.py                           # Build configuration (setuptools)
├── MANIFEST.in
├── requirements.txt                   # Python dependencies
├── dev-requirements.txt               # Dev dependencies (developer_mode only)
├── package.json                       # Node dependencies
├── my_custom_app/
│   ├── __init__.py
│   ├── hooks.py
│   ├── modules.txt
│   ├── patches.txt
│   └── [same inner structure as v15]
└── .git/
```

## Critical Files

### __init__.py (REQUIRED)

```python
# my_custom_app/__init__.py
__version__ = "0.0.1"
```

**CRITICAL**: Without `__version__`, the flit build FAILS and the app CANNOT be installed.

### pyproject.toml [v15+]

```toml
[build-system]
requires = ["flit_core >=3.4,<4"]
build-backend = "flit_core.buildapi"

[project]
name = "my_custom_app"
authors = [
    { name = "Your Company", email = "dev@example.com" }
]
description = "Description of your app"
requires-python = ">=3.10"
readme = "README.md"
dynamic = ["version"]
dependencies = []            # Python packages ONLY — NEVER Frappe/ERPNext

[tool.bench.frappe-dependencies]
frappe = ">=15.0.0,<16.0.0"
erpnext = ">=15.0.0,<16.0.0"  # Only if app extends ERPNext
```

**CRITICAL rules for pyproject.toml**:
- `name` MUST match the inner directory name exactly
- `dynamic = ["version"]` is REQUIRED — flit reads `__version__` from `__init__.py`
- NEVER put `frappe` or `erpnext` in `[project] dependencies` (they are not on PyPI)
- ALWAYS put Frappe app dependencies in `[tool.bench.frappe-dependencies]`

### setup.py [v14] (Legacy)

```python
from setuptools import setup, find_packages

setup(
    name="my_custom_app",
    version="0.0.1",
    description="Description of your app",
    author="Your Company",
    author_email="dev@example.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
)
```

### hooks.py (Minimal Skeleton)

```python
app_name = "my_custom_app"
app_title = "My Custom App"
app_publisher = "Your Company"
app_description = "Description"
app_email = "dev@example.com"
app_license = "MIT"

required_apps = ["frappe"]  # Or ["frappe", "erpnext"] if extending ERPNext

fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "My Custom App"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "My Custom App"]]},
]
```

## Modules

### modules.txt

```
My Custom App
Integrations
Settings
Reports
```

**Rules**:
- One module name per line — NEVER leave empty lines or trailing spaces
- Module name uses spaces; directory name uses underscores (`My Custom App` → `my_custom_app/`)
- Every DocType MUST belong to a registered module
- ALWAYS include `__init__.py` in every module directory

### Module Directory Structure

```
my_custom_app/
├── my_custom_app/       # "My Custom App" module
│   ├── __init__.py
│   └── doctype/
├── integrations/        # "Integrations" module
│   ├── __init__.py
│   └── doctype/
├── settings/            # "Settings" module
│   ├── __init__.py
│   └── doctype/
└── reports/             # "Reports" module
    ├── __init__.py
    └── report/
```

### DocType Directory (within a module)

```
doctype/my_doctype/
├── __init__.py              # Empty (REQUIRED)
├── my_doctype.json          # DocType definition (generated by UI)
├── my_doctype.py            # Python controller
├── my_doctype.js            # Client script
├── test_my_doctype.py       # Unit tests
└── my_doctype_dashboard.py  # Dashboard config
```

## Patches (Migration Scripts)

### patches.txt with INI Sections

```ini
[pre_model_sync]
# Runs BEFORE schema sync — old fields still available
myapp.patches.v1_0.backup_old_data

[post_model_sync]
# Runs AFTER schema sync — new fields available
myapp.patches.v1_0.populate_new_fields
myapp.patches.v1_0.cleanup_data
```

### Patch Implementation

```python
# myapp/patches/v1_0/populate_new_fields.py
import frappe

def execute():
    """Populate new fields with default values."""
    batch_size = 1000
    offset = 0

    while True:
        records = frappe.get_all(
            "MyDocType",
            filters={"new_field": ["is", "not set"]},
            fields=["name"],
            limit_page_length=batch_size,
            limit_start=offset,
        )
        if not records:
            break

        for record in records:
            frappe.db.set_value(
                "MyDocType", record.name,
                "new_field", "default_value",
                update_modified=False,
            )

        frappe.db.commit()
        offset += batch_size
```

### Pre vs Post Model Sync

| Situation | Section | Reason |
|-----------|---------|--------|
| Migrate data from old field | `[pre_model_sync]` | Old field still exists |
| Rename field + preserve data | `[pre_model_sync]` | Old name still available |
| Populate new required fields | `[post_model_sync]` | New field already exists |
| General data cleanup | `[post_model_sync]` | No schema dependency |

### Re-running a Patch

```
# Patches run ONCE. To re-run, make the line unique with a comment:
myapp.patches.v1_0.my_patch #2024-01-15
```

### bench migrate Workflow

1. `before_migrate` hooks execute
2. `[pre_model_sync]` patches execute
3. Database schema sync (DocType JSON → tables)
4. `[post_model_sync]` patches execute
5. Fixtures sync
6. `after_migrate` hooks execute

## Fixtures

### hooks.py Configuration

```python
fixtures = [
    "Category",                                              # All records
    {"dt": "Custom Field", "filters": [["module", "=", "My Custom App"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "My Custom App"]]},
    {"dt": "Role", "filters": [["name", "like", "MyApp%"]]},
]
```

### Exporting and Importing

```bash
# Export fixtures to JSON files
bench --site mysite export-fixtures --app my_custom_app

# Import happens automatically during bench migrate or install-app
```

### Fixtures vs Patches

| What | Fixtures | Patches |
|------|:--------:|:-------:|
| Custom Fields | YES | NO |
| Property Setters | YES | NO |
| Roles, Workflows | YES | NO |
| Data transformation | NO | YES |
| One-time migration | NO | YES |
| Seed configuration data | YES | NO |

### Fixture Ordering

ALWAYS order fixtures so dependencies come first:

```python
fixtures = [
    "Workflow State",   # FIRST — Workflow depends on states
    "Workflow",         # SECOND
]
```

## Version Differences

| Aspect | v14 | v15+ | v16+ |
|--------|-----|------|------|
| Build config | setup.py | pyproject.toml | pyproject.toml |
| Build backend | setuptools | flit_core | flit_core |
| Dependencies file | requirements.txt | pyproject.toml | pyproject.toml |
| Python minimum | >=3.10 | >=3.10 | >=3.14 |
| INI patches | YES | YES | YES |

### Migration v14 to v15

1. Create `pyproject.toml` with flit_core build-system
2. Move dependencies from `requirements.txt` to `[project] dependencies`
3. Verify `__version__` in `__init__.py`
4. Optionally remove: `setup.py`, `MANIFEST.in`, `requirements.txt`
5. Test with `bench get-app` and `bench install-app`

## Critical Rules

### ALWAYS

1. Define `__version__` in `__init__.py` — flit build fails without it
2. Add `dynamic = ["version"]` in pyproject.toml
3. Register EVERY module in `modules.txt`
4. Include `__init__.py` in EVERY Python directory
5. Put Frappe dependencies in `[tool.bench.frappe-dependencies]`, NEVER in `[project] dependencies`
6. Use batch processing and error handling in patches
7. Set `module` field on Custom Fields and Property Setters for correct fixture export
8. Order fixtures by dependency (states before workflows)

### NEVER

1. Put `frappe` or `erpnext` in pip dependencies (not on PyPI — install fails)
2. Create patches without try/except and logging
3. Include user data or transactional data (Sales Invoice, User) in fixtures
4. Hardcode site-specific values in patches
5. Process large datasets without batching and periodic `frappe.db.commit()`
6. Use spaces in directory names (spaces in `modules.txt` only)
7. Change module names after DocTypes have been created in production

## Reference Files

| File | Contents |
|------|----------|
| [structure.md](references/structure.md) | Complete directory structure for v14 and v15 |
| [pyproject-toml.md](references/pyproject-toml.md) | Full pyproject.toml and setup.py configuration |
| [modules.md](references/modules.md) | Module organization, naming, workspaces |
| [patches.md](references/patches.md) | Patch syntax, pre/post model sync, batch processing |
| [fixtures.md](references/fixtures.md) | Fixture configuration, filters, common DocTypes |
| [examples.md](references/examples.md) | Complete minimal and ERPNext extension app examples |
| [anti-patterns.md](references/anti-patterns.md) | Top 10 mistakes and corrections |

## See Also

- `frappe-syntax-hooks` — Full hooks.py reference
- `frappe-syntax-controllers` — DocType controller methods
- `frappe-impl-customapp` — Implementation patterns and workflows
---
name: frappe-syntax-doctypes
description: >
  Use when creating or modifying DocType JSON definitions, choosing fieldtypes, configuring naming rules, adding child tables, or setting up tree structures.
  Prevents invalid DocType configurations from wrong fieldtype choices, broken naming rules, and misconfigured child table links.
  Covers DocType JSON schema, all fieldtypes and their properties, autoname/naming_rule patterns, child table (Table fieldtype), tree DocTypes, virtual DocTypes, Single DocTypes.
  Keywords: DocType, fieldtype, naming_rule, autoname, child table, tree, virtual DocType, Single, JSON definition, Custom Field, Customize Form, add field without code, hierarchy, tree view, field types list..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# DocType JSON Design

DocTypes are the foundation of every Frappe application. A DocType defines both the **data model** (database schema) and the **view** (form layout). ALWAYS design DocTypes before writing any controller logic.

## Quick Reference

### DocType JSON Top-Level Properties

| Property | Type | Purpose |
|----------|------|---------|
| `name` | str | DocType identifier (singular, e.g. "Sales Invoice") |
| `module` | str | App module this DocType belongs to |
| `is_submittable` | bool | Enables Draft -> Submitted -> Cancelled workflow |
| `is_tree` | bool | Enables NestedSet hierarchy (lft/rgt columns) |
| `is_virtual` | bool | No database table; data from custom backend |
| `issingle` | bool | Single-instance settings document |
| `istable` | bool | Child table DocType (embedded in parent) |
| `is_calendar_and_gantt` | bool | Enables calendar/gantt views |
| `track_changes` | bool | Stores version history on every save |
| `track_seen` | bool | Tracks which users viewed the document |
| `track_views` | bool | Counts total document views |
| `allow_rename` | bool | Permits renaming after creation |
| `allow_copy` | bool | Enables "Duplicate" action |
| `allow_import` | bool | Enables Data Import for this DocType |
| `naming_rule` | str | Naming method selector (see Naming section) |
| `autoname` | str | Naming pattern string |
| `title_field` | str | Field used as display title |
| `search_fields` | str | Comma-separated fields for search results |
| `show_title_field_in_link` | bool | Display title instead of name in Link fields |
| `image_field` | str | Field containing image for avatar display |
| `sort_field` | str | Default sort column |
| `sort_order` | str | "ASC" or "DESC" |
| `default_print_format` | str | Print Format name |
| `max_attachments` | int | Attachment limit |

### Common Fieldtypes (Quick Lookup)

| Fieldtype | Stores | DB Column |
|-----------|--------|-----------|
| Data | Text up to 140 chars | VARCHAR(140) |
| Link | Reference to another DocType | VARCHAR(140) |
| Dynamic Link | Reference to any DocType | VARCHAR(140) |
| Select | Single choice from options | VARCHAR(140) |
| Table | Child table rows | Separate table |
| Table MultiSelect | Multi-select link rows | Separate table |
| Check | Boolean 0/1 | TINYINT |
| Int | Whole number | INT |
| Float | Decimal (9 places) | DECIMAL |
| Currency | Money value (6 decimals) | DECIMAL |
| Date | Calendar date | DATE |
| Datetime | Date + time | DATETIME |
| Text Editor | Rich text (HTML) | LONGTEXT |
| Attach | File reference | VARCHAR(140) |
| Small Text | Short multi-line text | TEXT |
| Long Text | Unlimited text | LONGTEXT |

> Full fieldtype reference with all 35+ types: [references/fieldtypes.md](references/fieldtypes.md)

### Essential Field Properties

| Property | Type | Purpose |
|----------|------|---------|
| `reqd` | bool | Field is mandatory |
| `unique` | bool | Database UNIQUE constraint |
| `search_index` | bool | Database INDEX for faster queries |
| `in_list_view` | bool | Show in list view columns |
| `in_standard_filter` | bool | Show as filter in list view |
| `in_preview` | bool | Show in document preview |
| `allow_on_submit` | bool | Editable after submission |
| `read_only` | bool | Not editable by user |
| `hidden` | bool | Not visible on form |
| `depends_on` | str | Visibility condition (e.g. `eval:doc.status=="Active"`) |
| `mandatory_depends_on` | str | Conditional mandatory |
| `read_only_depends_on` | str | Conditional read-only |
| `fetch_from` | str | Auto-populate from linked doc (e.g. `customer.customer_name`) |
| `fetch_if_empty` | bool | Only fetch when field is empty |
| `options` | str | Fieldtype-specific (DocType name, select options, etc.) |
| `default` | str | Default value (supports `__user`, `Today`, etc.) |
| `description` | str | Help text below field |
| `collapsible` | bool | Section starts collapsed (Section Break only) |

## Decision Tree: Which DocType Type?

```
Need to store data?
├─ YES: Need multiple records?
│  ├─ YES: Need submit/cancel workflow?
│  │  ├─ YES → Standard DocType + is_submittable=1
│  │  └─ NO: Need hierarchy/tree?
│  │     ├─ YES → Tree DocType (is_tree=1)
│  │     └─ NO: Embedded in parent?
│  │        ├─ YES → Child DocType (istable=1)
│  │        └─ NO → Standard DocType
│  └─ NO: Single config/settings → Single DocType (issingle=1)
└─ NO: Data from external source → Virtual DocType (is_virtual=1)
```

## Naming Rules

ALWAYS set `naming_rule` on the DocType. The `autoname` field holds the pattern.

| naming_rule Value | autoname Pattern | Example Output |
|-------------------|------------------|----------------|
| Set by User | _(empty)_ | User types name manually |
| Autoincrement | _(empty)_ | `1`, `2`, `3` |
| By Fieldname | `field:{fieldname}` | Value of that field |
| By Naming Series | `naming_series:` | `INV-2024-00001` (from series field) |
| Expression | `PRE-.#####` | `PRE-00001`, `PRE-00002` |
| Expression (Old Style) | `{prefix}-{YYYY}-{#####}` | `INV-2024-00001` |
| Random | `hash` | Random 10-char string |
| UUID | _(empty)_ | `550e8400-e29b-...` |
| By Script | _(custom)_ | Controller `autoname()` decides |

> NEVER use Autoincrement in production -- gaps appear when records are deleted. Use Expression or Naming Series instead.

> Full naming reference: [references/naming.md](references/naming.md)

## Child Table Design

A Child DocType is a DocType with `istable=1`. It ALWAYS belongs to a parent.

**Parent side** -- add a field with:
- `fieldtype`: `Table` (or `Table MultiSelect`)
- `options`: Child DocType name

**Child records automatically get**:
- `parent` -- name of the parent document
- `parenttype` -- DocType of the parent
- `parentfield` -- fieldname of the Table field in parent
- `idx` -- row order (1-based)

```python
# Adding child rows programmatically
doc = frappe.get_doc("Sales Invoice", "INV-001")
doc.append("items", {
    "item_code": "ITEM-001",
    "qty": 5,
    "rate": 100.0
})
doc.save()
```

> NEVER create a Child DocType without `istable=1`. NEVER reference a non-child DocType in a Table field.

### Table vs Table MultiSelect

| Aspect | Table | Table MultiSelect |
|--------|-------|-------------------|
| UI | Full editable grid with "Add Row" | Tag-style picker, no "Add Row" |
| Child DocType | Full child with many fields | Typically 1 Link field only |
| Use case | Line items, detail rows | Multi-select references |

## Single DocType (Settings Pattern)

Set `issingle=1`. Data is stored in `tabSingles` as key-value pairs, NOT in a dedicated table.

```python
# Access Single DocType
settings = frappe.get_single("My Settings")
value = settings.some_field

# Or directly
value = frappe.db.get_single_value("My Settings", "some_field")
```

- NEVER expect a list view for Single DocTypes -- they have exactly one instance.
- ALWAYS use for app-wide configuration (API keys, default values, feature toggles).

## Tree DocType (NestedSet)

Set `is_tree=1`. Frappe adds `lft`, `rgt`, `parent_{doctype_fieldname}`, `old_parent` columns automatically.

- ALWAYS define a `parent_field` in the DocType JSON (e.g. `parent_account` for Chart of Accounts).
- The NestedSet model uses `lft`/`rgt` integers for efficient subtree queries.
- NEVER manually edit `lft`/`rgt` values. Use `frappe.utils.nestedset.rebuild_tree()` if corrupted.

```python
# Get all descendants
descendants = frappe.get_all("Account",
    filters={"lft": [">", node.lft], "rgt": ["<", node.rgt]})

# Get ancestors (path to root)
ancestors = frappe.get_all("Account",
    filters={"lft": ["<", node.lft], "rgt": [">", node.rgt]},
    order_by="lft asc")
```

## Virtual DocType

Set `is_virtual=1`. No database table is created. ALWAYS implement these controller methods:

```python
class MyVirtualDoc(Document):
    def db_insert(self, *args, **kwargs):
        # Persist to your custom backend
        pass

    def load_from_db(self):
        # Load document data from your source
        pass

    def db_update(self, *args, **kwargs):
        # Update in your custom backend
        pass

    def delete(self):
        # Remove from your custom backend
        pass

    @staticmethod
    def get_list(args):
        # Return list of documents
        pass

    @staticmethod
    def get_count(args):
        # Return total count
        pass

    @staticmethod
    def get_stats(args):
        # Return statistics
        pass
```

> NEVER use `frappe.db.*` calls for Virtual DocType data -- they only work with the site database, not your custom backend.

## Customization APIs

### Custom Fields (Programmatic)

```python
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

# Dict format: {DocType: [field_dicts]}
create_custom_fields({
    "Sales Invoice": [
        dict(fieldname="custom_tracking", label="Tracking ID",
             fieldtype="Data", insert_after="naming_series")
    ],
    "Purchase Order": [
        dict(fieldname="custom_vendor_ref", label="Vendor Ref",
             fieldtype="Data", insert_after="supplier")
    ]
}, update=True)
```

### Property Setter (Programmatic)

```python
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

# Change a field property on an existing DocType
make_property_setter("Sales Invoice", "customer", "reqd", 1, "Check")
make_property_setter("Sales Invoice", "posting_date", "default", "Today", "Text")
```

> Full customization reference: [references/customization.md](references/customization.md)

## Data Masking (v16+)

Fields with `mask=1` hide sensitive values from users without `mask` permission at the field's `permlevel`. The server replaces values with patterns like `XXXXXXXX` before sending to the client. Administrator ALWAYS sees unmasked values.

```json
{ "fieldname": "phone", "fieldtype": "Data", "options": "Phone", "mask": 1, "permlevel": 1 }
```

> Full masking reference: [references/data-masking.md](references/data-masking.md)

## Python Type Stubs

Frappe auto-generates type annotations in controller files via `TypeExporter`. Fields get `DF.*` types inside a `TYPE_CHECKING` guard:

```python
if TYPE_CHECKING:
    from frappe.types import DF
    customer: DF.Link
    items: DF.Table[SalesInvoiceItem]
    status: DF.Literal["Draft", "Submitted", "Paid"]
```

NEVER modify code between `# begin: auto-generated types` and `# end: auto-generated types`.

> Full type stubs reference: [references/type-stubs.md](references/type-stubs.md)

## Critical Rules

1. ALWAYS name DocTypes in **singular** form ("Sales Invoice", not "Sales Invoices").
2. ALWAYS use the `tab` prefix mentally -- the DB table is `tabSales Invoice`.
3. NEVER exceed 140 characters for Data/Link/Select field values.
4. ALWAYS set `search_index=1` on fields used in frequent filters or `get_list` calls.
5. ALWAYS set `in_standard_filter=1` on fields users frequently filter by.
6. NEVER use `allow_on_submit=1` on child table fields that affect calculations without recalculating totals.
7. ALWAYS set `fetch_if_empty=1` alongside `fetch_from` unless you want to overwrite user edits.
8. NEVER define `depends_on` with raw Python -- use `eval:doc.fieldname == "value"` syntax.

## See Also

- [references/fieldtypes.md](references/fieldtypes.md) -- Complete fieldtype reference
- [references/naming.md](references/naming.md) -- All naming methods with examples
- [references/examples.md](references/examples.md) -- Real DocType JSON examples
- [references/anti-patterns.md](references/anti-patterns.md) -- Common schema design mistakes
- [references/customization.md](references/customization.md) -- Custom Fields and Property Setter APIs
- [references/data-masking.md](references/data-masking.md) -- Field-level data masking for privacy (v16+)
- [references/type-stubs.md](references/type-stubs.md) -- Python type hints, DF types, TypeExporter
---
name: frappe-syntax-hooks-events
description: >
  Use when implementing document lifecycle hooks via doc_events in hooks.py, understanding event execution order, or extending/overriding document behavior from another app.
  Prevents silent hook failures from wrong event names, incorrect execution order assumptions, and broken override chains.
  Covers doc_events hook syntax, all document events (before_insert, validate, on_submit, etc.), event execution order, extend vs override behavior, cross-app doc_events.
  Keywords: doc_events, hooks.py, before_insert, validate, on_submit, on_cancel, lifecycle, document events, override, extend, event order, which event fires when, before_save vs validate, document event list..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Document Lifecycle Hooks (doc_events)

## Quick Reference: Event Execution Order

### Insert (new document)

| Order | Event               | Purpose                              | Can Raise? |
|-------|---------------------|--------------------------------------|------------|
| 1     | `before_insert`     | Set defaults before naming           | YES        |
| 2     | `before_naming`     | Modify naming logic                  | YES        |
| 3     | `autoname`          | Set the `name` property              | YES        |
| 4     | `before_validate`   | Auto-set missing values              | YES        |
| 5     | `validate`          | Validation logic — throw to abort    | YES        |
| 6     | `before_save`       | Final mutations before DB write      | YES        |
| 7     | `db_insert`         | *Internal* — writes row to DB        | —          |
| 8     | `after_insert`      | Post-insert logic (runs once ever)   | YES        |
| 9     | `on_update`         | Post-save logic (runs on every save) | YES        |
| 10    | `on_change`         | Fires if any field value changed     | YES        |

### Save (existing document)

| Order | Event             | Purpose                           |
|-------|-------------------|-----------------------------------|
| 1     | `before_validate` | Auto-set missing values           |
| 2     | `validate`        | Validation logic — throw to abort |
| 3     | `before_save`     | Final mutations before DB write   |
| 4     | `db_update`       | *Internal* — updates row in DB    |
| 5     | `on_update`       | Post-save logic                   |
| 6     | `on_change`       | Fires if any field value changed  |

### Submit

| Order | Event             | Purpose                            |
|-------|-------------------|------------------------------------|
| 1     | `before_validate` | Auto-set missing values            |
| 2     | `validate`        | Validation logic                   |
| 3     | `before_save`     | Final mutations before DB write    |
| 4     | `before_submit`   | Pre-submit logic — throw to abort  |
| 5     | `db_update`       | *Internal* — updates row in DB     |
| 6     | `on_submit`       | Post-submit logic (GL entries etc) |
| 7     | `on_update`       | Post-save logic                    |
| 8     | `on_change`       | Fires if any field value changed   |

### Cancel

| Order | Event             | Purpose                             |
|-------|-------------------|-------------------------------------|
| 1     | `before_cancel`   | Pre-cancel validation               |
| 2     | `db_update`       | *Internal* — updates row in DB      |
| 3     | `on_cancel`       | Post-cancel logic (reverse GL etc)  |
| 4     | `on_change`       | Fires if any field value changed    |

### Delete

| Order | Event          | Purpose                        |
|-------|----------------|--------------------------------|
| 1     | `on_trash`     | Pre-delete cleanup             |
| 2     | `after_delete` | Post-delete logic              |

### Other Operations

| Operation              | Events (in order)                                        |
|------------------------|----------------------------------------------------------|
| Rename                 | `before_rename` → `after_rename`                         |
| Amend                  | `before_insert` chain runs on the new amended doc        |
| Update After Submit    | `before_update_after_submit` → `db_update` → `on_update_after_submit` → `on_change` |

---

## doc_events in hooks.py: Syntax

### Basic Structure

```python
# hooks.py
doc_events = {
    "Sales Invoice": {
        "on_submit": "myapp.events.sales_invoice.on_submit",
        "on_cancel": "myapp.events.sales_invoice.on_cancel",
    },
    "Purchase Order": {
        "validate": "myapp.events.purchase_order.validate",
    }
}
```

### Wildcard: Apply to ALL DocTypes

```python
doc_events = {
    "*": {
        "after_insert": "myapp.events.global_handler.after_insert_all",
        "on_update": "myapp.events.global_handler.track_changes",
    }
}
```

ALWAYS use `"*"` (string with asterisk) as the key. This fires the handler for every DocType.

### Multiple Handlers per Event

```python
doc_events = {
    "Sales Invoice": {
        "on_submit": [
            "myapp.events.accounting.create_gl_entries",
            "myapp.events.notifications.send_invoice_email",
        ]
    }
}
```

### Handler Function Signature

```python
# myapp/events/sales_invoice.py
def on_submit(doc, method=None):
    """
    doc    — the Document instance (e.g., Sales Invoice)
    method — string name of the event (e.g., "on_submit"), or None
    """
    if doc.grand_total > 10000:
        frappe.sendmail(...)
```

ALWAYS accept `method` as the second parameter (with default `None`). Frappe passes it automatically.

---

## Decision Tree: Which Event to Use

### "I need to validate data before saving"
→ Use `validate`. ALWAYS raise `frappe.throw()` here to block invalid saves.

### "I need to set default values automatically"
→ Use `before_validate`. This runs before `validate`, so your defaults are set before validation checks.

### "I need to run logic only on first creation"
→ Use `after_insert`. This fires ONLY on insert, NEVER on subsequent saves.

### "I need to run logic on every save (insert + update)"
→ Use `on_update`. This fires on both insert and save operations.

### "I need to create linked documents after submit"
→ Use `on_submit`. NEVER create linked docs in `validate` — the document is not yet committed.

### "I need to reverse linked documents on cancel"
→ Use `on_cancel`. ALWAYS clean up GL entries, stock ledger entries, and linked docs here.

### "I need to modify the document name"
→ Use `autoname` in the controller, or `before_naming` for conditional logic.

### "I need to prevent deletion under certain conditions"
→ Use `on_trash`. Raise `frappe.throw()` to block deletion.

### "I need to update a submitted document's fields"
→ Use `before_update_after_submit` for validation and `on_update_after_submit` for side effects.

### "I need logic that runs only when values actually changed"
→ Use `on_change`. This fires only when at least one field value differs from the DB state.

---

## doc_events vs Controller Events

Both mechanisms trigger the SAME events. The difference is WHERE you register them.

| Aspect              | Controller (class method)            | doc_events (hooks.py)                    |
|---------------------|--------------------------------------|------------------------------------------|
| **Location**        | `{doctype}.py` controller file       | `hooks.py` in your app                   |
| **Use when**        | You OWN the DocType                  | You are EXTENDING another app's DocType  |
| **Execution**       | Runs first (controller)              | Runs after controller method             |
| **Multiple apps**   | Only one controller per DocType      | Multiple apps can register handlers      |

ALWAYS use `doc_events` when hooking into a DocType you do NOT own. NEVER modify another app's controller file directly.

### Execution Order Within a Single Event

For a given event (e.g., `validate`):
1. Controller method runs first (`def validate(self)`)
2. `doc_events` handlers run in app installation order
3. Wildcard `"*"` handlers run after specific DocType handlers

---

## extend_doctype_class [v16+]

In Frappe v16+, `extend_doctype_class` provides a cleaner alternative to `doc_events` for adding methods to existing DocTypes.

### hooks.py

```python
extend_doctype_class = {
    "Sales Invoice": [
        "myapp.overrides.sales_invoice.SalesInvoiceExtension"
    ]
}
```

### Extension Class (Mixin)

```python
# myapp/overrides/sales_invoice.py
import frappe

class SalesInvoiceExtension:
    def validate(self):
        """This is called as part of the controller chain."""
        if self.grand_total < 0:
            frappe.throw("Grand total cannot be negative")

    def custom_method(self):
        """Custom methods are also available on the doc instance."""
        return self.items
```

### Key Rules

- ALWAYS use `extend_doctype_class` over `override_doctype_class` in v16+ when multiple apps may extend the same DocType.
- Multiple apps can extend the same DocType — extensions stack via MRO.
- Class resolution order follows hooks priority: `class Final(App2Mixin, App1Mixin, Original)`.
- Extension methods (like `validate`) run as part of the controller, NOT as separate doc_events handlers.

---

## override_doctype_class [v14+]

Completely replaces the controller class. Use with extreme caution.

```python
# hooks.py
override_doctype_class = {
    "ToDo": "myapp.overrides.todo.CustomToDo"
}
```

```python
# myapp/overrides/todo.py
from frappe.desk.doctype.todo.todo import ToDo

class CustomToDo(ToDo):
    def validate(self):
        super().validate()  # ALWAYS call super() to preserve original logic
        # Your additions here
```

NEVER use `override_doctype_class` if `extend_doctype_class` is available (v16+). Only ONE app can override a DocType — last-installed app wins, silently breaking other apps.

---

## Multi-App Event Ordering

When multiple apps register `doc_events` for the same DocType and event:

1. Handlers execute in **app installation order** (as listed in `sites/{site}/site_config.json` → `installed_apps`).
2. The order can be changed via **Setup > Installed Applications > Update Hooks Resolution Order**.
3. For `override_doctype_class`, the **last-installed app wins** (only one override applies).
4. For `extend_doctype_class` (v16+), all extensions stack cumulatively.

---

## Transaction Behavior

All document events from `before_validate` through `on_change` run inside a single database transaction.

- If ANY event raises an exception, the ENTIRE operation rolls back (including `db_insert`/`db_update`).
- `after_insert`, `on_update`, `on_submit`, `on_cancel` — all run BEFORE the transaction commits.
- The transaction commits only AFTER all events complete successfully.
- `after_delete` runs after the DELETE statement but still within the request transaction.

NEVER assume data is committed to DB inside any event handler. Other concurrent requests will NOT see your changes until the full request completes.

---

## Critical Rules

1. ALWAYS use `frappe.throw()` to abort operations — NEVER use `raise Exception`.
2. NEVER modify `doc.name` outside of `autoname` or `before_naming`.
3. ALWAYS call `super().{event}()` when overriding controller methods in subclasses.
4. NEVER use `doc.save()` inside `validate` or `before_save` — this causes infinite recursion.
5. ALWAYS use `doc.flags.ignore_permissions = True` explicitly if your hook needs to bypass permissions — NEVER assume hooks run as Administrator.
6. NEVER put slow operations (API calls, file I/O) in `validate` — use `after_insert` or `on_update` with `frappe.enqueue()` instead.
7. ALWAYS use `doc.flags` to communicate between events in the same request (e.g., `doc.flags.skip_notification = True`).
8. NEVER rely on `on_change` for critical logic — it only fires when values actually differ from the database state.

---

## See Also

- [Event Execution Order — Detailed Diagrams](references/event-order.md)
- [Working Examples for Common Patterns](references/examples.md)
- [Anti-Patterns and Common Mistakes](references/anti-patterns.md)
- `frappe-syntax-hooks-config` — App-level hooks (scheduler, fixtures, permissions)
- Official docs: https://docs.frappe.io/framework/user/en/basics/doctypes/controllers
---
name: frappe-syntax-hooks
description: >
  Use when configuring Frappe hooks.py for app events, scheduler tasks,
  document events, fixtures, boot session, jenv customization, or website
  routing. Covers v14/v15/v16 including extend_doctype_class. Keywords:
  hooks.py, doc_events, scheduler_events, fixtures, app_include_js,
  override_whitelisted_methods, extend_doctype_class,
  hooks.py example, how to register hook, available hooks list, extend_doctype_class example.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Configuration Hooks (hooks.py)

Configuration hooks in hooks.py enable custom apps to extend Frappe/ERPNext
behavior. This skill covers ALL non-document-event hooks. For `doc_events`
(validate, on_submit, on_update, etc.), see **frappe-syntax-hooks-events**.

## Quick Reference: Hook Categories

| Category | Key Hooks | Reference |
|----------|-----------|-----------|
| App metadata | `app_name`, `app_title`, `required_apps` | Below |
| Frontend assets | `app_include_js/css`, `web_include_js/css` | Below |
| Install/migrate | `before_install`, `after_install`, `after_migrate` | Below |
| Scheduler | `hourly`, `daily`, `cron`, `*_long` | [scheduler-events.md](references/scheduler-events.md) |
| Session/auth | `on_login`, `on_logout`, `auth_hooks` | [bootinfo.md](references/bootinfo.md) |
| Request middleware | `before_request`, `after_request` | [request-lifecycle.md](references/request-lifecycle.md) |
| Permissions | `permission_query_conditions`, `has_permission` | [permissions.md](references/permissions.md) |
| DocType overrides | `override_doctype_class`, `doctype_js` | [overrides.md](references/overrides.md) |
| Website/portal | `website_route_rules`, `portal_menu_items` | [request-lifecycle.md](references/request-lifecycle.md) |
| File handling | `before_write_file`, `write_file` | Below |
| Email | `override_email_send`, `default_mail_footer` | Below |
| PDF | `pdf_header_html`, `pdf_footer_html` | Below |
| Jinja | `jinja.methods`, `jinja.filters` | Below |
| Boot/client data | `extend_bootinfo`, `notification_config` | [bootinfo.md](references/bootinfo.md) |
| Data/fixtures | `fixtures`, `global_search_doctypes` | Below |
| Method overrides | `override_whitelisted_methods`, `standard_queries` | [overrides.md](references/overrides.md) |

---

## Decision Tree: Which Hook Do I Need?

```
What do you want to achieve?
|
+-- ADD JS/CSS to desk or portal?
|   +-- Desk --> app_include_js / app_include_css
|   +-- Portal --> web_include_js / web_include_css
|   +-- Specific form --> doctype_js
|   +-- List view --> doctype_list_js
|
+-- RUN periodic background tasks?
|   +-- < 5 min execution --> hourly / daily / weekly / monthly
|   +-- 5-25 min execution --> hourly_long / daily_long / etc.
|   +-- Exact time needed --> cron
|   See: frappe-syntax-hooks > scheduler-events.md
|
+-- SEND data to client at page load?
|   +-- extend_bootinfo
|
+-- MODIFY controller of existing DocType?
|   +-- v16+ --> extend_doctype_class (RECOMMENDED)
|   +-- v14/v15 --> override_doctype_class (last app wins)
|
+-- MODIFY API endpoint?
|   +-- override_whitelisted_methods
|
+-- CUSTOMIZE permissions?
|   +-- List filtering --> permission_query_conditions
|   +-- Document-level --> has_permission
|
+-- REACT to document save/submit/delete?
|   +-- See frappe-syntax-hooks-events skill
|
+-- EXPORT/IMPORT configuration?
|   +-- fixtures
|
+-- SETUP on install or migrate?
|   +-- after_install / after_migrate
|
+-- ADD custom Jinja functions?
|   +-- jinja.methods / jinja.filters
|
+-- CUSTOMIZE website routing?
|   +-- website_route_rules
|   See: request-lifecycle.md for full routing pipeline
|
+-- INTERCEPT every request/response?
|   +-- before_request / after_request
|   See: request-lifecycle.md for lifecycle flow
|
+-- CUSTOM page rendering?
|   +-- page_renderer hook
|   See: request-lifecycle.md for renderer architecture
```

---

## 1. App Metadata Hooks

ALWAYS include these in every hooks.py:

```python
app_name = "myapp"
app_title = "My App"
app_publisher = "My Company"
app_description = "Custom ERPNext extensions"
app_email = "info@mycompany.com"
app_license = "MIT"
required_apps = ["erpnext"]  # Declare dependencies
```

---

## 2. Frontend Asset Injection

```python
# Desk (backend UI) assets — loaded on EVERY desk page
app_include_js = "/assets/myapp/js/myapp.min.js"       # string or list
app_include_css = "/assets/myapp/css/myapp.min.css"

# Website/portal assets — loaded on EVERY web page
web_include_js = "/assets/myapp/js/web.min.js"
web_include_css = "/assets/myapp/css/web.min.css"

# Web form specific assets
webform_include_js = {"My Web Form": "public/js/my_webform.js"}
webform_include_css = {"My Web Form": "public/css/my_webform.css"}

# Form script extensions (extend OTHER apps' forms)
doctype_js = {"Sales Invoice": "public/js/sales_invoice.js"}

# List view script extensions
doctype_list_js = {"Sales Invoice": "public/js/sales_invoice_list.js"}

# Custom sounds
sounds = [{"name": "alert", "src": "/assets/myapp/sounds/alert.mp3", "volume": 0.5}]
```

NEVER put heavy libraries in `app_include_js` — they load on every page.

---

## 3. Installation & Migration Lifecycle

```python
before_install = "myapp.setup.before_install"
after_install = "myapp.setup.after_install"
after_sync = "myapp.setup.after_sync"            # After fixture sync
before_migrate = "myapp.setup.before_migrate"
after_migrate = "myapp.setup.after_migrate"
before_uninstall = "myapp.setup.before_uninstall"
after_uninstall = "myapp.setup.after_uninstall"
before_tests = "myapp.setup.seed_test_data"
```

All accept a single dotted-path string. The function receives no arguments.

---

## 4. Scheduler Events

See [scheduler-events.md](references/scheduler-events.md) for full reference.

```python
scheduler_events = {
    "all": ["myapp.tasks.every_minute"],            # ~60s interval
    "hourly": ["myapp.tasks.hourly_check"],         # default queue, 5 min timeout
    "daily": ["myapp.tasks.daily_report"],
    "weekly": ["myapp.tasks.weekly_cleanup"],
    "monthly": ["myapp.tasks.monthly_summary"],
    "daily_long": ["myapp.tasks.heavy_sync"],       # long queue, 25 min timeout
    "cron": {
        "0 9 * * 1-5": ["myapp.tasks.weekday_morning"]  # cron expression
    }
}
```

ALWAYS run `bench --site sitename migrate` after changing scheduler_events.
NEVER define task functions with arguments — they receive none.

---

## 5. Session & Authentication Hooks

```python
on_login = "myapp.auth.on_login"                     # Receives login_manager
on_logout = "myapp.auth.on_logout"                   # No arguments
on_session_creation = "myapp.auth.on_session_creation"  # No arguments
auth_hooks = ["myapp.auth.validate_request"]          # List of validators
```

Execution order: `on_login` --> session created --> `on_session_creation` --> `extend_bootinfo`.

---

## 6. Request/Response Middleware

See [request-lifecycle.md](references/request-lifecycle.md) for the full request
lifecycle flow, page renderer architecture, and router API.

```python
before_request = ["myapp.middleware.before_request"]   # List of dotted paths
after_request = ["myapp.middleware.after_request"]
before_job = ["myapp.middleware.before_job"]            # Before background job
after_job = ["myapp.middleware.after_job"]              # After background job
```

---

## 7. Permission Hooks

See [permissions.md](references/permissions.md) for full reference.

```python
permission_query_conditions = {
    "Sales Invoice": "myapp.permissions.si_query_conditions"
}
has_permission = {
    "Sales Invoice": "myapp.permissions.si_has_permission"
}
```

ALWAYS check `if not user: user = frappe.session.user` in handlers.
ALWAYS use `frappe.db.escape(user)` in SQL — NEVER string interpolation.
`permission_query_conditions` works ONLY with `get_list`, NOT `get_all`.

---

## 8. DocType Class Overrides

See [overrides.md](references/overrides.md) for full reference.

```python
# v14+ — Full replacement (LAST installed app wins)
override_doctype_class = {
    "Sales Invoice": "myapp.overrides.CustomSalesInvoice"
}

# v16+ — Mixin-based extension (ALL apps coexist) [RECOMMENDED]
extend_doctype_class = {
    "Address": ["myapp.extensions.AddressMixin"]
}
```

ALWAYS call `super().method()` in overrides. Forgetting super() breaks core logic.

---

## 9. Website & Portal Hooks

```python
# URL routing
website_route_rules = [
    {"from_route": "/custom-page/<name>", "to_route": "Custom Page"}
]
website_redirects = [
    {"source": "/old-url", "target": "/new-url"}
]
website_catch_all = "myapp.www.custom_404"

# Homepage
homepage = "my-custom-home"
role_home_page = {"Sales User": "sales-dashboard"}
get_website_user_home_page = "myapp.utils.get_home_page"

# Portal sidebar
portal_menu_items = [{"title": "My Orders", "route": "/orders", "role": "Customer"}]
standard_portal_menu_items = [{"title": "My Items", "route": "/my-items"}]

# Template overrides
base_template = "myapp/templates/base.html"
website_context = {"brand_html": "<b>My Brand</b>"}
update_website_context = "myapp.context.update_context"
```

---

## 10. File Handling Hooks

```python
before_write_file = "myapp.files.before_write"      # Pre-save hook
write_file = "myapp.files.custom_write"              # Replace file storage (e.g., S3/CDN)
delete_file_data_content = "myapp.files.custom_delete"  # Replace file deletion
```

Use `write_file` to redirect file storage to cloud providers (S3, GCS, Azure Blob).

---

## 11. Email Hooks

```python
override_email_send = "myapp.email.custom_send"       # Replace email backend
get_sender_details = "myapp.email.get_sender"          # Override From address
default_mail_footer = "myapp.email.get_footer"         # HTML footer for all emails
```

---

## 12. PDF Hooks

```python
pdf_header_html = "myapp.pdf.get_header"               # Custom PDF header
pdf_body_html = "myapp.pdf.get_body"                    # Custom PDF body wrapper
pdf_footer_html = "myapp.pdf.get_footer"                # Custom PDF footer
# pdf_generator = "myapp.pdf.generate"                  # [v16+] Replace PDF engine
```

---

## 13. Jinja Hooks

```python
# Add custom methods available in Jinja templates
jinja = {
    "methods": ["myapp.jinja_utils.get_balance"],
    "filters": ["myapp.jinja_utils.format_iban"]
}
```

```python
# myapp/jinja_utils.py
def get_balance(customer):
    """Usage in template: {{ get_balance(doc.customer) }}"""
    return frappe.db.get_value("Customer", customer, "outstanding_amount") or 0

def format_iban(value):
    """Usage in template: {{ bank_account|format_iban }}"""
    if not value: return ""
    return " ".join([value[i:i+4] for i in range(0, len(value), 4)])
```

---

## 14. Boot & Client Data

See [bootinfo.md](references/bootinfo.md) for full reference.

```python
extend_bootinfo = "myapp.boot.extend_boot"
notification_config = "myapp.notifications.get_config"
```

NEVER put secrets/API keys in bootinfo — it is sent to the browser.
NEVER run heavy queries in bootinfo — it runs on EVERY page load.

---

## 15. Data & Fixtures

```python
fixtures = [
    {"dt": "Custom Field", "filters": [["module", "=", "My App"]]},
    {"dt": "Property Setter", "filters": [["module", "=", "My App"]]},
    {"dt": "Role", "filters": [["name", "like", "MyApp%"]]}
]

global_search_doctypes = {"My DocType": {"index": 10}}
ignore_links_on_delete = ["Communication", "Activity Log"]
calendars = ["My Event DocType"]
clear_cache = "myapp.cache.clear_custom_cache"
```

ALWAYS use filters in fixtures — NEVER export unfiltered (exports everything).
NEVER put transactional data (Sales Invoice, Stock Entry) in fixtures.

---

## 16. Method Overrides

See [overrides.md](references/overrides.md) for full reference.

```python
override_whitelisted_methods = {
    "frappe.client.get_count": "myapp.overrides.custom_get_count"
}
standard_queries = {
    "Customer": "myapp.queries.customer_query"
}
```

ALWAYS match the original method signature exactly when overriding.

---

## Version Differences

| Hook | v14 | v15 | v16+ |
|------|-----|-----|------|
| `extend_doctype_class` | -- | -- | NEW |
| `extend_bootinfo` | Yes | Yes | Yes |
| `auth_hooks` | Yes | Yes | Yes |
| `after_sync` | Yes | Yes | Yes |
| `before_uninstall` | -- | Yes | Yes |
| `after_uninstall` | -- | Yes | Yes |
| `website_path_resolver` | -- | Yes | Yes |
| All other hooks | Yes | Yes | Yes |

---

## Critical Rules

1. ALWAYS run `bench --site sitename migrate` after ANY hooks.py change
2. NEVER import frappe at module level in hooks.py — it runs before init
3. ALWAYS use dotted paths (`"myapp.module.function"`) — NEVER lambdas
4. NEVER commit in hook handlers — Frappe manages transactions
5. ALWAYS test hooks in a dev environment before deploying

---

## Anti-Patterns Summary

| Wrong | Correct |
|-------|---------|
| No filters in fixtures | ALWAYS filter by module/app |
| Secrets in bootinfo | ONLY public config in bootinfo |
| Heavy queries in bootinfo | Cache or minimize data |
| `get_all` with permission hooks | Use `get_list` for permission filtering |
| Override without `super()` | ALWAYS call `super().method()` first |
| Scheduler tasks with args | Tasks receive NO arguments |
| Skip `bench migrate` | ALWAYS migrate after hook changes |

Full anti-patterns: [anti-patterns.md](references/anti-patterns.md)

---

## Reference Files

| File | Contents |
|------|----------|
| [hooks.md](references/hooks.md) | Complete hooks catalog by category |
| [scheduler-events.md](references/scheduler-events.md) | Scheduler frequencies, cron syntax, timeouts |
| [permissions.md](references/permissions.md) | Permission hooks in detail |
| [overrides.md](references/overrides.md) | DocType class override patterns |
| [bootinfo.md](references/bootinfo.md) | extend_bootinfo, session hooks, notification_config |
| [examples.md](references/examples.md) | Working hooks.py examples for each category |
| [request-lifecycle.md](references/request-lifecycle.md) | Request lifecycle, routing pipeline, page renderers, router API |
| [anti-patterns.md](references/anti-patterns.md) | Common hook mistakes and corrections |

For document lifecycle events (doc_events), see: **frappe-syntax-hooks-events**
---
name: frappe-syntax-jinja
description: >
  Use when writing Jinja templates for ERPNext/Frappe Print Formats, Email
  Templates, and Portal Pages. Covers template syntax, context variables,
  filters, macros, and v16 Chrome PDF rendering. Prevents common mistakes
  with doc context and child table iteration. Keywords: Jinja, print format,
  email template, portal page, template syntax, PDF, v14-v16,
  template syntax, Jinja example, print format code, how to show child table in print.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Jinja Templates Syntax

> Deterministic Jinja reference for Print Formats, Email Templates, Notification Templates, and Portal Pages in Frappe v14/v15/v16.

---

## When to Use This Skill

USE when:
- Creating or modifying Print Formats (Jinja-based)
- Writing Email Templates with dynamic fields
- Building Portal Pages (`www/*.html`) with Python controllers
- Writing Notification Templates (system/email/SMS)
- Registering custom Jinja methods or filters via `hooks.py`

DO NOT USE for:
- Report Print Formats — they use JavaScript templating (`{%= %}`), NOT Jinja
- Client Scripts — see `frappe-syntax-clientscripts`
- Server Scripts — see `frappe-syntax-serverscripts`

---

## Decision Tree: Which Template Type?

```
Need a printable document?
├─ YES → Is it for a Query/Script Report?
│        ├─ YES → Use JS Template ({%= %}), NOT Jinja
│        └─ NO  → Use Jinja Print Format
└─ NO  → Is it for email?
         ├─ YES → Is it triggered by workflow/notification?
         │        ├─ YES → Notification Template (Jinja)
         │        └─ NO  → Email Template (Jinja)
         └─ NO  → Is it a web page?
                  ├─ YES → Portal Page (www/*.html + .py controller)
                  └─ NO  → frappe.render_template() for ad-hoc rendering
```

---

## Quick Reference: Jinja Syntax

| Syntax | Purpose | Example |
|--------|---------|---------|
| `{{ }}` | Output expression | `{{ doc.name }}` |
| `{% %}` | Control statement | `{% if doc.status == "Paid" %}` |
| `{# #}` | Comment | `{# This is a comment #}` |
| `{{ _("text") }}` | Translation | `{{ _("Invoice") }}` |
| `{{ val \| filter }}` | Filter | `{{ name \| default("N/A") }}` |

### CRITICAL: Jinja vs JS Template Syntax

| Aspect | Jinja (Print Formats) | JS Template (Report Print Formats) |
|--------|----------------------|-------------------------------------|
| Output | `{{ expression }}` | `{%= expression %}` |
| Code block | `{% statement %}` | `{% js_code %}` |
| Language | Python | JavaScript |
| Context | `doc`, `frappe` | `data`, `filters` |

**NEVER use Jinja syntax in Report Print Formats. NEVER use `{%= %}` in standard Print Formats.**

---

## Context Objects by Template Type

### Print Formats

| Object | Description |
|--------|-------------|
| `doc` | The document being printed (full Document object) |
| `frappe` | Frappe module (whitelisted methods only) |
| `frappe.utils` | Utility functions |
| `_()` | Translation function |
| `doc.items`, `doc.taxes` | Child table accessors (by fieldname) |

### Email Templates

| Object | Description |
|--------|-------------|
| `doc` | The linked document (when triggered from a DocType) |
| `frappe` | Frappe module (limited) |
| `_()` | Translation function |

### Notification Templates

| Object | Description |
|--------|-------------|
| `doc` | The document that triggered the notification |
| `frappe` | Frappe module |
| `_()` | Translation function |

### Portal Pages (www/*.html)

| Object | Description |
|--------|-------------|
| `frappe` | Frappe module |
| `frappe.session.user` | Current authenticated user |
| `frappe.form_dict` | Query parameters from URL |
| `frappe.lang` | Current language code |
| Custom context | Set via `get_context(context)` in `.py` controller |

> **Full details**: `references/context-objects.md`

---

## Essential Methods (Whitelisted in Jinja)

### Formatting: ALWAYS Use for Display

```jinja
{# ALWAYS use get_formatted() for fields in Print Formats #}
{{ doc.get_formatted("posting_date") }}
{{ doc.get_formatted("grand_total") }}

{# Child table rows — ALWAYS pass parent doc for currency context #}
{% for row in doc.items %}
    {{ row.get_formatted("rate", doc) }}
    {{ row.get_formatted("amount", doc) }}
{% endfor %}

{# General formatting with explicit fieldtype #}
{{ frappe.format(value, {'fieldtype': 'Currency'}) }}
{{ frappe.format_date(doc.posting_date) }}
```

### Document Retrieval

```jinja
{# Full document — use only when multiple fields needed #}
{% set customer = frappe.get_doc("Customer", doc.customer) %}

{# Single field — ALWAYS prefer over get_doc for one field #}
{% set abbr = frappe.db.get_value("Company", doc.company, "abbr") %}

{# List of records (no permission check) #}
{% set tasks = frappe.get_all("Task",
    filters={"status": "Open"},
    fields=["title", "due_date"],
    order_by="due_date asc",
    page_length=10) %}

{# List with permission check (portal pages) #}
{% set orders = frappe.get_list("Sales Order",
    filters={"customer": doc.customer},
    fields=["name", "grand_total"]) %}
```

### Translation: REQUIRED for All User-Facing Strings

```jinja
<h1>{{ _("Invoice") }}</h1>
<p>{{ _("Total: {0}").format(doc.get_formatted("grand_total")) }}</p>
```

### System & Session

```jinja
{{ frappe.get_url() }}
{{ frappe.get_fullname() }}
{{ frappe.get_fullname(doc.owner) }}
{{ frappe.db.get_single_value("System Settings", "time_zone") }}
{% if frappe.session.user != "Guest" %}...{% endif %}
```

> **Full method reference**: `references/methods-reference.md`

---

## Control Structures

### Conditionals

```jinja
{% if doc.status == "Paid" %}
    <span class="paid">{{ _("Paid") }}</span>
{% elif doc.status == "Overdue" %}
    <span class="overdue">{{ _("Overdue") }}</span>
{% else %}
    <span>{{ doc.status }}</span>
{% endif %}
```

### Loops with Child Tables

```jinja
{% for item in doc.items %}
<tr>
    <td>{{ loop.index }}</td>
    <td>{{ item.item_name }}</td>
    <td>{{ item.get_formatted("amount", doc) }}</td>
</tr>
{% else %}
<tr><td colspan="3">{{ _("No items") }}</td></tr>
{% endfor %}
```

### Loop Variables

| Variable | Description |
|----------|-------------|
| `loop.index` | 1-indexed position |
| `loop.index0` | 0-indexed position |
| `loop.first` | `True` on first iteration |
| `loop.last` | `True` on last iteration |
| `loop.length` | Total number of items |

### Variables

```jinja
{% set total = 0 %}
{% set name = doc.customer_name | default("Unknown") %}
```

---

## Filters

| Filter | Example | Notes |
|--------|---------|-------|
| `default` | `{{ val \| default("N/A") }}` | ALWAYS use for optional fields |
| `length` | `{{ items \| length }}` | Count items |
| `join` | `{{ names \| join(", ") }}` | Join list to string |
| `truncate` | `{{ text \| truncate(100) }}` | Truncate with ellipsis |
| `escape` | `{{ input \| escape }}` | HTML-escape (default behavior) |
| `safe` | `{{ html \| safe }}` | Render raw HTML — NEVER for user input |
| `round` | `{{ num \| round(2) }}` | Round number |
| `lower` / `upper` | `{{ text \| upper }}` | Case conversion |

> **Full filter reference**: `references/filters-reference.md`

---

## Custom Jinja Methods & Filters via hooks.py

### hooks.py Registration

```python
# hooks.py
jenv = {
    "methods": [
        "myapp.jinja.methods"       # Module with callable functions
    ],
    "filters": [
        "myapp.jinja.filters"       # Module with filter functions
    ]
}
```

### Custom Method

```python
# myapp/jinja/methods.py
import frappe

def get_company_logo(company):
    """Returns company logo URL. Called as get_company_logo() in Jinja."""
    return frappe.db.get_value("Company", company, "company_logo") or ""
```

```jinja
<img src="{{ get_company_logo(doc.company) }}" alt="Logo">
```

### Custom Filter

```python
# myapp/jinja/filters.py
def nl2br(text):
    """Convert newlines to <br> tags. Used as {{ text | nl2br }}."""
    return (text or "").replace("\n", "<br>")
```

```jinja
{{ doc.notes | nl2br | safe }}
```

> **Details**: `references/methods.md`

---

## Print Format Patterns

### Minimal Print Format Template

```jinja
<style>
    .print-header { background: #f5f5f5; padding: 15px; }
    .item-table { width: 100%; border-collapse: collapse; }
    .item-table th, .item-table td { border: 1px solid #ddd; padding: 8px; }
    .text-right { text-align: right; }
</style>

<div class="print-header">
    <h1>{{ doc.select_print_heading or _("Invoice") }}</h1>
    <p>{{ doc.name }} — {{ doc.get_formatted("posting_date") }}</p>
</div>

<table class="item-table">
    <thead>
        <tr>
            <th>#</th>
            <th>{{ _("Item") }}</th>
            <th class="text-right">{{ _("Qty") }}</th>
            <th class="text-right">{{ _("Amount") }}</th>
        </tr>
    </thead>
    <tbody>
        {% for row in doc.items %}
        <tr>
            <td>{{ loop.index }}</td>
            <td>{{ row.item_name }}</td>
            <td class="text-right">{{ row.qty }}</td>
            <td class="text-right">{{ row.get_formatted("amount", doc) }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<p><strong>{{ _("Grand Total") }}: {{ doc.get_formatted("grand_total") }}</strong></p>
```

### Page Breaks

```css
/* v14/v15 (wkhtmltopdf) */
.page-break { page-break-before: always; }

/* v16 (Chrome PDF) — ALWAYS prefer break-* in v16 */
.page-break { break-before: page; }
```

> **Full examples**: `references/examples.md` | **Patterns**: `references/patterns.md`

---

## V16: Chrome PDF Rendering

| Aspect | v14/v15 (wkhtmltopdf) | v16 (Chrome) |
|--------|----------------------|--------------|
| CSS Support | Limited CSS3 | Full modern CSS |
| Flexbox/Grid | Partial | Full support |
| Page breaks | `page-break-*` | `break-*` preferred |
| Fonts | System fonts only | Web fonts supported |

### V16 Configuration

```json
// site_config.json
{
    "pdf_engine": "chrome",
    "chrome_path": "/usr/bin/chromium"
}
```

---

## Portal Page Pattern

### www/projects/index.html

```jinja
{% extends "templates/web.html" %}
{% block title %}{{ _("Projects") }}{% endblock %}

{% block page_content %}
<h1>{{ _("Projects") }}</h1>
{% for project in projects %}
    <h3>{{ project.title }}</h3>
    <p>{{ project.description | default("") | truncate(150) }}</p>
{% else %}
    <p>{{ _("No projects found.") }}</p>
{% endfor %}
{% endblock %}
```

### www/projects/index.py

```python
import frappe

def get_context(context):
    context.title = "Projects"
    context.no_cache = True
    context.projects = frappe.get_all("Project",
        filters={"is_public": 1},
        fields=["name", "title", "description"],
        order_by="creation desc")
    return context
```

> **Full structure**: `references/structure.md` | **Templates**: `references/templates.md`

---

## Critical Rules

### ALWAYS

1. Use `_()` for ALL user-facing strings
2. Use `get_formatted()` for currency, date, and numeric fields
3. Use `default()` filter for optional/nullable fields
4. Pass parent `doc` to child row `get_formatted("field", doc)`
5. Use `frappe.db.get_value()` when you need only one field
6. Keep calculations in Python controllers, not Jinja templates

### NEVER

1. Execute database queries inside loops (N+1 problem)
2. Use `| safe` on user-supplied input (XSS vulnerability)
3. Use Jinja syntax in Report Print Formats (they require JS `{%= %}`)
4. Use `frappe.get_doc()` when `frappe.db.get_value()` suffices
5. Hardcode strings without `_()` translation wrapper
6. Disable `safe_render` without security review

> **Anti-patterns with fixes**: `references/anti-patterns.md`

---

## Reference Files

| File | Contents |
|------|----------|
| `references/syntax.md` | Jinja syntax reference (tags, filters, tests, loops) |
| `references/methods.md` | Custom Jinja methods/filters via hooks |
| `references/context-objects.md` | Available objects per template type |
| `references/filters-reference.md` | All standard and custom Frappe filters |
| `references/methods-reference.md` | All frappe.* methods available in Jinja |
| `references/examples.md` | Complete Print Format, Email, Portal examples |
| `references/anti-patterns.md` | Common mistakes and correct alternatives |
| `references/templates.md` | Template structure patterns |
| `references/patterns.md` | Conditional rendering, loops, child tables |
| `references/structure.md` | File structure for template types |

---

## See Also

- `frappe-syntax-hooks` — jenv configuration in hooks.py
- `frappe-impl-printformat` — Print Format implementation patterns
- `frappe-errors-serverscripts` — Server-side error handling
---
name: frappe-syntax-print
description: >
  Use when creating print formats or generating PDFs in Frappe v14-v16.
  Covers Jinja print formats, Print Designer [v15+], Letter Head,
  PDF generation API (get_pdf, download_pdf), Report print formats
  ({%= %} syntax), page breaks, and print CSS patterns.
  Prevents common mistakes with template engine confusion and PDF rendering.
  Keywords: print format, PDF, get_pdf, Jinja, Letter Head, print designer,, PDF not generating, print format broken, custom PDF, letter head, wkhtmltopdf error.
  wkhtmltopdf, WeasyPrint, page-break, download_pdf.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "3.0"
---

# Frappe Print Formats & PDF Generation

> Deterministic reference for print formats, Letter Head, and PDF generation in Frappe v14/v15/v16.

---

## When to Use This Skill

USE when:
- Creating or modifying Print Formats (Jinja or JS)
- Generating PDFs programmatically (`get_pdf`, download endpoints)
- Configuring Letter Head (header/footer) for print output
- Working with Print Designer (v15+)
- Implementing page breaks, print CSS, or landscape layouts
- Building Report Print Formats ({%= %} syntax)

DO NOT USE for:
- General Jinja template syntax (emails, portals) -- see `frappe-syntax-jinja`
- Client Script UI logic -- see `frappe-syntax-clientscripts`
- Web views or portal pages -- see `frappe-syntax-jinja`

---

## Decision Tree: Which Print Format Type?

```
Need a printable/PDF document?
├─ YES → Is it a Query/Script Report?
│        ├─ YES → Use JS Template ({%= %} microtemplate)
│        │        Set print_format_for = "Report"
│        └─ NO  → Need visual drag-and-drop editor?
│                  ├─ YES → On v15+?
│                  │        ├─ YES → Use Print Designer (WeasyPrint)
│                  │        └─ NO  → NOT available on v14. Use Jinja.
│                  └─ NO  → Need full layout control?
│                           ├─ YES → Use Jinja Print Format (custom_format=1)
│                           └─ NO  → Use Standard Print Format (auto layout)
└─ NO  → This skill does not apply.
```

---

## Print Format Types

| Type | Engine | Version | When to Use |
|------|--------|---------|-------------|
| Standard | Auto from DocType field layout | v14+ | No customization needed |
| Jinja | Server-side Jinja2 (wkhtmltopdf) | v14+ | Full layout control |
| JS Template | Client-side microtemplate | v14+ | Report print formats only |
| Print Designer | WeasyPrint / Chrome | v15+ | Visual drag-and-drop builder |

### Standard Print Format

ALWAYS the default. Frappe auto-generates layout from DocType fields. No code needed. Controlled via Print Settings and field `print_hide` property.

### Jinja Print Format

Set `custom_format = 1` on the Print Format document. Full Jinja2 with server-side rendering.

**Context variables available in every Jinja Print Format:**

| Variable | Type | Content |
|----------|------|---------|
| `doc` | Document | The document being printed |
| `meta` | Meta | DocType metadata |
| `layout` | list | Field layout sections |
| `letter_head` | str | Rendered Letter Head HTML |
| `footer` | str | Rendered footer HTML |
| `print_settings` | dict | Print Settings configuration |
| `frappe` | module | Full frappe module access |

**Example — Minimal Jinja Print Format:**

```html
<h1>{{ doc.name }}</h1>
<p>Customer: {{ doc.customer_name }}</p>
<p>Date: {{ doc.posting_date | global_date_format }}</p>

<table class="table table-bordered">
  <thead>
    <tr><th>Item</th><th>Qty</th><th>Rate</th><th>Amount</th></tr>
  </thead>
  <tbody>
    {% for row in doc.items %}
    <tr>
      <td>{{ row.item_name }}</td>
      <td>{{ row.qty }}</td>
      <td>{{ frappe.utils.fmt_money(row.rate, currency=doc.currency) }}</td>
      <td>{{ frappe.utils.fmt_money(row.amount, currency=doc.currency) }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>

<p><strong>Grand Total:</strong> {{ frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}</p>
```

### JS Template (Report Print Formats)

ONLY for Query Reports and Script Reports. Uses `{%= %}` microtemplate syntax, NOT Jinja.

```javascript
// In report's .js file
{%= row.item_name %}
{% if (row.qty > 10) { %}
  <strong>Bulk order</strong>
{% } %}

{% for (var i = 0; i < rows.length; i++) { %}
  <tr>
    <td>{%= rows[i].item_name %}</td>
    <td>{%= rows[i].qty %}</td>
  </tr>
{% } %}
```

**CRITICAL:** NEVER mix Jinja `{{ }}` and JS `{%= %}` syntax. They are completely separate template engines.

### Print Designer (v15+ Only)

- Separate app: `bench get-app print_designer`
- Uses WeasyPrint (not wkhtmltopdf)
- Visual drag-and-drop builder in the browser
- NEVER attempt to use Print Designer on v14 -- it does not exist

---

## Letter Head

Letter Head provides consistent header/footer across all print formats.

### Configuration

| Field | Purpose |
|-------|---------|
| `source` | `"Image"` or `"HTML"` |
| `content` | Header HTML (Jinja-rendered with `doc` context) |
| `footer` | Footer HTML (Jinja-rendered, **PDF only**) |
| `image` | Header image (when source = "Image") |
| `align` | Image alignment: Left, Center, Right |

**IMPORTANT:** The `footer` field only displays in PDF output, never in browser print preview.

### Letter Head in Jinja Templates

```python
# Server-side: render Letter Head programmatically
from frappe.utils.print_format import render_letterhead_for_print

letterhead_html = render_letterhead_for_print(
    letter_head_name="My Company",
    doc=doc
)
```

### Dynamic Letter Head Content

Letter Head `content` and `footer` fields support Jinja with `doc` context:

```html
<!-- In Letter Head content field -->
<div style="text-align: right;">
  <strong>{{ doc.company }}</strong><br>
  Date: {{ doc.posting_date | global_date_format }}
</div>
```

---

## PDF Generation API

> See `references/pdf-api.md` for complete API reference.

### Quick Reference

```python
# Generate PDF bytes from HTML
from frappe.utils.pdf import get_pdf
pdf_bytes = get_pdf(html_string, options=None)

# Generate PDF from a specific document + print format
from frappe.utils.print_format import download_pdf
download_pdf(doctype, name, format=None, doc=None, no_letterhead=0)
```

### Download Endpoints

```
# Single document PDF
GET /api/method/frappe.utils.print_format.download_pdf
    ?doctype=Sales Invoice
    &name=SINV-00001
    &format=My Print Format
    &no_letterhead=0

# Multiple documents in one PDF
GET /api/method/frappe.utils.print_format.download_multi_pdf
    ?doctype=Sales Invoice
    &name=["SINV-00001","SINV-00002"]
    &format=My Print Format
```

### PDF Engine Selection (v15+)

| Engine | When | Config |
|--------|------|--------|
| wkhtmltopdf | Default on v14, fallback on v15+ | Default |
| Chrome | v15+ with Chromium installed | `pdf_generator = "chrome"` on Print Format |
| WeasyPrint | Print Designer formats only | Automatic for Print Designer |

ALWAYS use wkhtmltopdf on v14. On v15+, Chrome produces better CSS3 support.

---

## Page Breaks & Print CSS

### Page Break Classes

```html
<!-- Force page break after this element -->
<div class="page-break"></div>

<!-- Or use CSS directly -->
<div style="page-break-after: always;"></div>

<!-- Page break before -->
<div style="page-break-before: always;"></div>
```

### Print CSS Classes (Frappe Built-in)

| Class | Effect |
|-------|--------|
| `.print-format` | Container: max-width 8.3in, min-height 11.69in (A4 portrait) |
| `.print-format.landscape` | Width 11.69in (A4 landscape) |
| `.page-break` | `page-break-after: always` |
| `.print-heading` | Print title styling |
| `.hidden-pdf` | Hidden in PDF output only |
| `.visible-pdf` | Visible in PDF output only |

### PDF Header/Footer HTML

```python
# In hooks.py — inject header/footer into every PDF
pdf_header_html = "myapp.utils.get_pdf_header"
pdf_body_html = "myapp.utils.get_pdf_body"
pdf_footer_html = "myapp.utils.get_pdf_footer"
```

```html
<!-- Header/footer elements in print format HTML -->
<div id="header-html">
  <span class="page"></span> of <span class="topage"></span>
</div>

<div id="footer-html">
  <p style="text-align: center; font-size: 9px;">
    Printed on {{ frappe.utils.nowdate() }}
  </p>
</div>
```

### Print CSS Best Practices

```css
/* ALWAYS use relative units for print widths */
@media print {
  .print-format {
    max-width: 100%;
    margin: 0;
    padding: 15mm;
  }

  /* Prevent table rows from splitting across pages */
  tr {
    page-break-inside: avoid;
  }

  /* Constrain images */
  img {
    max-width: 100%;
    height: auto;
  }
}
```

---

## Custom App Print Formats

### Ship a Print Format with Your App

```
myapp/
└── mymodule/
    └── print_format/
        └── my_custom_format/
            ├── my_custom_format.json   # Print Format doc
            └── my_custom_format.html   # Jinja template
```

**In the JSON file, ALWAYS set:**

```json
{
  "doctype": "Print Format",
  "name": "My Custom Format",
  "doc_type": "Sales Invoice",
  "module": "My Module",
  "standard": "Yes",
  "custom_format": 1,
  "print_format_type": "Jinja"
}
```

ALWAYS set `standard = "Yes"` and `module` for app-shipped print formats. This ensures they are recognized as part of the app and not as site-level customizations.

---

## Jinja Filters for Print Formats

| Filter | Purpose | Example |
|--------|---------|---------|
| `global_date_format` | Format date per system settings | `{{ doc.posting_date \| global_date_format }}` |
| `json` | Serialize to JSON string | `{{ doc.items \| json }}` |
| `len` | Get length | `{{ doc.items \| len }}` |
| `int` | Cast to integer | `{{ value \| int }}` |
| `flt` | Cast to float | `{{ value \| flt }}` |
| `markdown` | Render Markdown to HTML | `{{ doc.description \| markdown }}` |
| `abs` | Absolute value | `{{ value \| abs }}` |

### Register Custom Jinja Filters/Methods

```python
# In hooks.py
jinja = {
    "methods": [
        "myapp.utils.jinja.my_custom_method"
    ],
    "filters": [
        "myapp.utils.jinja.my_custom_filter"
    ]
}
```

```python
# myapp/utils/jinja.py
def my_custom_method(value):
    """Available as {{ my_custom_method(doc.field) }} in templates."""
    return value.upper()

def my_custom_filter(value, arg=None):
    """Available as {{ doc.field | my_custom_filter }} in templates."""
    return f"[{value}]"
```

---

## Version Compatibility Matrix

| Feature | v14 | v15 | v16 |
|---------|-----|-----|-----|
| Jinja Print Formats | Yes | Yes | Yes |
| JS Report Templates | Yes | Yes | Yes |
| Standard Print Formats | Yes | Yes | Yes |
| Letter Head (Image/HTML) | Yes | Yes | Yes |
| wkhtmltopdf | Default | Fallback | Fallback |
| Chrome PDF engine | No | Yes | Yes |
| WeasyPrint | No | Yes | Yes |
| Print Designer app | No | Yes | Yes |
| `pdf_header_html` hook | Yes | Yes | Yes |
| `download_multi_pdf` | Yes | Yes | Yes |

---

## Common Anti-Patterns

> See `references/anti-patterns.md` for the complete list with fixes.

1. **NEVER** use `{{ }}` in Report Print Formats -- they use `{%= %}` (JS microtemplate)
2. **NEVER** call `frappe.get_doc()` inside a `{% for %}` loop in templates -- causes N+1 queries
3. **NEVER** put heavy business logic in Jinja templates -- move to Python and pass results
4. **NEVER** hardcode page dimensions in CSS -- use `.print-format` class or relative units
5. **NEVER** ignore the `no_letterhead` parameter when generating PDFs programmatically
6. **NEVER** use Print Designer on v14 -- it requires v15+
7. **NEVER** embed large base64 images in print templates -- use URLs with `max-width: 100%`

---

## Reference Files

- [Jinja Print Formats](references/jinja-print-formats.md) -- Jinja syntax, variables, filters, macros
- [PDF API](references/pdf-api.md) -- get_pdf(), download endpoints, page breaks, hooks
- [Anti-Patterns](references/anti-patterns.md) -- Common print format mistakes with fixes
---
name: frappe-syntax-query-builder
description: >
  Use when building database queries with frappe.qb in Frappe v14-v16.
  Covers the PyPika-based query builder: SELECT, INSERT, UPDATE, DELETE,
  joins, aggregation, subqueries, cross-DB compatibility (MariaDB/PostgreSQL),
  and migration from raw SQL. Prevents SQL injection and DB-specific bugs.
  Keywords: frappe.qb, query builder, DocType, Field, pypika, join,, frappe.qb example, how to write query, join tables, SQL replacement, parameterized query.
  aggregate, ImportMapper, cross-database, parameterized query.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "3.0"
---

# Frappe Query Builder (frappe.qb)

## Quick Reference

```python
from frappe.query_builder import DocType, Field
from frappe.query_builder.functions import Count, Sum, IfNull
from frappe.query_builder.custom import ConstantColumn, GROUP_CONCAT
from frappe.query_builder.terms import SubQuery
from frappe.query_builder.utils import ImportMapper, db_type_is
from pypika.terms import Case, ValueWrapper
from pypika import CustomFunction, Order
```

| Action | Pattern |
|--------|---------|
| SELECT | `frappe.qb.from_("DocType").select("field1", "field2")` |
| WHERE | `.where(Field("status") == "Open")` |
| ORDER | `.orderby("creation", order=Order.desc)` |
| LIMIT | `.limit(10).offset(0)` |
| JOIN | `.left_join(dt2).on(dt2.name == dt1.parent)` |
| COUNT | `.select(Count("*"))` |
| INSERT | `frappe.qb.into("DocType").columns("f1", "f2").insert("v1", "v2")` |
| UPDATE | `frappe.qb.update("DocType").set("field", "value").where(...)` |
| DELETE | `frappe.qb.from_("DocType").delete().where(...)` |
| RUN | `.run()` (tuples) / `.run(as_dict=True)` (dicts) |

---

## Decision Tree

```
Need to query the database?
│
├─ Simple get/list → frappe.db.get_value(), frappe.get_all()
│  (See frappe-core-database skill)
│
├─ Complex query with joins/aggregates/subqueries → frappe.qb ✓
│
├─ Very complex SQL not expressible in qb → frappe.db.sql()
│  (ALWAYS use parameterized values: frappe.db.sql(query, values))
│
└─ Need cross-DB compatibility → frappe.qb + ImportMapper ✓

Using frappe.qb?
│
├─ Table reference → DocType("Sales Order") — NEVER use Table()
├─ Field reference → dt.field_name or Field("field_name")
├─ Execute → .run() for tuples, .run(as_dict=True) for dicts
├─ DB-specific function → ImportMapper({db_type_is.MARIADB: X, db_type_is.POSTGRES: Y})
└─ Get SQL string → query.get_sql() — NEVER pass to frappe.db.sql()
```

---

## Core Patterns

### SELECT with DocType

```python
# ALWAYS use DocType() for table references — adds "tab" prefix
so = frappe.qb.DocType("Sales Order")
soi = frappe.qb.DocType("Sales Order Item")

orders = (
    frappe.qb.from_(so)
    .select(so.name, so.customer, so.grand_total)
    .where(so.status == "To Deliver and Bill")
    .where(so.docstatus == 1)
    .orderby(so.creation, order=Order.desc)
    .limit(20)
    .run(as_dict=True)
)
```

### JOIN

```python
result = (
    frappe.qb.from_(so)
    .left_join(soi).on(soi.parent == so.name)
    .select(so.name, so.customer, soi.item_code, soi.qty)
    .where(so.docstatus == 1)
    .where(soi.item_code.like("ITEM-%"))
    .run(as_dict=True)
)
```

### Aggregation

```python
from frappe.query_builder.functions import Count, Sum

gl = frappe.qb.DocType("GL Entry")
result = (
    frappe.qb.from_(gl)
    .select(gl.account, Sum(gl.debit).as_("total_debit"), Count("*").as_("entries"))
    .where(gl.docstatus == 1)
    .groupby(gl.account)
    .run(as_dict=True)
)

# Shortcut aggregation methods
total = frappe.qb.sum("GL Entry", "debit", filters={"account": "Sales"})
max_qty = frappe.qb.max("Stock Ledger Entry", "actual_qty", filters={"item_code": "ITEM-001"})
```

### INSERT / UPDATE / DELETE

```python
# INSERT
frappe.qb.into("Activity Log").columns("user", "action").insert("admin", "login").run()

# UPDATE
customer = frappe.qb.DocType("Customer")
(frappe.qb.update(customer)
    .set(customer.status, "Active")
    .where(customer.name == "CUST-001")
    .run())

# DELETE
frappe.qb.from_("Error Log").delete().where(Field("creation") < "2024-01-01").run()
```

---

## Filtering

```python
dt = frappe.qb.DocType("Sales Order")

# Equality
.where(dt.status == "Open")

# OR (pipe operator)
.where((dt.status == "Open") | (dt.status == "Draft"))

# AND (chain .where() calls)
.where(dt.status == "Open")
.where(dt.docstatus == 1)

# LIKE
.where(dt.customer.like("CUST-%"))

# IN
.where(dt.status.isin(["Open", "Draft"]))

# BETWEEN (bracket syntax)
.where(dt.creation[start_date:end_date])

# NULL checks
.where(dt.email.isnotnull())
.where(dt.phone.isnull())

# Comparison
.where(dt.grand_total > 1000)
.where(dt.grand_total >= 500)
.where(dt.status != "Cancelled")
```

---

## Cross-DB Compatibility

```python
from frappe.query_builder.utils import ImportMapper, db_type_is
from frappe.query_builder.custom import GROUP_CONCAT, STRING_AGG

# ImportMapper selects correct function per database
GroupConcat = ImportMapper({
    db_type_is.MARIADB: GROUP_CONCAT,
    db_type_is.POSTGRES: STRING_AGG,
})

dt = frappe.qb.DocType("Has Role")
result = (
    frappe.qb.from_(dt)
    .select(dt.parent, GroupConcat(dt.role))
    .groupby(dt.parent)
    .run(as_dict=True)
)
```

| MariaDB | PostgreSQL | Use ImportMapper |
|---------|-----------|-----------------|
| `GROUP_CONCAT` | `STRING_AGG` | Yes |
| `MATCH...AGAINST` | `TO_TSVECTOR` | Yes |
| `Locate` | `Strpos` | Yes |
| `Timestamp` | Extract-based | Auto-handled |

---

## Anti-patterns

1. **NEVER pass qb query to `frappe.db.sql()`** — bypasses parameterization
2. **NEVER use `Table()` for DocTypes** — use `DocType()` (adds `tab` prefix)
3. **NEVER forget `.run()`** — without it you get a query object, not results
4. **NEVER use raw SQL strings in `frappe.get_all(fields=[...])`** — use dict syntax
5. **ALWAYS use `ImportMapper` for DB-specific functions**
6. **ALWAYS chain `.run(as_dict=True)` when you need dicts** — default is tuples

---

## Version Differences

| Feature | v14 | v15 | v16 |
|---------|:---:|:---:|:---:|
| Core qb API | Introduced | Yes | Yes |
| ImportMapper | Yes | Yes | Yes |
| SQLite backend | -- | -- | Added |
| Masked fields | -- | -- | Added |
| Union queries (.walk) | -- | Added | Yes |
| Child query execution | -- | -- | Added |

---

## Reference Files

- [Functions & Aggregates](references/functions-reference.md) — All available qb functions
- [Migration Guide](references/migration-from-sql.md) — Converting raw SQL and get_all patterns
- [Cross-DB Patterns](references/cross-db-patterns.md) — ImportMapper and DB-specific functions
---
name: frappe-syntax-reports
description: >
  Use when building Query Reports, Script Reports, or configuring Report Builder, including chart data integration.
  Prevents report errors from wrong column definitions, missing permissions, and incorrect data formatting.
  Covers Query Report (SQL-based), Script Report (Python-based), Report Builder, report columns definition, filters, chart_data, report permissions, prepared_report.
  Keywords: Query Report, Script Report, Report Builder, report columns, filters, chart_data, frappe.query_report, prepared_report, report columns, how to build report, report not showing data, chart in report..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Reports: Query, Script & Report Builder

## Quick Reference

### Report Types at a Glance

| Type | Code Required | Use Case | Permission |
|------|--------------|----------|------------|
| Report Builder | None | Simple single-DocType listing with filters, group by | Any user |
| Query Report | SQL only | Direct SQL queries, legacy column format | System Manager |
| Script Report (Standard) | Python + JS | Complex logic, charts, summaries, trees | Administrator + Developer Mode |
| Script Report (Custom) | Python in UI | Quick custom reports without app deployment | System Manager |

### Script Report execute() Return Values

```python
def execute(filters=None):
    columns = [...]   # List of dicts
    data = [...]      # List of dicts or lists
    message = "..."   # Optional: HTML message above report
    chart = {...}     # Optional: chart configuration
    report_summary = [...]  # Optional: summary cards
    skip_total_row = False  # Optional: suppress auto-total
    return columns, data, message, chart, report_summary, skip_total_row
```

### Column Definition (Dict Format)

```python
columns = [
    {
        "fieldname": "customer",
        "label": _("Customer"),
        "fieldtype": "Link",
        "options": "Customer",
        "width": 200
    },
    {
        "fieldname": "amount",
        "label": _("Amount"),
        "fieldtype": "Currency",
        "options": "currency",  # field in row holding currency code
        "width": 120
    }
]
```

### Query Report Column Format (Legacy String)

```sql
SELECT
  name as "Sales Order:Link/Sales Order:200",
  customer as "Customer:Link/Customer:180",
  grand_total as "Total:Currency:120",
  transaction_date as "Date:Date:100"
FROM `tabSales Order`
WHERE docstatus = 1
```

Format: `"Label:Fieldtype/Options:Width"` — Options only needed for Link, Dynamic Link, Currency.

### Filter Definition (JS)

```javascript
frappe.query_reports["My Report"] = {
    filters: [
        {
            fieldname: "company",
            label: __("Company"),
            fieldtype: "Link",
            options: "Company",
            default: frappe.defaults.get_user_default("company"),
            reqd: 1
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            fieldname: "status",
            label: __("Status"),
            fieldtype: "Select",
            options: "\nDraft\nSubmitted\nCancelled"
        }
    ]
};
```

## Decision Tree: Which Report Type?

```
Need a report?
├─ Simple list/group of one DocType → Report Builder
│   (no code, UI-only, supports Group By with Count/Sum/Avg)
├─ Direct SQL query, no Python logic needed → Query Report
│   (SQL in Report doc, column format in aliases)
├─ Complex logic, calculations, charts → Script Report (Standard)
│   (Python .py + JS .js files, requires Developer Mode)
└─ Quick one-off with Python but no app deploy → Script Report (Custom)
    (Python in Report doc UI, System Manager can create)
```

```
Script Report returns what?
├─ Just data → return columns, data
├─ Data + chart → return columns, data, None, chart
├─ Data + summary → return columns, data, None, None, report_summary
├─ Data + message → return columns, data, message
└─ Everything → return columns, data, message, chart, report_summary, skip_total_row
```

## Supported Fieldtypes for Columns

| Fieldtype | Options Required | Notes |
|-----------|-----------------|-------|
| `Data` | No | Plain text |
| `Link` | DocType name | Clickable link to document |
| `Dynamic Link` | Fieldname holding DocType | Pair with a column containing DocType |
| `Currency` | Currency field or code | Fieldname in row that holds currency |
| `Float` | No | Decimal number |
| `Int` | No | Integer |
| `Percent` | No | Shows percentage bar |
| `Date` | No | Date display |
| `Datetime` | No | Date + time |
| `Check` | No | Boolean checkbox |
| `Select` | No | Dropdown value |
| `Text` | No | Long text |
| `HTML` | No | Raw HTML rendering |

## Supported Filter Fieldtypes

| Fieldtype | Options | Behavior |
|-----------|---------|----------|
| `Link` | DocType name | Autocomplete from DocType |
| `Select` | Newline-separated values | Dropdown with fixed options |
| `Date` | — | Date picker |
| `DateRange` | — | Returns `[from_date, to_date]` list |
| `Check` | — | Boolean toggle |
| `Dynamic Link` | Fieldname of Link filter | Depends on another filter value |
| `Data` | — | Free text input |
| `Int` | — | Numeric input |
| `MultiSelectList` | DocType name | Multiple value selection |

## Chart Data Format

```python
chart = {
    "data": {
        "labels": ["Jan", "Feb", "Mar", "Apr"],
        "datasets": [
            {"name": _("Revenue"), "values": [100, 200, 150, 300]},
            {"name": _("Expense"), "values": [80, 150, 120, 250]}
        ]
    },
    "type": "bar",        # bar, line, pie, donut, percentage
    "fieldtype": "Currency",
    "options": "currency",
    "currency": "USD",
    "colors": ["#5e64ff", "#ffa00a"]  # Optional custom colors
}
```

## Report Summary Format

```python
report_summary = [
    {
        "value": total_revenue,
        "label": _("Total Revenue"),
        "datatype": "Currency",
        "currency": "USD",
        "indicator": "Green"   # Green, Blue, Orange, Red
    },
    {
        "value": total_count,
        "label": _("Total Orders"),
        "datatype": "Int",
        "indicator": "Blue"
    }
]
```

## Prepared Reports

For reports processing large datasets, enable **Prepared Report** to run asynchronously:

1. Set `prepared_report = 1` in the Report document
2. User clicks "Generate New Report" — runs in background via `enqueue()`
3. Results stored in file; user downloads or views when ready
4. ALWAYS use for reports that query > 100k rows or take > 30 seconds

## Number Cards

| Source Type | Required Fields | How It Works |
|-------------|----------------|--------------|
| Document Type | `document_type`, `function`, `aggregate_function_based_on` | SQL aggregate on DocType |
| Report | `report_name`, `report_field`, `function` | Pulls value from a report column |
| Custom Method | `method` | Calls a whitelisted Python method |

Custom method signature:
```python
@frappe.whitelist()
def get_total_active_users(filters=None):
    return frappe.db.count("User", {"enabled": 1})
```

## Dashboard Charts

| Source | Configuration | Data Format |
|--------|--------------|-------------|
| Report | Set `chart_type = "Report"`, select report | Uses report's chart data |
| Custom | Set `chart_type = "Custom"`, define `source` | Hook returns `{"labels": [...], "datasets": [...]}` |
| Group By | Set `chart_type = "Group By"`, pick field | Auto-aggregates by field |

Dashboard Chart Source hook in `hooks.py`:
```python
dashboard_chart_source = [
    "myapp.dashboard_chart_source.get_chart_data"
]
```

## Critical Rules

- **ALWAYS** define columns as list of dicts with `fieldname`, `label`, `fieldtype`. The legacy string format is ONLY for Query Report SQL aliases.
- **NEVER** return `None` for `columns` or `data` in `execute()` — ALWAYS return empty lists `[]`.
- **ALWAYS** use `_(...)` for translatable labels in columns and report_summary.
- **NEVER** use `frappe.db.sql` with user-supplied filter values directly in f-strings — ALWAYS pass as parameters: `frappe.db.sql(query, filters, as_dict=True)`.
- **ALWAYS** set `Reference DocType` on the Report document — it controls user access permissions.
- **NEVER** omit `width` in column definitions — columns without width render poorly.
- **ALWAYS** match `datasets[].values` length to `labels` length in chart data — mismatched lengths cause chart rendering errors.

## See Also

- [references/query-report.md](references/query-report.md) — Complete Query Report API
- [references/script-report.md](references/script-report.md) — Script Report JS API
- [references/examples.md](references/examples.md) — Working report examples
- [references/anti-patterns.md](references/anti-patterns.md) — Common report mistakes
- [references/dashboard.md](references/dashboard.md) — Number Cards, Dashboard Charts
---
name: frappe-syntax-scheduler
description: >
  Use when configuring scheduler events and background jobs in Frappe/ERPNext
  v14/v15/v16. Covers scheduler_events in hooks.py, frappe.enqueue() for
  async jobs, queue configuration, job deduplication, error handling, and
  monitoring. Keywords: scheduler, background job, cron, RQ worker, job
  queue, async task, frappe.enqueue, scheduled task,
  cron syntax, how often does it run, background job example, enqueue example.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Scheduler & Background Jobs

Deterministic syntax reference for Frappe scheduler events and background job processing via Redis Queue (RQ).

## Decision Tree

```
Need periodic execution?
├─ Fixed interval (hourly/daily/weekly/monthly) → scheduler_events in hooks.py
├─ Custom cron schedule → scheduler_events.cron in hooks.py
├─ User-configurable interval → Scheduled Job Type DocType
└─ No, triggered by user/event
   ├─ Run method on a specific document → frappe.enqueue_doc()
   ├─ Run standalone function async → frappe.enqueue()
   └─ Run from controller on self → self.queue_action()
```

## Quick Reference: Scheduler Events (hooks.py)

```python
# hooks.py — ALWAYS run bench migrate after changes
scheduler_events = {
    # Standard events (default queue)
    "all": ["myapp.tasks.every_tick"],           # Every tick [v14: 240s, v15+: 60s]
    "hourly": ["myapp.tasks.hourly_task"],
    "daily": ["myapp.tasks.daily_task"],
    "weekly": ["myapp.tasks.weekly_task"],
    "monthly": ["myapp.tasks.monthly_task"],

    # Long queue events (for heavy processing)
    "hourly_long": ["myapp.tasks.hourly_heavy"],
    "daily_long": ["myapp.tasks.daily_heavy"],
    "weekly_long": ["myapp.tasks.weekly_heavy"],
    "monthly_long": ["myapp.tasks.monthly_heavy"],

    # Cron events (croniter-compatible syntax)
    "cron": {
        "*/15 * * * *": ["myapp.tasks.every_15_min"],
        "0 9 * * 1-5": ["myapp.tasks.weekday_9am"],
        "0 0 1 * *": ["myapp.tasks.first_of_month"],
    }
}
```

**CRITICAL**: ALWAYS run `bench migrate` after ANY change to scheduler_events. Without it, changes are NOT applied.

## Scheduler Event Types

| Event | Frequency | Queue | Use Case |
|-------|-----------|-------|----------|
| `all` | Every tick [v14: 4min, v15+: 60s] | default | Frequent polling |
| `hourly` | Once per hour | default | Sync, cleanup |
| `daily` | Once per day | default | Reports, summaries |
| `weekly` | Once per week | default | Archival |
| `monthly` | Once per month | default | Billing, statements |
| `hourly_long` | Once per hour | **long** | Heavy sync |
| `daily_long` | Once per day | **long** | Large exports |
| `weekly_long` | Once per week | **long** | Data warehousing |
| `monthly_long` | Once per month | **long** | Annual reports |
| `cron` | Custom schedule | configurable | Any custom timing |

## Cron Syntax

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * *
```

| Symbol | Meaning | Example |
|--------|---------|---------|
| `*` | Any value | `* * * * *` = every minute |
| `,` | List | `1,15 * * * *` = minute 1 and 15 |
| `-` | Range | `0 9-17 * * *` = hours 9 through 17 |
| `/` | Interval | `*/10 * * * *` = every 10 minutes |

Common patterns:
- Every 5 min: `*/5 * * * *`
- Weekdays at 9:00: `0 9 * * 1-5`
- Monday at 8:00: `0 8 * * 1`
- Business hours hourly: `0 9-17 * * 1-5`

## Quick Reference: frappe.enqueue()

```python
frappe.enqueue(
    method,                      # REQUIRED: function or "dotted.module.path"
    queue="default",             # "short", "default", "long", or custom
    timeout=None,                # Override queue timeout (seconds)
    is_async=True,               # False = run synchronously (skip worker)
    now=False,                   # True = run via frappe.call() directly
    job_id=None,                 # [v15+] Unique ID for deduplication
    enqueue_after_commit=False,  # Wait for DB commit before enqueue
    at_front=False,              # Place at front of queue
    on_success=None,             # Success callback
    on_failure=None,             # Failure callback
    **kwargs                     # Arguments passed to method
)
```

## Queue Types

| Queue | Default Timeout | Use When |
|-------|-----------------|----------|
| `short` | 300s (5 min) | Task < 30 seconds |
| `default` | 300s (5 min) | Task 30s - 5 min |
| `long` | 1500s (25 min) | Task 5 - 25 min |
| `long` + custom timeout | user-defined | Task > 25 min |

```python
# Short queue — quick status update
frappe.enqueue("myapp.tasks.update_status", queue="short", doc=doc.name)

# Long queue — heavy report generation
frappe.enqueue("myapp.tasks.generate_report", queue="long", timeout=3600)
```

## frappe.enqueue_doc()

Enqueue a controller method on a specific document.

```python
frappe.enqueue_doc(
    "Sales Invoice",              # DocType
    "SINV-00001",                 # Document name
    "send_notification",          # Controller method name
    queue="long",
    timeout=600,
    recipient="user@example.com"  # kwargs passed to method
)
```

The controller method MUST be decorated with `@frappe.whitelist()`:

```python
class SalesInvoice(Document):
    @frappe.whitelist()
    def send_notification(self, recipient):
        # self is the loaded document
        pass
```

## self.queue_action()

Alternative from within a controller:

```python
class SalesOrder(Document):
    def on_submit(self):
        self.queue_action("send_emails", emails=email_list)

    def send_emails(self, emails):
        for email in emails:
            send_mail(email)
```

## Job Deduplication

### [v15+] Recommended Pattern

```python
from frappe.utils.background_jobs import is_job_enqueued

job_id = f"import::{doc.name}"
if not is_job_enqueued(job_id):
    frappe.enqueue(
        "myapp.tasks.import_data",
        job_id=job_id,
        doc_name=doc.name
    )
else:
    frappe.msgprint("Import already in progress")
```

### [v14] Legacy Pattern (NEVER use in new code)

```python
from frappe.core.page.background_jobs.background_jobs import get_info
enqueued = [d.get("job_name") for d in get_info()]
if name not in enqueued:
    frappe.enqueue(..., job_name=name)
```

## Error Handling Pattern

ALWAYS use try/except with commit/rollback per record in batch jobs:

```python
def process_records(records):
    success, errors = 0, 0
    for record in records:
        try:
            process_single(record)
            frappe.db.commit()
            success += 1
        except Exception:
            frappe.db.rollback()
            frappe.log_error(
                frappe.get_traceback(),
                f"Process Error: {record}"
            )
            errors += 1
    return {"success": success, "errors": errors}
```

## Retry Pattern

```python
def task_with_retry(data, retry_count=0, max_retries=3):
    try:
        external_api_call(data)
    except Exception:
        if retry_count < max_retries:
            frappe.enqueue(
                "myapp.tasks.task_with_retry",
                queue="default",
                data=data,
                retry_count=retry_count + 1,
                max_retries=max_retries,
                enqueue_after_commit=True
            )
            frappe.log_error(f"Retry {retry_count+1}/{max_retries}", "Task Retry")
        else:
            frappe.log_error(frappe.get_traceback(), f"Failed after {max_retries} retries")
            raise
```

## Callbacks

```python
def on_success_handler(job, connection, result, *args, **kwargs):
    frappe.publish_realtime("show_alert", {"message": "Done!"})

def on_failure_handler(job, connection, type, value, traceback):
    frappe.log_error(f"Job {job.id} failed: {value}", "Job Error")

frappe.enqueue(
    "myapp.tasks.risky_task",
    on_success=on_success_handler,
    on_failure=on_failure_handler,
)
```

## Progress Updates

```python
def long_task(items, user):
    total = len(items)
    for i, item in enumerate(items):
        process_item(item)
        frappe.publish_realtime(
            "task_progress",
            {"progress": (i + 1) / total * 100, "current": i + 1, "total": total},
            user=user,
        )
```

## User Context

**CRITICAL**: Scheduler jobs run as **Administrator**. ALWAYS set explicit ownership when creating documents:

```python
def scheduled_task():
    doc = frappe.new_doc("ToDo")
    doc.owner = "user@example.com"
    doc.insert(ignore_permissions=True)
```

## Monitoring

| Tool | Purpose |
|------|---------|
| `bench doctor` | Scheduler status, worker health |
| RQ Worker (DocType) | Worker status: busy/idle |
| RQ Job (DocType) | Job status, queue filtering |
| Scheduled Job Log (DocType) | Execution history, errors |
| `logs/worker.error.log` | Worker exceptions |
| `logs/scheduler.log` | Scheduler activity |

## Version Differences

| Feature | v14 | v15+ |
|---------|-----|------|
| Tick interval (`all` event) | ~240s (4 min) | ~60s |
| Config key for tick | `scheduler_interval` | `scheduler_tick_interval` |
| Deduplication | `job_name` (deprecated) | `job_id` + `is_job_enqueued()` |

Custom tick in `common_site_config.json`:

```json
{ "scheduler_tick_interval": 120 }
```

## Critical Rules

1. **ALWAYS** run `bench migrate` after any scheduler_events change in hooks.py
2. **ALWAYS** use `job_id` + `is_job_enqueued()` for deduplication [v15+]
3. **ALWAYS** choose the correct queue: short/default/long based on task duration
4. **ALWAYS** commit per record and rollback on error in batch jobs
5. **ALWAYS** remember that scheduler jobs run as Administrator
6. **NEVER** run heavy logic directly in a scheduler event — enqueue it instead
7. **NEVER** use `job_name` for deduplication in new code (v14 legacy)

## Reference Files

- **[scheduler-events.md](references/scheduler-events.md)**: All event types, cron syntax, configuration
- **[enqueue-api.md](references/enqueue-api.md)**: Complete frappe.enqueue / enqueue_doc API
- **[queues.md](references/queues.md)**: Queue types, timeouts, custom queues, workers
- **[monitoring.md](references/monitoring.md)**: RQ DocTypes, bench doctor, log files, alerts
- **[error-handling.md](references/error-handling.md)**: Error patterns, retry, batch processing
- **[examples.md](references/examples.md)**: Complete working examples
- **[anti-patterns.md](references/anti-patterns.md)**: Common mistakes and corrections

## See Also

- `frappe-syntax-hooks` — Full hooks.py reference
- `frappe-core-background` — Background job architecture
- `frappe-errors-jobs` — Job failure debugging
---
name: frappe-syntax-serverscripts
description: >
  Use when writing Python code for ERPNext/Frappe Server Scripts including
  Document Events, API endpoints, Scheduler Events, and Permission Queries.
  Prevents the #1 AI mistake: using import statements in Server Scripts
  (sandbox blocks ALL imports). Covers frappe.* methods, event name mapping,
  and correct v14/v15/v16 syntax. Keywords: Server Script, frappe, ERPNext,
  sandbox, import, doc event, validate, on_submit, before_save,
  server script example, import not allowed, sandbox rules, which script type to use.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Frappe Server Scripts — Complete Reference

Server Scripts are Python scripts managed via **Setup > Server Script** in the
Frappe/ERPNext UI. They run inside a **RestrictedPython sandbox**.

## CRITICAL: The Sandbox Rule

```
┌──────────────────────────────────────────────────────────────────┐
│  ALL import STATEMENTS ARE BLOCKED                               │
│                                                                  │
│  import json             → ImportError: __import__ not found     │
│  from datetime import *  → ImportError: __import__ not found     │
│  import frappe           → ImportError (even frappe itself!)     │
│                                                                  │
│  EVERYTHING you need is pre-loaded in the frappe namespace.      │
│  NEVER write an import line. ALWAYS use frappe.utils.*, etc.     │
└──────────────────────────────────────────────────────────────────┘
```

**ALWAYS** use the pre-loaded namespace instead of imports:

| Blocked import | Use instead |
|---|---|
| `import json` | `frappe.parse_json()` / `frappe.as_json()` |
| `from datetime import date` | `frappe.utils.today()` / `frappe.utils.now_datetime()` |
| `from frappe.utils import cint` | `frappe.utils.cint()` (already loaded) |
| `import requests` | `frappe.make_get_request()` / `frappe.make_post_request()` |
| `import re` | Not available — restructure logic without regex |
| `import os` / `import sys` | Not available — use a custom app instead |

## Enabling Server Scripts

```bash
# v14: enabled by default
# v15+: DISABLED by default — you MUST enable explicitly:
bench set-config -g server_script_enabled 1
# Or set server_script_enabled: true in site_config.json
```

**NEVER** expect Server Scripts to work on Frappe Cloud shared benches — they
require a private bench.

## Script Types

| Type | Trigger | Key Variable |
|---|---|---|
| **Document Event** | Document lifecycle (save, submit, cancel) | `doc` |
| **API** | HTTP request to `/api/method/{name}` | `frappe.form_dict` |
| **Scheduler Event** | Cron schedule | (none) |
| **Permission Query** | Document list filtering | `user`, `conditions` |

## Event Name Mapping (Document Events)

**CRITICAL**: The UI names differ from internal hook names:

| Server Script UI | Internal Hook | Fires When |
|---|---|---|
| Before Insert | `before_insert` | Before new doc saved to DB |
| After Insert | `after_insert` | After first DB insert |
| Before Validate | `before_validate` | Before framework validation |
| **Before Save** | **`validate`** | Before save (new + update) |
| After Save | `on_update` | After successful save |
| Before Submit | `before_submit` | Before submit (docstatus 0→1) |
| After Submit | `on_submit` | After submit completes |
| Before Cancel | `before_cancel` | Before cancel (docstatus 1→2) |
| After Cancel | `on_cancel` | After cancel completes |
| Before Delete | `on_trash` | Before permanent delete |
| After Delete | `after_delete` | After permanent delete |

**NEVER** confuse "Before Save" with `before_save` — the UI label "Before Save"
maps to the `validate` hook. The actual `before_save` hook runs AFTER `validate`.

## Decision Tree: Server Script vs Document Controller

```
Need custom Python logic for a DocType?
│
├─► Can you install a custom Frappe app?
│   ├─► YES: Use a Document Controller when you need:
│   │   • import statements (any Python library)
│   │   • File system access
│   │   • Complex class inheritance
│   │   • autoname / before_naming hooks
│   │   • Unit-testable code
│   │
│   └─► NO: Use a Server Script when:
│       • You only have UI access (no bench CLI)
│       • Logic is simple validation / field calculation
│       • You need a quick API endpoint
│       • You need dynamic permission filtering
│
└─► Is logic > 50 lines or needs external libraries?
    ├─► YES → Document Controller in a custom app
    └─► NO  → Server Script is fine
```

## Quick Reference: Available in Sandbox

### Pre-loaded Objects

```python
doc                         # Current document (Document Event only)
frappe                      # Core namespace — ALWAYS available
frappe.db                   # Database operations
frappe.utils                # Date, number, string utilities
frappe.session              # Current session (user, csrf_token)
frappe.form_dict            # Request parameters (API scripts)
frappe.response             # Response object (API scripts)
frappe.request              # Werkzeug request object
frappe.qb                   # Query Builder (v14+)
json                        # Python json module (pre-loaded)
```

### Core Methods

```python
# Documents
frappe.get_doc(doctype, name)           # Fetch document
frappe.new_doc(doctype)                 # Create new document
frappe.get_cached_doc(doctype, name)    # Cached fetch (read-only)
frappe.get_last_doc(doctype)            # Most recent document
frappe.get_mapped_doc(...)              # Map fields between DocTypes
frappe.delete_doc(doctype, name)        # Delete document
frappe.rename_doc(doctype, old, new)    # Rename document

# Querying
frappe.get_all(doctype, filters, fields, order_by, limit)   # No permission check
frappe.get_list(doctype, filters, fields, order_by, limit)  # With permission check
frappe.db.get_value(doctype, name, fieldname)
frappe.db.get_single_value(doctype, fieldname)
frappe.db.set_value(doctype, name, fieldname, value)
frappe.db.exists(doctype, name_or_filters)
frappe.db.count(doctype, filters)
frappe.db.sql(query, values, as_dict)   # ALWAYS parameterize!
frappe.db.escape(value)                 # SQL escape
frappe.db.commit()                      # ONLY in Scheduler scripts
frappe.db.rollback()                    # ONLY in Scheduler scripts

# Messaging
frappe.throw(msg, exc, title)           # Stop execution + show error
frappe.msgprint(msg, title, indicator)  # User notification
frappe.log_error(message, title)        # Error Log entry

# HTTP (yes, these work in sandbox!)
frappe.make_get_request(url, params, headers)
frappe.make_post_request(url, data, headers)
frappe.make_put_request(url, data, headers)

# Email
frappe.sendmail(recipients, sender, subject, message)

# Utilities
frappe.utils.today()                    # "2024-01-15"
frappe.utils.now()                      # "2024-01-15 10:30:00"
frappe.utils.now_datetime()             # datetime object
frappe.utils.add_days(date, n)          # Date arithmetic
frappe.utils.add_months(date, n)
frappe.utils.date_diff(d1, d2)          # Days between dates
frappe.utils.flt(val)                   # Safe float (None → 0.0)
frappe.utils.cint(val)                  # Safe int (None → 0)
frappe.utils.cstr(val)                  # Safe string (None → "")
frappe.parse_json(string)               # JSON string → dict/list
frappe.as_json(obj)                     # dict/list → JSON string
frappe.render_template(template, ctx)   # Jinja rendering
frappe.get_url()                        # Site URL
frappe.get_hooks(hook)                  # Read app hooks
run_script(script_name, **kwargs)       # Call another Server Script

# Session / Permissions
frappe.session.user                     # Current user email
frappe.get_roles(user)                  # User's roles list
frappe.has_permission(doctype, ptype, doc)
frappe.get_fullname(user)               # User's display name
_("translatable string")               # Translation function
```

### Python Builtins Available

```python
str, int, float, bool, list, dict, tuple, set  # Types
range, enumerate, zip, map, filter              # Iteration
sum, min, max, len, sorted, reversed            # Aggregation
isinstance, type, hasattr, getattr              # Introspection
all, any, abs, round, divmod                    # Math/logic
print                                           # → server log
True, False, None                               # Constants
```

### Python Builtins BLOCKED

```python
open, file          # No file I/O
eval, exec, compile # No dynamic code execution
__import__          # No imports (this is the root cause)
globals, locals     # No scope introspection
```

## Syntax Per Script Type

### Document Event

```python
# Config: Reference DocType = Sales Invoice, Event = Before Save
if doc.grand_total < 0:
    frappe.throw("Total MUST NOT be negative")

doc.requires_approval = 1 if doc.grand_total > 10000 else 0
```

### API

```python
# Config: API Method = get_customer_orders, Allow Guest = No
# Endpoint: /api/method/get_customer_orders
customer = frappe.form_dict.get("customer")
if not customer:
    frappe.throw("Parameter 'customer' is required")

orders = frappe.get_all("Sales Order",
    filters={"customer": customer, "docstatus": 1},
    fields=["name", "grand_total", "status"],
    order_by="creation desc",
    limit=20
)
frappe.response["message"] = {"orders": orders, "count": len(orders)}
```

### Scheduler Event

```python
# Config: Event Frequency = Cron, Cron Format = 0 9 * * *
overdue = frappe.get_all("Sales Invoice",
    filters={"status": "Unpaid", "due_date": ["<", frappe.utils.today()], "docstatus": 1},
    fields=["name", "customer", "grand_total"]
)
for inv in overdue:
    frappe.log_error(f"Overdue: {inv.name} ({inv.customer})", "Invoice Reminder")

frappe.db.commit()  # ALWAYS commit in Scheduler scripts
```

### Permission Query

```python
# Config: Reference DocType = Sales Invoice
# Variables available: user, conditions
roles = frappe.get_roles(user)
if "System Manager" in roles:
    conditions = ""
elif "Sales User" in roles:
    conditions = f"`tabSales Invoice`.owner = {frappe.db.escape(user)}"
else:
    conditions = "1=0"
```

## Version Differences

| Feature | v14 | v15 | v16 |
|---|---|---|---|
| Server Scripts enabled | By default | **Disabled by default** | Disabled by default |
| Enable command | Not needed | `bench set-config -g server_script_enabled 1` | Same as v15 |
| `frappe.qb` (Query Builder) | Available | Available | Available |
| `run_script()` for libraries | v13+ | Available | Available |
| `frappe.make_get_request()` | Available | Available | Available |
| Frappe Cloud shared bench | Supported | **NOT supported** | NOT supported |

## Top 5 Rules

1. **NEVER** write `import` — everything is in the `frappe` namespace
2. **NEVER** call `doc.save()` inside a Before Save script — causes infinite loop
3. **NEVER** call `frappe.db.commit()` in Document Event scripts — framework handles it
4. **ALWAYS** call `frappe.db.commit()` at the end of Scheduler scripts
5. **ALWAYS** use parameterized queries: `%(var)s` with dict, NEVER f-strings in SQL

## References

- **[references/methods.md](references/methods.md)** — Complete sandbox API reference
- **[references/events.md](references/events.md)** — Document lifecycle and execution order
- **[references/examples.md](references/examples.md)** — Working examples per script type
- **[references/anti-patterns.md](references/anti-patterns.md)** — Sandbox violations and common mistakes
- **[references/syntax.md](references/syntax.md)** — Quick syntax cheat sheet
- **[references/patterns.md](references/patterns.md)** — Common patterns (validation, auto-fill, API)
- **[references/hooks.md](references/hooks.md)** — Server Scripts vs hooks.py interaction

## Cross-References

- **frappe-syntax-api** — Frappe REST API and whitelisted methods
- **frappe-syntax-doctype** — DocType field types and schema
- **frappe-core-database** — frappe.db deep dive
- **frappe-core-permissions** — Permission system architecture
- **frappe-errors-common** — Error handling patterns
---
name: frappe-syntax-whitelisted
description: >
  Use when creating Frappe Whitelisted Methods (Python API endpoints) for
  v14/v15/v16. Covers @frappe.whitelist() decorator, frappe.call/frm.call
  invocations, permission checks, error handling, response formats, and
  client-server communication. Keywords: whitelisted, API endpoint,
  frappe.call, frm.call, REST API, @frappe.whitelist, allow_guest,
  API endpoint example, frappe.whitelist syntax, how to expose function.
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---
# Frappe Syntax: Whitelisted Methods

Whitelisted methods expose Python functions as HTTP API endpoints via `/api/method/`.

## Quick Reference

```python
import frappe
from frappe import _

# Authenticated endpoint (default)
@frappe.whitelist()
def get_customer_summary(customer):
    frappe.has_permission("Customer", "read", throw=True)
    return frappe.get_doc("Customer", customer).as_dict()

# Public endpoint — ALWAYS validate input thoroughly
@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_contact(name, email, message):
    if not name or not email:
        frappe.throw(_("Name and email required"), frappe.ValidationError)
    return {"success": True}

# Controller method — called via frm.call('method_name')
class SalesOrder(Document):
    @frappe.whitelist()
    def calculate_taxes(self, include_shipping=False):
        return {"tax": self.grand_total * 0.21}
```

**Endpoint URL**: `/api/method/myapp.module.function_name`

---

## Decorator Signature [v14+]

```python
@frappe.whitelist(
    allow_guest=False,   # True = accessible without login
    xss_safe=False,      # True = do NOT escape HTML in response
    methods=None,        # ["GET"], ["POST"], or ["GET","POST"] — default: all
    force_types=None     # True = require type annotations [v15+]
)
```

| Parameter | Default | Effect |
|-----------|---------|--------|
| `allow_guest` | `False` | `True` = Guest role can call; ALWAYS add extra input validation |
| `xss_safe` | `False` | `True` = HTML not escaped; NEVER use without sanitized output |
| `methods` | `None` (all) | Restrict allowed HTTP verbs |
| `force_types` | `None` | `True` = all params MUST have type annotations [v15+] |

Full details: [decorator-options.md](references/decorator-options.md)

---

## Decision Tree

```
What kind of endpoint?
|
+-- Standalone API (utility, integration, dashboard)?
|   --> @frappe.whitelist() on a module-level function
|   --> Call via: frappe.call('myapp.api.function')
|   --> URL: /api/method/myapp.api.function
|
+-- Document-specific action?
|   --> @frappe.whitelist() on a Document class method
|   --> Call via: frm.call('method_name')
|   --> URL: /api/method/run_doc_method (internal)
|
+-- Server Script (no-code)?
    --> Use Server Script DocType instead (no decorator needed)

Who may call the API?
|
+-- Anyone (including guests)?
|   --> allow_guest=True + thorough input validation + rate limiting
|
+-- Logged-in users only?
    +-- Specific role? --> frappe.only_for("RoleName")
    +-- DocType-level? --> frappe.has_permission(doctype, ptype, throw=True)
    +-- Document-level? --> frappe.has_permission(doctype, ptype, doc, throw=True)

Which HTTP methods?
|
+-- Read only? --> methods=["GET"]
+-- Write only? --> methods=["POST"]
+-- Both? --> methods=["GET","POST"] or default
```

---

## Permission Patterns

ALWAYS check permissions inside every whitelisted method. The `@frappe.whitelist()` decorator only verifies the user is logged in — it does NOT check DocType or document-level permissions.

```python
# DocType-level permission (throw=True raises PermissionError automatically)
@frappe.whitelist()
def get_orders():
    frappe.has_permission("Sales Order", "read", throw=True)
    return frappe.get_all("Sales Order", limit=20)

# Document-level permission
@frappe.whitelist()
def get_order(name):
    frappe.has_permission("Sales Order", "read", name, throw=True)
    return frappe.get_doc("Sales Order", name).as_dict()

# Role-based restriction
@frappe.whitelist()
def admin_action():
    frappe.only_for("System Manager")  # throws if user lacks role
    return {"secret": "data"}
```

Full patterns: [permission-patterns.md](references/permission-patterns.md)

---

## Parameter Handling

Parameters arrive as **strings** from HTTP requests. ALWAYS convert explicitly.

```python
@frappe.whitelist()
def calculate(amount, quantity, items=None):
    amount = float(amount)          # ALWAYS cast numeric params
    quantity = int(quantity)
    if isinstance(items, str):      # ALWAYS parse JSON strings
        items = frappe.parse_json(items)
    return amount * quantity
```

Access all request parameters via `frappe.form_dict`:
```python
@frappe.whitelist()
def dynamic_handler():
    all_params = frappe.form_dict
    customer = frappe.form_dict.get("customer")
```

### Type Annotations [v15+]

Frappe v15+ validates type annotations automatically at request time via Pydantic:

```python
@frappe.whitelist()
def get_orders(customer: str, limit: int = 10, active: bool = True) -> dict:
    # Frappe auto-validates: limit MUST be convertible to int
    return {"orders": frappe.get_all("Sales Order", limit=limit)}
```

### force_types and require_type_annotated_api_methods [v15+]

- `@frappe.whitelist(force_types=True)` — EVERY parameter MUST have a type annotation
- App-level enforcement via `hooks.py`: `require_type_annotated_api_methods = 1`
- Missing annotations raise `FrappeTypeError`

Full details: [parameter-handling.md](references/parameter-handling.md)

---

## Client Calls

### frappe.call(): Standalone APIs

```javascript
// Promise-based (ALWAYS prefer this)
frappe.call({
    method: 'myapp.api.get_summary',
    args: { customer: 'CUST-001' },
    freeze: true,
    freeze_message: __('Loading...')
}).then(r => {
    console.log(r.message);  // return value is in r.message
}).catch(err => {
    frappe.show_alert({ message: __('Error'), indicator: 'red' });
});
```

### frm.call(): Controller Methods

```javascript
frm.call('calculate_taxes', { include_shipping: true })
    .then(r => frm.set_value('tax_amount', r.message.tax_amount));
```

### REST API (External Clients)

```bash
# Token auth (ALWAYS use for external integrations)
curl -H "Authorization: token api_key:api_secret" \
     -H "Content-Type: application/json" \
     -X POST https://site.com/api/method/myapp.api.create_order \
     -d '{"customer": "CUST-001"}'
```

Full patterns: [client-calls.md](references/client-calls.md)

---

## Error Handling

```python
@frappe.whitelist()
def process_order(order_id):
    if not order_id:
        frappe.throw(_("Order ID required"), frappe.ValidationError)

    if not frappe.has_permission("Sales Order", "write", order_id):
        frappe.throw(_("Not permitted"), frappe.PermissionError)

    try:
        result = heavy_operation(order_id)
        return {"success": True, "data": result}
    except Exception:
        frappe.log_error(frappe.get_traceback(), "process_order")
        frappe.throw(_("Operation failed. Contact support."))
```

| Exception | HTTP Code | When to Use |
|-----------|-----------|-------------|
| `frappe.ValidationError` | 417 | Input validation failure |
| `frappe.PermissionError` | 403 | Access denied |
| `frappe.DoesNotExistError` | 404 | Document not found |
| `frappe.DuplicateEntryError` | 409 | Duplicate record |
| `frappe.AuthenticationError` | 401 | Not logged in |

Full patterns: [error-handling.md](references/error-handling.md)

---

## Response Patterns

```python
# Return value auto-wraps as {"message": <return_value>}
@frappe.whitelist()
def get_data():
    return {"key": "value"}   # Client receives: {"message": {"key": "value"}}

# Custom HTTP status
@frappe.whitelist()
def create_item(data):
    doc = frappe.get_doc(data).insert()
    frappe.local.response["http_status_code"] = 201
    return {"name": doc.name}

# File download
@frappe.whitelist()
def download_report(name):
    content = generate_pdf(name)
    frappe.response.filename = f"{name}.pdf"
    frappe.response.filecontent = content
    frappe.response.type = "download"
```

Full patterns: [response-patterns.md](references/response-patterns.md)

---

## Rate Limiting [v14+]

```python
from frappe.rate_limiter import rate_limit

@frappe.whitelist(allow_guest=True)
@rate_limit(limit=5, seconds=60)  # 5 requests per 60 seconds per IP
def public_endpoint():
    return {"status": "ok"}
```

`rate_limit` signature:
```python
rate_limit(key=None, limit=5, seconds=86400, methods="ALL", ip_based=True)
```

ALWAYS apply `@rate_limit` on `allow_guest=True` endpoints to prevent abuse.

---

## Version Differences

| Feature | v14 | v15+ | v16+ |
|---------|-----|------|------|
| `@frappe.whitelist()` | Yes | Yes | Yes |
| `allow_guest`, `xss_safe`, `methods` | Yes | Yes | Yes |
| Type annotation validation | No | Yes (auto via Pydantic) | Yes |
| `force_types` parameter | No | Yes | Yes |
| `require_type_annotated_api_methods` hook | No | Yes | Yes |
| `@rate_limit()` decorator | Yes | Yes | Yes |
| `FrappeTypeError` for missing annotations | No | Yes | Yes |

---

## Critical Rules

1. **NEVER skip permission checks** — `@frappe.whitelist()` only confirms login, not authorization
2. **NEVER use user input in raw SQL** — ALWAYS use parameterized queries or ORM
3. **NEVER leak stack traces** — log with `frappe.log_error()`, show generic messages
4. **ALWAYS validate input types** — parameters arrive as strings from HTTP
5. **ALWAYS apply `@rate_limit` on guest endpoints** — prevents abuse
6. **NEVER use `ignore_permissions=True` without a preceding role check**
7. **ALWAYS use `JSON.stringify()` for complex JS args** — arrays and objects

Full anti-patterns: [anti-patterns.md](references/anti-patterns.md)

---

## Security Checklist

For EVERY whitelisted method, verify:

- [ ] Permission check present (`frappe.has_permission()` or `frappe.only_for()`)
- [ ] Input validated (types, ranges, formats)
- [ ] SQL queries parameterized (NEVER string interpolation)
- [ ] Error messages contain no internal details
- [ ] `allow_guest=True` only with explicit reason + rate limiting
- [ ] `ignore_permissions=True` only with preceding role check
- [ ] HTTP methods restricted where possible
- [ ] Response contains only necessary fields (no sensitive data leaks)

---

## Reference Files

| File | Content |
|------|---------|
| [decorator-options.md](references/decorator-options.md) | All `@frappe.whitelist()` parameters and `force_types` |
| [parameter-handling.md](references/parameter-handling.md) | Request parameters, type coercion, `frappe.form_dict` |
| [response-patterns.md](references/response-patterns.md) | Return types, file downloads, streaming, HTTP status |
| [client-calls.md](references/client-calls.md) | `frappe.call()`, `frm.call()`, REST API, fetch patterns |
| [permission-patterns.md](references/permission-patterns.md) | Permission checks, role guards, custom logic |
| [error-handling.md](references/error-handling.md) | Exception types, `frappe.throw()`, logging |
| [examples.md](references/examples.md) | Complete working API examples |
| [anti-patterns.md](references/anti-patterns.md) | Security mistakes and performance pitfalls |
| [hooks.md](references/hooks.md) | Declaring whitelisted methods in `hooks.py` |
| [syntax.md](references/syntax.md) | Core decorator syntax and registration mechanics |
---
name: frappe-testing-cicd
description: >
  Use when setting up CI/CD pipelines for Frappe apps, configuring GitHub Actions test workflows, or adding linting and security scanning.
  Prevents broken CI from incorrect test matrix configuration, missing MariaDB/Redis services, and uncaught code quality issues.
  Covers GitHub Actions workflows, test matrix (Python/Node versions), semgrep rules, pre-commit hooks, linting (ruff, eslint), CI test environment setup.
  Keywords: CI/CD, GitHub Actions, test matrix, semgrep, pre-commit, linting, ruff, eslint, continuous integration, automated tests, GitHub Actions, CI pipeline, pre-commit, code quality check..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# CI/CD Pipelines

## Quick Reference

| Task | Tool / File |
|------|------------|
| Install pre-commit hooks | `pre-commit install --hook-type pre-commit --hook-type commit-msg` |
| Run all pre-commit checks | `pre-commit run --all-files` |
| Run linter | `ruff check .` |
| Run formatter | `ruff format .` |
| Run ESLint | `npx eslint "**/*.js" --quiet` |
| Run tests in CI | `bench --site test_site run-tests --app myapp` |
| Run parallel tests | `bench --site test_site run-parallel-tests --total-builds 2 --build-number 0` |
| Generate coverage | `coverage run -m pytest && coverage xml` |
| Generate JUnit XML | `bench --site test_site run-tests --junit-xml-output report.xml` |

## Decision Tree: CI/CD Setup

```
Setting up CI for a Frappe app?
├─ Start with GitHub Actions workflow
│   ├─ ALWAYS include MariaDB + Redis services
│   ├─ ALWAYS use test matrix for Python versions
│   └─ Optionally add PostgreSQL for dual-DB support
├─ Add pre-commit hooks
│   ├─ ALWAYS include ruff (Python linting + formatting)
│   ├─ ALWAYS include eslint + prettier (JS/Vue)
│   └─ Add commitlint for conventional commits
├─ Add security scanning?
│   └─ YES → Add semgrep with Frappe-specific rules
└─ Need release automation?
    └─ YES → Add tag-based release workflow
```

## GitHub Actions Workflow for Frappe Apps

### Standard Server Test Workflow

```yaml
name: Server Tests
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

concurrency:
  group: server-tests-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 60

    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
        db: ["mariadb"]

    services:
      mariadb:
        image: mariadb:11.4
        ports:
          - 3306:3306
        env:
          MARIADB_ROOT_PASSWORD: db_root
        options: >-
          --health-cmd="healthcheck.sh --connect --innodb_initialized"
          --health-interval=5s
          --health-timeout=5s
          --health-retries=10

      redis-cache:
        image: redis:alpine
        ports:
          - 13000:6379
      redis-queue:
        image: redis:alpine
        ports:
          - 11000:6379

    steps:
      - name: Checkout frappe
        uses: actions/checkout@v4
        with:
          repository: frappe/frappe
          path: frappe-bench/apps/frappe

      - name: Checkout app
        uses: actions/checkout@v4
        with:
          path: frappe-bench/apps/myapp

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install bench
        run: pip install frappe-bench

      - name: Init bench
        working-directory: frappe-bench
        run: |
          bench init --skip-assets --skip-redis-config-generation .
          bench set-config -g db_root_password db_root
          bench set-config -g redis_cache redis://localhost:13000
          bench set-config -g redis_queue redis://localhost:11000

      - name: Install app
        working-directory: frappe-bench
        run: |
          bench get-app --skip-assets myapp ./apps/myapp
          bench setup requirements --dev
          bench new-site test_site \
            --db-root-password db_root \
            --admin-password admin \
            --no-mariadb-socket
          bench --site test_site install-app myapp
          bench build --apps myapp

      - name: Run tests
        working-directory: frappe-bench
        run: bench --site test_site run-tests --app myapp --failfast

      - name: Upload coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.python-version }}-${{ matrix.db }}
          path: frappe-bench/sites/coverage.xml
```

### PostgreSQL Support (Additional Matrix Entry)

```yaml
    strategy:
      matrix:
        include:
          - python-version: "3.12"
            db: "postgres"

    services:
      postgres:
        image: postgres:16
        ports:
          - 5432:5432
        env:
          POSTGRES_PASSWORD: db_root
        options: >-
          --health-cmd pg_isready
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
```

When using PostgreSQL, change the `bench new-site` command:
```bash
bench new-site test_site \
  --db-type postgres \
  --db-root-password db_root \
  --admin-password admin
```

## Pre-Commit Configuration

### Minimal .pre-commit-config.yaml for Frappe Apps

```yaml
exclude: "node_modules|.git"
default_stages: [pre-commit]
fail_fast: false

repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
        files: "myapp.*"
        exclude: ".*json$|.*txt$|.*csv$|.*md$|.*svg$"
      - id: check-merge-conflict
      - id: check-ast
      - id: check-json
      - id: check-toml
      - id: check-yaml
      - id: debug-statements

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--select=I, --fix]
        name: ruff (import sorter)
      - id: ruff
        name: ruff (linter)
      - id: ruff-format
        name: ruff (formatter)

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v2.7.1
    hooks:
      - id: prettier
        types_or: [javascript, vue, scss]
        exclude: ".*dist.*|node_modules"

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.44.0
    hooks:
      - id: eslint
        types: [javascript]
        args: [--quiet]
        exclude: ".*dist.*|node_modules"

  - repo: https://github.com/alessandrojcm/commitlint-pre-commit-hook
    rev: v9.16.0
    hooks:
      - id: commitlint
        stages: [commit-msg]
        additional_dependencies:
          - conventional-changelog-conventionalcommits
```

ALWAYS run `pre-commit install --hook-type pre-commit --hook-type commit-msg` after cloning.

## Ruff Configuration (pyproject.toml)

```toml
[tool.ruff]
line-length = 110
target-version = "py311"

[tool.ruff.lint]
select = [
    "F",   # Pyflakes
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "I",   # isort
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "RUF", # Ruff-specific rules
]
ignore = [
    "E501",  # line too long (handled by formatter)
    "F401",  # unused import (common in __init__.py)
    "F403",  # wildcard import (Frappe convention)
    "F405",  # undefined from wildcard (Frappe convention)
    "E402",  # module-level import order (Frappe convention)
]

[tool.ruff.format]
quote-style = "double"
indent-style = "tab"
docstring-code-format = true

[tool.ruff.lint.per-file-ignores]
# Ignore in auto-generated boilerplate
"**/doctype/**/boilerplate/**" = ["ALL"]
```

**Rules**:
- ALWAYS use `indent-style = "tab"` for Frappe projects — this is the framework convention
- ALWAYS ignore F401/F403/F405 — Frappe uses wildcard imports by convention
- NEVER set `line-length` below 110 — Frappe standard is 110 characters

## ESLint Configuration

```json
{
    "env": {
        "browser": true,
        "node": true,
        "es2021": true
    },
    "extends": "eslint:recommended",
    "globals": {
        "frappe": "readonly",
        "cur_frm": "readonly",
        "__": "readonly",
        "cur_dialog": "readonly",
        "cur_page": "readonly",
        "cur_list": "readonly"
    },
    "rules": {
        "no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }],
        "no-console": "warn"
    }
}
```

ALWAYS declare Frappe globals (`frappe`, `cur_frm`, `__`, etc.) — otherwise ESLint reports false positives.

## Semgrep Security Rules

```yaml
# .semgrep/frappe-security.yml
rules:
  - id: frappe-sql-injection
    pattern: frappe.db.sql($X.format(...))
    message: "NEVER use .format() in SQL — use parameterized queries"
    severity: ERROR
    languages: [python]

  - id: frappe-raw-sql-concat
    pattern: frappe.db.sql($X + ...)
    message: "NEVER concatenate strings in SQL — use parameterized queries"
    severity: ERROR
    languages: [python]

  - id: frappe-eval-usage
    pattern: eval(...)
    message: "NEVER use eval() — use frappe.safe_eval() instead"
    severity: ERROR
    languages: [python]
```

Add to CI:
```yaml
      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: .semgrep/
```

## Test Coverage

### Setup coverage.py

```ini
# .coveragerc
[run]
source = myapp
omit =
    */test_*.py
    */tests/*
    */setup.py

[report]
exclude_lines =
    pragma: no cover
    if frappe.flags.in_test:
    if TYPE_CHECKING:
```

### CI Coverage Step

```yaml
      - name: Run tests with coverage
        working-directory: frappe-bench
        run: |
          cd apps/myapp
          coverage run -m pytest
          coverage xml -o ../../sites/coverage.xml

      - name: Upload to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: frappe-bench/sites/coverage.xml
          token: ${{ secrets.CODECOV_TOKEN }}
```

## Release Workflow

```yaml
name: Release
on:
  push:
    tags:
      - "v*"

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Generate changelog
        id: changelog
        uses: mikepenz/release-changelog-builder-action@v4
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v2
        with:
          body: ${{ steps.changelog.outputs.changelog }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Branch Protection Rules

ALWAYS configure these branch protection rules for `main` and `develop`:

1. **Require status checks**: Server Tests must pass before merging
2. **Require pull request reviews**: At least 1 approval
3. **Require up-to-date branches**: Force rebase before merge
4. **Require linear history**: Enforce squash or rebase merging

Configure via GitHub CLI:
```bash
gh api repos/{owner}/{repo}/branches/main/protection -X PUT \
  -f "required_status_checks[strict]=true" \
  -f "required_status_checks[contexts][]=Server Tests" \
  -f "required_pull_request_reviews[required_approving_review_count]=1"
```

## Common CI Failures and Fixes

| Failure | Cause | Fix |
|---------|-------|-----|
| `MariaDB not ready` | Health check too short | Increase `--health-retries` to 10+ |
| `Redis connection refused` | Wrong port mapping | Verify port mapping matches `bench set-config` |
| `ModuleNotFoundError` | Missing app install | Ensure `bench get-app` and `bench install-app` both run |
| `Site not found` | Missing `bench new-site` | ALWAYS create site before running tests |
| `Permission denied on bench` | pip install location | Use `pip install frappe-bench` without sudo |
| `Assets build failed` | Node version mismatch | Use Node 18 or 20 (NEVER Node 16) |
| `frappe.exceptions.DoesNotExistError` | Missing test fixtures | Ensure `test_records.json` exists for dependent DocTypes |
| `Timeout in parallel tests` | Too many parallel builds | Reduce `--total-builds` or increase `timeout-minutes` |

## See Also

- [references/examples.md](references/examples.md) — Complete workflow examples
- [references/anti-patterns.md](references/anti-patterns.md) — CI/CD mistakes to avoid
- [references/github-actions.md](references/github-actions.md) — Full GitHub Actions reference
- [references/linting.md](references/linting.md) — Linting and formatting deep dive
- [frappe-testing-unit](../frappe-testing-unit/) — Unit and integration testing
---
name: frappe-testing-unit
description: >
  Use when writing unit tests, integration tests, creating test fixtures, or running tests with bench run-tests.
  Prevents flaky tests from missing fixtures, incorrect test isolation, and wrong test base classes.
  Covers frappe.tests.utils, IntegrationTestCase, UnitTestCase, test fixtures, bench run-tests flags, test naming conventions.
  Keywords: unit test, integration test, IntegrationTestCase, fixtures, bench run-tests, frappe.tests, test_*.py, how to write test, test fixtures, run tests, test fails, bench run-tests example..
license: MIT
compatibility: "Claude Code, Claude.ai Projects, Claude API. Frappe v14-v16."
metadata:
  author: OpenAEC-Foundation
  version: "2.0"
---

# Unit & Integration Testing

## Quick Reference

| Task | Command / Class |
|------|----------------|
| Run all tests | `bench --site test_site run-tests` |
| Run tests for app | `bench --site test_site run-tests --app myapp` |
| Run tests for doctype | `bench --site test_site run-tests --doctype "Sales Order"` |
| Run single test method | `bench --site test_site run-tests --doctype "Sales Order" --test test_submit` |
| Run tests for module | `bench --site test_site run-tests --module "myapp.mymodule.doctype.mydt.test_mydt"` |
| Run with profiler | `bench --site test_site run-tests --doctype "Task" --profile` |
| Run with failfast | `bench --site test_site run-tests --failfast` |
| Generate JUnit XML | `bench --site test_site run-tests --junit-xml-output /path/report.xml` |
| Skip fixture loading | `bench --site test_site run-tests --skip-test-records --skip-before-tests` |
| Base class (v14) | `from frappe.tests.utils import FrappeTestCase` |
| Unit test class (v15+) | `from frappe.tests.classes import UnitTestCase` |
| Integration test class (v15+) | `from frappe.tests.classes import IntegrationTestCase` |

## Decision Tree: Which Test Base Class?

```
Need to test a function or method in isolation?
├─ YES → Does it require database access?
│   ├─ NO → UnitTestCase (v15+) or FrappeTestCase (v14)
│   └─ YES → IntegrationTestCase (v15+) or FrappeTestCase (v14)
└─ NO → Need to test document lifecycle (create/submit/cancel)?
    ├─ YES → IntegrationTestCase (v15+) or FrappeTestCase (v14)
    └─ NO → Need to test permissions or user context?
        ├─ YES → IntegrationTestCase (v15+) or FrappeTestCase (v14)
        └─ NO → UnitTestCase (v15+) or FrappeTestCase (v14)
```

**Version note**: In v14, `FrappeTestCase` is the ONLY base class. In v15+, it still works (deprecated wrapper) but ALWAYS prefer `UnitTestCase` or `IntegrationTestCase` for new code.

## Test Base Classes

### FrappeTestCase (v14: still works in v15+ as compatibility wrapper)

```python
from frappe.tests.utils import FrappeTestCase

class TestMyDoctype(FrappeTestCase):
    def test_something(self):
        doc = frappe.get_doc({"doctype": "My Doctype", "field": "value"})
        doc.insert()
        self.assertEqual(doc.field, "value")
```

**Behavior**: Resets `frappe.local.flags` after each test. Database transactions start before each test and rollback afterward. ALWAYS call `super().setUpClass()` if you override `setUpClass`.

### UnitTestCase (v15+): No Database Access

```python
from frappe.tests.classes import UnitTestCase

class TestMyUtils(UnitTestCase):
    def test_calculation(self):
        result = my_calculation(10, 20)
        self.assertEqual(result, 30)

    def test_html_output(self):
        html = generate_html()
        self.assertEqual(self.normalize_html(html), self.normalize_html(expected))
```

**Behavior**: Sets `frappe.set_user("Administrator")` in `setUpClass`. Auto-detects doctype from module path. Provides `normalize_html()`, `normalize_sql()`, `assertDocumentEqual()`, `assertQueryEqual()`, `assertSequenceSubset()`.

### IntegrationTestCase (v15+): Full Database Access

```python
from frappe.tests.classes import IntegrationTestCase

class TestSalesOrder(IntegrationTestCase):
    def test_submit_order(self):
        so = frappe.get_doc({
            "doctype": "Sales Order",
            "customer": "_Test Customer",
            "items": [{"item_code": "_Test Item", "qty": 1, "rate": 100}]
        }).insert()
        so.submit()
        self.assertEqual(so.docstatus, 1)
```

**Behavior**: Extends `UnitTestCase`. Calls `frappe.init()` and sets up site connection. Loads test record dependencies via `make_test_records()`. Provides `primary_connection()` and `secondary_connection()` context managers. `maxDiff = 10_000`.

## Test File Structure

ALWAYS place test files in the doctype directory following this naming convention:

```
myapp/
└── mymodule/
    └── doctype/
        └── my_doctype/
            ├── my_doctype.py          # DocType controller
            ├── my_doctype.json        # DocType definition
            ├── test_my_doctype.py     # Test file (MUST start with test_)
            └── test_records.json      # Optional: test fixtures
```

**Rules**:
- ALWAYS prefix test files with `test_` — the test runner ignores files without this prefix
- ALWAYS use `test_{doctype_in_snake_case}.py` for doctype tests
- NEVER place test files outside the doctype directory for doctype-specific tests
- Non-doctype tests can live in any module, but MUST follow the `test_*.py` naming

## Test Fixtures

### Method 1: test_records.json (Static Fixtures)

Create a `test_records.json` file in the doctype directory:

```json
[
    {
        "doctype": "My Doctype",
        "field1": "_Test Value 1",
        "field2": 100
    },
    {
        "doctype": "My Doctype",
        "field1": "_Test Value 2",
        "field2": 200
    }
]
```

**Rules**:
- ALWAYS prefix test data values with `_Test` to distinguish from production data
- The test runner auto-loads these before running tests for the doctype
- Link field dependencies are resolved automatically — the runner builds records for linked DocTypes first

### Method 2: _test_records List (In-Module Fixtures)

```python
_test_records = [
    {"doctype": "My Doctype", "field1": "_Test Value 1"},
    {"doctype": "My Doctype", "field1": "_Test Value 2"},
]
```

### Method 3: Programmatic Fixtures (Recommended for Complex Data)

```python
def create_test_data():
    if frappe.flags.test_data_created:
        return
    frappe.set_user("Administrator")
    frappe.get_doc({
        "doctype": "My Doctype",
        "field1": "_Test Value",
    }).insert()
    frappe.flags.test_data_created = True

class TestMyDoctype(IntegrationTestCase):
    def setUp(self):
        create_test_data()
```

ALWAYS use `frappe.flags` to prevent duplicate fixture creation across test methods.

## Testing Patterns

### Testing Document Lifecycle

```python
class TestInvoice(IntegrationTestCase):
    def test_full_lifecycle(self):
        # Create
        doc = frappe.get_doc({"doctype": "Sales Invoice", ...}).insert()
        self.assertEqual(doc.docstatus, 0)  # Draft

        # Submit
        doc.submit()
        self.assertEqual(doc.docstatus, 1)  # Submitted

        # Cancel
        doc.cancel()
        self.assertEqual(doc.docstatus, 2)  # Cancelled
```

### Testing Permissions

```python
class TestPermissions(IntegrationTestCase):
    def test_user_cannot_read_private(self):
        frappe.set_user("test1@example.com")
        doc = frappe.get_doc("Event", {"subject": "_Test Private Event"})
        self.assertFalse(frappe.has_permission("Event", doc=doc))

    def tearDown(self):
        # ALWAYS reset user in tearDown
        frappe.set_user("Administrator")
```

### Testing with User Context (v15+ Context Manager)

```python
class TestAccess(IntegrationTestCase):
    def test_restricted_access(self):
        with self.set_user("test1@example.com"):
            self.assertRaises(
                frappe.PermissionError,
                frappe.get_doc, "Salary Slip", "SAL-001"
            )
        # User automatically restored after context manager exits
```

### Testing Whitelisted Methods

```python
class TestAPI(IntegrationTestCase):
    def test_whitelisted_method(self):
        frappe.set_user("test1@example.com")
        result = frappe.call("myapp.api.get_dashboard_data", filters={})
        self.assertIsInstance(result, dict)
        self.assertIn("total", result)
```

### Mocking External Services

```python
from unittest.mock import patch, MagicMock

class TestIntegration(IntegrationTestCase):
    @patch("myapp.integrations.stripe.requests.post")
    def test_payment_gateway(self, mock_post):
        mock_post.return_value = MagicMock(
            status_code=200,
            json=lambda: {"status": "success", "id": "ch_123"}
        )
        result = process_payment(amount=1000, currency="USD")
        self.assertEqual(result["status"], "success")
        mock_post.assert_called_once()
```

### Testing with Settings Changes

```python
class TestFeature(IntegrationTestCase):
    def test_with_modified_settings(self):
        with self.change_settings("Selling Settings", {"so_required": 1}):
            # Settings temporarily changed
            self.assertRaises(frappe.ValidationError, create_delivery_note)
        # Settings automatically reverted
```

### Testing with Hook Overrides

```python
class TestHooks(IntegrationTestCase):
    def test_custom_hook(self):
        with self.patch_hooks({"on_submit": ["myapp.hooks.custom_on_submit"]}):
            doc = create_and_submit_doc()
            # Verify hook was executed
```

## Context Managers Reference

| Context Manager | Available On | Purpose |
|----------------|-------------|---------|
| `set_user(user)` | UnitTestCase, IntegrationTestCase | Temporarily switch user context |
| `change_settings(dt, **kw)` | UnitTestCase, IntegrationTestCase | Temporarily modify settings |
| `patch_hooks(overrides)` | UnitTestCase, IntegrationTestCase | Temporarily override hooks |
| `freeze_time(time)` | UnitTestCase, IntegrationTestCase | Freeze time for deterministic tests |
| `debug_on(*exceptions)` | UnitTestCase, IntegrationTestCase | Drop into debugger on exception |
| `timeout(seconds)` | Decorator | Fail test if it exceeds time limit |
| `enable_safe_exec()` | IntegrationTestCase | Enable server scripts temporarily |
| `switch_site(site)` | IntegrationTestCase | Switch to a different site |
| `assertQueryCount(n)` | IntegrationTestCase | Assert exact SQL query count |
| `assertRedisCallCounts(**kw)` | IntegrationTestCase | Assert Redis command counts |
| `assertRowsRead(n)` | IntegrationTestCase | Assert row-level DB access limits |

## Database State Management

- **IntegrationTestCase**: ALWAYS rolls back database after each test — no cleanup needed
- **UnitTestCase**: No database connection — NEVER use `frappe.db` calls
- Each test gets a clean state: transactions start in `setUp` and rollback in `tearDown`
- NEVER call `frappe.db.commit()` in tests — this breaks test isolation
- Use `frappe.flags.in_test` to check if code is running under the test runner

## Detecting Test Mode

```python
if frappe.flags.in_test:
    # Skip external API calls, emails, etc.
    return mock_response()
```

NEVER use `frappe.flags.in_test` to skip validation logic — tests MUST exercise the same code paths as production.

## Common Pitfalls

1. **NEVER forget `super().setUpClass()`** — omitting this breaks fixture loading and user setup
2. **NEVER call `frappe.db.commit()`** in tests — this persists data across tests and breaks isolation
3. **ALWAYS reset user in `tearDown`** if you called `frappe.set_user()` directly (v14 pattern)
4. **ALWAYS prefix test data with `_Test`** — makes cleanup and identification easy
5. **NEVER rely on test execution order** — each test MUST be independent
6. **ALWAYS use `frappe.flags`** to guard fixture creation — prevents duplicate inserts

## See Also

- [references/examples.md](references/examples.md) — Complete test examples
- [references/anti-patterns.md](references/anti-patterns.md) — Common mistakes and fixes
- [references/fixtures.md](references/fixtures.md) — Fixture patterns in depth
- [references/api-reference.md](references/api-reference.md) — Full API reference for test utilities
- [frappe-testing-cicd](../frappe-testing-cicd/) — CI/CD pipeline setup
