# 0001: Using TEDS with TAMS and TADS

## Abstract

TEDS refers to objects in TAMS (flows and sources) and TADS (tracks), and links an entity to them by role.
TEDS never calls TAMS or TADS ([ADR 0013](../adr/0013-teds-does-not-check-link-targets.md)): the client that writes a link checks its target there first.
This note describes the **tag contract**: tags a process may write on the TAMS and TADS objects it creates, so that a client can find and check what to link, and the rules for writing them.
It also describes how a TEDS role refers to a TADS payload schema, which TADS itself has no notion of families for.

The tag contract is version 1, reported by `GET /service` as `contract_version`.

## Content

### Tags TEDS reserves on its own resources

TEDS resources carry `tags` exactly as TADS resources do (a string, or an array of strings).
Any tag whose name starts `teds.` is written only by TEDS itself, and a client that writes one is refused (400), as TADS reserves its own prefix.

### Tags a producer writes on TAMS and TADS objects

A process that creates a TAMS flow or source, or a TADS track, may stamp it with these tags **in the same request that creates it**.
TEDS reads none of them; they are for the clients that write links:

| Tag | On | Value | Written by |
|---|---|---|---|
| `teds.entity` | TAMS flow/source, TADS track | the entity id | the first producer, which is given the entity id |
| `teds.role` | the same | a role from the vocabulary | every producer |
| `teds.key.<name>` | the same | the key value, such as `en` or `main` | producers of `cardinality: many` roles |
| `teds.derived_from` | TAMS flow, TADS track | the id of the flow or track it was made from | every derived producer |
| `teds.rollup_of` | TADS track | the id of the base track | summary-track writers |
| `teds.tier` | TADS track | the bucket size in seconds, such as `"60"` | summary-track writers |
| `teds.contract` | all of the above | `"1"` | every producer |
| `teds.family`, `teds.version` | TADS **Payload Schema** | the payload family and version | whoever registers the payload schema |

### Rules

1. **Derived producers inherit.**
   A process that reads flow or track X copies X's `teds.entity` onto what it writes, and sets `teds.derived_from` to X.
   Only the first producer (typically the recorder) is told the entity; everything downstream finds it by inheritance.
2. **Never overwrite another producer's stamp.**
   If a stamp is wrong, correct the link in TEDS, not the tags in TAMS or TADS.
3. **A stamp is a claim, not proof.**
   A client that links a stamped object still checks it against the role's `match` (for example, a thumbnails flow must have codec `image/jpeg`), because TEDS does not.
4. **Stamp in the creating request.**
   A tag written later leaves a window in which the object exists but cannot be found by its tags.

### Structure a client can read without any tags

Some evidence needs no tags at all, because TAMS and TADS already hold it:

- a TAMS flow's `flow_collection`, whose members carry a collection role (for example, a recording's thumbnails flow as role `thumbnails`)
- a TADS track's `timeline_reference.entity_id`, which names the flow the track annotates

A schema's `link` rules once said which of these TEDS used for each role; they are deprecated and ignored ([ADR 0013](../adr/0013-teds-does-not-check-link-targets.md)).

### TADS payload-schema families

A role for TADS data says which kind of track it expects, as `match.schemaFamily`, for example `media.audio.loudness`.
TADS payload schemas have no family concept, so the family is carried as tags on the TADS **Payload Schema**: `teds.family` and `teds.version`.
Whoever registers a payload schema in TADS should tag it, so that a client can check a track against a role before linking it.

### Time

Link validity uses TAMS timestamps and timeranges, on the TAI timescale ([ADR 0011](../adr/0011-media-times-are-tai.md)).
TEDS joins TAMS and TADS timelines, so it depends on both using the same timeline.
A deployment in which recorders label TAMS timestamps as UTC rather than TAI will see links and spans offset by the TAI–UTC difference (37 seconds at the time of writing), and should resolve that before relying on TEDS spans.
