<section id="abstract">

This document is a *non-normative primer* for Façade-X. It introduces the model informally —
through motivation and worked examples — to help developers, implementers, and users build an
intuition for how Façade-X represents heterogeneous data as RDF. The precise definitions live in
the companion [Façade-X Concepts and Metamodel](metamodel.html) and
[Façade-X RDF Vocabulary](rdf.html) documents. Wherever this primer and those documents appear to
disagree, the normative documents take precedence.

</section>

<section id="sotd">

This document is currently in active development. It is informative throughout and places no
requirements on implementations.

</section>

<section>

## Issues

<!-- BUILD:ISSUES label="FX Primer" -->

</section>

<section class="informative">

## How to read this document

Façade-X is described normatively in two places: the
[Concepts and Metamodel](metamodel.html) document, which defines the model in first-order logic,
and the [RDF Vocabulary](rdf.html) document, which defines the `fx:` terms that realise it in RDF.
Those documents are precise but deliberately terse. This primer sits alongside them and answers a
different question: *what does Façade-X actually look like, and why is it shaped the way it is?*

The intended audience is threefold:

- **Users** who want to query heterogeneous data and need a mental model of the RDF they will get back.
- **Implementers** building an engine that exposes some format through Façade-X.
- **Contributors** to the Community Group who want the intuition behind the formal constraints.

