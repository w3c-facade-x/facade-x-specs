---
title: <code>Façade-X</code> Data Access in SPARQL
subtitle: Accessing heterogeneous resources as Façade-X through the SPARQL <code>SERVICE</code> clause.
order: 5
---

<section id="abstract">

This document specifies how a Façade-X view of a heterogeneous resource is accessed from within a
SPARQL query. It defines the `SERVICE` clause and IRI scheme through which an engine is asked to
build the Façade-X representation of a resource, how options from the
[Engine vocabulary](engine.html) are supplied to it, and how the members of the resulting
containers are queried. It is a companion to the [Façade-X Concepts and Metamodel](metamodel.html),
[Façade-X Schema Vocabulary](schema.html), and [Façade-X Engine Vocabulary](engine.html) documents.

</section>

<section id="sotd">

This document is currently in active development. The mechanism described here is the one provided
by the reference implementation, [SPARQL Anything](https://sparql-anything.cc/); the naming of the
IRI scheme in particular is expected to be revisited before standardisation (see the
[Issues](#Issues) section).

</section>

<section class="informative" id="Introduction">

## Introduction

The [metamodel](metamodel.html) and [Schema vocabulary](schema.html) documents describe *what* a
Façade-X view of a resource is: a single root container, holding slots keyed by number or string,
whose values are literals or further containers. The [Engine vocabulary](engine.html) names the
options that control how an engine builds that view. This document describes *how* a SPARQL query
obtains and queries it.

The mechanism is a *magic* `SERVICE` clause. Rather than materialising the Façade-X RDF of a
resource ahead of time, a query names the resource inside a `SERVICE` block whose IRI carries a
reserved scheme. A conforming engine intercepts that clause, produces the Façade-X representation of
the named resource, and evaluates the enclosed graph pattern against it. The resource is thus
queried in place, as ordinary RDF, with no separate transformation step.

<section id="Namespaces">

### Namespaces

| Prefix | Namespace | Description |
|---|---|---|
| fx | `http://sparql.xyz/facade-x/ns/` | The [Schema vocabulary](schema.html), and the reserved term `fx:properties` defined here |
| fxe | `http://sparql.xyz/facade-x/engine/` | The [Engine vocabulary](engine.html) |
| xyz | `http://sparql.xyz/facade-x/data/` | The default namespace for properties and classes derived from source data |
| rdf | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` | Container-membership properties (`rdf:_1`, `rdf:_2`, …) |
| rdfs | `http://www.w3.org/2000/01/rdf-schema#` | `rdfs:member` |

</section>

</section>

<section>

## Issues

<!-- BUILD:ISSUES label="FX access in SPARQL" -->

The reserved IRI scheme is currently `x-sparql-anything:`, the scheme used by the reference
implementation. A vendor-neutral scheme name is expected to be chosen before this document reaches
Recommendation status; until then, the implementation-specific scheme is used throughout.

This document types the root container `fx:Root`, in agreement with the
[Schema vocabulary](schema.html#Root) document. Some implementations currently emit the lowercase
`fx:root`; the casing is to be reconciled across the specifications and implementations.

Options given as triples use Engine vocabulary terms (`fxe:location`). The reference implementation
uses the Schema namespace (`fx:location`); see the [Engine vocabulary](engine.html) issues.

</section>

<section id="ServiceClause">

## The Façade-X `SERVICE` clause

A Façade-X view is requested through a SPARQL `SERVICE` block whose IRI uses the reserved scheme
`x-sparql-anything:`. The general form is:

```example
SERVICE <x-sparql-anything:[OPTIONS]> {
  [GROUP GRAPH PATTERN]
}
```

An engine that conforms to this specification MUST, on encountering a `SERVICE` block whose IRI uses
the `x-sparql-anything:` scheme:

1. collect the options given in the `SERVICE` clause (see [Providing options](#Options)) and
   interpret them as defined by the [Engine vocabulary](engine.html), which requires exactly one
   [source option](engine.html#SourceOptions);
2. construct the Façade-X representation of the resource as defined by the
   [metamodel](metamodel.html) and realised by the [Schema vocabulary](schema.html); and
3. evaluate the enclosed group graph pattern against that representation, returning solutions as for
   any other `SERVICE` invocation.

The resulting representation is a single Façade-X data source: one container typed
[`fx:Root`](schema.html#Root), reachable from which are its slots, values, and nested containers.
Where a resource yields more than one data source, each is produced in its own named graph, as
described in [Named Graphs](schema.html#NamedGraphs).

An engine MAY support options beyond those defined in the Engine vocabulary. An engine MUST NOT
return different solutions for an operation because of an option it does not support, other than by
raising an error.

</section>

<section id="Options">

## Providing options

Options are supplied to the engine in either of two modalities, which MAY be combined.

<section id="OptionsInIRI">

### Options in the service IRI

Options may be written in the `SERVICE` IRI itself, after the scheme, as a comma-separated list of
`name=value` pairs, where `name` is the local name of an Engine vocabulary term:

```example
SERVICE <x-sparql-anything:location=https://example.org/people.json,media-type=application/json> {
  ?root a fx:Root ; xyz:name ?name .
}
```

As a shorthand, a service IRI consisting of the scheme followed by a single argument with no
`name=value` form treats that argument as the value of `fxe:location`:

```example
SERVICE <x-sparql-anything:https://example.org/people.json> {
  ?root a fx:Root ; xyz:name ?name .
}
```

</section>

<section id="OptionsAsTriples">

### Options as triples

Options may instead be given as triples inside the `SERVICE` block. Such triples MUST have the
reserved resource [`fx:properties`](#properties) as subject, an Engine vocabulary term as predicate,
and a literal or a variable as object:

```example
SERVICE <x-sparql-anything:> {
  fx:properties fxe:location   "https://example.org/people.json" ;
                fxe:media-type "application/json" .
  ?root a fx:Root ; xyz:name ?name .
}
```

Using a variable as the object of an option triple allows the option value to be bound elsewhere in
the query, for example from another `SERVICE` clause or from the enclosing query's bindings.

Option triples configure the engine. They are not matched against the Façade-X representation.

</section>

<section id="OptionsPrecedence">

### Combining and precedence

The two modalities MAY be mixed within a single `SERVICE` clause; options given as triples take
precedence over options of the same name given in the IRI. An implementation MAY additionally accept
options from outside the query (for example, a command-line default); such external options are
overridden by options given in the IRI, which are in turn overridden by options given as triples.

</section>

<section class="term" id="properties">
<h3 id="h-properties">fx:properties</h3>

The reserved resource `fx:properties` identifies the engine configuration of the enclosing
`SERVICE` clause. It is only meaningful as the subject of an option triple.

</section>

</section>

<section id="ContainerMembers">

## Querying container members

A triple pattern with `rdfs:member` as predicate matches any numbered slot of a container. The
pattern `?c rdfs:member ?v` binds `?v` to each value held by a slot `rdf:_1`, `rdf:_2`, … of the
container `?c`, regardless of its position. This lets a query traverse the members of a container
without enumerating their indices.

An engine MUST evaluate `rdfs:member` in this way within a Façade-X `SERVICE` block, whether or not
`rdfs:member` triples are materialised (see [`fxe:use-rdfs-member`](engine.html#use-rdfs-member)).
The result is the same as under RDFS entailment, where every container-membership property is a
sub-property of `rdfs:member`.

```example
PREFIX fx:   <http://sparql.xyz/facade-x/ns/>
PREFIX fxe:  <http://sparql.xyz/facade-x/engine/>
PREFIX xyz:  <http://sparql.xyz/facade-x/data/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?name ?pet WHERE {
  SERVICE <x-sparql-anything:> {
    fx:properties fxe:location "people.json" .
    ?root a fx:Root ;
          xyz:name ?name ;
          xyz:pets ?pets .
    ?pets rdfs:member ?pet .
  }
}
```

The reference implementation provides the same behaviour through the magic property `fx:anySlot`.
An engine MAY accept `fx:anySlot` as a synonym of `rdfs:member`.

Functions over container-membership properties, such as retrieving the index of a slot or comparing
the order of two slots, are provided by implementations. Their standardisation is discussed in
[issue #18](https://github.com/w3c-facade-x/facade-x-specs/issues/18).

</section>

<section class="informative" id="Examples">

## Examples

Interpreting an inline JSON literal, with the media type stated explicitly because it cannot be
inferred from a file extension:

```example
PREFIX fx:  <http://sparql.xyz/facade-x/ns/>
PREFIX fxe: <http://sparql.xyz/facade-x/engine/>
PREFIX xyz: <http://sparql.xyz/facade-x/data/>

SELECT ?name ?surname WHERE {
  SERVICE <x-sparql-anything:> {
    fx:properties fxe:content    "{\"name\":\"Vincent\",\"surname\":\"Vega\"}" ;
                  fxe:media-type "application/json" .
    ?root a fx:Root ;
          xyz:name    ?name ;
          xyz:surname ?surname .
  }
}
```

Requesting minted IRIs instead of blank nodes for containers, using the IRI modality for the source
and a triple for the remaining option:

```example
PREFIX fx:  <http://sparql.xyz/facade-x/ns/>
PREFIX fxe: <http://sparql.xyz/facade-x/engine/>

CONSTRUCT { ?s ?p ?o } WHERE {
  SERVICE <x-sparql-anything:location=https://example.org/people.json> {
    fx:properties fxe:blank-nodes false .
    ?s ?p ?o .
  }
}
```

</section>

<section class="informative" id="References">

## References

- [Façade-X Concepts and Metamodel](metamodel.html) — the model this document provides access to.
- [Façade-X Schema Vocabulary](schema.html) — the RDF terms produced for a Façade-X data source.
- [Façade-X Engine Vocabulary](engine.html) — the options accepted by an engine.
- [RDF Schema 1.1](https://www.w3.org/TR/rdf-schema/) — `rdfs:member` and container-membership properties.
- [SPARQL Anything](https://sparql-anything.cc/) — the reference implementation of the mechanism
  specified here.

</section>