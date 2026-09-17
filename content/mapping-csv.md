<section id="abstract">

This document specifies how a CSV resource is represented as a Fa&ccedil;ade-X data source.

</section>

<section id="sotd">

This document is a first draft. It follows the behaviour of the reference implementation,
[SPARQL Anything](https://sparql-anything.cc/), and the test cases in
[facade-x-tests](https://github.com/w3c-facade-x/facade-x-tests/tree/main/tests/csv).

</section>

<section class="informative" id="Introduction">

## Introduction

A CSV resource is a sequence of records, and each record is a sequence of fields [[RFC4180](#bib-rfc4180)].
In Fa&ccedil;ade-X, the resource is a root container holding one container per record. A record
container holds its fields either by position or, when headers are used, by column name.

This document applies the [common principles](mappings.html#Principles) of the format mappings.

<section id="Namespaces">

### Namespaces

| Prefix | Namespace |
|---|---|
| fx | `http://sparql.xyz/facade-x/ns/` |
| fxe | `http://sparql.xyz/facade-x/engine/` |
| xyz | `http://sparql.xyz/facade-x/data/` |
| rdf | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` |

</section>

</section>

<section>

## Issues

<!-- BUILD:ISSUES label="Mapping: CSV" -->

</section>

<section id="Selection">

## Selection

An engine MUST apply this mapping to a resource whose media type is one of:

- `text/csv`
- `text/tab-separated-values`

When the media type is not given, an engine SHOULD apply this mapping to resources with the file
extensions `csv`, `tsv`, and `tab`. For `text/tab-separated-values` and for the extensions `tsv` and
`tab`, the default delimiter is the tab character.

</section>

<section id="Mapping">

## Mapping

<section id="DataSource">

### Data source

A CSV resource yields exactly one data source. Its triples are placed in the named graph whose IRI
is the value of [`fxe:root`](engine.html#root).

The data source has one root container, typed `fx:Root`.

</section>

<section id="Records">

### Records

Each record is represented by a container. The root container holds the record containers in
numbered slots, in the order of the records in the resource: the first record in `rdf:_1`, the
second in `rdf:_2`, and so on.

When [`fxe:csv.headers`](#csv.headers) is `true`, the header row is not represented as a record and
the numbering starts from the first record after it.

A resource with no records yields a root container with no slots.

</section>

<section id="Fields">

### Fields

When `fxe:csv.headers` is `false`, each field is held by a numbered slot of its record container,
in the order of the fields in the record: the first field in `rdf:_1`, the second in `rdf:_2`, and
so on.

When `fxe:csv.headers` is `true`, each field is held by a string slot. The slot IRI is minted from
the header of the field's column, as defined in the [common principles](mappings.html#Principles).
With the default namespace, a column headed `name` gives the slot `xyz:name`.

When [`fxe:csv.ignore-columns-with-no-header`](#csv.ignore-columns-with-no-header) is `true`,
fields in columns without a header are not represented.

</section>

<section id="Values">

### Values

Each field value is a literal of type `xsd:string`. CSV defines no value types, so no other
datatype is used.

The lexical form of the literal is the content of the field after parsing:

- enclosing quote characters are removed;
- a doubled quote character inside a quoted field stands for one quote character;
- delimiters and line breaks inside a quoted field are part of the value;
- leading and trailing whitespace is kept, unless [`fxe:trim-strings`](engine.html#trim-strings)
  is `true`.

An empty field, quoted or not, is represented by the empty string `""`. It is not omitted, unless
it matches `fxe:null-string` or `fxe:csv.null-string`.

</section>

</section>

<section id="Options">

## Options

These options are terms of the [Engine vocabulary](engine.html) and apply only to this mapping.

| Term | Range | Default | Description |
|---|---|---|---|
| <span id="csv.headers"></span>`fxe:csv.headers` | `xsd:boolean` | false | Use the values of the header row to mint slot IRIs for the fields. |
| <span id="csv.headers-row"></span>`fxe:csv.headers-row` | `xsd:positiveInteger` | 1 | The number of the row that holds the headers. |
| <span id="csv.delimiter"></span>`fxe:csv.delimiter` | `xsd:string` | `,` (tab for tab-separated values) | The single character that separates fields. |
| <span id="csv.quote-char"></span>`fxe:csv.quote-char` | `xsd:string` | `"` | The single character that encloses fields. An empty string disables quoting. |
| <span id="csv.null-string"></span>`fxe:csv.null-string` | `xsd:string` | — | Omit fields whose value equals the given string. |
| <span id="csv.ignore-columns-with-no-header"></span>`fxe:csv.ignore-columns-with-no-header` | `xsd:boolean` | false | Omit fields in columns that have no header. |

The reference implementation also supports `csv.format`, which selects a predefined format of the
Apache Commons CSV library, and `csv.headers.sanitize`. These are not part of this specification.

</section>

<section class="informative" id="Examples">

## Examples

<section id="ExampleBase">

### Without headers

Input:

```example
name,age
Alice,30
Bob,25
```

Fa&ccedil;ade-X representation, with default options:

```turtle
@prefix fx:  <http://sparql.xyz/facade-x/ns/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

[] a fx:Root ;
   rdf:_1 [ rdf:_1 "name"  ; rdf:_2 "age" ] ;
   rdf:_2 [ rdf:_1 "Alice" ; rdf:_2 "30" ] ;
   rdf:_3 [ rdf:_1 "Bob"   ; rdf:_2 "25" ] .
```

</section>

<section id="ExampleHeaders">

### With headers

The same input, with `fxe:csv.headers` set to `true`:

```turtle
@prefix fx:  <http://sparql.xyz/facade-x/ns/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xyz: <http://sparql.xyz/facade-x/data/> .

[] a fx:Root ;
   rdf:_1 [ xyz:name "Alice" ; xyz:age "30" ] ;
   rdf:_2 [ xyz:name "Bob"   ; xyz:age "25" ] .
```

</section>

<section id="ExampleQuoting">

### Quoting and empty fields

Input, with `fxe:csv.headers` set to `true`:

```example
id,name,notes
2,"Bob, Jr.",""
3,"Carol ""CJ"" Jones",
4,Dan,"first line
second line"
```

Fa&ccedil;ade-X representation:

```turtle
@prefix fx:  <http://sparql.xyz/facade-x/ns/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xyz: <http://sparql.xyz/facade-x/data/> .

[] a fx:Root ;
   rdf:_1 [ xyz:id "2" ; xyz:name "Bob, Jr." ; xyz:notes "" ] ;
   rdf:_2 [ xyz:id "3" ; xyz:name "Carol \"CJ\" Jones" ; xyz:notes "" ] ;
   rdf:_3 [ xyz:id "4" ; xyz:name "Dan" ; xyz:notes "first line\nsecond line" ] .
```

</section>

<section id="ExampleQuery">

### Query

Selecting the names of people older than 26:

```example
PREFIX fx:  <http://sparql.xyz/facade-x/ns/>
PREFIX fxe: <http://sparql.xyz/facade-x/engine/>
PREFIX xyz: <http://sparql.xyz/facade-x/data/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?name WHERE {
  SERVICE <x-sparql-anything:> {
    fx:properties fxe:location    "people.csv" ;
                  fxe:csv.headers true .
    ?record xyz:name ?name ;
            xyz:age  ?age .
    FILTER (xsd:integer(?age) > 26)
  }
}
```

</section>

</section>

<section class="informative" id="References">

## References

<dt id="bib-rfc4180">[RFC4180]</dt>
<dd><a href="https://www.rfc-editor.org/rfc/rfc4180">Common Format and MIME Type for Comma-Separated Values (CSV) Files</a>. Y. Shafranovich. IETF. October 2005. Informational.</dd>
<dt id="bib-sa-csv">[sparql-anything-csv]</dt>
<dd><a href="https://sparql-anything.readthedocs.io/stable/formats/CSV/">SPARQL Anything — CSV</a>.</dd>

</section>