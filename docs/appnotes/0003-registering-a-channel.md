# 0003: Registering a channel

## Abstract

A recorded channel becomes a complete TEDS entity when the system that sets up the recording writes its entity and its links.
This note walks through that for the core `teds.channel.logging` schema: who writes each link, what they check first, and how a person corrects the result.
TEDS itself calls no other service and links nothing on its own ([ADR 0013](../adr/0013-teds-does-not-check-link-targets.md)).

## Content

### Who writes links

1. **Declared.**
   The system that sets up the recording (a declaring principal) creates the entity and writes the links for what it deploys.
2. **Curated.**
   Anyone else, typically a person in an admin tool, writes or corrects a link.

Both go through `POST /entities/{id}/links`.
TEDS checks a link against the schema's role declaration (store, kind, cardinality, key, tier) and the overlap rule, and nothing else.

### What the writer checks first

TEDS does not look the target up, so before writing a link the client checks, in TAMS or TADS:

- that the target exists, and is of the role's `kind` (a flow, a source or a track);
- that it satisfies the role's `match`: for a TAMS flow its `format` and `codec`; for a TADS track the `teds.family` and `teds.version` tags of its Payload Schema ([AppNote 0001](./0001-using-teds-with-tams-and-tads.md)) and its `allow_overlaps`;
- for a summary tier, that the track matches the tier's own `schemaFamily` where it names one.

A client that offers a person a choice of targets should offer only those that pass, and check a pasted id the same way.

### Worked example: a logging channel

1. A channel entity is created from `teds.channel.logging` with its name, provider, territory, expected subtitle languages (`en`, `cy`) and audio programmes (`main`, `ad`).
2. The recorder registers, in TAMS, the transport stream flow, a thumbnails flow and a thumbnail-index flow.
   The system that deployed it links `av`, `thumbnails` and `thumbnail-index` to them.
3. A keyframe generator writes a keyframes flow; whoever deployed it links `keyframes`.
4. A loudness extractor writes one TADS track per audio programme and its one-minute, one-hour and one-day summary tracks.
   `audio.loudness` is linked keyed `{programme: main}`, and each summary track as a tier of it.
5. `GET /entities/{id}/status` now reports the channel complete except for `audio.loudness` for `ad`, which nothing has produced yet.

### When a recorder restarts

If a recorder registers a new flow for the same channel, the new `av` link is written starting at the new flow's first segment, and TEDS closes the old one at that moment.
`GET /entities/{id}/resolve?role=av&at=<t>` returns whichever flow served the channel at time `t`.

### Correcting the result

- A wrong link is closed (by setting the end of its `valid`) or removed, and the right one written in its place.
- Removing a link touches nothing in TAMS or TADS.
- TEDS does not notice a target deleted later: the link stays until it is closed, and a reader must be ready for a link whose target is gone ([ADR 0004](../adr/0004-links-carry-role-key-validity-and-tier.md)).
