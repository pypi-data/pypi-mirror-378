
.. highlight:: sh

Create a New Project
====================

Now that you've setup your development environment, you're ready to create a
new Rattail-based project.

.. note::
   If you wish to simply install and run this rattail-tutorial project,
   *instead* of creating a new project for yourself, please keep reading.  This
   document aims to address both use cases.  However you can skip ahead to
   :ref:`mkvirtualenv`.

Note again that while Rattail is a project in itself, your app is yet another
project, which is "based" on Rattail but otherwise has a life of its own.  It
is *not* a "fork" of Rattail but intsead uses Rattail as a library.

Notes About Names
-----------------

There are some points to be made here, regarding project names.

First point has to do with the "types" of names involved.  Really there are 3:

* "repo" name
* "project" name
* "package" name

What we're calling "repo" name here, refers to the so-called "slug" name for
the repo, e.g. the actual folder name for the repo on disk.

What we're calling "project" name here, refers to the "official" project name,
e.g. as it might be registered on PyPI or generally referenced in
documentation, etc.

What we're calling "package" name here, refers to the actual name of the Python
package contained within the project.

And there technically is a 4th, the "virtualenv" name.  This refers to the
Python virtual environment you will create, within which you will install your
project.  This virtualenv name need not be related necessarily, to your project
name, but in practice it usually would be.  In some cases you may have multiple
virtualenvs and each must of course get a unique name.

Some examples will surely help.

.. todo::
   should really have a table instead of lists here?

Example Project: Poser

* repo name: poser
* project name: Poser
* package name: poser

Example Project: rattail-tutorial

* repo name: rattail-tutorial
* project name: rattail-tutorial
* package name: rattut

Note how the "Poser" name is much more friendly and homogenous as compared to
the "rattail-tutorial" name, when considering all 3 "types" of names involved.
Really "rattail-tutorial" is not an example of a good name per se, but it was
given to this project for other reasons.

This sort of brings us to the second point about names, which is that they
*should* be "good" generally speaking.  You ideally would want a name more like
"Poser" in that it's simple and easily recognizable, etc.

.. todo::
   link to "how to name project" doc
   (https://rattailproject.org/moin/LilSnippets/ProjectNaming)

.. _mkvirtualenv:

Creating the Virtual Environment
--------------------------------

As mentioned above, the name you give your virtual environment is really up to
you, and needn't "match" your project name etc.

Let's assume for a moment that you are creating a new project (described next)
named "Poser" - you likely will want to make a virtualenv named "poser" also::

   mkvirtualenv --python=/usr/bin/python3 poser
    
Note that you should specify the path to your Python 3 executable, to avoid
using the "default" which is likely still Python 2 at this time.

For the sake of this tutorial, we'll be using the "rattut" env name::

   mkvirtualenv --python=/usr/bin/python3 rattut
    
Please note that pretty much all subsequent commands shown, will assume your
virtual environment (regardless what you named it) is currently *active*.  It
should be obvious when a virtualenv is active, since it should modify the shell
prompt to reflect that.

If you do need to deactivate your current virtualenv, you can do that with::

   deactivate

And then to re-activate your virtualenv you do::

   workon rattut

Or maybe ``workon poser`` etc., whatever named env you want to activate.

Installing Rattail Packages
---------------------------

At this point you have an "empty" virtual environment, to which we will now
install some Rattail software packages.

If you are wanting to create a new project for yourself, then the only thing
you must do for this step is::

   pip install Tailbone

However if you're not wanting a new project, but wish to run this
rattail-tutorial app instead, you should do this::

   mkdir -p ~/src
   cd ~/src
   git clone https://forgejo.wuttaproject.org/rattail/rattail-tutorial.git
   pip install -e rattail-tutorial

Creating the Project
--------------------

If you're just wanting to run the rattail-tutorial app you can skip this step.

First of all you should change directory to wherever you want to create the
actual project source folder.  Rattail docs will generally assume that's at
``~/src`` in which case you should do something like::

   mkdir -p ~/src
   cd ~/src

Remember all that talk about names, up above?  Well now you will be specifying
a *single* name when creating your project.  In practice the name you provide:

* should be lower-cased
* will be used as-is for the "repo" name
* will be capitalized (and weird chars replaced) to obtain "project" name
* will be used as-is for the "package" name, except weird chars replaced by "_"

Got all that straight?  If not, no worries, just try this a few times and see
what you end up with.  Assuming you did want the project name "Poser" you would
run the command::

   pcreate -s rattail poser

This will use the "scaffold" (basically, set of templates) which is named
"rattail" to generate a new folder containing files which define a new "Poser"
project, within the "poser" folder under current directory.

Since this tutorial project is named "rattail-tutorial" and there's no possible
way for the scaffold to know that we want to use "rattut" as the Python package
name, we had to simply "pick our poison" when generating the initial tutorial
project.  In other words we did::

   pcreate -s rattail rattail-tutorial

Note that per the above rules, what the scaffold assumed by default was:

* repo name was "rattail-tutorial"
* project name was "Rattail_tutorial"
* package name was "rattail_tutorial"

We'll clean that up a bit shortly, but first let's start Git tracking.

Making a Git Repo
-----------------

We never want to start a new project without also starting a proper Git repo
for it.  We will want to be able to ``git push`` the code to a central
location, e.g. GitHub or similar.

Change directory to your new project's source repo folder and then initialize::

   cd ~/src/rattail-tutorial
   git init

We also want our first commit to include all the generated code so far::

   git add .
   git commit -m "Initial content as generated from project scaffold"

Now we'll establish our upstream and do our first push.  How exactly you go
about this may vary, and certainly the commands shown here will *not* work for
you as-is, since your "origin" at least will need to be different::

   git remote add origin git@rattailproject.org:/srv/git/rattail-tutorial.git
   git push --set-upstream origin master

And finally, at least in the case of this tutorial project, we wanted to go
through and clean up some of the generated names, as well as assign authorship
and project description etc. within the ``setup.py`` file.  (Then commit those
changes and do another push, so we again have "clean" git status.)

Installing Your Project
-----------------------

If you've just created a new project, technically we haven't yet shown how to
"install" it within your virtualenv.  Here's how to do that::

   pip install -e ~/src/poser

Of course replace "poser" with your project's repo name there.

This step is listed last within this section, to avoid the situation where you
first install the project, then decide to change its name.  So ideally you
should have settled on the name by now, and are happy with contents of
``setup.py`` etc. before installing the project to your virtualenv.
