---
title: <code>Fa&ccedil;ade-X</code> mapping for XML
subtitle: Representing XML in Fa&ccedil;ade-X.
parent: mappings
---

<section id="abstract">

This document specifies how an XML resource is represented as a Fa&ccedil;ade-X data source.

</section>

<section id="sotd">

This document is a first draft. It follows the behaviour of the reference implementation,
[SPARQL Anything](https://sparql-anything.cc/), and the test cases in
[facade-x-tests](https://github.com/w3c-facade-x/facade-x-tests/tree/main/tests/xml), as summarised
in [issue #31](https://github.com/w3c-facade-x/facade-x-specs/issues/31).

</section>

<section class="informative" id="Introduction">

## Introduction

An XML document is a tree of [elements](https://www.w3.org/TR/xml/#sec-logical-struct)
[[XML](#bib-xml)]. Each element has a name, a set of
[attributes](https://www.w3.org/TR/xml/#attdecls), and an ordered sequence of content: child
elements and character data. Element and attribute names may belong to a namespace
[[XML-NAMES](#bib-xml-names)].

In Fa&ccedil;ade-X, each element is a container typed with the element name. Its attributes are
held by string slots, and its content by numbered slots, in document order. Character data are
values.

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

<!-- BUILD:ISSUES label="Mapping: XML" -->

</section>

<section id="Selection">

## Selection

An engine MUST apply this mapping to a resource whose media type is `application/xml` or
`text/xml` [[RFC7303](#bib-rfc7303)], or any media type with the
[structured syntax suffix `+xml`](https://www.rfc-editor.org/rfc/rfc7303#section-4.2)
(e.g. `image/svg+xml`), unless another format mapping applies to that media type.

When the media type is not given, an engine SHOULD apply this mapping to resources with the file
extensions `xml` and `svg`.

</section>

<section id="Mapping">

## Mapping

<section id="DataSource">

### Data source

An XML resource yields exactly one data source. Its triples are placed in the named graph whose IRI
is the value of [`fxe:root`](engine.html#root).

The [document element](https://www.w3.org/TR/xml/#dt-root) is represented by the root container,
which is typed both `fx:Root` and with the name of the document element.

The XML declaration, the document type declaration, and any comments and processing instructions
outside the document element are not represented.

</section>

<section id="Names">

### Names

Element and attribute names are turned into IRIs as follows:

1. A name with a namespace name [[XML-NAMES](#bib-xml-names)] gives the namespace name followed by
   the local part. When the namespace name does not end with `/` or `#`, a `#` is inserted between
   them. For example, the element `item` in the namespace `http://example.org/catalog` gives
   `http://example.org/catalog#item`, and `dc:title`, with `dc` bound to
   `http://purl.org/dc/elements/1.1/`, gives `http://purl.org/dc/elements/1.1/title`.
2. A name without a namespace name is minted from the local part and the value of
   [`fxe:namespace`](engine.html#namespace), as defined in the
   [common principles](mappings.html#Principles). With the default namespace, `person` gives
   `xyz:person`.

As defined in [[XML-NAMES](#bib-xml-names)], an unprefixed attribute has no namespace name, even
when a default namespace is declared: it is minted with `fxe:namespace`. The prefix `xml` is bound
to `http://www.w3.org/XML/1998/namespace`, so `xml:lang` gives
`http://www.w3.org/XML/1998/namespace#lang`.

</section>

<section id="Elements">

### Elements

Each element is represented by a container typed (`rdf:type`) with the IRI of the element name.

Each attribute of the element is held by a string slot whose IRI is the IRI of the attribute name.
Namespace declarations (`xmlns` and `xmlns:*` attributes) are not represented.

The content of the element is held by numbered slots, in document order: the first item in
`rdf:_1`, the second in `rdf:_2`, and so on. The items are:

- each child element, held as the container that represents it;
- each text node, held as a value (see [Values](#Values)).

A text node is a maximal sequence of character data between two pieces of markup. Character
references, entity references and CDATA sections are replaced by the characters they stand for
and are part of the surrounding text node.

The following are not represented, and do not use up a slot number:

- text nodes that consist only of whitespace (spaces, tabs, carriage returns and line feeds);
- comments;
- processing instructions.

An element with no attributes and no represented content gives a container that is only typed.
`<empty/>`, `<empty></empty>` and `<empty>   </empty>` have the same representation.

</section>

<section id="Values">

### Values

XML without a schema defines no value types. Following the
[common principles](mappings.html#Principles), every attribute value and text node is a literal of
type `xsd:string`, including values such as `10.50` or `true`.

The lexical form of a text node is its character data, with whitespace kept: `Text ` and ` tail`
keep their spaces. Line ends are normalised as required by
[XML 1.0 §2.11](https://www.w3.org/TR/xml/#sec-line-ends).

The lexical form of an attribute value is the value after
[attribute-value normalisation](https://www.w3.org/TR/xml/#AVNormalize). A line feed written as
the character reference `&#10;` is kept as a line feed.

</section>

</section>

<section id="Options">

## Options

These options are terms of the [Engine vocabulary](engine.html) and apply only to this mapping.

| Term | Range | Default | Description |
|---|---|---|---|
| <span id="xml.path"></span>`fxe:xml.path` | `xsd:string` | — | An XPath expression [[XPATH](#bib-xpath)]. Only the nodes it selects, and their content, are represented. |

The reference implementation accepts several values for `xml.path` as numbered options
(`xml.path.1`, `xml.path.2`, …). Whether this form is kept is open.

</section>

<section id="Security">

## Security considerations

An engine SHOULD NOT retrieve external entities or external DTD subsets referenced by a document,
since doing so can disclose local files or cause requests to other hosts.

</section>

<section class="informative" id="Examples">

## Examples

<section id="ExampleBase">

### Element, attribute and text

Input:

```example
<?xml version="1.0" encoding="UTF-8"?>
<person id="p1">
  <name>Alice</name>
</person>
```

Fa&ccedil;ade-X representation:

```turtle
@prefix fx:  <http://sparql.xyz/facade-x/ns/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xyz: <http://sparql.xyz/facade-x/data/> .

[] a fx:Root, xyz:person ;
   xyz:id "p1" ;
   rdf:_1 [ a xyz:name ; rdf:_1 "Alice" ] .
```

The whitespace between the elements gives no text nodes.

</section>

<section id="ExampleNamespaces">

### Namespaces

Input:

```example
<catalog xmlns="http://example.org/catalog"
         xmlns:dc="http://purl.org/dc/elements/1.1/"
         xmlns:ex="http://example.org/ext"
         version="1.0" xml:lang="en">
  <dc:title>Sample catalog</dc:title>
  <item id="i1" ex:status="active">
    <price currency="EUR">10.50</price>
  </item>
</catalog>
```

Fa&ccedil;ade-X representation:

```turtle
@prefix fx:  <http://sparql.xyz/facade-x/ns/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xyz: <http://sparql.xyz/facade-x/data/> .
@prefix cat: <http://example.org/catalog#> .
@prefix ex:  <http://example.org/ext#> .
@prefix dc:  <http://purl.org/dc/elements/1.1/> .

[] a fx:Root, cat:catalog ;
   xyz:version "1.0" ;
   <http://www.w3.org/XML/1998/namespace#lang> "en" ;
   rdf:_1 [ a dc:title ; rdf:_1 "Sample catalog" ] ;
   rdf:_2 [ a cat:item ;
            xyz:id "i1" ;
            ex:status "active" ;
            rdf:_1 [ a cat:price ; xyz:currency "EUR" ; rdf:_1 "10.50" ] ] .
```

The elements take the default namespace, but the unprefixed attributes `version`, `id` and
`currency` do not.

</section>

<section id="ExampleMixed">

### Mixed content and ignored markup

Input:

```example
<doc>
  <mixed>Text <b>bold</b> and <i>italic</i> tail</mixed>
  <!-- a comment -->
  <empty/>
  <whitespace>   </whitespace>
</doc>
```

Fa&ccedil;ade-X representation:

```turtle
@prefix fx:  <http://sparql.xyz/facade-x/ns/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xyz: <http://sparql.xyz/facade-x/data/> .

[] a fx:Root, xyz:doc ;
   rdf:_1 [ a xyz:mixed ;
            rdf:_1 "Text " ;
            rdf:_2 [ a xyz:b ; rdf:_1 "bold" ] ;
            rdf:_3 " and " ;
            rdf:_4 [ a xyz:i ; rdf:_1 "italic" ] ;
            rdf:_5 " tail" ] ;
   rdf:_2 [ a xyz:empty ] ;
   rdf:_3 [ a xyz:whitespace ] .
```

The comment does not use up a slot number, so `empty` is held by `rdf:_2`.

</section>

<section id="ExampleQuery">

### Query

Listing the items of the catalog with their price:

```example
PREFIX fx:  <http://sparql.xyz/facade-x/ns/>
PREFIX fxe: <http://sparql.xyz/facade-x/engine/>
PREFIX xyz: <http://sparql.xyz/facade-x/data/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX cat: <http://example.org/catalog#>

SELECT ?id ?price WHERE {
  SERVICE <x-sparql-anything:> {
    fx:properties fxe:location "catalog.xml" .
    ?item a cat:item ;
          xyz:id ?id ;
          ?slot ?p .
    ?p a cat:price ;
       rdf:_1 ?price .
  }
}
```

</section>

</section>

<section class="informative" id="References">

## References

<dt id="bib-xml">[XML]</dt>
<dd><a href="https://www.w3.org/TR/xml/">Extensible Markup Language (XML) 1.0 (Fifth Edition)</a>. Tim Bray; Jean Paoli; C. M. Sperberg-McQueen; Eve Maler; François Yergeau. W3C. 26 November 2008. W3C Recommendation.</dd>
<dt id="bib-xml-names">[XML-NAMES]</dt>
<dd><a href="https://www.w3.org/TR/xml-names/">Namespaces in XML 1.0 (Third Edition)</a>. Tim Bray; Dave Hollander; Andrew Layman; Richard Tobin; Henry Thompson. W3C. 8 December 2009. W3C Recommendation.</dd>
<dt id="bib-rfc7303">[RFC7303]</dt>
<dd><a href="https://www.rfc-editor.org/rfc/rfc7303">XML Media Types</a>. H. Thompson; C. Lilley. IETF. July 2014. Proposed Standard.</dd>
<dt id="bib-xpath">[XPATH]</dt>
<dd><a href="https://www.w3.org/TR/xpath-31/">XML Path Language (XPath) 3.1</a>. Jonathan Robie; Michael Dyck; Josh Spiegel. W3C. 21 March 2017. W3C Recommendation.</dd>
<dt id="bib-sa-xml">[sparql-anything-xml]</dt>
<dd><a href="https://sparql-anything.readthedocs.io/stable/formats/XML/">SPARQL Anything — XML</a>.</dd>

</section>