
Hide / Disable Unwanted Web Views
=================================

The first thing we'll want to do is take stock of the views currently exposed
by the web app, and either hide or outright "remove" any we don't want (yet).

There are sort of 3 different aspects to whether or not a particular web view
is "available" for a given user:

* is the view even defined?
* does user have permission to access the view?
* is there a menu (or other) link to the view?

Removing a (Master) View
------------------------

There are a few "core" web views which will "always" be defined, but the vast
majority are really optional.  The so-called "master" web views, each of which
basically corresponds to a particular table in the DB, are (almost?) entirely
optional.  For instance if your organization needs to track customers but not
products, within your Poser app, then you might go so far as to "remove" the
product views from your app.

If you do this, then e.g. navigating to http://localhost:9080/products/ (or
whatever your URL is) would result in a 404 not found error regardless of user
permissions, i.e. even if you "become root".  However by default (using code
generated via scaffold) the product views *are* enabled, so this URL *would*
work.

Whether or not a given view(s) is "defined" will depend on whether or not the
module containing this view(s) has been "included" by the Pyramid (web app)
Configurator object.  In other words we're leveraging this "include" concept
from `Pyramid`_ in order to control which views are brought into the running
app.

.. _Pyramid: https://trypyramid.com/

In practice what that means is usually just that you must curate the list of
views which are included, within your own project.  This config thing works
recursively, but we try to keep the primary list within a conventional place.
In our (tutorial's) case this file is at
``~/src/rattail-tutorial/rattail_tutorial/web/views/__init__.py`` and by
default (freshly generated via scaffold) it looks something like this::

   def includeme(config):

       # core views
       config.include('rattail_tutorial.web.views.common')
       config.include('tailbone.views.auth')
       config.include('tailbone.views.tables')
       config.include('tailbone.views.upgrades')
       config.include('tailbone.views.progress')

       # main table views
       config.include('tailbone.views.brands')
       config.include('tailbone.views.customers')
       config.include('tailbone.views.customergroups')
       config.include('tailbone.views.datasync')
       config.include('tailbone.views.departments')
       config.include('tailbone.views.email')
       config.include('tailbone.views.employees')
       config.include('tailbone.views.messages')
       config.include('tailbone.views.people')
       config.include('tailbone.views.products')
       config.include('tailbone.views.reportcodes')
       config.include('tailbone.views.roles')
       config.include('tailbone.views.settings')
       config.include('tailbone.views.shifts')
       config.include('tailbone.views.stores')
       config.include('tailbone.views.subdepartments')
       config.include('tailbone.views.users')
       config.include('tailbone.views.vendors')

       # batch views
       config.include('tailbone.views.handheld')
       config.include('tailbone.views.inventory')

In our case the only thing we'll remove for now is the "shifts" entry, i.e. we
wish to remove the line that says::

   config.include('tailbone.views.shifts')

That's because these views have to do with staff scheduling and time clock
stuff, which (at least for now) we won't concern ourselves with.

Note that the underlying *tables* which might contain such data, are left in
place within our database.  We're just declaring that we do not need our web
app to support master views for interacting with those tables.
