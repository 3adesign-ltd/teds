#!/usr/bin/env python3
"""Check the TEDS specification repository.

What an OpenAPI linter cannot check, and what bbc/tads checks in its CI workflows, in one
place with no Docker needed:

  json-format     every *.json is jq's 4-space format (`make conform-json` fixes it)
  refs            every relative $ref in the spec and the API schemas names a real file
  meta            api/schemas/definition.json is a valid Draft 2020-12 schema
  entity-schemas  every entity schema (entity-schemas/core, entity-schemas/examples) is a
                  valid definition: the meta-schema, the embedded metadata schema, the rules
                  the meta-schema cannot express (appnote 0002), and its deterministic id
  entities        every example entity validates against its schema; example links against
                  the schema's roles and the API's link-post; per-user ids (appnote 0004)
  vocabulary      vocabulary/roles.json agrees with the API schemas and with appnote 0002
  agreement       patterns and enums the API schemas and the meta-schema both state
  neutral         the normative files name no product or organisation
  docs            every ADR and AppNote is listed in docs/README.md; no ADR is "proposed"

Exit 0 when everything passes, 1 otherwise. `--only <check>` runs one check.
"""
from __future__ import annotations

import argparse
import functools
import json
import re
import sys
import uuid
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "api"
SCHEMAS = API / "schemas"
SPEC = API / "TypedEntityDataStore.yaml"
META = SCHEMAS / "definition.json"
CORE = ROOT / "entity-schemas" / "core"
EXAMPLES = ROOT / "entity-schemas" / "examples"
VOCAB_FILE = ROOT / "vocabulary" / "roles.json"
DOCS = ROOT / "docs"

# UUIDv5 namespace for deterministic ids (ADR 0003). Must never change.
NS = uuid.UUID("cd261b94-a66a-473f-b491-da5ec582a34b")
TEMPLATE = re.compile(r"\{([^{}]+)\}")
FACET_TYPES = {"string", "integer", "boolean"}

errors: list[str] = []


def err(where: str, msg: str) -> None:
    errors.append(f"{where}: {msg}")


def load(p: Path):
    return json.loads(p.read_text())


def rel(p: Path) -> str:
    return str(p.relative_to(ROOT))


# ── the API schemas, as a registry so sibling "$ref": "uuid.json" resolves ──────────────
def _retrieve(uri: str) -> Resource:
    # The API schemas carry no $schema (as bbc/tads's do not): they are OpenAPI 3.1 schema
    # objects, which are Draft 2020-12.
    return DRAFT202012.create_resource(load(Path(uri.removeprefix("file://"))))


REGISTRY = Registry(retrieve=_retrieve)


def api_validator(name: str) -> Draft202012Validator:
    path = SCHEMAS / f"{name}.json"
    return Draft202012Validator({"$ref": path.as_uri()}, registry=REGISTRY)


# ── checks ────────────────────────────────────────────────────────────────────────────────
def check_json_format() -> None:
    for p in sorted(ROOT.rglob("*.json")):
        if any(part.startswith(".") or part in {"node_modules", "docs"} for part in p.relative_to(ROOT).parts[:-1]):
            continue
        text = p.read_text()
        try:
            want = json.dumps(json.loads(text), indent=4, ensure_ascii=False) + "\n"
        except json.JSONDecodeError as e:
            err(rel(p), f"not JSON: {e}")
            continue
        if text != want:
            err(rel(p), "not in jq 4-space format (run `make conform-json`)")


def check_refs() -> None:
    def walk(o, where, base: Path):
        if isinstance(o, dict):
            r = o.get("$ref")
            if isinstance(r, str) and not r.startswith("#") and "://" not in r:
                target = (base / r.split("#")[0]).resolve()
                if not target.exists():
                    err(where, f"$ref {r!r} names no file")
            for v in o.values():
                walk(v, where, base)
        elif isinstance(o, list):
            for v in o:
                walk(v, where, base)
    walk(yaml.safe_load(SPEC.read_text()), rel(SPEC), API)
    for p in sorted(SCHEMAS.glob("*.json")):
        walk(load(p), rel(p), SCHEMAS)


def vocabulary() -> dict[str, dict]:
    return {r["role"]: r for r in load(VOCAB_FILE)["roles"]}


def check_meta() -> Draft202012Validator:
    meta = load(META)
    Draft202012Validator.check_schema(meta)
    return Draft202012Validator(meta)


