# 0002: Roles, keys and timeline types

## Abstract

A role names the part an object plays for an entity: its picture and sound, its thumbnails, its loudness.
Roles come from a shared **vocabulary**, so that any TEDS client can find the same thing on any entity of any schema.
Each role also carries a **timeline type**, which tells a viewer how to draw it with no per-channel configuration.
This note describes the vocabulary, keys and timeline types, and the rules an entity schema must follow that its meta-schema cannot express.

The vocabulary is version 1, held machine-readably in [`vocabulary/roles.json`](../../vocabulary/roles.json) and reported by `GET /service` as `role_vocabulary_version`.

## Content

### Timeline types

| Type | Shape of the data |
|---|---|
| `scalar` | a number sampled over time, drawn as a band from a min/max/mean pyramid |
| `state` | a value that holds until it changes |
| `interval` | a bounded span, possibly overlapping, possibly labelled |
| `instant` | a point in time, typed |
| `text` | a span carrying language, readable when the scale allows |
| `image` | a frame at a point in time |

`density` is not a type of data.
It is what a dense role becomes when zoomed out far enough, drawn from its coarse tiers.

### Keys

A role declared `cardinality: many` has a **key**, which tells its instances apart: `lang` for subtitles, `programme` for audio.
A key's value comes from the `teds.key.<name>` tag on the linked object ([AppNote 0001](./0001-using-teds-with-tams-and-tads.md)).
A schema may say which key values an entity is **expected** to have, for example `{metadata.languages}`, so that `GET /entities/{id}/status` can report "Welsh subtitles expected, none found".

### The vocabulary

| Role | Store / kind | Timeline | Key | Meaning |
|---|---|---|---|---|
| `av` | tams flow | image | — | Primary picture+sound (e.g. MPEG-TS `format:multi`) |
| `video` | tams flow | image | — | Primary picture when stored apart from sound |
| `audio` | tams flow | — | `programme` | Primary sound when stored apart from picture |
| `proxy` | tams flow | image | — | Browse proxy |
| `mezzanine` | tams flow | image | — | Edit-quality media |
| `thumbnails` | tams flow | image | — | Thumbnails (recorder `flow_collection` role) |
| `thumbnail-index` | tams flow | — | — | Thumbnail index (recorder `flow_collection` role) |
| `keyframes` | tams flow | image | — | Per-second keyframes (keyframe generator) |
| `keyframe-index` | tams flow | — | — | Keyframe frame index (keyframe generator) |
| `subtitles.cue` | tads track | text | `lang` | Subtitle cues, overlapping |
| `subtitles.gap` | tads track | interval | `lang` | Missing-subtitle spans |
| `audio.loudness` | tads track | scalar | `programme` | EBU R128 / BS.1770 samples, with tiers |
| `audio.loudness.breach` | tads track | interval | `programme` | Over/under target spans |
| `audio.silence` | tads track | interval | `programme` | Silence spans |
| `audio.format` | tads track | state | `programme` | Channel layout / codec changes |
| `video.black` | tads track | interval | — | Black spans |
| `video.freeze` | tads track | interval | — | Freeze spans |
| `video.format` | tads track | state | — | Resolution / rate / aspect changes |
| `video.shotchange` | tads track | instant | — | Shot boundaries |
| `signal.loss` | tads track | interval | — | Input/video/audio loss |
| `signal.scte35` | tads track | instant | — | SCTE-35 cues |
| `schedule` | tads track | interval | — | Planned schedule (EPG) |
| `asrun` | tads track | interval | — | What actually aired; navigation backbone |
| `transcript.asr` | tads track | text | `lang` | Speech-to-text |
| `operator.annotation` | tads track | text | — | Human notes (`editable_events: true`) |
| `operator.marks` | tads track | interval | — | Export marks / evidence ranges (replaces localStorage clips) |

A schema may use a role outside the vocabulary only with an `x-` prefix, for example `x-example.promo-slate`.
Adding a role to the vocabulary is a vocabulary version bump.

### Rules an entity schema must follow

The meta-schema [`api/schemas/definition.json`](../../api/schemas/definition.json) checks the shape of a definition.
These rules it cannot express, and a server checks them on upload (as does `tools/validate.py` in this repository):

1. `metadata` is a valid Draft 2020-12 JSON Schema of `type: object`.
2. Every `facets` and `search` entry names a property in `metadata.properties`.
   Facets must be strings, integers, booleans, or arrays of strings.
3. Roles are unique within a schema, and each is in the vocabulary or `x-`-prefixed.
4. A role's `store` and `kind` agree with the vocabulary.
5. Templates reference only things that exist: `{entity.id}`, `{member.<role>}` (a role this schema declares), `{member.self}` and `{tier.bucketSec}` (in `tierLink` only), and `{metadata.<path>}` (a path in `metadata`).
6. `tiers` are allowed only on TADS roles, with distinct `bucketSec` values.
7. `key` is required when `cardinality` is `many`, and forbidden when it is `one`.
8. Link rules reference only roles the schema declares, and never the role itself.

### Identifiers and names

- A **family** is dot-separated lowercase with at least two segments, matching `^[a-z][a-z0-9-]*(\.[a-z0-9-]+)+$`.
  `teds.*` is reserved for the core schemas; everyone else uses their own prefix.
- A **version** is an integer of at least 1, and `(family, version)` is unique.
- A **role** matches `^(x-)?[a-z][a-z0-9-]*(\.[a-z0-9-]+)*$`.
- A **key name** matches `^[a-z][a-z0-9_]*$`.
