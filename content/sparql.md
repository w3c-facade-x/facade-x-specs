<section id="abstract">

This document specifies how a Façade-X view of a heterogeneous resource is accessed from within a
SPARQL query. It defines the `SERVICE` clause and IRI scheme through which an engine is asked to
build the Façade-X representation of a resource, the *options* (properties) that control how the
resource is interpreted, and the *magic properties* that support querying the resulting containers.
It is a companion to the [Façade-X Concepts and Metamodel](metamodel.html) and
[Façade-X RDF Vocabulary](rdf.html) documents: the former defines the model, the latter its RDF
terms, and this document defines how that RDF is obtained and queried in SPARQL.

</section>

<section id="sotd">

This document is currently in active development. The mechanism described here is the one provided
by the reference implementation, [SPARQL Anything](https://sparql-anything.cc/); the naming of the
IRI scheme in particular is expected to be revisited before standardisation (see the
[Issues](#Issues) section).

</section>

<section class="informative" id="Introduction">

## Introduction

The [metamodel](metamodel.html) and [RDF vocabulary](rdf.html) documents describe *what* a Façade-X
view of a resource is: a single root container, holding slots keyed by number or string, whose
values are literals or further containers. This document describes *how* a SPARQL query obtains and
queries such a view.

The mechanism is a *magic* `SERVICE` clause. Rather than materialising the Façade-X RDF of a
resource ahead of time, a query names the resource inside a `SERVICE` block whose IRI carries a
reserved scheme. A conforming engine intercepts that clause, produces the Façade-X representation of
the named resource according to the [metamodel](metamodel.html) and [RDF vocabulary](rdf.html), and
evaluates the enclosed graph pattern against it. The resource is thus queried in place, as ordinary
RDF, with no separate transformation step.

<section id="Namespaces">
<h3 id="h-namespaces" resource="#h-namespaces">Namespaces</h3>
<table class="model">
  <tbody>
    <tr>
      <th>Prefix</th>
      <th>Namespace</th>
      <th>Description</th>
    </tr>
    <tr>
      <td>fx</td>
      <td>http://sparql.xyz/facade-x/ns/</td>
      <td>The Façade-X vocabulary, including the option and magic properties defined here</td>
    </tr>
    <tr>
      <td>xyz</td>
      <td>http://sparql.xyz/facade-x/data/</td>
      <td>The default namespace for properties and classes derived from source data</td>
    </tr>
    <tr>
      <td>rdf</td>
      <td>http://www.w3.org/1999/02/22-rdf-syntax-ns#</td>
      <td>Used for container-membership properties (<code>rdf:_1</code>, <code>rdf:_2</code>, …)</td>
    </tr>
  </tbody>
</table>
</section>

</section>

<section>

## Issues

<p class="issue" data-number="24"></p>

The reserved IRI scheme is currently `x-sparql-anything:`, the scheme used by the reference
implementation. A vendor-neutral scheme name is expected to be chosen before this document reaches
Recommendation status; until then, the implementation-specific scheme is used throughout.

This document types the root container `fx:Root`, in agreement with the
[RDF vocabulary](rdf.html#Root) document. Some implementations currently emit the lowercase
`fx:root`; the casing is to be reconciled across the specifications and implementations.

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

1. determine the resource and interpretation from the options provided (see
   [Providing options](#Options)), where exactly one *source* option — `fx:location`, `fx:content`,
   or `fx:command` — MUST be given;
2. construct the Façade-X representation of that resource as defined by the
   [metamodel](metamodel.html) and realised by the [RDF vocabulary](rdf.html); and
3. evaluate the enclosed group graph pattern against that representation, returning solutions as for
   any other `SERVICE` invocation.

The resulting representation is a single Façade-X data source: one container typed
[`fx:Root`](rdf.html#Root), reachable from which are its slots, values, and nested containers. Where
a resource yields more than one data source, each is produced in its own named graph, as described
in [Named Graphs](rdf.html#NamedGraphs).

</section>

<section id="Options">

## Providing options

Options are supplied to the engine in either of two modalities, which MAY be combined.

<section id="OptionsInIRI">

### Options in the service IRI

Options may be written in the `SERVICE` IRI itself, after the scheme, as a comma-separated list of
`name=value` pairs:

```example
SERVICE <x-sparql-anything:location=https://example.org/people.json,media-type=application/json> {
  ?root a fx:Root ; xyz:name ?name .
}
```

As a shorthand, a service IRI consisting of the scheme followed by a single argument with no
`name=value` form treats that argument as the source `fx:location` (or `fx:content`):

```example
SERVICE <x-sparql-anything:https://example.org/people.json> {
  ?root a fx:Root ; xyz:name ?name .
}
```

</section>

<section id="OptionsAsTriples">

### Options as triples

Options may instead be given as triples inside the `SERVICE` block. Such triples MUST have the
reserved resource `fx:properties` as subject, an option property `fx:[NAME]` as predicate, and a
literal or a variable as object:

```example
SERVICE <x-sparql-anything:> {
  fx:properties fx:location   "https://example.org/people.json" ;
                fx:media-type "application/json" .
  ?root a fx:Root ; xyz:name ?name .
}
```

Using a variable as the object of an option triple allows the option value to be bound elsewhere in
the query, for example from another `SERVICE` clause or from the enclosing query's bindings.

</section>

<section id="OptionsPrecedence">

### Combining and precedence

The two modalities MAY be mixed within a single `SERVICE` clause; options given as triples take
precedence over options of the same name given in the IRI. An implementation MAY additionally accept
options from outside the query (for example, a command-line default); such external options are
overridden by options given in the IRI, which are in turn overridden by options given as triples.

</section>

</section>

<section id="SourceOptions">

## Source options

Exactly one source option MUST be provided. It identifies the resource whose Façade-X view is to be
queried.

<table class="model">
  <tbody>
    <tr>
      <th>Option</th>
      <th>Value</th>
      <th>Description</th>
    </tr>
    <tr>
      <td>fx:location</td>
      <td>A URL, or an absolute or relative file-system path</td>
      <td>The resource to be interpreted as a Façade-X data source.</td>
    </tr>
    <tr>
      <td>fx:content</td>
      <td>A literal</td>
      <td>Inline content to be interpreted directly, in place of a located resource.</td>
    </tr>
    <tr>
      <td>fx:command</td>
      <td>A literal</td>
      <td>An external command line whose standard output is interpreted, according to <code>fx:media-type</code>.</td>
    </tr>
  </tbody>
</table>

</section>

<section id="InterpretationOptions">

## Interpretation options

The following options control how the source is mapped onto the Façade-X model. All are optional.

<table class="model">
  <tbody>
    <tr>
      <th>Option</th>
      <th>Value</th>
      <th>Default</th>
      <th>Description</th>
    </tr>
    <tr>
      <td>fx:media-type</td>
      <td>A media type</td>
      <td>Inferred from the file extension</td>
      <td>The media type of the source, selecting how it is interpreted. Required when it cannot be inferred (e.g. for <code>fx:content</code> or <code>fx:command</code>).</td>
    </tr>
    <tr>
      <td>fx:namespace</td>
      <td>An IRI</td>
      <td>http://sparql.xyz/facade-x/data/</td>
      <td>The namespace used to mint properties (string slots) and classes (types) from source keys and tags.</td>
    </tr>
    <tr>
      <td>fx:blank-nodes</td>
      <td>true | false</td>
      <td>true</td>
      <td>Whether containers are represented as blank nodes. When <code>false</code>, containers are given minted IRIs derived from <code>fx:root</code>.</td>
    </tr>
    <tr>
      <td>fx:root</td>
      <td>An IRI</td>
      <td>Derived from the source</td>
      <td>The IRI of the root container, also used as the base for minting graph and container IRIs. Defaults to the location, or to a hash of the content or command.</td>
    </tr>
    <tr>
      <td>fx:trim-strings</td>
      <td>true | false</td>
      <td>false</td>
      <td>Trim leading and trailing whitespace from string values.</td>
    </tr>
    <tr>
      <td>fx:null-string</td>
      <td>A literal</td>
      <td>—</td>
      <td>Suppress any triple whose object value would equal the given string.</td>
    </tr>
    <tr>
      <td>fx:use-rdfs-member</td>
      <td>true | false</td>
      <td>false</td>
      <td>Use the property <code>rdfs:member</code> in place of the numbered container-membership properties <code>rdf:_1</code>, <code>rdf:_2</code>, …</td>
    </tr>
  </tbody>
</table>

Formats define further, format-specific options (for example CSV delimiters and header handling, or
JSON and XML path expressions). These are defined alongside each format and are out of scope for
this document.

</section>

<section id="ExecutionOptions">

## Execution options

The following options affect how the representation is built and evaluated, but not the mapping
itself. All are optional.

<table class="model">
  <tbody>
    <tr>
      <th>Option</th>
      <th>Value</th>
      <th>Description</th>
    </tr>
    <tr>
      <td>fx:strategy</td>
      <td>0 | 1</td>
      <td>Triplification strategy: <code>0</code> materialises all triples; <code>1</code> materialises only triples that can match a pattern in the query.</td>
    </tr>
    <tr>
      <td>fx:ondisk</td>
      <td>A directory path</td>
      <td>Use an on-disk graph stored at the given directory, allowing very large sources to be processed without exhausting memory.</td>
    </tr>
    <tr>
      <td>fx:ondisk.reuse</td>
      <td>true | false</td>
      <td>When an on-disk graph is used, reuse a previously created one rather than rebuilding it.</td>
    </tr>
    <tr>
      <td>fx:slice</td>
      <td>true | false</td>
      <td>Process the source in slices, evaluating the graph pattern against each slice in turn, so that large sources can be streamed.</td>
    </tr>
    <tr>
      <td>fx:audit</td>
      <td>true | false</td>
      <td>Emit an additional auditing graph (<code>&lt;http://sparql.xyz/facade-x/data/audit&gt;</code>) describing the triplification.</td>
    </tr>
  </tbody>
</table>

</section>

<section id="MagicProperties">

## Magic properties

Beyond the terms defined by the [RDF vocabulary](rdf.html), an engine recognises a small number of
*magic properties* within a Façade-X `SERVICE` block. These are not asserted triples but query-time
constructs the engine evaluates specially.

<section class="term" id="anySlot">
<h3 id="h-anySlot">fx:anySlot</h3>

The property `fx:anySlot` matches any container-membership slot of a container. A triple pattern
`?c fx:anySlot ?v` binds `?v` to each value held by a numbered slot (`rdf:_1`, `rdf:_2`, …) of the
container `?c`, regardless of its position. It lets a query traverse the members of a container
without enumerating their indices.

```example
PREFIX fx:  <http://sparql.xyz/facade-x/ns/>
PREFIX xyz: <http://sparql.xyz/facade-x/data/>

SELECT ?name ?pet WHERE {
  SERVICE <x-sparql-anything:> {
    fx:properties fx:location "people.json" .
    ?root a fx:Root ;
          xyz:name ?name ;
          xyz:pets ?pets .
    ?pets fx:anySlot ?pet .
  }
}
```

</section>

Engines additionally provide functions over container-membership properties — for example
`fx:cardinal(?p)`, which returns the numeric index of a membership property, and `fx:before(?a, ?b)`
and `fx:after(?a, ?b)`, which compare the order of two membership properties. A fuller library of
helper functions is provided by implementations and is out of scope for this document.

</section>

<section class="informative" id="Examples">

## Examples

Interpreting an inline JSON literal, with the media type stated explicitly because it cannot be
inferred from a file extension:

```example
PREFIX fx:  <http://sparql.xyz/facade-x/ns/>
PREFIX xyz: <http://sparql.xyz/facade-x/data/>

SELECT ?name ?surname WHERE {
  SERVICE <x-sparql-anything:> {
    fx:properties fx:content    "{\"name\":\"Vincent\",\"surname\":\"Vega\"}" ;
                  fx:media-type "application/json" .
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
PREFIX xyz: <http://sparql.xyz/facade-x/data/>

CONSTRUCT { ?s ?p ?o } WHERE {
  SERVICE <x-sparql-anything:location=https://example.org/people.json> {
    fx:properties fx:blank-nodes false .
    ?s ?p ?o .
  }
}
```

</section>

<section class="informative" id="References">

## References

- [Façade-X Concepts and Metamodel](metamodel.html) — the model this document provides access to.
- [Façade-X RDF Vocabulary](rdf.html) — the RDF terms produced for a Façade-X data source.
- [SPARQL Anything](https://sparql-anything.cc/) — the reference implementation of the mechanism
  specified here.

</section>
