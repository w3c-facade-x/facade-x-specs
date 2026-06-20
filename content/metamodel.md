<section id="abstract">

This document specifies the Fa&ccedil;ade-X concepts and metamodel.

</section>

<section id="sotd">

This document is currently in active development.

</section>

<section class="informative">

## Introduction

Fa&ccedil;ade-X is the (meta-)model resulting from the abstraction of all the basic data structures used to
represent source data formats, combined into a unified model.
RDF languages can implement it to provide users direct access to external, heterogeneus data formats.
The Figure below provide an intuive overview of Fa&ccedil;ade-X.
The related RDF vocabulary is [under preparation].

<figure id="figure">
  <img src="model.png" alt="Facade-X model" />
  <figcaption>A diagram of the Fa&ccedil;ade-X model</figcaption>
</figure>

</section>

<section>

## Issues

<p class="issue" data-number="1"></p>
<!-- <p class="issue" data-number="2"></p> -->
<p class="issue" data-number="3"></p>
<p class="issue" data-number="12"></p>
<p class="issue" data-number="13"></p>
<!-- Issue can automatically be populated from GitHub -->

</section>

<section id="resources_datasources">

## Resources and Data Sources

We rely on the generic notion of *resource* to refer to a digital artifact that wraps some data (to not be
confused with the concept of Resource in RDFS).
We say that a resource contains one or more *data sources*, to refer to actual data contained in them.

Intuitively, a CSV is a file (then, a resource) that includes some tabular data (hence, a single data source).
A Spreadsheet is a file (then, a resource) containing many tabs, each one of them including tabular data
(hence, possibly multiple data sources).

**Predicate Definition**
`Resource(x)` denotes a digital artifact (e.g., a file or service).
`DataSource(x)` denotes a collection of data contained in a resource.
`includes(r, ds)` means that resource `r` contains data source `ds`.

Every resource must contain at least one data source.

```math
\forall r . \exists ds.  \mathrm{Resource}(r) \Rightarrow   \mathrm{includes}(r, ds) 
```

The first argument of the includes predicate is a resource and the second is a data source.

```math
\forall r, ds .  \mathrm{includes}(r, ds) \Rightarrow \mathrm{Resource}(r) \wedge \mathrm{DataSource}(ds) 
```

Every data source must belong to some resource.

```math
\forall ds.  \exists r. \mathrm{DataSource}(ds) \Rightarrow  \mathrm{includes}(r, ds) \wedge \mathrm{Resource}(r)  
```

A data source cannot belong to two different resources; it is included in one at most.

```math
\forall ds, r_1, r_2 .  \mathrm{includes}(r_1, ds) \wedge \mathrm{includes}(r_2, ds) \Rightarrow r_1 = r_2
```

</section>

<section>

## Containers, Slots, and Values

The framework introduces the notion of *Container* as an abstraction of both lists and maps through the
notion of *Slots*.
A *Slot* is an allotted place for an object, namely a primitive value or another container,
*&ldquo;contained&rdquo;* in a *Container*.

Containers are collections of unique key/value pairs (slots) where:
the key of the slot is unique in the collection and can be either a number (i.e. `NumberSlot`)
or a sequence of alphanumeric characters (i.e. `StringSlot`);
the value can be either a primitive value or another container.

We say that a container `c` *contains* a slot `s` if
`(c,s)` is in the interpretation of the predicate
`hasSlot`.
Moreover, we say that a slot `s` *holds* a value
`v` (or a container `c`) if
`(s,v)` (resp. `(s,c)`) is in the interpretation of
`hasValue` (resp. `hasContainer`).
In this case we can also say that `v` (resp. `c`) is assigned to a slot.

