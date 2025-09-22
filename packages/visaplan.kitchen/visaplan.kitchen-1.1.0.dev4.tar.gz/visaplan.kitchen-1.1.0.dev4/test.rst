.. image:: https://travis-ci.org/visaplan/kitchen.svg?branch=master
       :target: https://travis-ci.org/visaplan/kitchen
.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

================
visaplan.kitchen
================

This package tackles "soup", i.e. trees which are created by the well-known
beautifulsoup4_ package from parsed HTML or XML sources.
It might be possible to accomplish the same by using lxml_ directly,
but it might have been more difficult, and thus it is left to another
package.

Features
========

- ``spoons`` module, for tackling "soup", e.g.

  - ``has_any_class`` (a filter function to check for one of the given classes)

- ``forks`` module
  (named mainly for historical reasons; for poking around in the soup), e.g.
  ``extract_linktext``, ``convert_dimension_styles``

- ``ids`` module, for creation of new ids for HTML elements

  - ``id_factory``::

        new_id = id_factory(...)
        id = new_id(prefix)


Tests remark
============

The modules are documented and tested by doctests.
However, they currently don't fully work because of import problems;
see the `issue tracker`_.

Help is appreciated.

Examples
========

This add-on can be seen in action at the following sites:

- https://www.unitracc.de
- https://www.unitracc.com


Documentation
=============

For now, the functions are documented by doctests.


Installation
============

Install visaplan.kitchen by adding it to your buildout::

    [buildout]

    ...

    eggs =
        visaplan.kitchen


and then running ``bin/buildout``


Contribute
==========

- Issue Tracker: https://github.com/visaplan/kitchen/issues
- Source Code: https://github.com/visaplan/kitchen


Support
=======

If you are having issues, please let us know;
please use the `issue tracker`_ mentioned above.


License
=======

The project is licensed under the GPLv2.

.. _`issue tracker`: https://github.com/visaplan/kitchen/issues
.. _`beautifulsoup4`: https://pypi.org/project/beautifulsoup4

.. vim: tw=79 cc=+1 sw=4 sts=4 si et


To Do
=====

- .extract module:

  - implement head(words=N) constraint

  - Create generic `wordcount` facility? (after the ``wc`` program;
    count words, characters, and probably lines as well)



Changelog
=========


1.1.0 (unreleased)
------------------

Improvements:

- Improved Python 3 compatibility

New Features:

- `.spoons.swap_classes`, supporting both `add` and `remove` options,
  and by default removing an empty `class` attribute

Requirements:

- Support *(but don't require yet)* visaplan.tools_ v1.4+

Miscellaneous:

- Zope/Plone entry point and ``configure.zcml`` removed,
  which didn't do anything interesting

[tobiasherp]


1.0.5 (2024-04-09)
------------------

New Features:

- .extract.head supports the `verbose` option to
  aid processing of multiple fields; code example included.

Improvements:

- Added a doctest for .extract.head: yes, we accept text/plain as well.

Miscellaneous:

- .extract._head_kwargs: when injecting the fuzz default value, we ignore
  a words restriction now, which may be given additionally;
  only the chars restriction is needed.

[tobiasherp]


1.0.4 (2023-12-21)
------------------

Bugfixes:

- .spoons.stripped_soup raises an IndexError when called with empty content.

[tobiasherp]


1.0.3 (2022-09-20)
------------------

New Features:

- New function .spoons.generate_image_infos

[tobiasherp]


1.0.2 (2021-10-27)
------------------

Improvements:

- Imports sorted by isort_

New Features:

- New ``extract`` module to create extracts of HTML text
  (e.g. a `head`, containing the first NN visible characters)

Requirements:

- lxml_ v3.7.0+ (`collect_ids` argument)
- six_ explicitly required
- visaplan.tools_ v1.3.7+

[tobiasherp]


1.0.1 (2020-02-25)
------------------

- Python_ 3 compatibility (``python-modernize``)
  [tobiasherp]


1.0 (2018-09-17)
----------------

- Initial release.
  [tobiasherp]

.. _isort: https://pypi.org/project/isort
.. _lxml: https://lxml.de
.. _Python: https://www.python.org
.. _six: https://pypi.org/project/six
.. _visaplan.tools: https://pypi.org/project/visaplan.tools

