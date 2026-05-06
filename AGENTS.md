# 🤖 AGENTS.md: Operational Protocol for fadl_pos

This document serves as the **Master Instruction Set** for any AI Agent or Developer working on the `fadl_pos` project. 

---

## 🎯 1. Project Objective & Vision
`fadl_pos` is a high-performance, decoupled PWA POS backend for **ERPNext v16**. 
*   **Goal:** Create an API-first architecture that provides 100% functional parity with native ERPNext POS while integrating premium features from POS Next.
*   **Philosophy:** **"Native-First Hybrid."** We never reinvent stable native logic; we orchestrate it.

---

## 📦 2. The Source Warehouse (`_source_warehouse/`)
The directory `_source_warehouse/` is the **Single Source of Truth** for existing logic.
*   It contains raw source files from both **Native ERPNext** and **POS Next**.
*   **Constraint:** Agents MUST analyze these files before implementing any feature.
*   **Extraction:** Identify "Cool Features" (e.g., weighted barcodes, loyalty wallets) and refactor them into our service layer without breaking native compatibility.

---

## 🧪 3. Mandatory Testing Policy
No feature is considered "Done" without tests.
*   **Requirement:** All services must be covered by unit tests.
*   **Sentinel Checks:** You must write tests that compare the output of our API with native ERPNext Desk actions to ensure zero calculation drift.

---

## 🏗️ 4. Architecture & Hierarchy (DO NOT MODIFY)
The current directory structure is **ideal and must be preserved**:
*   `api/`: Whitelisted Frappe endpoints.
*   `services/`: OOP logic (inheriting from `BaseService`).
*   `serializers/`: Data contracts using `TypedDict`.
*   `tests/`: Test cases.
*   `_source_warehouse/`: Reference files.
**Strict Rule:** Do not change the folder hierarchy or move logic across these layers.

---

## 📜 5. Operational Skills & Patterns
Agents must strictly follow the established coding patterns:
*   **OOP First:** All logic lives in services, never in the API controller or the DocType.
*   **Native Compatibility:** Always check if a feature can be solved by importing a native ERPNext function before writing custom SQL.
*   **Type Safety:** Use serializers for all input/output data.
*   **Skill Integration:** Use the specialized skills found in `.cursor/skills/` (e.g., `frappe-core-*`, `frappe-impl-*`).
*   **Fadl-Specific Rules:** 
    *   Changes must stay within `apps/fadl_pos`.
    *   No `Customize Form`; use code-based customizations (Hooks, Fixtures, Migrations).
    *   Strict security: Never log secrets, PINs, or raw token material.

---

## ⚠️ 6. Logic Integrity & Desync Prevention
**The Golden Rule:** Our API must NOT produce results that differ from the ERPNext Desk UI.
*   **No Logic Desync:** Taxes, totals, and stock validations must exactly match the behavior of `POS Invoice` and `POS Opening Entry` in the standard Desk interface.
*   **Server-Side Truth:** The server (Python) is the final validator. Do not trust frontend calculations; always re-verify in the service layer.

---

> [!IMPORTANT]
> Always cross-reference `_source_warehouse/README.md` for the current implementation status and mapping of files to functionalities.
