# ServiceNow Change Management

## Overview

Change Management controls the lifecycle of changes to IT infrastructure and
services, enabling beneficial changes with minimal disruption. Change requests
are stored in the `change_request` table.

## Change Types

ServiceNow supports three change models out of the box:

### Normal Change
A change that follows the full lifecycle: Assess, Authorize, Scheduled,
Implement, Review, Closed. Normal changes require CAB (Change Advisory Board)
authorization before implementation.

### Standard Change
A pre-authorized, low-risk, repeatable change (for example, adding memory to a
server). Standard changes are created from templates in the **Standard Change
Catalog** and skip the approval phases. Each template has its own record in
the `std_change_producer_version` table and must itself be approved before it
can be used.

### Emergency Change
A change required to resolve a major incident or apply a critical security
patch. Emergency changes have an abbreviated approval path — they go to the
Emergency CAB (ECAB) and can be implemented before full documentation is
complete.

## Change States

Normal change lifecycle states:

1. **New** – Draft; requester fills in details.
2. **Assess** – Peer/technical approval. Risk assessment is completed here.
3. **Authorize** – CAB approval. The CAB workbench is used to manage agendas.
4. **Scheduled** – Approved and waiting for the planned start date.
5. **Implement** – Work in progress; change tasks are executed.
6. **Review** – Post-implementation review (PIR); verify success.
7. **Closed** – Closure code set: Successful, Successful with issues, or Unsuccessful.

## Risk Assessment

Risk is calculated using either:

- **Risk conditions** – declarative rules evaluating fields (e.g. if the CI is
  production, risk is at least Moderate).
- **Risk assessment surveys** – questionnaires whose scored answers compute risk.

The risk value (High, Moderate, Low) drives which approvals are required.

## CAB Workbench

The CAB workbench lets the change manager run CAB meetings: build agendas
automatically from change conditions, walk through each change, and record
approve/reject decisions. It requires the `sn_change_cab.cab_manager` role.

## Conflict Detection

Change conflict detection checks for scheduling conflicts:

- The same CI already scheduled for another change in the window
- The CI being in a blackout window
- Related CIs (parent/child) affected in overlapping windows

Conflicts appear on the Conflicts tab of the change form; the Conflict status
field is set to Conflict or No Conflict after the conflict checker runs.

## Key Tables

| Table | Purpose |
|-------|---------|
| `change_request` | Core change records |
| `change_task` | Implementation tasks under a change |
| `std_change_record_producer` | Standard change templates |
| `cab_meeting` | CAB meeting records |
| `change_collision` | Detected scheduling conflicts |
