# ServiceNow CMDB (Configuration Management Database)

## Overview

The CMDB stores configuration items (CIs) — the servers, applications,
services, and network gear that make up the IT environment — together with
their relationships. A healthy CMDB underpins impact analysis for incidents
and changes.

## CI Class Hierarchy

All CIs live in tables extending the base `cmdb_ci` table. Common classes:

| Class | Table |
|-------|-------|
| Server | `cmdb_ci_server` |
| Linux Server | `cmdb_ci_linux_server` |
| Windows Server | `cmdb_ci_win_server` |
| Application | `cmdb_ci_appl` |
| Business Service | `cmdb_ci_service` |
| Database | `cmdb_ci_database` |
| Network Gear | `cmdb_ci_netgear` |

The **CI Class Manager** is the UI for browsing and extending the class
hierarchy, managing identification rules, and setting reconciliation rules.

## Relationships

CI relationships are stored in `cmdb_rel_ci` with a type from
`cmdb_rel_type` (for example, *Runs on::Runs*, *Depends on::Used by*).
Relationships power:

- **Dependency views** – the graphical map on a CI form showing upstream and
  downstream dependencies.
- **Impact analysis** – when a CI has an outage, related business services
  are flagged as impacted.

## Identification and Reconciliation Engine (IRE)

The IRE prevents duplicate CIs when data comes from multiple sources
(Discovery, Service Mapping, integrations, manual entry):

- **Identification rules** define which attributes uniquely identify a CI of
  a class (e.g. serial number for hardware). Rules can be independent
  (identify on the CI's own attributes) or dependent (identify via a related
  CI).
- **Reconciliation rules** define which data source is authoritative for
  which attributes, so a lower-trust source cannot overwrite Discovery data.
- Data should be inserted through the IRE APIs (`createOrUpdateCI`) or
  Import Sets configured with **robust transform engine (RTE)** — never by
  direct inserts into `cmdb_ci` tables.

## Discovery

ServiceNow Discovery populates the CMDB automatically:

1. A **MID Server** (an agent installed in the customer network) executes probes/patterns.
2. **Patterns** log in to devices (SSH/WMI/SNMP) and collect attributes.
3. Results pass through the IRE into the CMDB.

Discovery schedules control which IP ranges are scanned and how often.

## CMDB Health

CMDB Health dashboards score the CMDB on three KPI categories:

- **Completeness** – required and recommended fields populated
- **Correctness** – duplicates, staleness, orphan and stale relationships
- **Compliance** – audit results against desired-state definitions

Health inclusion rules define which CIs are scored.

## CSDM (Common Service Data Model)

CSDM is the recommended data model for organizing services in the CMDB. Key
domains: Design (application services blueprint), Build, Manage Technical
Services, Sell/Consume (business services). Following CSDM ensures modules
like Service Portfolio Management and Service Mapping interoperate correctly.