def metadata_path_exists(schema: dict, dotted: str) -> bool:
    node = schema
    for part in dotted.split("."):
        props = node.get("properties", {})
        if part not in props:
            return False
        node = props[part]
    return True


def check_templates(where, value, roles, metadata, allow_self, allow_tier) -> None:
    if isinstance(value, dict):
        for v in value.values():
            check_templates(where, v, roles, metadata, allow_self, allow_tier)
        return
    if isinstance(value, list):
        for v in value:
            check_templates(where, v, roles, metadata, allow_self, allow_tier)
        return
    if not isinstance(value, str):
        return
    for ref in TEMPLATE.findall(value):
        if ref == "entity.id":
            continue
        if ref == "member.self":
            if not allow_self:
                err(where, "{member.self} is only meaningful in tierLink")
        elif ref == "tier.bucketSec":
            if not allow_tier:
                err(where, "{tier.bucketSec} is only meaningful in tierLink")
        elif ref.startswith("member."):
            if ref[len("member."):] not in roles:
                err(where, f"{{{ref}}} names a role this schema does not declare")
        elif ref.startswith("metadata."):
            if not metadata_path_exists(metadata, ref[len("metadata."):]):
                err(where, f"{{{ref}}} is not a path in metadata")
        else:
            err(where, f"unknown template {{{ref}}}")


def check_entity_definition(where: str, d: dict, vocab: dict[str, dict]) -> None:
    """The rules appnote 0002 states that the meta-schema cannot express."""
    md = d["metadata"]
    props = md.get("properties", {})
    for f in d.get("facets", []):
        if f not in props:
            err(where, f"facet {f!r} is not a metadata property")
            continue
        t = props[f].get("type")
        if t == "array":
            items = props[f].get("items", {})
            if items.get("type") != "string" and "enum" not in items:
                err(where, f"facet {f!r}: arrays must be of strings")
        elif t not in FACET_TYPES and "enum" not in props[f]:
            err(where, f"facet {f!r}: type {t!r} cannot be a facet")
    for s in d.get("search", []):
        if s not in props:
            err(where, f"search field {s!r} is not a metadata property")
    names = [r["role"] for r in d["roles"]]
    dupes = {r for r in names if names.count(r) > 1}
    if dupes:
        err(where, f"duplicate roles {sorted(dupes)}")
    declared = set(names)
    check_templates(f"{where} display", d.get("display", {}), declared, md, False, False)
    for r in d["roles"]:
        rw = f"{where} role {r['role']}"
        name = r["role"]
        if not name.startswith("x-"):
            v = vocab.get(name)
            if v is None:
                err(rw, "not in vocabulary/roles.json and not x- prefixed")
            elif (v["store"], v["kind"]) != (r["store"], r["kind"]):
                err(rw, f"store/kind {r['store']}/{r['kind']} disagrees with the vocabulary {v['store']}/{v['kind']}")
        tiers = [t["bucketSec"] for t in r.get("tiers", [])]
        if len(tiers) != len(set(tiers)):
            err(rw, "duplicate tier bucketSec")
        for rule in r.get("link", []):
            for k in ("collectionOf", "derivedFrom", "timelineReferenceOf"):
                if k in rule and rule[k] not in declared:
                    err(rw, f"link rule {k}={rule[k]!r} names an undeclared role")
                if k in rule and rule[k] == name:
                    err(rw, f"link rule {k} refers to the role itself")
            check_templates(rw, rule, declared, md, False, False)
        if "tierLink" in r:
            check_templates(f"{rw} tierLink", r["tierLink"], declared, md, True, True)
        if "key" in r and "expected" in r["key"]:
            exp = r["key"]["expected"]
            check_templates(f"{rw} key.expected", exp, declared, md, False, False)
            if isinstance(exp, str):
                m = TEMPLATE.fullmatch(exp)
                path = m.group(1)[len("metadata."):] if m and m.group(1).startswith("metadata.") else None
                if not path:
                    err(rw, "key.expected as a string must be exactly one {metadata.<path>} template")
                elif metadata_path_exists(md, path):
                    node = md
                    for part in path.split("."):
                        node = node["properties"][part]
                    if node.get("type") != "array":
                        err(rw, f"key.expected {{metadata.{path}}} must name an array")
        if "scale" in r and isinstance(r["scale"].get("reference"), str):
            check_templates(f"{rw} scale", r["scale"]["reference"], declared, md, False, False)


