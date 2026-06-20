<section id="abstract">

This document specifies the Fa&ccedil;ade-X RDF vocabulary.

</section>

<section id="sotd">

This document is currently in active development.

</section>

<section class="informative" id="Introduction">

## Introduction

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
      <td>The Façade-X RDF vocabulary: configuration and primitives</td>
    </tr>
    <tr>
      <td>xyz</td>
      <td>http://sparql.xyz/facade-x/data/</td>
      <td>The Façade-X RDF vocabulary: namespace for derived data</td>
    </tr>
    <tr>
      <td>rdf</td>
      <td>http://www.w3.org/1999/02/22-rdf-syntax-ns#</td>
      <td>[<cite><a class="bibref" href="#bib-rdf-schema">rdf-schema</a></cite>]</td>
    </tr>
    <tr>
      <td>rdfs</td>
      <td>http://www.w3.org/2000/01/rdf-schema#</td>
      <td>[<cite><a class="bibref" href="#bib-rdf-schema">rdf-schema</a></cite>]</td>
    </tr>
    <tr>
      <td>xsd</td>
      <td>http://www.w3.org/2001/XMLSchema#</td>
      <td>[<cite><a class="bibref" href="#bib-xmlschema-2">xmlschema-2</a></cite>]</td>
    </tr>
  </tbody>
</table>
</section>

</section>

<section>

## Issues

<!-- <p class="issue" data-number="2"></p> -->
<p class="issue" data-number="7"></p>
<p class="issue" data-number="9"></p>
<p class="issue" data-number="11"></p>
<p class="issue" data-number="14"></p>
<!-- Issue can automatically be populated from GitHub -->

</section>

<section id="Vocabulary">

## Fa&ccedil;ade-X Vocabulary

The namespace used for the Fa&ccedil;ade-X Vocabulary is: `http://sparql.xyz/facade-x/ns/`

<div class="termtoc">
  <a href="#Container">Container</a> |
  <a href="#Slot">Slot</a> |
  <a href="#SlotString">SlotString</a> |
  <a href="#SlotNumber">SlotNumber</a> |
  <a href="#Type">Type</a> |
  <a href="#Value">Value</a> |
  <a href="#Root">Root</a>
</div>

<section class="term" id="Container">
<h3 id="h-Container">Container</h3>
<p>The class of containers</p>
<div class="tech">
  <ul>
    <li><strong>IRI:</strong> http://sparql.xyz/facade-x/ns/Container</li>
    <li><strong>Sub Class Of:</strong> http://www.w3.org/2000/01/rdf-schema#Class </li>
	<li><strong>Predicates:</strong> ANY instance of <a href="#Slot">fx:Slot</a>, <a href="https://www.w3.org/1999/02/22-rdf-syntax-ns#type">rdf:type</a></li>
  </ul>
</div>
</section>

<section class="term" id="Slot">
<h3 id="h-Slot">Slot</h3>
<p>The class of slots</p>
<div class="tech">
  <ul>
    <li><strong>IRI:</strong> http://sparql.xyz/facade-x/ns/Slot</li>
    <li><strong>Sub Class Of:</strong> rdfs:Property </li>
    <li><strong>Instances - Domain:</strong> http://sparql.xyz/facade-x/ns/Container </li>
    <li><strong>Instances - Range:</strong> http://sparql.xyz/facade-x/ns/Container [OR] http://sparql.xyz/facade-x/ns/Value</li>
  </ul>
</div>
</section>

<section class="term" id="SlotNumber">
<h3 id="h-SlotNumber">SlotNumber</h3>
<p>The class of slots in the source data that are numbers</p>
<div class="tech">
  <ul>
    <li><strong>IRI:</strong> http://sparql.xyz/facade-x/ns/SlotNumber</li>
    <li><strong>Sub Class Of:</strong> http://sparql.xyz/facade-x/ns/Slot [AND] rdfs:ContainerMembershipProperty</li>
    <li><strong>Instances - Domain:</strong> http://sparql.xyz/facade-x/ns/Container </li>
    <li><strong>Instances - Range:</strong> http://sparql.xyz/facade-x/ns/Container [OR] http://sparql.xyz/facade-x/ns/Value</li>
    <li><strong>Generator:</strong> rdf:_[cardinal number]</li>
  </ul>
</div>
</section>

<section class="term" id="SlotString">
<h3 id="h-SlotString">SlotString</h3>
<p>The class of slots in the source data that are strings</p>
<div class="tech">
  <ul>
    <li><strong>IRI:</strong> http://sparql.xyz/facade-x/ns/SlotString</li>
    <li><strong>Sub Class Of:</strong> http://sparql.xyz/facade-x/ns/Slot</li>
    <li><strong>Instances - Domain:</strong> http://sparql.xyz/facade-x/ns/Container </li>
    <li><strong>Instances - Range:</strong> http://sparql.xyz/facade-x/ns/Container [OR] http://sparql.xyz/facade-x/ns/Value</li>
    <li><strong>Generator:</strong> xyz:[source string]</li>
  </ul>
</div>
</section>

<section class="term" id="Type">
<h3 id="h-Type">Type</h3>
<p>The class of types in the source data</p>
<div class="tech">
  <ul>
    <li><strong>IRI:</strong> http://sparql.xyz/facade-x/ns/Type</li>
    <li><strong>Sub Class Of:</strong> rdfs:Class</li>
    <li><strong>Generator:</strong> xyz:[source string]</li>
  </ul>
</div>
</section>

