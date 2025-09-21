
=====
Menus
=====

The default POS screen uses a "master menu" control to draw all button
menus on the right half of the screen.

This area is further broken down into 4 quadrants, each of which is
managed by a "menu" control.  These quadrants are:

* ``tenkey`` (top left)
* ``meta`` (top right)
* ``context`` (bottom left)
* ``suspend`` (bottom right)

.. warning::

   These names will likely change, as well as (possibly) the overall
   structure.  Things are being documented as-is for now.


Custom Menus
------------

You may override any of the above quadrant menu controls by specifying
your preferred control in your config file.

Most typically you would override the ``context`` menu:

.. code-block:: ini

   [wuttapos.menus]
   context.spec = poser.menus.context:PoserContextMenu

Of course that is after you have defined ``PoserContextMenu`` which
should be a subclass of :class:`wuttapos.controls.menus.WuttaMenu`.


Dynamic Context Menu
--------------------

The default ``context`` menu is actually empty; all the more reason
you would want to override it as described in the previous section.

But this quadrant is special in that the POS expects that menu to be
"swapped out" dynamically based on user action.

The way this works is to invoke the POS command named ``context_menu``
and specify the "key" of the menu you wish to show.  This is generally
wired up to a button, so clicking the button would show a certain
menu::

   from wuttapos.controls.menus import WuttaMenu

   class PoserContextMenu(WuttaMenu):

       def build_controls(self):
           return [

               self.make_button_row([

                   self.make_button("SHOW STUFF",
                                    bgcolor='yellow',
                                    pos_cmd='context_menu',
                                    pos_cmd_entry='stuff'),
               ]),
           ]

The above would show a menu whose key was ``stuff`` - so your config
must define the spec for this menu as well:

.. code-block:: ini

   [wuttapos.menus]
   stuff.spec = poser.menus.stuff:PoserStuffMenu

And that menu is conceptually no different than the ``context``
example above.  It can show whichever buttons it needs, and it is
usually a good idea for some button(s) to load other menus.  For
example this (``stuff`` menu) includes a "BACK" button to load the
original ``context`` menu::

   from wuttapos.controls.menus import WuttaMenu

   class PoserStuffMenu(WuttaMenu):

       def build_controls(self):
           return [

               self.make_button_row([

                   self.make_button("VOID",
                                    bgcolor='red',
                                    pos_cmd='void_dwim'),

                   self.make_button("BACK",
                                    bgcolor='yellow',
                                    pos_cmd='context_menu',
                                    pos_cmd_entry='context'),
               ]),
           ]
