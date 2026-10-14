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

### Disk components

Disk definitions are in `graph/disks.ttl` and are imported by `graph.ttl`.
`Disk` is a component superclass with `SSD` and `HDD` subclasses. Disk capacity
is stored as a decimal number of GB (`1 TB` = `1000 GB`); buffer size is in MB,
read/write speeds are the UserBenchmark Average Bench results in MB/s, and IOPS
and HDD RPM are integers. Each sample records its benchmark source on the disk
individual. These results are observed benchmark averages, not manufacturer
maximum specifications.
Values that are not available for a model are left unspecified. Buffer size
represents dedicated DRAM, not an SSD's dynamic SLC cache.
Interface, size, and installation type are strings so additional values can be
represented; the suggested values are documented on their properties in the
Turtle file. Portability is a boolean, NAND type is specific to SSDs, and RPM
is specific to HDDs.
