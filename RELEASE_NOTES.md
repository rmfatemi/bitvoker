### What's changed?

This release adds web UI authentication, TCP message token verification, improved socket reliability, and modernizes the build system. This update is fully backwards compatible — existing deployments can update without any configuration changes.

- **Web UI Authentication**: Protect the web interface with username/password login. Set `BITVOKER_USERNAME` and `BITVOKER_PASSWORD` environment variables to enable. When not set, the UI remains open as before.
- **TCP Message Authentication**: Configure a `message_token` in settings to require a token prefix (`TOKEN:secret:message`) on incoming TCP messages. Messages without a valid token are rejected. When no token is configured, all messages are accepted as before.
- **Socket Reading Fix**: Fixed an unreliable socket reading mechanism that could truncate messages under certain network conditions (SSL fragmentation, slow connections). Messages of any size are now read reliably on both TCP and TLS.
- **Frontend Package Updates**: Updated Material UI to v6, DataGrid to v7, and all other frontend dependencies to their latest versions.
- **Build System Migration**: Replaced Poetry with setuptools and pip for simpler dependency management and faster builds.
- **Docker Image Optimization**: Added `.dockerignore` and improved the multi-stage build to reduce image size and build time.
- **Test Coverage**: Added 85 unit tests covering all modules (auth, config, database, handler, matcher, notifier, router, AI, utils).
