========
miniwerk
========

Minimal KRAFTWERK amulation to be able to run a RASENMAEHER+products deployment on any VM

There are some required ENV configs check out example_env.sh for them (.env file is also supported)

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

    docker build --ssh default --target devel_shell -t miniwerk:devel_shell .
    docker create --name miniwerk_devel -v `pwd`":/app" -p 80:80 -it `echo $DOCKER_SSHAGENT` miniwerk:devel_shell
    docker start -i miniwerk_devel

pre-commit considerations
^^^^^^^^^^^^^^^^^^^^^^^^^

Hooks are run via prek_, a drop-in replacement for pre-commit that reuses the same
``.pre-commit-config.yaml``. If working in Docker instead of native env you need to run
the hooks in docker too::

    docker exec -i miniwerk_devel /bin/bash -c "prek install --install-hooks"
    docker exec -i miniwerk_devel /bin/bash -c "prek run --all-files"

You need to have the container running, see above. Or alternatively use the docker run syntax but using
the running container is faster::

    docker run --rm -it -v `pwd`":/app" miniwerk:devel_shell -c "prek run --all-files"

.. _prek: https://github.com/j178/prek

Test suite
^^^^^^^^^^

You can use the devel shell to run py.test when doing development, for CI use
the "tox" target in the Dockerfile::

    docker build --ssh default --target tox -t miniwerk:tox .
    docker run --rm -it -v `pwd`":/app" `echo $DOCKER_SSHAGENT` miniwerk:tox

Production docker
^^^^^^^^^^^^^^^^^

There's a "production" target as well for running the application, remember to change that
architecture tag to arm64 if building on ARM::

    docker build --ssh default --target production -t miniwerk:amd64-latest .
    docker run -it --name miniwerk miniwerk:amd64-latest

Development
-----------

TLDR:

- Create and activate a Python 3.11 virtualenv (assuming virtualenvwrapper)::

    mkvirtualenv -p `which python3.11` my_virtualenv

- change to a branch::

    git checkout -b my_branch

- install uv: https://docs.astral.sh/uv/getting-started/installation/
- Install project deps and git hooks::

    uv sync
    uv run prek install --install-hooks
    uv run prek run --all-files

- Ready to go.

Remember to activate your virtualenv whenever working on the repo, this is needed
because the mypy pre-commit hook uses the "system" python for now (because reasons).

Versioning
----------

Versioning is handled with bump-my-version_. To increment, use ``bump-my-version bump <patch/minor/major>``.

You can use ``bump-my-version show-bump`` to see how each option would affect the version.

.. _bump-my-version: https://github.com/callowayproject/bump-my-version
