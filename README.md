# ProPC-logic
The purpose of this project is to use first-order logic to determine whether a PC configuration is valid or not.

# Architecture
We're using KGs. Basically, we have classes, like Components, CPUs (subclass of Components), Brands...

Individuals have atributes depending on which class they're in. For instance, if an individual is a CPU, it uses a specific kind of Socket, and a Motherboard has a specific kind of Socket. For every CPU and every Motherboard, this CPU is compatible with this Motherboard if the Socket that the CPU needs is the one that the Motherboard has.

So we're writing the graph in a '.ttl' file. That graph is processed with RDF, and we make queries in it using SPARQL, with Python orchestrating everything.

# Current Status
For now, we're currently focusing on improving the ttl with more individuals and atributes. We're also working on a web based GUI.

# For the future
We want, firstly, to make a software that is capable of determining whether a CPU is compatible with a Motherboard. After testing and improving that part, we'll add more types of components. The goal is to make a web app that is capable of recommending a full PC configuration that is valid and fits with what the user needs.
