# CryptPad Local Compose Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a fully local CryptPad stack that uses the official two-origin model with Docker Compose and can be started with one command.

**Architecture:** Run CryptPad behind Nginx with `cryptpad.localhost` and `sandbox.cryptpad.localhost`, generate a local certificate covering both names, and persist all application data in bind mounts that are ready for later integration into a larger Compose deployment.

**Tech Stack:** Docker Compose, Docker multi-stage builds, CryptPad 2025.9.0, Nginx, OpenSSL, shell entrypoints

---

### Task 1: Scaffold the local deployment layout

**Files:**
- Create: `compose.yaml`
- Create: `.gitignore`
- Create: `README.md`
- Create: `config/config.js`
- Create: `customize/application_config.js`
- Create: `docker/cryptpad/Dockerfile`
- Create: `docker/cryptpad/docker-entrypoint.sh`
- Create: `docker/nginx/Dockerfile`
- Create: `docker/nginx/nginx.conf`
- Create: `docker/scripts/generate-local-cert.sh`
- Create: `docker/scripts/prepare-bind-mounts.sh`

**Step 1: Write the failing configuration check**

Run: `docker compose config`

Expected: FAIL because the Compose file does not exist yet.

**Step 2: Write the minimal deployment files**

Create the Compose stack, custom images, runtime config, and helper scripts needed for local TLS and writable storage.

**Step 3: Run configuration check**

Run: `docker compose config`

Expected: PASS and render a valid Compose model.

### Task 2: Build and start the stack

**Files:**
- Modify: `compose.yaml`
- Modify: `docker/cryptpad/Dockerfile`
- Modify: `docker/nginx/Dockerfile`
- Modify: `docker/nginx/nginx.conf`

**Step 1: Write the failing startup check**

Run: `docker compose up -d --build`

Expected: If anything is missing, a build or startup error should identify the missing dependency or config.

**Step 2: Fix startup issues minimally**

Adjust the image or Compose wiring until all services start cleanly.

**Step 3: Verify running services**

Run: `docker compose ps`

Expected: CryptPad and Nginx are running, while one-shot init services have exited successfully.

### Task 3: Verify local-domain behavior

**Files:**
- Modify: `README.md`

**Step 1: Write the failing HTTP checks**

Run: `curl -kI https://cryptpad.localhost`

Expected: FAIL until the proxy and certificate are working.

**Step 2: Make the minimum fixes**

Adjust proxying, certificates, or origin config until both hostnames respond over HTTPS.

**Step 3: Verify the main and sandbox origins**

Run:

- `curl -kI https://cryptpad.localhost`
- `curl -kI https://sandbox.cryptpad.localhost`

Expected: Both return successful HTTPS responses.

### Task 4: Capture operator workflow

**Files:**
- Modify: `README.md`

**Step 1: Document first-run flow**

Add the commands and URLs needed to:

- start the stack
- retrieve the onboarding URL from logs
- visit the `/checkup/` page
- understand the browser warning for the local certificate

**Step 2: Verify the documented commands**

Run:

- `docker compose logs --no-color cryptpad`
- `docker compose ps`

Expected: The documented flow matches the working stack.
