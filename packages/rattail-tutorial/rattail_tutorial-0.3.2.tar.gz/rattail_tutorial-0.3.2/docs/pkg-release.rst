
.. highlight:: sh

Build a Release for the Project
===============================

Even though our app does very little at this stage, we wish to go ahead and
"release" our first version for it.

.. note::
   Whether or not you actually need to build releases for your project, may
   depend on your use case.  For instance if you have reason to run the app(s)
   directly from source (i.e. git HEAD) then you may have no use for a built
   package.


Project Versioning
------------------

The project's current version "number" is kept in only one place really, in our
case ``~/src/rattail-tutorial/rattail_tutorial/_version.py``.  Other files are
configured to read the current project version from there.

The initial version for a new project will generally be '0.1.0' and it's
assumed that subsequent versions will be '0.1.1' then '0.1.2' etc. until you've
decided that it's time to do a '0.2.0' release, and the cycle begins again.

You can be as aggressive or conservative as you like when it comes to
incrementing the more "major" parts of the version number, e.g. you can
increment conservatively to where you've just released say, '0.1.427' before you
finally go to '0.2.0'.  The only real "requirement" (assumption) here is that
you will build a new version release *every time* you update the production
environment(s).  Sometimes that may mean multiple releases in a given day,
e.g. if the first one ships with a bug and you have to push a release to fix.


Install Invoke
--------------

While you can most certainly go about the build/release task in various ways,
the convention within Rattail-land is to use `Invoke`_.

.. _Invoke: https://www.pyinvoke.org/

So next we'll install that to your virtualenv::

   pip install invoke

You may also want to declare this within your project's dependencies (in
``setup.py``), but that's up to you.


Create Tasks File
-----------------

The ``invoke`` command will invoke tasks which we have defined in a tasks file.
(Duh!)

We will now create a file at ``~/src/rattail-tutorial/tasks.py`` and in it
place some minimal contents:

.. code-block:: python3

   # -*- coding: utf-8; -*-
   """
   Tasks for 'rattail-tutorial' project
   """

   from invoke import task

   # this is needed to read current `__version__` value
   #import os
   #here = os.path.abspath(os.path.dirname(__file__))
   #exec(open(os.path.join(here, 'rattail_tutorial', '_version.py')).read())


   @task
   def release(c):
       """
       Release a new version of `rattail-tutorial`.
       """
       # clear out previous package info
       c.run('rm -rf rattail_tutorial.egg-info')

       # build fresh package!
       c.run('python setup.py sdist --formats=gztar')

       # enable this if you intend to publish package to PyPI
       #c.run('twine upload dist/rattail-tutorial-{}.tar.gz'.format(__version__))

If you're creating your own project then you can use the above as a starting
point for your own file.  Instead of using ``twine`` to upload the package to
`PyPI`_, you may need to push to some private package repository which you
control.

.. _PyPI: https://pypi.org/


Run Release Task
----------------

As you can see above, ``release`` is the one and only task we have defined so
far.  In most cases that will be the only task you ever define for the project,
but YMMV.

At any rate it's all we need for now, so let's run it::

   cd ~/src/rattail-tutorial
   invoke release

If you're feeling lazy you can even shorten that second one to::

   inv release

This will build a new "release" which may then be found within e.g. the
``~/src/rattail-tutorial/dist/`` folder.  Depending on the specifics of your
tasks file, this release may also be uploaded to some (public or private)
package index.
