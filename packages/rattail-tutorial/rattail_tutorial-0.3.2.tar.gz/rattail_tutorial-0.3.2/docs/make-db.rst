
.. highlight:: sh

Establish Main App Database
===========================

Now that you have a hang of how to use the Rattail-style command line
(somewhat), let's move on to the database.

The main reason to wait until now to add a DB to the mix, was simply to show
that the "core" of Rattail does not need a DB.  However in practice there *are*
definitely some commands which Rattail comes with out of the box, and which
also would require one or even multiple databases to be present.


Create User for PostgreSQL 
--------------------------

Before we make our database, let's first establish a user account within
Postgres, which we will designate as the "owner" of our database(s).

It is convention within Rattail, to create a PG user named "rattail" for this
purpose.  You are free to use another name if you prefer::

   sudo -u postgres createuser --no-createdb --no-createrole --no-superuser rattail

You also should declare a password for the user::

   sudo -u postgres psql -c "alter user rattail password 'newpassword'"


Create Database
---------------

Now that we know who to use as the "owner" we will create a new Postgres
database::

   sudo -u postgres createdb --owner rattail rattut

Of course we named our database "rattut" here only because we're assuming this
tutorial project is the app, but your name may be different.

At this point you should update your ``app/rattail.conf`` file to reflect your
chosen database name and user credentials:

.. code-block:: ini

   [rattail.db]
   default.url = postgresql://rattail:newpassword@localhost/rattut


Install DB Schema
-----------------

So you have a DB but it’s empty; you can confirm that with::

   sudo -u postgres psql -c '\d' rattut

But we'll fix that now. Schema is managed entirely via Alembic "version"
scripts, so to install the schema we merely run all the scripts::

   cdvirtualenv
   bin/alembic -c app/rattail.conf upgrade heads

(Note that you must use ``rattail.conf`` for that; ``quiet.conf`` won't work.)

If you check the DB again you should see a good amount of tables.


.. _make-user:

Create Admin User in DB
-----------------------

We include this here not so much because you *need* an admin user in your DB at
this point (although you will for the web app), but rather just to confirm that
everything is setup correctly thus far.

You currently should have no users in your DB::

   sudo -u postgres psql -c 'select * from "user"' rattut

Okay then let's make an admin user for you::

   bin/rattail -c app/quiet.conf make-user --admin myusername

Now if you query the ``user`` table again you should see your new account.
