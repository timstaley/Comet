.. _sec-history:

Release History
===============

See the :ref:`release procedure <sec-release>` section for more details on
version numbering and how releases are made.

Version 2.0.0
-------------

2.0.0 (2016-01-31) [`Download <//github.com/jdswinbank/Comet/tarball/2.0.0>`__]
    Switch dependency from `ipaddr-py`_ to `py2-ipaddress`_. The latter is a
    backport of the Python 3 functionality, so this helps clear the way for an
    eventual Python 3 version of Comet.

    Use the ``$TMPDIR`` environment variable, if set, to store the event
    database. Otherwise, fall back to ``tmp``.

    Drop support for Python 2.6, following the same change made in Twisted.

    Improve checking for valid IVORNs.

    Some extremely old versions of Comet (dating from before the 1.0.0
    release) used a different format for the database of seen events. All
    released versions through 1.2.2 automatically update old-style databases
    to the new format when run. As of this release, this support for legacy
    databases has been dropped. It is necessary to use a previous Comet
    release to update the database format before upgrading to this version.

    Refactor the codebase caused a minor API change: logging facilities are
    now available from the ``comet.log`` module. End user code — notably event
    handling plugins — should replace statements to the effect of ``from
    comet.utility import log`` with ``import comet.log as log``. The
    convenience aliases ``log.msg`` and ``log.warning`` have been removed: use
    ``log.info`` and ``log.warn`` instead.

.. _ipaddr-py: https://code.google.com/p/ipaddr-py/
.. _py2-ipaddress: https://bitbucket.org/kwi/py2-ipaddress/

Version 1.2.x
-------------

1.2.2 (2015-04-20) [`Download <//github.com/jdswinbank/Comet/tarball/1.2.2>`__]
    Disable XML entity expansion for documents received from the network.
    This eliminates a class of potential resource exhaustion attacks.

    Update documentation to request citation of the `paper`_ in published work
    which makes use of Comet.

1.2.1 (2014-09-02) [`Download <//github.com/jdswinbank/Comet/tarball/1.2.1>`__]
    Correctly check that the (required) ``--local-ivo`` command line option
    was provided (`GitHub #35`_).

1.2.0 (2014-08-26) [`Download <//github.com/jdswinbank/Comet/tarball/1.2.0>`__]
    When subscribing to a remote broker, we wait for a short period after the
    initial connection is made before marking it as successful. This means
    that if the broker rapidly drops the connection (e.g. due to an
    authentication failure), we retry the connection with an exponential
    back-off rather than an immediate reconnection (`GitHub #29`_).

    Timestamps in ``iamalive`` messages are marked as being in UTC.

    ``authenticate`` messages which specify XPath filters are schema
    compliant (`GitHub #31`_).

    Subscriber refuses to start if an XPath ``--filter`` is specified with
    invalid syntax (`GitHub #33`_).

    Require that a valid IVOA identifier (IVORN) be supplied by the end user
    when starting Comet rather than relying on a default.

    Require that events submitted to the broker by authors have valid IVORNs.

.. _paper: http://adsabs.harvard.edu/abs/2014A%26C.....7...12S
.. _GitHub #29: https://github.com/jdswinbank/Comet/issues/29
.. _GitHub #31: https://github.com/jdswinbank/Comet/issues/31
.. _GitHub #33: https://github.com/jdswinbank/Comet/issues/33
.. _GitHub #35: https://github.com/jdswinbank/Comet/issues/33


Version 1.1.x
-------------

1.1.2 (2014-08-26) [`Download <//github.com/jdswinbank/Comet/tarball/1.1.2>`__]
    Fix a bug which could result in malformed event IVORNs exhausting the
    available resources and ultimately rendering Comet unable to process more
    events (`GitHub #34`_).

1.1.1 (2014-07-08) [`Download <https://github.com/jdswinbank/Comet/tarball/1.1.1>`__]
    Fix a bug which could result in the same VOEvent message being processed
    multiple times (`GitHub #30`_).

    Add compatibility with DBM-style databases which do not provide an
    ``.items()`` method.

1.1.0 (2014-02-26) [`Download <https://github.com/jdswinbank/Comet/tarball/1.1.0>`__]
    Improved documentation.

    Interval between broadcast test events is user configurable, and they may
    be disabled. See the ``--broadcast-test-interval`` option.

    Test events now include details of the version of Comet used to generate
    them.

    Event handler plugin system reworked. Plugins may now take command line
    options. See the :ref:`event handler documentation <sec-handlers>` for
    details. Note that the syntax for invoking the ``print-event`` handler has
    changed (now ``--print-event`` rather than ``--action=print-event``).

    Plugin which writes events received to file (``--save-event``).

.. _GitHub #30: https://github.com/jdswinbank/Comet/issues/30
.. _GitHub #34: https://github.com/jdswinbank/Comet/issues/34


Version 1.0.x
-------------

1.0.4 (2013-11-13) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.4>`__]
   ``comet-sendvo`` will choose its Python interpreter based on the
   environment.

1.0.3 (2013-11-12) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.3>`__]
   Update ``MANIFEST.in`` so that ``requirements.txt`` is included in the
   distribution. This changes nothing on an installed system.

1.0.2 (2013-11-12) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.2>`__]
   Add a ``requirements.txt`` file and specify the installation requirements
   in ``setup.py``. This makes installation easier, but changes nothing on an
   installed system.

1.0.1 (2012-08-28) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.1>`__]
   Fix for badly formed XML ``Transport`` element.

1.0.0 (2012-08-27) [`Download <https://github.com/jdswinbank/Comet/tarball/1.0.0>`__]
   Initial public release


Future Plans
------------

* Cryptographic authentication of VOEvent messages and subscribers.
* Port to Python 3.