<section class="term" id="Value">
<h3 id="h-Value">Value</h3>
<p>The class of values in the source data</p>
<div class="tech">
  <ul>
    <li><strong>IRI:</strong> http://sparql.xyz/facade-x/ns/Value</li>
    <li><strong>Sub Class Of:</strong> rdfs:Literal</li>
    <li><strong>Generator:</strong> xyz:[source string]</li>
  </ul>
</div>
</section>

<section class="term" id="Root">
<h3 id="h-Root">Root</h3>
<p>The type of the main container. There can only be a single container of type fx:Root.</p>
<div class="tech">
  <ul>
    <li><strong>IRI:</strong> http://sparql.xyz/facade-x/ns/Root</li>
    <li><strong>Sub Class Of:</strong> rdfs:Class</li>
  </ul>
</div>
</section>

</section>

<section id="NamedGraphs">

## Named Graphs

In Façade-X, named graphs are used to associate each data source with its container hierarchy.
When a resource is processed, each of its data sources is assigned a distinct graph IRI.
All triples belonging to that data source — its root container, slots, and values — are placed
within the corresponding named graph. This allows multiple data sources to coexist within the
same RDF dataset without ambiguity: the graph IRI acts as the identity of the data source,
and querying or reasoning over a specific source is simply a matter of selecting its graph.
For resources that contain a single data source, a single named graph is produced; for
resources such as spreadsheets that contain multiple data sources (e.g. one per sheet),
a named graph is produced for each.

</section>

<section id="ManchesterSyntax">

## Façade-X Vocabulary in OWL Manchester Syntax

The following provides a representation of the Façade-X vocabulary in
<a href="https://www.w3.org/TR/owl2-manchester-syntax/">OWL 2 Manchester Syntax</a>.
It is derived directly from the term definitions in the <a href="#Vocabulary">Façade-X Vocabulary</a>
section above.

<pre data-nomath class="example">
Prefix: fx: &lt;http://sparql.xyz/facade-x/ns/&gt;
Prefix: xyz: &lt;http://sparql.xyz/facade-x/data/&gt;
Prefix: rdf: &lt;http://www.w3.org/1999/02/22-rdf-syntax-ns#&gt;
Prefix: rdfs: &lt;http://www.w3.org/2000/01/rdf-schema#&gt;
Prefix: xsd: &lt;http://www.w3.org/2001/XMLSchema#&gt;
Prefix: owl: &lt;http://www.w3.org/2002/07/owl#&gt;

Ontology: &lt;http://sparql.xyz/facade-x/ns/&gt;


## Classes

Class: fx:Container
    Annotations:
        rdfs:label "Container",
        rdfs:comment "The class of containers."
    SubClassOf:
        rdfs:Class
    DisjointWith:
        fx:Slot,
        fx:Value,
        fx:Type

Class: fx:Slot
    Annotations:
        rdfs:label "Slot",
        rdfs:comment "The class of slots. Any instance of fx:Slot is a property
                      with domain fx:Container and range fx:Container or fx:Value."
    SubClassOf:
        rdfs:Property,
        rdfs:domain value fx:Container,
        rdfs:range value (fx:Container or fx:Value)
    DisjointWith:
        fx:Container,
        fx:Value,
        fx:Type

Class: fx:SlotNumber
    Annotations:
        rdfs:label "SlotNumber",
        rdfs:comment "The class of slots whose key is a cardinal number.
                      Any instance of fx:SlotNumber is also an instance of
                      fx:Slot and of rdfs:ContainerMembershipProperty."
    SubClassOf:
        fx:Slot,
        rdfs:ContainerMembershipProperty
    DisjointWith:
        fx:SlotString

Class: fx:SlotString
    Annotations:
        rdfs:label "SlotString",
        rdfs:comment "The class of slots whose key is a string.
                      Any instance of fx:SlotString is also an instance of fx:Slot."
    SubClassOf:
        fx:Slot
    DisjointWith:
        fx:SlotNumber

Class: fx:Type
    Annotations:
        rdfs:label "Type",
        rdfs:comment "The class of types in the source data."
    SubClassOf:
        rdfs:Class
    DisjointWith:
        fx:Container,
        fx:Slot,
        fx:Value

Class: fx:Value
    Annotations:
        rdfs:label "Value",
        rdfs:comment "The class of values in the source data."
    SubClassOf:
        rdfs:Literal
    DisjointWith:
        fx:Container,
        fx:Slot,
        fx:Type

Class: fx:Root
    Annotations:
        rdfs:label "Root",
        rdfs:comment "The type of the main container. There can only be a single container of type fx:Root."
    SubClassOf:
        fx:Container
    DisjointWith:
        fx:Slot,
        fx:Value,
        fx:Type
</pre>

</section>

<section class="informative" id="References">

## References


<dt id="bib-rdf-schema">[rdf-schema]</dt>
<dd><a href="https://www.w3.org/TR/rdf-schema/" property="dc:requires"><cite>RDF Schema 1.1</cite></a>. Dan Brickley; Ramanathan Guha. W3C. 25 February 2014. W3C Recommendation. URL: <a href="https://www.w3.org/TR/rdf-schema/" property="dc:requires">https://www.w3.org/TR/rdf-schema/</a></dd>
<dt id="bib-xmlschema-2">[xmlschema-2]</dt>
<dd><a href="https://www.w3.org/TR/xmlschema-2/" property="dc:requires"><cite>XML Schema Part 2: Datatypes Second Edition</cite></a>. Paul V. Biron; Ashok Malhotra. W3C. 28 October 2004. W3C Recommendation. URL: <a href="https://www.w3.org/TR/xmlschema-2/" property="dc:requires">https://www.w3.org/TR/xmlschema-2/</a></dd>

</section>
