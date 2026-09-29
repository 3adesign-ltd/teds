---
status: "accepted"
---
# Media times are TAI

## Context and Problem Statement

TEDS joins TAMS and TADS timelines.
A link's validity, the `at` of a status or resolve request, and the instant a viewer asks about are all compared with flow and track timeranges.
TAMS timestamps are TAI, and TADS follows TAMS.
Which timescale should TEDS use for those times, and for "now"?

## Decision Drivers

* A link's validity must compare with a TAMS flow's or a TADS track's timerange without conversion
* No leap-second arithmetic in clients, which get it wrong
* Audit times (`created`, `updated`) are read by people and logs, not compared with media

## Considered Options

* TAI for every media time, as TAMS and TADS; RFC 3339 UTC for audit times
* UTC for every time
* TAI for everything, audit times included

## Decision Outcome

Chosen option: "TAI for every media time, as TAMS and TADS; RFC 3339 UTC for audit times".

* A **media time** is a TAMS timestamp (`<seconds>:<nanoseconds>`) or timerange, on the TAI timescale.
  This covers link `valid`, the `at` parameter, and the `at` of status and resolution responses.
* **Audit times** (`created`, `updated` on every resource) are RFC 3339 date-times in UTC.
  They record when a request was made, and nothing compares them with media.
* "Now" is the current TAI instant: UTC plus TAI−UTC from the IERS leap-second list.
  The server does this conversion wherever a default of "now" applies, such as the default `at`.
  Clients never convert.
* A server keeps its leap-second list current.
  When the IERS announces a leap second, a server that has not been updated is one second off from the moment it takes effect.

### Consequences

* Good, because link validity, flow timeranges and track timeranges compare directly
* Good, because a client passes through the timestamps it read from TAMS or TADS unchanged
* Bad, because "now" needs a leap-second table, and a stale table is a one-second error
* Bad, because a producer that stamps UTC into TAMS offsets every TEDS span by TAI−UTC ([AppNote 0001](../appnotes/0001-using-teds-with-tams-and-tads.md))

## Pros and Cons of the Options

### UTC for every time

* Good, because people read UTC
* Bad, because every comparison with TAMS or TADS needs a leap-second-aware conversion, and a timerange spanning a leap second cannot be represented exactly

### TAI for everything

* Good, because there is one timescale
* Bad, because audit times would be unfamiliar in logs and tools, and nothing gains from them being TAI