No prior familiarity with the metamodel is assumed, though a working knowledge of RDF and
[Turtle](https://www.w3.org/TR/turtle/) is helpful.

</section>

<section class="informative">

## The problem Façade-X addresses

Real-world data arrives in many shapes: CSV files, JSON documents and APIs, spreadsheets, XML
feeds, and more. Each format imposes its own structural conventions, and the usual way to bring
such data into a knowledge graph is to write a bespoke, format-specific transformation for every
source. These pipelines are effort-intensive to build and brittle to maintain: a change in the
source shape ripples through hand-written mapping code.

Façade-X takes a different route. Instead of a new mapping language per format, it observes that
the common data formats are all built from the same two structural ingredients — *ordered
sequences* (lists, arrays, rows) and *keyed collections* (maps, objects, records) — holding
*primitive values* at the leaves. If those ingredients are captured once, in a single abstract
model, then any format can be presented *as if* it were RDF, and queried directly with SPARQL,
without a transformation step written in advance.

The rest of this primer shows what that single model is and how a few familiar formats land in it.

</section>

<section class="informative">

## The model in one picture

Façade-X describes every data source with a small, fixed vocabulary of structural primitives.

<figure id="figure">
  <img src="model.png" alt="The Façade-X model: containers holding slots, slots holding values or nested containers" />
  <figcaption>An intuitive overview of the Façade-X model.</figcaption>
</figure>

The pieces are:

- A **Container** is a collection of slots. It is the single abstraction that stands in for both a
  *list* and a *map* — the difference between the two is pushed down into how the slots are keyed.
- A **Slot** is an allotted place inside a container. Each slot holds exactly one thing: either a
  primitive value or a nested container. A slot is keyed either by a *number*
  (a **NumberSlot**, giving list-like, positional access) or by a *string*
  (a **StringSlot**, giving map-like, named access).
- A **Value** is a primitive datum at a leaf — a string, a number, a boolean, and so on.
- A **Type** is an optional classification attached to a container, used when the source format
  names its structures (for example, an XML element name).
- The **Root** is the single top-level container of a data source: the entry point from which
  everything else in that source is reachable.

Two framing terms sit above these. A **Resource** is a digital artifact — a file or a service —
and it *includes* one or more **Data Sources**, the actual collections of data inside it. A CSV
file is a resource that includes one data source (its table); a spreadsheet is a resource that
includes several (one per sheet). Each data source has exactly one Root container.

That is the whole model. Everything below is a matter of showing how ordinary data maps onto these
few pieces.

</section>

<section class="informative">

## A first example: JSON

Consider a small JSON document:

```json
{
  "name": "Alice",
  "age": 30,
  "pets": ["cat", "dog"]
}
```

Read through the Façade-X lens, this is a single data source whose Root is the outer object. That
object is a **Container** with three **StringSlots** — `name`, `age`, and `pets`. The first two
hold **Values**; the third holds a nested **Container** (the array), whose two **NumberSlots** hold
the values `"cat"` and `"dog"` in order.

Realised with the `fx:` vocabulary, the RDF looks like this (in Turtle):

```turtle
@prefix fx:  <http://sparql.xyz/facade-x/ns/> .
@prefix xyz: <http://sparql.xyz/facade-x/data/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

_:root a fx:Root ;
    xyz:name "Alice" ;
    xyz:age  30 ;
    xyz:pets _:pets .

_:pets rdf:_1 "cat" ;
       rdf:_2 "dog" .
```

A few things to notice, each of which is a general rule rather than a detail of this example:

- The Root container carries the type `fx:Root`. There is exactly one such container per data source.
- String keys from the source become **StringSlot** properties minted in the `xyz:` namespace
  (`xyz:name`, `xyz:age`, `xyz:pets`).
- Positional membership in the array is expressed with **NumberSlot** properties `rdf:_1`, `rdf:_2`, …,
  the standard RDF container-membership properties. Order is preserved by these indices.
- Leaves are plain RDF literals; nesting is just another container hanging off a slot.

</section>

<section class="informative">

## A second example: CSV

Tabular data maps just as directly. Take:

```csv
name,age
Alice,30
Bob,25
```

Here the table is the Root container. Its slots are positional — one **NumberSlot** per data row —
and each holds a nested container standing for that row. When the first line is treated as a header,
each row container has **StringSlots** named after the columns:

```turtle
@prefix fx:  <http://sparql.xyz/facade-x/ns/> .
@prefix xyz: <http://sparql.xyz/facade-x/data/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

_:table a fx:Root ;
    rdf:_1 _:row1 ;
    rdf:_2 _:row2 .

_:row1 xyz:name "Alice" ;
       xyz:age  "30" .

_:row2 xyz:name "Bob" ;
       xyz:age  "25" .
```

Note that the CSV values come through as strings (`"30"`, not `30`): CSV carries no datatype
information, so Façade-X reports what the format actually provides rather than guessing. Whether the
header row is interpreted as names or treated as ordinary data is a choice an implementation exposes
to the user; the shape above corresponds to the header-aware reading.

</section>

<section class="informative">

## Mapping intuitions for common formats

The same handful of primitives recur across formats. The table below summarises how familiar
structures land in the model.

<table class="model">
  <tbody>
    <tr>
      <th>Source structure</th>
      <th>Façade-X primitive</th>
      <th>Typical RDF realisation</th>
    </tr>
    <tr>
      <td>Object / map / record</td>
      <td>Container with StringSlots</td>
      <td><code>xyz:</code> key properties on a container</td>
    </tr>
    <tr>
      <td>Array / list / sequence of rows</td>
      <td>Container with NumberSlots</td>
      <td><code>rdf:_1</code>, <code>rdf:_2</code>, … on a container</td>
    </tr>
    <tr>
      <td>Primitive cell / scalar</td>
      <td>Value</td>
      <td>RDF literal</td>
    </tr>
    <tr>
      <td>XML / element tag name</td>
      <td>Type on a container</td>
      <td><code>rdf:type</code> with an <code>xyz:</code> IRI</td>
    </tr>
    <tr>
      <td>Whole document / table / sheet</td>
      <td>Root container of a data source</td>
      <td>a container typed <code>fx:Root</code></td>
    </tr>
  </tbody>
</table>

Where a resource holds more than one data source — the sheets of a spreadsheet, say — each data
source is kept in its own [named graph](rdf.html#NamedGraphs), so several sources can share one RDF
dataset without their containers being confused for one another.

</section>

<section class="informative">

## Why the constraints matter

The metamodel states several structural constraints that can look like formalities at first glance.
Read through the primer's lens they each earn their place, because together they guarantee that
*every* data source maps to a predictable, tree-shaped RDF structure with a single entry point —
which is exactly what lets a generic engine translate any format uniformly and lets query authors
rely on a stable shape.

- **A single Root per data source** gives every source one well-defined entry point. A query can
  always start from `?root a fx:Root` without knowing anything else about the format.
- **Each container belongs to exactly one data source.** Containers are never shared across sources,
  so the boundaries between two files sheets stay crisp. 
- **The primitives are pairwise disjoint** — nothing is both a container and a value, or a slot and
  a type. This restricts the types of SPARQL basic graph patterns that have a solution on such a graph.
- **The containment hierarchy is acyclic**: no container can contain itself, directly or through a
  chain of slots and containers. This constraint (discussed in
  [issue #13](https://github.com/w3c-facade-x/facade-x-specs/issues/13)) reflects the fact that the
  source formats being modelled — JSON, XML, CSV trees — are themselves finite and non-recursive in
  structure. Its practical payoff is that traversing or materialising a façade always terminates,
  and the RDF produced for a source is finite and tree-like.

None of these are restrictions the user has to think about; they are properties the model provides,
and the reason the mapping from *any* supported format is well-defined.

</section>

<section class="informative">

## Querying Façade-X data

A façade need not be produced as a file before it can be queried. In the reference implementation,
[SPARQL Anything](https://sparql-anything.cc/), the façade of a source is exposed *inside a query*
through a magic `SERVICE` clause whose IRI uses the `x-sparql-anything:` protocol. The engine
intercepts that clause, builds the Façade-X representation of the resource named there, and
evaluates the enclosed graph pattern against it — so an ordinary SPARQL 1.1 query reads the source
directly, with no prior transformation step.

Options are passed to the engine as triples inside the `SERVICE` block: the special subject
`fx:properties` carries one `fx:`-prefixed option per triple, the only mandatory one being the
source `fx:location` (a URL or file path). Returning to the JSON example, this query lists each pet
together with the owner's name:

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

The pattern starts from the Root, reads the `name` value, and follows the `pets` slot to the nested
container. Rather than enumerate that container's numeric slots by hand (`rdf:_1`, `rdf:_2`, …), it
uses the magic property `fx:anySlot`, which matches any of a container's membership slots at once —
collecting the values `"cat"` and `"dog"` with a single pattern.

The same options may equivalently be written inline in the protocol IRI, so
`SERVICE <x-sparql-anything:location=people.json>` is shorthand for the `fx:location` triple above;
further options (`fx:media-type`, `fx:namespace`, format-specific settings, and so on) are supplied
the same way. Nothing in the graph pattern is specific to JSON: point the same `SERVICE` clause at a
CSV file, an XML document, or a spreadsheet and the identical query shape applies, because every
source presents the same Façade-X primitives.

</section>

<section class="informative">

## Where to go next

- The [Façade-X Concepts and Metamodel](metamodel.html) document gives the precise, first-order
  definitions of the concepts introduced informally here.
- The [Façade-X RDF Vocabulary](rdf.html) document specifies every `fx:` term, its RDF Schema
  characterisation, and the use of named graphs.
- Discussion of open questions happens in the project's
  [issue tracker](https://github.com/w3c-facade-x/facade-x-specs/issues).

</section>
