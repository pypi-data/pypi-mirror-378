
=============
 Quick Start
=============

.. highlight:: sh

WuttaPOS is a `Python`_ app based on `Rattail`_.

.. _Python: https://www.python.org/
.. _Rattail: https://rattailproject.org/

As such it requires a Rattail DB to already be established, containing
data for users (cashiers), customers, products etc.  Getting all that
setup is outside the scope of this guide; for more info see the
`Rattail Manual`_.

.. _Rattail Manual: https://rattailproject.org/docs/rattail-manual/

Here we are focused only on getting the WuttaPOS app setup.


Installation
------------

Make a virtual environment::

   python -m venv /srv/envs/wuttapos

Install the WuttaPOS package into it::

   cd /srv/envs/wuttapos
   bin/pip install WuttaPOS


Configuration
-------------

Make a basic config file::

   cd /srv/envs/wuttapos
   bin/rattail make-config -T rattail -O app

Then edit ``app/rattail.conf`` to suit your needs.  In particular you
must specify the DB connection.


Usage
-----

Now you can run the app::

   cd /srv/envs/wuttapos
   bin/wuttapos open


Access Control
--------------

Note that the app will only allow a user to login to POS, if they have
permissions specific to the POS, namely "ring sales"
(``pos.ring_sales``).

Once logged in, additional POS-specific permissions will determine
whether the user may perform some actions, or not.  In the latter case
the user may *initiate* the action but then another user
(e.g. manager) must login to complete the action.

All permissions must be managed externally, e.g. via your Rattail
back-office web app.  WuttaPOS will honor them but does not expose a
way to manage them.
