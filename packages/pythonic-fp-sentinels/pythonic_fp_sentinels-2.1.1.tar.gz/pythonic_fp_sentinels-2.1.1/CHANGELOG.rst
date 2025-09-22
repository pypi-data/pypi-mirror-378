CHANGELOG
=========

PyPI pythonic-fp-sentinels project.

Semantic Versioning
-------------------

Strict 3 digit semantic versioning

- **MAJOR** version incremented for incompatible API changes
- **MINOR** version incremented for backward compatible added functionality
- **PATCH** version incremented for backward compatible bug fixes

See `Semantic Versioning 2.0.0 <https://semver.org>`_.

Releases and Important Milestones
---------------------------------

PyPI 2.1.0 - 2025-08-28
~~~~~~~~~~~~~~~~~~~~~~~

Corrected some documentation irregularities.

PyPI v2.0.0 - 2025-08-27
~~~~~~~~~~~~~~~~~~~~~~~~

First PyPI release as pythonic-fp-sentinels.

New Repo - 2025-08-14
~~~~~~~~~~~~~~~~~~~~~

GitHub repo renamed pythonic-fp-sentinels. The singletons
effort will be continued as the sentinel package. The PyPI
pythonic-fp-singletons project is deprecated in favor of 
the pythonic-fp-sentinels project.

Update - 2025-08-14
~~~~~~~~~~~~~~~~~~~

Last development version as pythonic-fp-singletons.

- moved module pythonic_fp.singletons.sbool to pythonic_fp.booleans

  - module ``singletons.sbool`` refactored into modules ``subtypable_bool`` and ``flavored_bool``

- removed pythonic_fp.nada module

  - learned a lot about Python getting it to work
  - decided its use case was not worth the effort to maintain it

- extended class Singleton

  - from declaring multiple singletons with strings
  - to declaring multiple "flavors" of any hashable type

PyPI v1.0.0 - 2025-08-02
~~~~~~~~~~~~~~~~~~~~~~~~

Moved singletons.py from fptools. Also incorporated bool.py
into the singleton's package.
