# ServiceNow Incident Management

## Overview

Incident Management restores normal service operation as quickly as possible
while minimizing impact to business operations. Incidents are stored in the
`incident` table and follow the ITIL incident lifecycle.

## Incident Lifecycle States

An incident moves through the following states:

1. **New** – The incident has been logged but not yet assigned.
2. **In Progress** – An agent has been assigned and is actively working the incident.
3. **On Hold** – Work is paused. A hold reason is required: Awaiting Caller,
   Awaiting Change, Awaiting Problem, or Awaiting Vendor.
4. **Resolved** – A fix has been applied. The caller is notified and asked to
   confirm. Resolution code and resolution notes are mandatory fields at this state.
5. **Closed** – The incident is confirmed fixed. By default, resolved incidents
   auto-close after 7 days if the caller does not respond. Closed incidents are
   read-only and cannot be reopened.
6. **Canceled** – The incident was logged in error or is no longer needed.

## Priority Calculation

Priority is not set directly. It is calculated from **Impact** and **Urgency**
using the priority data lookup table (`dl_u_priority`):

| Impact \ Urgency | 1 - High | 2 - Medium | 3 - Low |
|------------------|----------|------------|---------|
| 1 - High         | 1 - Critical | 2 - High | 3 - Moderate |
| 2 - Medium       | 2 - High | 3 - Moderate | 4 - Low |
| 3 - Low          | 3 - Moderate | 4 - Low | 5 - Planning |

- **Impact** measures the effect on business operations (how many users or
  services are affected).
- **Urgency** measures how quickly a resolution is required.

Priority 1 (Critical) incidents typically trigger the Major Incident
Management process.

## Assignment

Incidents are routed using **assignment rules** or **predictive intelligence**.
Common patterns:

- Assignment rules match on category, subcategory, or configuration item and
  set the assignment group.
- The `incident.do` form shows the assignment group and assigned-to fields;
  the assigned-to user must be a member of the assignment group.
- The `itil` role is required to be assigned an incident and to work incidents.

## Major Incidents

A major incident is a high-impact incident requiring a coordinated response.
Key points:

- Any incident can be **proposed** as a major incident; a major incident
  manager **promotes** or rejects the proposal.
- Major Incident Management requires the Major Incident Management plugin
  (com.snc.incident.mim).
- A major incident gets a dedicated workbench showing timeline, impacted
  services, communication tasks, and post-incident review.

## SLAs

Incident SLAs are defined in SLA definitions applied via SLA conditions.
A typical P1 SLA is 15-minute response and 4-hour resolution. SLA timers
pause when the incident is On Hold with reason Awaiting Caller. Breached SLAs
appear in the SLA related list on the incident form and drive escalation
notifications.

## Key Tables

| Table | Purpose |
|-------|---------|
| `incident` | Core incident records |
| `task_sla` | SLA instances attached to incidents |
| `incident_task` | Child tasks created to work parts of an incident |
| `sys_user_group` | Assignment groups |
