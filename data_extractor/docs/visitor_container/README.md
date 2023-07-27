# Visitor Enviroment

In case you want to communiate with the other docker container inside of a namespace
you need an independent pod, which is in the namespace. This is the intention of the 
vistor docker. This docker has not many functionalities beside wget, vim and python.
If you want to add more functionalities feel free to adjust the apt-get install part to
add more programs or extent the requirements list for Python.

The Dockerfile can be loaded directly from the visitor_container folder. For example with docker
directly it would be:

docker build --rm -f docker_visitor -t docker_visitor:latest .