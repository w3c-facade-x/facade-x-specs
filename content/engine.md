---
title: <code>Fa&ccedil;ade-X</code> Engine vocabulary
subtitle: Options for engines that build Fa&ccedil;ade-X representations of resources.
order: 4
---

<section id="abstract">

This document specifies the Fa&ccedil;ade-X Engine vocabulary: the terms used to configure an engine
that builds the Fa&ccedil;ade-X representation of a resource. The vocabulary is independent of the
[Fa&ccedil;ade-X Schema vocabulary](schema.html), which describes the representation itself, and of
the language used to request it, such as [SPARQL](sparql.html).

</section>

<section id="sotd">

This document is currently in active development. The terms are derived from the configuration
options of the reference implementation, [SPARQL Anything](https://sparql-anything.cc/).

</section>

<section class="informative" id="Introduction">

## Introduction

An engine takes a resource and a set of options and produces a Fa&ccedil;ade-X data source, as
defined by the [metamodel](metamodel.html) and the [Schema vocabulary](schema.html). This document
names those options.

The Schema and Engine vocabularies are kept separate for three reasons:

- an implementation MAY produce data that conforms to the Schema vocabulary without supporting the
  Engine vocabulary;
- the Engine vocabulary MAY be used outside SPARQL, for example in configuration files, command-line
  tools, or pipeline descriptions;
- the two vocabularies can evolve at different paces.

<section id="Namespaces">

### Namespaces

| Prefix | Namespace | Description |
|---|---|---|
| fxe | `http://sparql.xyz/facade-x/engine/` | The Fa&ccedil;ade-X Engine vocabulary (this document) |
| fx | `http://sparql.xyz/facade-x/ns/` | The [Fa&ccedil;ade-X Schema vocabulary](schema.html) |
| xyz | `http://sparql.xyz/facade-x/data/` | The default namespace for derived data |
| rdf | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` | [[rdf-schema](#bib-rdf-schema)] |
| rdfs | `http://www.w3.org/2000/01/rdf-schema#` | [[rdf-schema](#bib-rdf-schema)] |
| xsd | `http://www.w3.org/2001/XMLSchema#` | [[xmlschema-2](#bib-xmlschema-2)] |

</section>

</section>

<section>

## Issues

<!-- BUILD:ISSUES label="FX Engine Vocabulary" -->

The namespace `http://sparql.xyz/facade-x/engine/` is a placeholder. The reference implementation
currently uses the Schema namespace for options (e.g. `fx:location`). Until the namespace is settled,
an implementation MAY accept each option both as `fxe:[NAME]` and as `fx:[NAME]`.

Execution options (e.g. `strategy`, `slice`, `ondisk`), and options for HTTP and S3 access, are not
yet covered.

Format-specific options (e.g. `csv.headers`, `json.path`, `xml.path`) are out of scope for this
document and are expected to be specified with the format mappings.

</section>

<section id="Classes">

## Classes

<section class="term" id="Configuration">
<h3 id="h-Configuration">Configuration</h3>
<p>The class of engine configurations. A configuration is a set of option values applied to one
invocation of an engine.</p>
<div class="tech">
  <ul>
    <li><strong>IRI:</strong> http://sparql.xyz/facade-x/engine/Configuration</li>
    <li><strong>Sub Class Of:</strong> rdfs:Resource</li>
    <li><strong>Predicates:</strong> ANY instance of <a href="#Option">fxe:Option</a></li>
  </ul>
</div>
</section>

<section class="term" id="Option">
<h3 id="h-Option">Option</h3>
<p>The class of engine options. Every term in the <a href="#Options">Options</a> section is an
instance of this class.</p>
<div class="tech">
  <ul>
    <li><strong>IRI:</strong> http://sparql.xyz/facade-x/engine/Option</li>
    <li><strong>Sub Class Of:</strong> rdf:Property</li>
    <li><strong>Instances - Domain:</strong> http://sparql.xyz/facade-x/engine/Configuration</li>
  </ul>
</div>
</section>

</section>

<section id="Options">

## Options

All options are optional, except that exactly one source option (`fxe:location`, `fxe:content`,
`fxe:command`, `fxe:read-from-std-in`, or `fxe:query`) MUST be given. Values are literals; an
engine MUST accept the lexical form of the stated range as a plain string.

<section id="SourceOptions">

### Source options

Options that identify the resource and how its bytes are read.

| Term | Range | Default | Description |
|---|---|---|---|
| <span id="location"></span>`fxe:location` | `xsd:string` | — | A URL, or an absolute or relative file-system path, of the resource to be interpreted. |
| <span id="content"></span>`fxe:content` | `xsd:string` | — | Inline content to be interpreted in place of a located resource. Without `fxe:media-type` the content is interpreted as plain text. |
| <span id="command"></span>`fxe:command` | `xsd:string` | — | An external command line whose standard output is interpreted according to `fxe:media-type`. |
| <span id="read-from-std-in"></span>`fxe:read-from-std-in` | `xsd:boolean` | false | Read the content from standard input and use it as the value of `fxe:content`. |
| <span id="query"></span>`fxe:query` | `xsd:string` | — | Location of a SPARQL query whose result (bindings, graph, or dataset) is used as the source. When set, other options are ignored. |
| <span id="from-archive"></span>`fxe:from-archive` | `xsd:string` | — | Location of an archive; `fxe:location` is then resolved as an entry within it. |
| <span id="archive-format"></span>`fxe:archive-format` | `xsd:string` | Inferred from the archive location | Format of the archive given in `fxe:from-archive` (e.g. `zip`, `tar`). |
| <span id="media-type"></span>`fxe:media-type` | `xsd:string` | Inferred from the file extension | The media type of the source, selecting the interpretation. Required when it cannot be inferred. |
| <span id="charset"></span>`fxe:charset` | `xsd:string` | UTF-8 | The character encoding of the source. |

</section>

<section id="MappingOptions">

### Mapping options

Options that change the Fa&ccedil;ade-X representation produced for a resource. Two engines given the
same resource and the same mapping options MUST produce isomorphic representations.

| Term | Range | Default | Description |
|---|---|---|---|
| <span id="root"></span>`fxe:root` | `xsd:anyURI` | Location + `#`, or `xyz:` + md5(content or command) + `#` | IRI of the root container; also the base for minting graph and container IRIs. |
| <span id="namespace"></span>`fxe:namespace` | `xsd:anyURI` | `http://sparql.xyz/facade-x/data/` | Namespace used to mint string-slot properties and types from source keys and tags. |
| <span id="blank-nodes"></span>`fxe:blank-nodes` | `xsd:boolean` | true | Represent containers as blank nodes. When `false`, container IRIs are minted from `fxe:root`. |
| <span id="trim-strings"></span>`fxe:trim-strings` | `xsd:boolean` | false | Trim leading and trailing whitespace from string values. |
| <span id="null-string"></span>`fxe:null-string` | `xsd:string` | — | Omit any triple whose object value would equal the given string. |
| <span id="use-rdfs-member"></span>`fxe:use-rdfs-member` | `xsd:boolean` | false | Use `rdfs:member` in place of `rdf:_1`, `rdf:_2`, … |
| <span id="annotate-triples-with-slot-keys"></span>`fxe:annotate-triples-with-slot-keys` | `xsd:boolean` | false | Annotate slot triples with their key using `fx:slot-key` (RDF 1.2 triple terms). |
| <span id="generate-predicate-labels"></span>`fxe:generate-predicate-labels` | `xsd:boolean` | false | Emit `rdfs:label` for minted properties and types. |
| <span id="metadata"></span>`fxe:metadata` | `xsd:boolean` | false | Extract resource metadata into the graph `xyz:metadata`. |
| <span id="audit"></span>`fxe:audit` | `xsd:boolean` | false | Emit an audit graph `xyz:audit` describing each generated graph. |

</section>

</section>

<section id="Serialisations">

## Using the vocabulary

<section id="InRDF">

### In RDF

A configuration can be described in RDF as an instance of `fxe:Configuration`:

```turtle
@prefix fxe: <http://sparql.xyz/facade-x/engine/> .

<#people> a fxe:Configuration ;
    fxe:location   "https://example.org/people.json" ;
    fxe:media-type "application/json" ;
    fxe:blank-nodes false .
```

</section>

<section id="InSPARQL">

### In SPARQL

The [SPARQL access](sparql.html) document defines how options are supplied in a `SERVICE` clause,
either in the service IRI (by local name) or as triples with the reserved subject `fx:properties`.

</section>

<section id="AsKeyValue">

### As key-value pairs

Outside RDF, an option MAY be written by its local name, e.g. `media-type=application/json`, as in
command-line arguments or configuration files.

</section>

</section>

<section id="Security">

## Security considerations

`fxe:command` executes a program on the engine host. `fxe:location`, `fxe:query`, and
`fxe:read-from-std-in` may give access to the local file system or process input. An engine exposed
to untrusted requests SHOULD allow these options to be disabled or restricted.

</section>

<section id="Turtle">

## Vocabulary in Turtle

```turtle
@prefix fxe:  <http://sparql.xyz/facade-x/engine/> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .

<http://sparql.xyz/facade-x/engine/> rdfs:label "Façade-X Engine vocabulary" .

fxe:Configuration a rdfs:Class ;
    rdfs:label "Configuration" ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:Option a rdfs:Class ;
    rdfs:label "Option" ;
    rdfs:subClassOf rdf:Property ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

# Source options
fxe:location a rdf:Property, fxe:Option ;
    rdfs:label "location" ;
    rdfs:comment "A URL, or an absolute or relative file-system path, of the resource to be interpreted." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:string ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:content a rdf:Property, fxe:Option ;
    rdfs:label "content" ;
    rdfs:comment "Inline content to be interpreted in place of a located resource. Without fxe:media-type the content is interpreted as plain text." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:string ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:command a rdf:Property, fxe:Option ;
    rdfs:label "command" ;
    rdfs:comment "An external command line whose standard output is interpreted according to fxe:media-type." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:string ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:read-from-std-in a rdf:Property, fxe:Option ;
    rdfs:label "read-from-std-in" ;
    rdfs:comment "Read the content from standard input and use it as the value of fxe:content." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:boolean ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:query a rdf:Property, fxe:Option ;
    rdfs:label "query" ;
    rdfs:comment "Location of a SPARQL query whose result (bindings, graph, or dataset) is used as the source. When set, other options are ignored." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:string ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:from-archive a rdf:Property, fxe:Option ;
    rdfs:label "from-archive" ;
    rdfs:comment "Location of an archive; fxe:location is then resolved as an entry within it." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:string ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:archive-format a rdf:Property, fxe:Option ;
    rdfs:label "archive-format" ;
    rdfs:comment "Format of the archive given in fxe:from-archive (e.g. zip, tar)." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:string ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:media-type a rdf:Property, fxe:Option ;
    rdfs:label "media-type" ;
    rdfs:comment "The media type of the source, selecting the interpretation. Required when it cannot be inferred." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:string ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:charset a rdf:Property, fxe:Option ;
    rdfs:label "charset" ;
    rdfs:comment "The character encoding of the source." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:string ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

# Mapping options
fxe:root a rdf:Property, fxe:Option ;
    rdfs:label "root" ;
    rdfs:comment "IRI of the root container; also the base for minting graph and container IRIs." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:anyURI ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:namespace a rdf:Property, fxe:Option ;
    rdfs:label "namespace" ;
    rdfs:comment "Namespace used to mint string-slot properties and types from source keys and tags." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:anyURI ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:blank-nodes a rdf:Property, fxe:Option ;
    rdfs:label "blank-nodes" ;
    rdfs:comment "Represent containers as blank nodes. When false, container IRIs are minted from fxe:root." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:boolean ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:trim-strings a rdf:Property, fxe:Option ;
    rdfs:label "trim-strings" ;
    rdfs:comment "Trim leading and trailing whitespace from string values." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:boolean ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:null-string a rdf:Property, fxe:Option ;
    rdfs:label "null-string" ;
    rdfs:comment "Omit any triple whose object value would equal the given string." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:string ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:use-rdfs-member a rdf:Property, fxe:Option ;
    rdfs:label "use-rdfs-member" ;
    rdfs:comment "Use rdfs:member in place of rdf:_1, rdf:_2, …" ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:boolean ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:annotate-triples-with-slot-keys a rdf:Property, fxe:Option ;
    rdfs:label "annotate-triples-with-slot-keys" ;
    rdfs:comment "Annotate slot triples with their key using fx:slot-key (RDF 1.2 triple terms)." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:boolean ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:generate-predicate-labels a rdf:Property, fxe:Option ;
    rdfs:label "generate-predicate-labels" ;
    rdfs:comment "Emit rdfs:label for minted properties and types." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:boolean ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:metadata a rdf:Property, fxe:Option ;
    rdfs:label "metadata" ;
    rdfs:comment "Extract resource metadata into the graph xyz:metadata." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:boolean ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .

fxe:audit a rdf:Property, fxe:Option ;
    rdfs:label "audit" ;
    rdfs:comment "Emit an audit graph xyz:audit describing each generated graph." ;
    rdfs:domain fxe:Configuration ;
    rdfs:range xsd:boolean ;
    rdfs:isDefinedBy <http://sparql.xyz/facade-x/engine/> .
```

</section>

<section class="informative" id="References">

## References

<dt id="bib-rdf-schema">[rdf-schema]</dt>
<dd><a href="https://www.w3.org/TR/rdf-schema/">RDF Schema 1.1</a>. Dan Brickley; Ramanathan Guha. W3C. 25 February 2014. W3C Recommendation.</dd>
<dt id="bib-xmlschema-2">[xmlschema-2]</dt>
<dd><a href="https://www.w3.org/TR/xmlschema-2/">XML Schema Part 2: Datatypes Second Edition</a>. Paul V. Biron; Ashok Malhotra. W3C. 28 October 2004. W3C Recommendation.</dd>
<dt id="bib-sparql-anything">[sparql-anything]</dt>
<dd><a href="https://sparql-anything.readthedocs.io/stable/Configuration/">SPARQL Anything — Configuration</a>.</dd>

</section>