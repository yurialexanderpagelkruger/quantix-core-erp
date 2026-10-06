# Quantix Core

**Quantix Core** is a comprehensive operational management, traceability, and access control platform engineered for small and medium-sized enterprises (SMBs) and retail businesses. Developed from rigorous business process analysis and functional specification, *Quantix Core* replaces decentralized, error-prone spreadsheets with a structured, secure, and end-to-end traceable enterprise solution.

Featuring a workflow tailored for daily operations, the platform centralizes real-time inventory tracking, order management, shift scheduling, billing, and role-based access control (RBAC)—eliminating data redundancy and delivering dependable commercial analytics.

---

## 📸 Screenshots

<div align="center">
  <table>
    <tr>
      <td align="center" valign="bottom" style="padding: 10px;">
        <p><b>Desktop Version</b></p>
        <img src="screenshot.png" alt="Desktop Version" height="420" style="border: 1px solid #30363d; border-radius: 6px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); display: block;" />
      </td>
      <td align="center" valign="bottom" style="padding: 10px;">
        <p><b>Mobile Version</b></p>
        <img src="screenshot2.png" alt="Mobile Version" height="420" style="border: 1px solid #30363d; border-radius: 6px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); display: block;" />
      </td>
    </tr>
  </table>
</div>

---

## ✨ Key Features

* **Normalized Data Architecture:** Relational database designed in 3NF with strict referential integrity, indexed foreign keys, and audit triggers for complete historical traceability.

* **Multi-Language Support (i18n):** Fully localized interface supporting 3 languages: English, Spanish, and Portuguese, enabling friction-free operations across multicultural workforces.

* **Adaptive Theming (Dark & Light Mode):** Native support for both Dark and Light themes that dynamically toggles or adapts to system settings, ensuring high readability across different warehouse and office environments.

* **Formal Functional Documentation:** Includes comprehensive Software Requirements Specification (SRS) accompanied by detailed use cases, business process model flows (BPMN), and traceability matrices.

* **Role-Based Access Control (RBAC):** Multi-tier authentication and authorization engine (Admin, Operator, Read-Only) enforcing secure password hashing and granular module-level permission enforcement.

* **End-to-End Operational Audit Trail:** Immutable internal activity log that captures user IDs, ISO timestamps, and before/after payloads for every sensitive inventory or financial update.

* **Dynamic Inventory & Reorder Point Control:** Real-time stock level monitoring, automatic critical stock computation, and proactive purchase reorder notifications.

* **Unified Customer & Order Management:** Centralized registry covering the complete lifecycle of customer orders (Pending, Processing, Dispatched, Cancelled) mapped directly to line-of-credit statements.

* **Executive Reporting Engine:** Automated PDF and Excel export generation for sales velocity, cash register balances, inventory turnover rates, and advanced multi-filter queries.

* **Ergonomic Operator Experience:** Designed for fast data entry via keyboard shortcuts, real-time input validations, and client-side duplicate submission prevention.

---

## ⚙️ What It Does (System Modules)

Upon authenticating with assigned credentials, the platform provisions the following functional modules based on user authorization levels:

1. **Authentication & Identity Security:** Validates credentials against the directory, mounts the corresponding RBAC permission model, and records session initialization inside the audit log.

2. **Internationalization & Dynamic Theming:** Centralized client configuration manager handling translations across 3 languages (English, Spanish, Portuguese) and dynamic UI token switching between Dark and Light mode.

3. **Inventory & Warehouse Logistics:** Manages stock movements (inbound, outbound, returns, stock counts) with mandatory change justifications, updating valuation metrics and sales pricing in real time.

4. **Point of Sale (POS) & Billing:** Processes counter sales, generates structured fiscal receipts, handles multiple payment instruments, and posts adjustments to ledger balances instantly.

5. **Shift Scheduling & Dispatch:** Coordinates work orders and staff scheduling, preventing double-booking and exposing resource availability in real time.

6. **Reporting & Accounting Telemetry:** Generates balance sheets, operating margin metrics, and structured financial exports formatted for audit inspection in a single click.

---

## 🛠️ Built With

* **Core Language:** C# 12 / .NET 8 (or Python 3.12).
* **UI & Styling:** Semantic responsive layout with custom design tokens for native Dark/Light theme modes.
* **Localization:** Resource-driven i18n localization dictionary layer (English, Spanish, Portuguese).
* **Architecture:** Clean Architecture / Layered separation (Domain, Application, Infrastructure, Presentation) following MVC-MVVM patterns.
* **Database Engine:** PostgreSQL / MariaDB with strict ACID compliance and isolated transactions.
* **Security & Access:** Argon2id / BCrypt credential hashing with token/role-governed session state.
* **Systems Analysis & Design:** UML Modeling (Use Case, Sequence), Entity-Relationship Models (ERD), and SRS standard IEEE 830 compliance.
* **Development Environment:** Visual Studio Enterprise 2026 / Visual Studio Code.

---

## 🚀 Installation and Usage

1. Clone the project repository:
   ```bash
   git clone [https://github.com/yurialexanderpagelkruger/quantix-core-erp.git](https://github.com/yurialexanderpagelkruger/quantix-core-erp.git)
   cd quantix-core-erp

## 👨‍💻 Author

Developed by **Yuri Alexander Pagel Krüger**
