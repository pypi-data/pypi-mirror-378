
.. highlight:: sh

Run the Web App
===============

At this point we assume you already have a project installed to your
virtualenv, and have done basic configuration as well as established your app
database.


Make/Edit Config
----------------

If you've been following along with this tutorial you may have already done
this step, but in any case we'll revisit now.

If you do *not* yet have a file at e.g. ``/srv/envs/rattut/app/web.conf`` then
you should now run::

   cdvirtualenv app
   rattail make-config -T web

Then you must edit the generated file, looking for TODO notes and such, and
generally tweaking things to your liking.


Start the Web App
-----------------

The web app is effectively a daemon, in that it's meant to be a long-running
process which continues to listen for and respond to incoming requests.

In production, this may be wired up in various ways, but for now we're only
concerned with development, where we'll be starting the web app "server" from
command line::

   cdvirtualenv
   bin/pserve --reload file+ini:app/web.conf

Note that this command will "block" - meaning control will not immediately fall
back to your shell prompt.  You may use Ctrl+C whenever you like, to kill the
web app.


Browse the Web App
------------------

This will only work when the above ``pserve`` command is running, but assuming
it is currently, you can access the web app at http://localhost:9080/

Note that the default ``web.conf`` specifies 9080 as the port on which the web
app will listen.  You can modify this as needed, but if you do, and are also
using Vagrant, you may also need to modify your ``Vagrantfile`` (and do a
``vagrant reload``).


Login to Web App
----------------

If you've been following along with the tutorial then you probably have already
created an admin account for yourself.  But in case you haven't, please see
:ref:`make-user`.

Once that's set then you should be able to login to the web app with those same
credentials.

The very first thing you see is likely "not much" - most of the menu will be
hidden to you, since by default you do not have sufficient permissions to
access the features they represent.

However you are an "admin" user - which really just means your user account
belongs to the special "Administrators" role.  This role is special in that
anyone who belongs to it, is given an extra "Become Root" option in the menu.
This works similarly to the Linux "root" concept, in that if you become root,
you will be implicitly granted *all* permissions and nothing will be hidden
from you.  This lasts until you "stop being root" or logout.
