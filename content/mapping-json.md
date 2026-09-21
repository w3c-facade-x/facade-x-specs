---
title: <code>Fa&ccedil;ade-X</code> mapping for JSON
subtitle: Representing JSON in Fa&ccedil;ade-X.
---

<section id="abstract">

This document specifies how a JSON resource is represented as a Fa&ccedil;ade-X data source.

</section>

<section id="sotd">

This document is a first draft. It follows the behaviour of the reference implementation,
[SPARQL Anything](https://sparql-anything.cc/), and the test cases in
[facade-x-tests](https://github.com/w3c-facade-x/facade-x-tests/tree/main/tests/json), except where
the [Issues](#Issues) section says otherwise.

</section>

<section class="informative" id="Introduction">

## Introduction

A [JSON text](https://www.rfc-editor.org/rfc/rfc8259#section-2) is a single [value](https://www.rfc-editor.org/rfc/rfc8259#section-3): an
[object](https://www.rfc-editor.org/rfc/rfc8259#section-4), an [array](https://www.rfc-editor.org/rfc/rfc8259#section-5), a
[string](https://www.rfc-editor.org/rfc/rfc8259#section-7), a [number](https://www.rfc-editor.org/rfc/rfc8259#section-6),
`true`, `false`, or `null` [[RFC8259](#bib-rfc8259)]. Objects hold members by name, and arrays hold
elements by position.
In Fa&ccedil;ade-X, objects and arrays are containers. Object members are held by string slots and
array elements by numbered slots. Strings, numbers and booleans are values.

This document applies the [common principles](mappings.html#Principles) of the format mappings.

<section id="Namespaces">

### Namespaces

| Prefix | Namespace |
|---|---|
| fx | `http://sparql.xyz/facade-x/ns/` |
| fxe | `http://sparql.xyz/facade-x/engine/` |
| xyz | `http://sparql.xyz/facade-x/data/` |
| rdf | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` |
| xsd | `http://www.w3.org/2001/XMLSchema#` |

</section>

</section>

<section>

## Issues

<!-- BUILD:ISSUES label="Mapping: JSON" -->

The typing of numbers follows the decision in
[issue #41](https://github.com/w3c-facade-x/facade-x-specs/issues/41). It differs from the
reference implementation, which types every number as `xsd:decimal` (giving ill-typed literals for
numbers with an exponent) and writes `-0` as `"0"`.

When `fxe:json.include-null-values` is `true`, the reference implementation represents `null` with
the IRI `xyz:null`. Whether `null` should have a term in the Schema vocabulary is open.

The representation of a top-level string, number or boolean, and the treatment of duplicate member
names (which [RFC 8259 §4](https://www.rfc-editor.org/rfc/rfc8259#section-4) allows, although names SHOULD be unique), are not yet
specified.

</section>

<section id="Selection">

## Selection

An engine MUST apply this mapping to a resource whose media type is
[`application/json`](https://www.rfc-editor.org/rfc/rfc8259#section-11), or any media type with the
[structured syntax suffix `+json`](https://www.rfc-editor.org/rfc/rfc6839#section-3.1)
[[RFC6839](#bib-rfc6839)] (e.g. `application/problem+json`).

When the media type is not given, an engine SHOULD apply this mapping to resources with the file
extension `json`.

</section>

<section id="Mapping">

## Mapping

<section id="DataSource">

### Data source

A JSON resource yields exactly one data source. Its triples are placed in the named graph whose IRI
is the value of [`fxe:root`](engine.html#root).

The top-level value is represented by the root container, typed `fx:Root`:

- a top-level object gives a root container holding the object's members;
- a top-level array gives a root container holding the array's elements.

</section>

<section id="Objects">

### Objects

An object is represented by a container. Each member is held by a string slot whose IRI is minted
from the member name, as defined in the [common principles](mappings.html#Principles). With the
default namespace, the member `"name"` gives the slot `xyz:name`.

Characters that are not allowed in an IRI are percent-encoded as UTF-8; other characters, including
non-ASCII letters, are kept. The member `"key with spaces"` gives `xyz:key%20with%20spaces`, and the
empty member name `""` gives the namespace IRI itself.

A member whose value is an object or an array holds the container that represents it. An empty
object gives a container with no slots.

</section>

<section id="Arrays">

### Arrays

An array is represented by a container. Each element is held by a numbered slot, in the order of the
array: the first element in `rdf:_1`, the second in `rdf:_2`, and so on.

A `null` element keeps its position: no triple is produced for it, and the following element keeps
its own index. For example, in `[1, null, 3]` the value `3` is held by `rdf:_3`.

An element that is an object or an array holds the container that represents it. An empty array
gives a container with no slots.

</section>

<section id="Values">

### Values

JSON defines value types. Following the [common principles](mappings.html#Principles), the
lexical form of every value is its source form, and the datatype is chosen so that the literal is
well-typed [[XMLSCHEMA11-2](#bib-xmlschema11-2)]:

| JSON value | Literal |
|---|---|
| [string](https://www.rfc-editor.org/rfc/rfc8259#section-7) | `xsd:string`; the lexical form is the sequence of Unicode characters the string denotes, after unescaping |
| [number](https://www.rfc-editor.org/rfc/rfc8259#section-6) without an exponent | `xsd:decimal`, with the numeral as written in the source |
| [number](https://www.rfc-editor.org/rfc/rfc8259#section-6) with an exponent (`exp`) | `xsd:double`, with the numeral as written in the source |
| `true`, `false` | `xsd:boolean` |
| `null` | no triple, unless [`fxe:json.include-null-values`](#json.include-null-values) is `true` |

Numbers are typed as follows:

1. The [JSON number grammar](https://www.rfc-editor.org/rfc/rfc8259#section-6) is a decimal numeral with an optional fraction
   (`frac`) and exponent (`exp`). The natural datatype for a JSON number is `xsd:decimal`, whose
   [value space](https://www.w3.org/TR/xmlschema11-2/#decimal) contains every JSON number exactly.
   A numeral without an exponent is always in the
   [lexical space of `xsd:decimal`](https://www.w3.org/TR/xmlschema11-2/#decimal-lexical-representation),
   so it is typed `xsd:decimal` (e.g. `3.0` gives `"3.0"^^xsd:decimal`, and `-0` gives `"-0"^^xsd:decimal`).
2. The lexical space of `xsd:decimal` has no exponent notation. A numeral with an exponent is in the
   [lexical space of `xsd:double`](https://www.w3.org/TR/xmlschema11-2/#sec-lex-double), so it is
   typed `xsd:double` (e.g. `1.5e3` gives `"1.5e3"^^xsd:double`).
3. A numeral that is in neither lexical space is typed `xsd:string`. This does not happen for a
   well-formed JSON text.

The value of an `xsd:double` literal is the nearest double-precision value to the number, so it may
differ from the number written in the source (e.g. `2E-4`). The lexical form keeps the number as
written.

</section>

</section>

<section id="Options">

## Options

These options are terms of the [Engine vocabulary](engine.html) and apply only to this mapping.

| Term | Range | Default | Description |
|---|---|---|---|
| <span id="json.include-null-values"></span>`fxe:json.include-null-values` | `xsd:boolean` | false | Produce a triple for members and elements whose value is `null`. |
| <span id="json.path"></span>`fxe:json.path` | `xsd:string` | — | A JSONPath query [[RFC9535](#bib-rfc9535)]. The root container holds the nodes selected by the query in numbered slots, in the order they are selected. |
| <span id="json.literalize"></span>`fxe:json.literalize` | `xsd:string` | — | A member name. The values of members with this name are represented as a single literal holding their JSON text, instead of as containers. |

The reference implementation accepts several values for `json.path` and `json.literalize` as
numbered options (`json.path.1`, `json.path.2`, …). Whether this form is kept is open.

</section>

<section class="informative" id="Examples">

## Examples

<section id="ExampleBase">

### Object

Input:

```example
{
  "name": "Alice",
  "age": 30
}
```

Fa&ccedil;ade-X representation:

```turtle
@prefix fx:  <http://sparql.xyz/facade-x/ns/> .
@prefix xyz: <http://sparql.xyz/facade-x/data/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

[] a fx:Root ;
   xyz:name "Alice" ;
   xyz:age  "30"^^xsd:decimal .
```

</section>

<section id="ExampleNested">

### Nested objects and arrays

Input:

```example
{
  "object": { "nested": { "deep": "value" } },
  "array": [1, "two", 3.0, true, null, {"key": "value"}, ["nested", "array"], [], {}],
  "emptyObject": {},
  "key with spaces": "spaces in key"
}
```

Fa&ccedil;ade-X representation:

```turtle
@prefix fx:  <http://sparql.xyz/facade-x/ns/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xyz: <http://sparql.xyz/facade-x/data/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

[] a fx:Root ;
   xyz:object [ xyz:nested [ xyz:deep "value" ] ] ;
   xyz:array [
       rdf:_1 "1"^^xsd:decimal ;
       rdf:_2 "two" ;
       rdf:_3 "3.0"^^xsd:decimal ;
       rdf:_4 true ;
       rdf:_6 [ xyz:key "value" ] ;
       rdf:_7 [ rdf:_1 "nested" ; rdf:_2 "array" ] ;
       rdf:_8 [ ] ;
       rdf:_9 [ ]
   ] ;
   xyz:emptyObject [ ] ;
   <http://sparql.xyz/facade-x/data/key%20with%20spaces> "spaces in key" .
```

The `null` element produces no triple, so there is no `rdf:_5`.

</section>

<section id="ExampleNumbers">

### Numbers

Input:

```example
{
  "integer": 42,
  "negativeZero": -0,
  "decimal": 3.0,
  "exponent": 1.5e3,
  "negativeExponent": 2E-4,
  "bigInteger": 12345678901234567890
}
```

Fa&ccedil;ade-X representation:

```turtle
@prefix fx:  <http://sparql.xyz/facade-x/ns/> .
@prefix xyz: <http://sparql.xyz/facade-x/data/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

[] a fx:Root ;
   xyz:integer          "42"^^xsd:decimal ;
   xyz:negativeZero     "-0"^^xsd:decimal ;
   xyz:decimal          "3.0"^^xsd:decimal ;
   xyz:exponent         "1.5e3"^^xsd:double ;
   xyz:negativeExponent "2E-4"^^xsd:double ;
   xyz:bigInteger       "12345678901234567890"^^xsd:decimal .
```

</section>

<section id="ExampleQuery">

### Query

Listing each element of the `array` member, with its position:

```example
PREFIX fx:   <http://sparql.xyz/facade-x/ns/>
PREFIX fxe:  <http://sparql.xyz/facade-x/engine/>
PREFIX xyz:  <http://sparql.xyz/facade-x/data/>

SELECT ?slot ?value WHERE {
  SERVICE <x-sparql-anything:> {
    fx:properties fxe:location "features.json" .
    ?root a fx:Root ;
          xyz:array ?array .
    ?array ?slot ?value .
  }
}
```

</section>

</section>

<section class="informative" id="References">

## References

<dt id="bib-rfc8259">[RFC8259]</dt>
<dd><a href="https://www.rfc-editor.org/rfc/rfc8259">The JavaScript Object Notation (JSON) Data Interchange Format</a>. T. Bray. IETF. December 2017. Internet Standard.</dd>
<dt id="bib-rfc6839">[RFC6839]</dt>
<dd><a href="https://www.rfc-editor.org/rfc/rfc6839">Additional Media Type Structured Syntax Suffixes</a>. T. Hansen; A. Melnikov. IETF. January 2013. Informational.</dd>
<dt id="bib-rfc9535">[RFC9535]</dt>
<dd><a href="https://www.rfc-editor.org/rfc/rfc9535">JSONPath: Query Expressions for JSON</a>. S. Gössner; G. Normington; C. Bormann. IETF. February 2024. Proposed Standard.</dd>
<dt id="bib-xmlschema11-2">[XMLSCHEMA11-2]</dt>
<dd><a href="https://www.w3.org/TR/xmlschema11-2/">W3C XML Schema Definition Language (XSD) 1.1 Part 2: Datatypes</a>. David Peterson; Shudi Gao; Ashok Malhotra; C. M. Sperberg-McQueen; Henry S. Thompson. W3C. 5 April 2012. W3C Recommendation.</dd>
<dt id="bib-sa-json">[sparql-anything-json]</dt>
<dd><a href="https://sparql-anything.readthedocs.io/stable/formats/JSON/">SPARQL Anything — JSON</a>.</dd>

</section>