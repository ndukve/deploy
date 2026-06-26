========
KeyCloak
========

Templates, init container etc to setup keycloak automagically with ENV variables.

Used as git submodule
---------------------

This repo is used as submodule in https://github.com/pvarki/docker-rasenmaeher-integration
it is probably a good idea to handle all development via it because it has docker composition
for bringin up all the other services rasenmaeher-api depends on

Versioning
----------

Versioning is handled with bump-my-version_. To increment, use ``bump-my-version bump build``.

You can use ``bump-my-version show-bump`` to see how each option would affect the version.

  - Major, minor and patch are the Keycloak version
  - Build is change date for *this repo*

.. _bump-my-version: https://github.com/callowayproject/bump-my-version

pre-commit notes
----------------

Make sure pre-commit is installed::

    pre-commit install --install-hooks

And it's a good idea to run it regularly before committing::

    pre-commit run --all-files
