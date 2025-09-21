
.. highlight:: sh

Setup Development Environment
=============================

These are the main requirements for a development environment, as pertains to
Rattail:

* Linux (Debian-ish)
* Git
* Python (3.x)
* virtualenvwrapper
* PostgreSQL

Technically it's possible for you to work around some of these, but not all.
However this tutorial will assume that all these requirements are met.

Now we'll go through these requirements in more detail, and how to satisfy each
one.

Linux
-----

So, the operating system upon which production Rattail software runs, is
generally assumed to be `Linux`_.  To the author's knowledge, this holds true
across all existing production installs.

.. _Linux: https://en.wikipedia.org/wiki/Linux

There is technically one exception to this: the Rattail "File Monitor service"
(which is the Windows equivalent of the Rattail "File Monitor daemon" on Linux)
of course does run (only) on Windows, and has been used heavily in production.
But one of its primary tasks is usually just to move files (e.g. which emanate
from POS system) over to the "real" Rattail server on Linux somewhere.

It is possible that you could run a full Rattail stack on Windows (or MacOS for
that matter?), e.g. with PostgreSQL database and web app, possibly even
datasync etc.  However there is no effort put toward supporting that currently,
so again Linux is assumed here.

Now that we've established Linux, we go a bit further and specify
"Debian-ish" - in practice the only two distros used so far, are `Debian`_ and
`Ubuntu`_.  You are encouraged to use a "stable" version here, regardless of
which distro you prefer.  It's likely other distros would work also, as far as
just running the app(s); however some of Rattail's "configuration management"
utilities (use of which is of course optional) are built with Debian/Ubuntu in
mind.

.. _Debian: https://www.debian.org/
.. _Ubuntu: https://ubuntu.com/

The "where" question is worth mentioning here too.  In practice a production
Rattail server can be either a bare-metal machine running on your local
network, or indeed a "virtual" machine running either locally or in the cloud.
Whether you run locally or in the cloud usually will depend on other factors,
e.g. if the app must integrate directly with a POS system then it probably must
run on the local network.  (And of course you can always run in "both" places,
with datasync keeping everything flowing smoothly between them.)

Setting It Up
^^^^^^^^^^^^^

In this tutorial we will be using `Vagrant`_ to spin up a local Debian Linux
virtual machine (VM) with `VirtualBox`_ as the "provider".  This is primarily
so we can show an example which you could reproduce on your end, but also one
which could stay "isolated" and not interfere with any other stuff you may have
going on.

.. _Vagrant: https://www.vagrantup.com/
.. _VirtualBox: https://www.virtualbox.org/

First thing then, will be to install VirtualBox and Vagrant if you do not
already have them.  You must install these to your "bare-metal development"
machine, i.e. your laptop.

Once those are in place, you can use the ``Vagrantfile`` which comes with this
(rattail-tutorial) project, to create a new VM.  Note that this VM does not
come with any special behavior, it's as "vanilla" as possible.

Here is the contents of this ``Vagrantfile`` in case you need to create your
own, outside of the rattail-tutorial project:

.. literalinclude:: ../Vagrantfile
   :language: ruby

Change to the directory which contains your ``Vagrantfile`` and then run
``vagrant up``, e.g.::

   cd ~/src/rattail-tutorial
   vagrant up

Those commands assume your "host" machine (i.e. your laptop) runs Linux too,
though of course that may not be so.  Please adjust accordingly.

Confirming It Works
^^^^^^^^^^^^^^^^^^^

There are really two things you should check, to confirm "all is well"
regarding your new Linux machine, regardless of whether it's a Vagrant VM, or
some bare-metal machine.

**Check #1** - Can you open a console terminal for the machine?  If it's
bare-metal then this probably just means making sure the keyboard and/or mouse
are working, and you can login.  If it's virtual then this probably means
making sure you can ssh into it.  (You may want to use ssh even if it's
bare-metal, depending on its role etc.)

**Check #2** - Are you able to use ``sudo`` for elevated privileges?  If the
Check #1 passed then you should be able to run e.g. ``sudo whoami`` on the
terminal.  It's okay to be prompted for a password as long as you know what
that is. ;) Otherwise this check fails.

