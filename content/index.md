<section id="abstract">

This page provides an overview of the Façade-X specification documents.
Façade-X is the (meta-)model resulting from the abstraction of all the basic data structures used to
represent source data formats, combined into a unified model. RDF languages can implement it to
provide users with direct access to external, heterogeneous data formats without requiring
format-specific transformations.

</section>

<section id="sotd">

This document is currently in active development.

</section>

<section class="informative">

## Overview

Modern data landscapes are inherently heterogeneous: CSV files, JSON documents, spreadsheets,
XML, and many other formats each impose their own structural conventions. Façade-X addresses this
fragmentation by identifying the minimal set of structural primitives —
*containers*, *slots*, and *values* — that are sufficient to faithfully
represent any of these formats within a single, coherent model.

The model is intentionally abstract. A container generalises both ordered lists and associative
maps; a slot is the allotted place for a value or a nested container, identified either by a
cardinal number (a *NumberSlot*) or by a string key (a *StringSlot*).
This small vocabulary, together with a precisely stated set of logical axioms, constitutes the
metamodel from which format-specific RDF mappings are derived.

This repository contains two companion specification documents:
the formal metamodel, expressed in first-order logic, and the RDF vocabulary that realises it
under the namespace `http://sparql.xyz/facade-x/ns/`.

</section>

<section>

## Specification Documents

<section>

### [Façade-X Concepts and Metamodel](metamodel.html)

This document provides the formal definition of the Façade-X metamodel using first-order
logic axioms. It introduces and specifies the following concepts:

- **Resources and Data Sources** — digital artifacts and the data collections they contain.
- **Containers, Slots, and Values** — the core structural primitives of the model, abstracting over lists and maps.
- **Types** — classifications that can be assigned to containers.
- **Root Container** — the unique top-level entry point for each data source.
- **Disjointness** — a complete set of axioms ensuring the concepts are pairwise disjoint.

</section>

<section>

### [Façade-X RDF Vocabulary](rdf.html)

This document specifies the RDF realisation of the Façade-X metamodel.
It defines the vocabulary terms under the `fx:` namespace
(`http://sparql.xyz/facade-x/ns/`), including:

- `fx:Container` — the class of containers.
- `fx:Slot`, `fx:SlotNumber`, `fx:SlotString` — the slot hierarchy.
- `fx:Value` — the class of primitive values.
- `fx:Type` — the class of types assignable to containers.
- `fx:Root` — the type of the unique top-level container of a data source.

</section>

</section>