@functools.cache
def entity_schemas() -> dict[str, dict]:
    """Every valid entity schema, by id. Entity schemas are the <family>-v<N>.json files. Cached, so
    the two checks that need them report each problem once."""
    meta_v = check_meta()
    vocab = vocabulary()
    good: dict[str, dict] = {}
    versioned = re.compile(r".+-v\d+\.json$")
    for p in sorted(p for p in [*CORE.glob("*.json"), *EXAMPLES.glob("*.json")] if versioned.fullmatch(p.name)):
        where = rel(p)
        res = load(p)
        d = res["definition"]
        before = len(errors)
        for e in meta_v.iter_errors(d):
            err(where, f"definition: {e.message} at {'/'.join(map(str, e.absolute_path))}")
        if len(errors) > before:
            continue
        for e in Draft202012Validator(Draft202012Validator.META_SCHEMA).iter_errors(d["metadata"]):
            err(where, f"embedded JSON Schema: {e.message}")
        check_entity_definition(where, d, vocab)
        want = str(uuid.uuid5(NS, f"schema:{d['family']}:{d['version']}"))
        if res["id"] != want:
            err(where, f"id {res['id']} is not v5(NS, schema:{d['family']}:{d['version']}) = {want}")
        if p.parent == CORE and not d["family"].startswith("teds."):
            err(where, "a core schema's family must start teds.")
        if p.parent == EXAMPLES and d["family"].startswith("teds."):
            err(where, "teds.* families are reserved for core schemas")
        if len(errors) == before:
            good[res["id"]] = d
    return good


def check_entities(schemas: dict[str, dict]) -> None:
    link_post = api_validator("link-post")
    origins = load(SCHEMAS / "origin.json")["enum"]
    for p in sorted(EXAMPLES.glob("entity-*.json")):
        where = rel(p)
        ent = load(p)
        d = schemas.get(ent["schema_id"])
        if d is None:
            err(where, f"schema_id {ent['schema_id']} is not a valid entity schema in this repo")
            continue
        for e in Draft202012Validator(d["metadata"]).iter_errors(ent["metadata"]):
            err(where, f"metadata: {e.message} at {'/'.join(map(str, e.absolute_path))}")
        if "_user_sub" in ent:
            want = str(uuid.uuid5(NS, f"user:{d['family']}:{ent['_user_sub']}"))
            if ent["id"] != want:
                err(where, f"per-user entity id {ent['id']} is not v5(NS, user:{d['family']}:<sub>) = {want}")
        roles = {r["role"]: r for r in d["roles"]}
        for i, link in enumerate(ent.get("_links_example", [])):
            lw = f"{where} link[{i}]"
            r = roles.get(link["role"])
            if r is None:
                err(lw, f"role {link['role']!r} not in the schema")
                continue
            if (link["store"], link["target"]["kind"]) != (r["store"], r["kind"]):
                err(lw, "store/kind disagrees with the role")
            want_keys = {r["key"]["name"]} if "key" in r else set()
            if set(link.get("key", {})) != want_keys:
                err(lw, f"key {link.get('key')} does not match the role's key {sorted(want_keys)}")
            if "tier" in link and link["tier"] not in {t["bucketSec"] for t in r.get("tiers", [])}:
                err(lw, f"tier {link['tier']} is not declared on role {r['role']}")
            if link.get("origin") not in origins:
                err(lw, f"origin {link.get('origin')!r} is not in api/schemas/origin.json")
            for e in link_post.iter_errors({k: v for k, v in link.items() if k != "origin"}):
                err(lw, f"not a valid link-post body: {e.message}")
    bogus = {"role": "av", "store": "tams", "target": {"kind": "flow", "id": str(uuid.uuid4())},
             "valid": "[0:0_", "id": str(uuid.uuid4())}
    if not list(link_post.iter_errors(bogus)):
        err("api/schemas/link-post.json", "accepted a body carrying the server-assigned `id`")