Note that if you're using Vagrant, you should be able to do ``vagrant ssh`` in
order to connect, and from there ``sudo`` should be no problem.

Git
---

This one's pretty obvious and you may already have it, but we'll cover it
anyway to be thorough.

Setting It Up
^^^^^^^^^^^^^

Install with::

   sudo apt install -y git

But we'll also want to define your Git user identity, e.g.::

   git config --global user.name "John Doe"
   git config --global user.email "john@example.com"

Confirming It Works
^^^^^^^^^^^^^^^^^^^

This should work as expected::

   git --version
    
Also these should output the same values as you defined above::

   git config --global user.name
   git config --global user.email

Python
------

Since we're assuming Linux here (e.g. on the Vagrant VM), you probably already
have Python installed.  However we do want to make sure you have Python 3.x -
since Python 2 is EOL quite soon as of this writing.

Setting It Up
^^^^^^^^^^^^^

To make sure you have Python 3.x, run the following command::

   sudo apt install -y python3 python3-dev

Confirming It Works
^^^^^^^^^^^^^^^^^^^

You should now be able to confirm a Python 3.x binary with this command::

   python3 --version

You probably also should find out where exactly this binary lives::

   which python3

The output from that most likely points to ``/usr/bin/python3`` but please make
a note of your location if it's different.

Misc. Other Dependencies
------------------------

These don't really fit any other category, and aren't *necessarily* required,
depending on your project etc.  But they're often necessary and we might as
well install them just in case::

   sudo apt install -y build-essential

virtualenvwrapper
-----------------

The `virtualenvwrapper`_ package is, in this author's opinion, quite useful for
both Rattail development, as well as production installs.  For this reason,
this tutorial will assume its presence, even though technically Rattail does
not require it.

.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/

Setting It Up
^^^^^^^^^^^^^

Before actually installing virtualenvwrapper, let's prep our "workon home"
directory.  This tutorial assumes, as do all Rattail docs, that the workon home
resides at ``/srv/envs`` - again you're free to use another location, but all
docs will assume that one.  These commands should prep the workon home folder
(adjust path and/or username as needed)::

   sudo mkdir /srv/envs
   sudo chown you:you /srv/envs

Note that for development it's often convenient to make this folder owned by
"you" whereas in production installs the author recommends making this folder
owned by a special "rattail" system user.

Now for virtualenvwrapper itself.  There are technically a few ways to go about
this, but for the sake of the tutorial we'll just do this::

   sudo apt install -y virtualenvwrapper

Next you must add the following to your ``~/.bashrc`` file::

   export WORKON_HOME=/srv/envs
   source /usr/share/virtualenvwrapper/virtualenvwrapper.sh

And finally you must "re-run" your ``.bashrc`` so these things actually take
effect for your current session::

   source ~/.bashrc

Confirming It Works
^^^^^^^^^^^^^^^^^^^

First of all just to be 100% sure, you ideally should reboot your new machine,
or perhaps at least logout and then login again.

But really the check here, is to make sure the following command runs okay::

   workon --help

PostgreSQL
----------

Rattail uses `PostgreSQL`_ exclusively, for its "primary" database backend.  So
whereas Rattail can interact with many other types of SQL databases, it uses
Postgres for its "own" database(s).

.. _PostgreSQL: https://www.postgresql.org/

Technically the database is optional, depending on how you need to use Rattail,
although it is required for the web app.

Setting It Up
^^^^^^^^^^^^^

There are really two aspects of this setup, a) Postgres proper, and b) Python
support for Postgres.

We'll tackle the first aspect, well, first::

   sudo apt install -y postgresql

Next we'll tackle the second aspect::

   sudo apt install -y libpq-dev

Confirming It Works
^^^^^^^^^^^^^^^^^^^

As with the setup for Postgres, there are really two things to check here.

First, is the PostgreSQL service running and available?  You should be able to
confirm that with (should output list of databases)::

   sudo -u postgres psql -l

Second, is Python support for Postgres installed correctly?

.. todo::
   what else should we say about the second aspect here?  other than, TBD
   (aka. "when you need it you'll know")
