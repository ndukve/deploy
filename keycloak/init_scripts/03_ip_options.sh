#!/usr/bin/env -S /bin/bash
export JAVA_OPTS_APPEND="${JAVA_OPTS_APPEND:-} -Djava.net.preferIPv4Stack=true -Djava.net.preferIPv6Stack=false"