Finally, we say that a container $c$ *recursively contains* a container
$c'$ if there exists a sequence
$s_0,\ldots,s_n$ and containers
$c_1,\ldots,c_n$ such that
$(c,s_0),(c_1,s_1)\ldots(c_n,s_n)$ is in the
interpretation of
`hasSlot` and
$(s_0,c_1),(s_1,c_2),\ldots,(s_n,c')$ is in the
interpretation of
`hasContainer`.

**Predicate Definition**
`Container(x)` represents a collection of slots (list or map).
`Slot(x)` is an allotted place for an object within a container.
`NumberSlot(x)` and `StringSlot(x)` identify the type of the slot.
`Value(x)` denotes a primitive datum.
`hasSlot(c,s)` links a container to a slot.
`hasValue(s,v)` links a slot to a value.
`hasContainer(s,c)` links a slot to a nested container.
`includesContainer(ds,c)` associates a data source with its containers.

The first argument of hasSlot is a Container and the second is a Slot.

```math
\forall c, s.  \mathrm{hasSlot}(c, s) \Rightarrow \mathrm{Container}(c) \wedge \mathrm{Slot}(s)
```

The first argument of hasValue is a slot and the second is a value.

```math
\forall s, v.  \mathrm{hasValue}(s, v) \Rightarrow \mathrm{Slot}(s) \wedge \mathrm{Value}(v) 
```

The first argument of hasContainer is a slot and the second is a container.

```math
\forall s, c .  \mathrm{hasContainer}(s, c) \Rightarrow \mathrm{Slot}(s) \wedge \mathrm{Container}(c) 
```

The first argument of includesContainer is a data source and the second is a container.

```math
\forall ds, c .  \mathrm{includesContainer}(ds, c) \Rightarrow \mathrm{DataSource}(ds) \wedge \mathrm{Container}(c) 
```

Every NumberSlot is a slot.

```math
\forall s .  \mathrm{NumberSlot}(s) \Rightarrow \mathrm{Slot}(s) 
```

Every StringSlot is a slot.

```math
\forall s . \mathrm{StringSlot}(s) \Rightarrow \mathrm{Slot}(s)
```

A slot identified by a string cannot also be a NumberSlot.

```math
\forall s . \mathrm{StringSlot}(s) \Rightarrow \neg \mathrm{NumberSlot}(s) 
```

Every slot must be either a NumberSlot or a StringSlot.

```math
\forall s .  \mathrm{Slot}(s) \Rightarrow \mathrm{NumberSlot}(s) \vee \mathrm{StringSlot}(s) 
```

```math
\nexists s. \mathrm{NumberSlot}(s) \wedge \mathrm{StringSlot}(s) 
```

Every container must belong to some data source.

```math
\forall c . \exists ds .   \mathrm{Container}(c) \Rightarrow  \mathrm{includesContainer}(ds, c) \wedge \mathrm{DataSource}(ds) 
```

A container cannot belong to more than one data source.

```math
\forall c, ds_1, ds_2 .  \mathrm{includesContainer}(ds_1, c) \wedge \mathrm{includesContainer}(ds_2, c) \Rightarrow ds_1 = ds_2 
```

</section>

<section>

## Properties of Slots

Values must be assigned to a slot.
Slots must be contained by a single container.
Slots must hold either a single container or a single value.
There cannot exist a container c and a slot s such that c contains s and s holds c.
Each container cannot recursively contain itself through a sequence of slots and containers.

Every value must be assigned to some slot.

```math
\forall v . \exists s . \mathrm{Value}(v) \Rightarrow \mathrm{hasValue}(s, v)
```

Every slot must be contained in some container.

```math
\forall s . \exists c.  \mathrm{Slot}(s) \Rightarrow   \mathrm{hasSlot}(c, s) 
```

Each slot belongs to exactly one container.

```math
\forall s, c_1, c_2 .  \mathrm{hasSlot}(c_1, s) \wedge \mathrm{hasSlot}(c_2, s) \Rightarrow c_1 = c_2
```

Every slot must hold either a container or a value.

```math
\forall s . \exists x. \mathrm{Slot}(s) \Rightarrow  \mathrm{hasContainer}(s, x)  \vee  \mathrm{hasValue}(s, x) 
```

A slot cannot simultaneously hold a container and a value.

```math
\forall s, x . \mathrm{hasContainer}(s, x) \Rightarrow \neg \mathrm{hasValue}(s, x)
```

A slot can hold at most one container.

```math
\forall s, c_1, c_2 . \mathrm{hasContainer}(s, c_1) \wedge \mathrm{hasContainer}(s, c_2) \Rightarrow c_1 = c_2 
```

A slot can hold at most one value.

```math
\forall s, v_1, v_2 . \mathrm{hasValue}(s, v_1) \wedge \mathrm{hasValue}(s, v_2) \Rightarrow v_1 = v_2 
```

A container cannot directly contain itself via one of its slots.

```math
\forall c, s . \mathrm{hasSlot}(c, s) \Rightarrow \neg \mathrm{hasContainer}(s, c) 
```

No container may (even indirectly) contain itself, namely, the containment graph is acyclic.

```math
\neg \exists c, s_1,\ldots,s_n, c_1,\ldots,c_n .
  \mathrm{hasSlot}(c, s_1) \wedge \mathrm{hasContainer}(s_1, c_1) \wedge \ldots \wedge \mathrm{hasSlot}(c_{n-1}, s_n) \wedge \mathrm{hasContainer}(s_n, c)
```

Each container can only be held by a single slot (it is not possible for two slots to hold the same container).

```math
\forall c, s_1, s_2. \mathrm{hasSlot}(s_1,c) \wedge \mathrm{hasSlot}(s_2, c) \Rightarrow s_1 = s_2
```

</section>

<section>

## Types

Containers can have types.
Every type must be assigned to a container.
To this end we introduce the unary predicate `Type` and the binary predicate `hasType`.

**Predicate Definition**
`Type(x)` denotes a classification assigned to containers.
`hasType(c,t)` links a container to a type.

The first argument of hasType is a container and the second is a type.

```math
\forall c, t  . \mathrm{hasType}(c, t) \Rightarrow \mathrm{Container}(c) \wedge \mathrm{Type}(t) 
```

Every type must be assigned to at least one container.

```math
\forall t . \exists c . \mathrm{Type}(t) \Rightarrow  \mathrm{hasType}(c, t) 
```

</section>

<section>

## Root Container

For each data source, there exists one and only one Root container.
The Root container cannot be assigned to a slot.
Containers that are not root must be assigned to a slot.
To identify the root container we introduce the unary predicate `Root` as a specialisation of Container
and the binary predicate `hasRoot` that connects a data source to its root container.

**Predicate Definition**
For each data source there is a distinguished top-level container, the root.
The root is the entry point of the container hierarchy and cannot be nested in any slot.
All other containers must be reachable from it.

Every data source must have at least one root container.

```math
\forall ds . \exists r . \mathrm{DataSource}(ds) \Rightarrow  \mathrm{hasRoot}(ds, r) 
```

The first argument of hasRoot is a data source and the second is a root.

```math
\forall ds, r . \mathrm{hasRoot}(ds, r) \Rightarrow \mathrm{DataSource}(ds) \wedge \mathrm{Root}(r) 
```

Every root container is the root of some data source.

```math
\forall r . \exists ds . \mathrm{Root}(r) \Rightarrow  \mathrm{hasRoot}(ds, r) 
```

The root container of a data source is included in that data source.

```math
\forall ds, r . \mathrm{hasRoot}(ds, r) \Rightarrow \mathrm{includesContainer}(ds, r) 
```

Every root is also a container.

```math
\forall x . \mathrm{Root}(x) \Rightarrow \mathrm{Container}(x) 
```

A root container cannot be nested inside any slot.

```math
\forall r, s . \mathrm{Root}(r) \Rightarrow \neg \mathrm{hasContainer}(s, r) 
```

Each data source cannot have more than one root container.

```math
\forall ds, r_1, r_2 . \mathrm{hasRoot}(ds, r_1) \wedge \mathrm{hasRoot}(ds, r_2) \Rightarrow r_1 = r_2 
```

Every non-root container must be contained in some slot.

```math
\forall c . \exists s . \mathrm{Container}(c) \wedge \neg \mathrm{Root}(c) \Rightarrow \mathrm{hasContainer}(s, c) 
```

</section>

<section>

## Disjointness

The unary predicates Container, Slot, Value, and Type are pairwise disjoint.
The unary predicates DataSource and Resource are disjoint from Container, Slot, Value, and Type.
The unary predicate Root is disjoint from Type, Slot, Value, DataSource, and Resource.
The binary predicates includes, includesContainer, hasType, hasSlot, hasContainer, and hasValue are pairwise disjoint.

Nothing can be both a container and a slot.

```math
\forall x . \mathrm{Container}(x) \Rightarrow \neg \mathrm{Slot}(x) 
```

Nothing can be both a container and a value.

```math
\forall x . \mathrm{Container}(x) \Rightarrow \neg \mathrm{Value}(x) 
```

Nothing can be both a container and a type.

```math
\forall x . \mathrm{Container}(x) \Rightarrow \neg \mathrm{Type}(x) 
```

Nothing can be both a slot and a container.

```math
\forall x . \mathrm{Slot}(x) \Rightarrow \neg \mathrm{Container}(x) 
```

Nothing can be both a slot and a value.

```math
\forall x . \mathrm{Slot}(x) \Rightarrow \neg \mathrm{Value}(x) 
```

Nothing can be both a slot and a type.

```math
\forall x . \mathrm{Slot}(x) \Rightarrow \neg \mathrm{Type}(x) 
```

Nothing can be both a value and a container.

```math
\forall x . \mathrm{Value}(x) \Rightarrow \neg \mathrm{Container}(x) 
```

Nothing can be both a value and a slot.

```math
\forall x . \mathrm{Value}(x) \Rightarrow \neg \mathrm{Slot}(x) 
```

Nothing can be both a value and a type.

```math
\forall x . \mathrm{Value}(x) \Rightarrow \neg \mathrm{Type}(x) 
```

Nothing can be both a type and a container.

```math
\forall x . \mathrm{Type}(x) \Rightarrow \neg \mathrm{Container}(x)
```

Nothing can be both a type and a slot.

```math
\forall x . \mathrm{Type}(x) \Rightarrow \neg \mathrm{Slot}(x) 
```

Nothing can be both a type and a value.

```math
\forall x . \mathrm{Type}(x) \Rightarrow \neg \mathrm{Value}(x) 
```

Nothing can be both a data source and a container.

```math
\forall x . \mathrm{DataSource}(x) \Rightarrow \neg \mathrm{Container}(x) 
```

Nothing can be both a data source and a slot.

```math
\forall x . \mathrm{DataSource}(x) \Rightarrow \neg \mathrm{Slot}(x) 
```

Nothing can be both a data source and a value.

```math
\forall x . \mathrm{DataSource}(x) \Rightarrow \neg \mathrm{Value}(x) 
```

Nothing can be both a data source and a type.

```math
\forall x . \mathrm{DataSource}(x) \Rightarrow \neg \mathrm{Type}(x) 
```

Nothing can be both a resource and a container.

```math
\forall x . \mathrm{Resource}(x) \Rightarrow \neg \mathrm{Container}(x) 
```

Nothing can be both a resource and a slot.

```math
\forall x . \mathrm{Resource}(x) \Rightarrow \neg \mathrm{Slot}(x) 
```

Nothing can be both a resource and a value.

```math
\forall x . \mathrm{Resource}(x) \Rightarrow \neg \mathrm{Value}(x) 
```

Nothing can be both a resource and a type.

```math
\forall x . \mathrm{Resource}(x) \Rightarrow \neg \mathrm{Type}(x) 
```

Nothing can be both a root and a type.

```math
\forall x . \mathrm{Root}(x) \Rightarrow \neg \mathrm{Type}(x) 
```

Nothing can be both a root and a slot.

```math
\forall x . \mathrm{Root}(x) \Rightarrow \neg \mathrm{Slot}(x) 
```

Nothing can be both a root and a value.

```math
\forall x . \mathrm{Root}(x) \Rightarrow \neg \mathrm{Value}(x) 
```

Nothing can be both a root and a data source.

```math
\forall x . \mathrm{Root}(x) \Rightarrow \neg \mathrm{DataSource}(x) 
```

Nothing can be both a root and a resource.

```math
\forall x . \mathrm{Root}(x) \Rightarrow \neg \mathrm{Resource}(x) 
```

No pair can be related by both includes and includesContainer.

```math
\forall x, y . \mathrm{includes}(x, y) \Rightarrow \neg \mathrm{includesContainer}(x, y) 
```

No pair can be related by both includes and hasType.

```math
\forall x, y . \mathrm{includes}(x, y) \Rightarrow \neg \mathrm{hasType}(x, y) 
```

No pair can be related by both includes and hasSlot.

```math
\forall x, y . \mathrm{includes}(x, y) \Rightarrow \neg \mathrm{hasSlot}(x, y) 
```

No pair can be related by both includes and hasContainer.

```math
\forall x, y . \mathrm{includes}(x, y) \Rightarrow \neg \mathrm{hasContainer}(x, y) 
```

No pair can be related by both includes and hasValue.

```math
\forall x, y . \mathrm{includes}(x, y) \Rightarrow \neg \mathrm{hasValue}(x, y) 
```

No pair can be related by both includesContainer and hasType.

```math
\forall x, y . \mathrm{includesContainer}(x, y) \Rightarrow \neg \mathrm{hasType}(x, y) 
```

No pair can be related by both includesContainer and hasSlot.

```math
\forall x, y . \mathrm{includesContainer}(x, y) \Rightarrow \neg \mathrm{hasSlot}(x, y) 
```

No pair can be related by both includesContainer and hasContainer.

```math
\forall x, y . \mathrm{includesContainer}(x, y) \Rightarrow \neg \mathrm{hasContainer}(x, y) 
```

No pair can be related by both includesContainer and hasValue.

```math
\forall x, y . \mathrm{includesContainer}(x, y) \Rightarrow \neg \mathrm{hasValue}(x, y) 
```

No pair can be related by both hasType and hasSlot.

```math
\forall x, y . \mathrm{hasType}(x, y) \Rightarrow \neg \mathrm{hasSlot}(x, y) 
```

No pair can be related by both hasType and hasContainer.

```math
\forall x, y . \mathrm{hasType}(x, y) \Rightarrow \neg \mathrm{hasContainer}(x, y) 
```

No pair can be related by both hasType and hasValue.

```math
\forall x, y . \mathrm{hasType}(x, y) \Rightarrow \neg \mathrm{hasValue}(x, y) 
```

No pair can be related by both hasSlot and hasContainer.

```math
\forall x, y . \mathrm{hasSlot}(x, y) \Rightarrow \neg \mathrm{hasContainer}(x, y) 
```

No pair can be related by both hasSlot and hasValue.

```math
\forall x, y . \mathrm{hasSlot}(x, y) \Rightarrow \neg \mathrm{hasValue}(x, y) 
```

No pair can be related by both hasContainer and hasValue.

```math
\forall x, y . \mathrm{hasContainer}(x, y) \Rightarrow \neg \mathrm{hasValue}(x, y) 
```

</section>
