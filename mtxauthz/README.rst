==========
rmmtxauthz
==========

Do HTTP based authz for MediaMTX


Docker
------

For more controlled deployments and to get rid of "works on my computer" -syndrome, we always
make sure our software works under docker.

It's also a quick way to get started with a standard development environment.

SSH agent forwarding
^^^^^^^^^^^^^^^^^^^^

We need buildkit_::

    export DOCKER_BUILDKIT=1

.. _buildkit: https://docs.docker.com/develop/develop-images/build_enhancements/

And also the exact way for forwarding agent to running instance is different on OSX::

    export DOCKER_SSHAGENT="-v /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock -e SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock"

and Linux::

    export DOCKER_SSHAGENT="-v $SSH_AUTH_SOCK:$SSH_AUTH_SOCK -e SSH_AUTH_SOCK"

Creating a development container
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Build image, create container and start it::

    docker build --ssh default --target devel_shell -t rmmtxauthz:devel_shell .
    docker create --name rmmtxauthz_devel -v "$(pwd)/rune/output/rune.json:/opt/templates/mediamtx.json" -v "$(pwd):/app" -it $(echo $DOCKER_SSHAGENT) rmmtxauthz:devel_shell
    docker start -i rmmtxauthz_devel

pre-commit considerations
^^^^^^^^^^^^^^^^^^^^^^^^^

If working in Docker instead of native env you need to run the pre-commit checks in docker too::

    docker exec -i rmmtxauthz_devel /bin/bash -c "prek install"
    docker exec -i rmmtxauthz_devel /bin/bash -c "prek run --all-files"

You need to have the container running, see above. Or alternatively use the docker run syntax but using
the running container is faster::

    docker run --rm -it -v "$(pwd):/app" rmmtxauthz:devel_shell -c "prek run --all-files"

Test suite
^^^^^^^^^^

You can use the devel shell to run py.test when doing development, for CI use
the "tox" target in the Dockerfile::

    docker build --ssh default --target tox -t rmmtxauthz:tox .
    docker run --rm -it -v "$(pwd):/app" $(echo $DOCKER_SSHAGENT) rmmtxauthz:tox

Production docker
^^^^^^^^^^^^^^^^^

There's a "production" target as well for running the application, remember to change that
architecture tag to arm64 if building on ARM::

    docker build --ssh default --target production -t rmmtxauthz:amd64-latest .
    docker run -it --name rmmtxauthz rmmtxauthz:amd64-latest

Development
-----------

TLDR:

- change to a branch::

    git checkout -b my_branch

- install uv: https://docs.astral.sh/uv/getting-started/installation/
- Install project deps and pre-commit hooks::

    uv sync
    git add uv.lock
    uv run prek install
    uv run prek run --all-files

- Use the project virtual environment::

    source .venv/bin/activate

If you get weird errors about missing packages from prek try running it with "uv run prek".

- Ready to go.

Remember to activate your virtualenv whenever working on the repo, this is needed
because mypy hook uses the "system" python for now (to account for required dependencies).

Running "prek run --all-files" and "py.test -v" regularly during development and
especially before committing will save you some headache.

Versioning
----------

Versioning is handled with bump-my-version_. To increment, use ``bump-my-version bump <patch/minor/major>``.

You can use ``bump-my-version show-bump`` to see how each option would affect the version.

.. _bump-my-version: https://github.com/callowayproject/bump-my-version
