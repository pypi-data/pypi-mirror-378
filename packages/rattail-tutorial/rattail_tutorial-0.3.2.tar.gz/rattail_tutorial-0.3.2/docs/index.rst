
Rattail Tutorial
================

First of all, welcome to Rattail!

This project is a tutorial of sorts, to show how to use Rattail in the real
world.  (It is accordingly named 'rattail-tutorial'.)

While it aims to cover many areas, this tutorial is not exhaustive.  This
project's goals include:

* show how to setup your development environment
* show how to create a new project
* show how to get your project up and running, i.e. with a database and web app
* show how to customize and extend your app in various ways, to suit your needs
* show how to integrate with another system (CORE-POS) in a custom way
* provide a "working example" of all documented concepts

That last one means, you can install and run the rattail-tutorial app yourself,
and e.g. further customize it to get a feel for Rattail.

Please see `https://rattailproject.org/docs/rattail-tutorial/
<https://rattailproject.org/docs/rattail-tutorial/>`_ for the latest version of
this document.


Front Matter
------------

It will be helpful to understand a few things before you get started:

**Rattail itself is a "library" more than it is an "app".** The idea is that the
Rattail Project will provide "most" of the base functionality you need from an
app, but ultimately you must create a project of your own, which "uses" Rattail
functionality to accomplish *your* goals.

**Rattail docs always refer to "your" app with the name "Poser".** In fact this
tutorial will *not* be using the name "Poser" (much) - but that is usually what
you will see in all *other* docs, to represent "your" (i.e. any custom) app.

**This "rattail-tutorial" project is a proper app.** Following from the
previous point, this project/app is named "rattail-tutorial" and therefore
instead of using the name "Poser" within this tutorial, we will be using its
*actual* name.


Table of Contents
-----------------

.. toctree::
   :maxdepth: 2

   setup-dev
   create-project
   start-docs
   configure
   pkg-release
   make-db
   run-webapp
   customize/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