def check_vocabulary() -> None:
    vocab = vocabulary()
    role_v = api_validator("role")
    stores = load(SCHEMAS / "store.json")["enum"]
    kinds = load(SCHEMAS / "target-kind.json")["enum"]
    timelines = load(SCHEMAS / "resolution.json")["properties"]["timeline"]["enum"]
    for name, r in vocab.items():
        where = f"vocabulary/roles.json {name}"
        for e in role_v.iter_errors(name):
            err(where, f"role name: {e.message}")
        if r["store"] not in stores:
            err(where, f"store {r['store']!r} not in api/schemas/store.json")
        if r["kind"] not in kinds:
            err(where, f"kind {r['kind']!r} not in api/schemas/target-kind.json")
        if (r["store"] == "tads") != (r["kind"] == "track"):
            err(where, "TADS roles are tracks; TAMS roles are flows or sources")
        if "timeline" in r and r["timeline"] not in timelines:
            err(where, f"timeline {r['timeline']!r} not a timeline type")
        if "key" in r and not re.fullmatch(r"[a-z][a-z0-9_]*", r["key"]):
            err(where, f"key {r['key']!r} is not a key name")
    note = DOCS / "appnotes" / "0002-roles-keys-and-timeline-types.md"
    if note.exists():
        section = note.read_text().split("### The vocabulary", 1)[-1].split("\n### ", 1)[0]
        listed = re.findall(r"^\| `([a-z][a-z0-9.-]*)` \|", section, re.M)
        if sorted(listed) != sorted(vocab):
            err(rel(note), f"its role table {sorted(set(listed) ^ set(vocab))} differs from vocabulary/roles.json")
    else:
        err(rel(note), "missing: the vocabulary must be documented")


def check_agreement() -> None:
    meta = load(META)["$defs"]

    def same(label, a, b):
        if a != b:
            err("agreement", f"{label}: {a!r} != {b!r}")
    same("role pattern (api/schemas/role.json vs meta)", load(SCHEMAS / "role.json")["pattern"], meta["role"]["pattern"])
    same("family pattern (api/schemas/family.json vs meta)", load(SCHEMAS / "family.json")["pattern"], meta["family"]["pattern"])
    same("timeline types (resolution.json vs meta)", sorted(load(SCHEMAS / "resolution.json")["properties"]["timeline"]["enum"]),
         sorted(meta["roleDeclaration"]["properties"]["timeline"]["enum"]))
    same("stores (store.json vs meta)", sorted(load(SCHEMAS / "store.json")["enum"]),
         sorted(meta["roleDeclaration"]["properties"]["store"]["enum"]))
    same("target kinds (target-kind.json vs meta)", sorted(load(SCHEMAS / "target-kind.json")["enum"]),
         sorted(meta["roleDeclaration"]["properties"]["kind"]["enum"]))


NEUTRAL = re.compile(r"(?i)\b(phrame|bbc)\b")


def check_neutral() -> None:
    """The normative files name no product or organisation (ADR 0010)."""
    spec = yaml.safe_load(SPEC.read_text())
    files = {SPEC: SPEC.read_text().replace(spec["info"]["contact"]["url"], "")}
    for p in [*SCHEMAS.glob("*.json"), *CORE.glob("*.json"), VOCAB_FILE]:
        files[p] = p.read_text()
    for p, text in files.items():
        for m in NEUTRAL.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            err(f"{rel(p)}:{line}", f"names {m.group(0)!r}; the normative files must be product-neutral")


def check_docs() -> None:
    index = (DOCS / "README.md").read_text()
    for kind in ("adr", "appnotes"):
        for p in sorted((DOCS / kind).glob("[0-9]*.md")):
            if f"./{kind}/{p.name}" not in index:
                err(rel(p), "not listed in docs/README.md")
    for p in sorted((DOCS / "adr").glob("[0-9]*.md")):
        head = p.read_text().split("\n---", 1)[0]
        if re.search(r'^status: "proposed"', head, re.M):
            err(rel(p), 'still has status "proposed"; accept or reject it before merging')


CHECKS = {
    "json-format": check_json_format,
    "refs": check_refs,
    "meta": lambda: check_meta(),
    "entity-schemas": lambda: entity_schemas(),
    "entities": lambda: check_entities(entity_schemas()),
    "vocabulary": check_vocabulary,
    "agreement": check_agreement,
    "neutral": check_neutral,
    "docs": check_docs,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", choices=sorted(CHECKS))
    args = ap.parse_args()
    for name, fn in CHECKS.items():
        if args.only and name != args.only:
            continue
        before = len(errors)
        fn()
        print(f"{'ok  ' if len(errors) == before else 'FAIL'} {name}")
        # A file that is not JSON at all would crash every later check that reads it, and
        # bury the one error that matters under a traceback.
        if name == "json-format" and any("not JSON" in e for e in errors[before:]):
            print("   (stopping: fix the files that are not JSON first)")
            break
    for e in errors:
        print("  ", e)
    print(f"{len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
