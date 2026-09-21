<section id="abstract">

This page lists the Fa&ccedil;ade-X format mappings. A format mapping specifies how resources in one
source format are represented as Fa&ccedil;ade-X data sources, using the
[metamodel](metamodel.html) and the [Schema vocabulary](schema.html).

</section>

<section id="sotd">

This document is currently in active development. The list of formats and the status of each
mapping will change as drafts are added.

</section>

<section class="informative" id="Introduction">

## Introduction

Each format mapping specifies:

- the media types and file extensions that select the mapping;
- how a resource yields one or more data sources, each in its own [named graph](schema.html#NamedGraphs);
- which source structures become containers, which become slots, and which become values;
- how slot IRIs and types are minted from source names;
- how values are typed;
- the format-specific options, in terms of the [Engine vocabulary](engine.html).

A format mapping is selected by the media type of the resource, given by
[`fxe:media-type`](engine.html#media-type) or inferred by the engine.

</section>

<section>

## Issues

<!-- BUILD:ISSUES label="FX Mappings" -->

</section>

<section id="Principles">

## Common principles

The following principles apply to every format mapping, unless the mapping states otherwise.

**Values are strings.** Every value is a literal of type `xsd:string`, unless the source format
defines its own value types. Engines MUST NOT infer types from the lexical form of a string.

**Lexical forms are kept.** The lexical form of a value is its form in the source; engines MUST NOT
rewrite it. When the source format defines value types, the datatype of a value is chosen so that
the literal is well-typed:

1. the natural XML Schema datatype for the source type, when the source form is in its lexical space;
2. otherwise, another XML Schema datatype whose lexical space accepts the source form;
3. otherwise, `xsd:string`.

Each mapping specifies this decision for its value types (see
[issue #41](https://github.com/w3c-facade-x/facade-x-specs/issues/41)).

**Order is kept.** Where the source format orders its members, the order is kept in the numbers of
the container-membership properties `rdf:_1`, `rdf:_2`, …, starting from 1.

**Names become slot IRIs.** Where a source member has a name (a key, a column header, an element or
attribute name), the slot is a property whose IRI is minted from that name and the value of
[`fxe:namespace`](engine.html#namespace). The minting rules are shared by all mappings;
see [issue #9](https://github.com/w3c-facade-x/facade-x-specs/issues/9).

**Container identity.** Containers are blank nodes, unless
[`fxe:blank-nodes`](engine.html#blank-nodes) is `false`. Deterministic container IRIs are discussed
in [issue #17](https://github.com/w3c-facade-x/facade-x-specs/issues/17).

**Mapping options apply.** The [mapping options](engine.html#MappingOptions) of the Engine
vocabulary (for example `fxe:trim-strings` and `fxe:null-string`) apply to every format.

</section>

<section id="Formats">

## Formats

| Format | Media types | Status | Document | Issue |
|---|---|---|---|---|
| CSV | `text/csv`, `text/tab-separated-values` | Draft | [CSV mapping](mapping-csv.html) | [#29](https://github.com/w3c-facade-x/facade-x-specs/issues/29) |
| JSON | `application/json` | Planned | — | [#30](https://github.com/w3c-facade-x/facade-x-specs/issues/30) |
| XML | `application/xml`, `text/xml` | Planned | — | [#31](https://github.com/w3c-facade-x/facade-x-specs/issues/31) |
| HTML | `text/html` | Not started | — | — |
| Markdown | `text/markdown` | Not started | — | — |
| YAML | `application/yaml` | Not started | — | — |
| Spreadsheets | XLS, XLSX | Not started | — | — |
| Text | `text/plain` | Not started | — | — |
| Folders and archives | ZIP, TAR, file system | Not started | — | — |

Whether XML and HTML share a single mapping based on the Document Object Model is an open question
(see the [2026-07-06 meeting](https://github.com/w3c-facade-x/meetings/tree/main/meetings/2026-07-06)).

</section>

<section id="Tests">

## Tests

Test cases for the format mappings are maintained in the
[facade-x-tests](https://github.com/w3c-facade-x/facade-x-tests) repository, organised by format.

</section>