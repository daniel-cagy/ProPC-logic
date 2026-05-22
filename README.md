# ProPC-logic
The purpose of this project is to use first-order logic to determine whether a PC configuration is valid or not.

## Architecture
We're using Knowledge Graphs (KGs) to model PC components. The system is structured as follows:

- **Classes**: Components, CPUs (subclass of Components), Brands, Motherboards, etc.
- **Attributes**: Individuals inherit attributes based on their class. For example:
  - CPUs have a specific Socket type
  - Motherboards have a compatible Socket type
  - Components have properties like brand, TDP, etc.

The knowledge graph is defined in a `.ttl` file (Turtle RDF format), which is processed using RDF tools. We query the graph using SPARQL, with Python orchestrating the entire workflow.
