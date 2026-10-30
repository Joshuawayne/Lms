# Patched esbuild dependency

Nuxt UI's font tooling pulls esbuild through `fontless`, whose declared range
currently selects an affected 0.27 release. The frontend npm override selects 0.28.2,
which fixes the maintainer's Windows development-server advisory:
https://github.com/evanw/esbuild/security/advisories/GHSA-g7r4-m6w7-qqqr

The application disables remote font loading. The override also keeps the installed
dependency tree on the patched version. Verify the frontend build, types and tests
after changing this override, and remove it when the upstream dependency range allows
a patched release naturally. This is a dependency decision, not a claim that the
complete LMS security model has been implemented.

The frontend and root tooling use independent npm dependency roots and lockfiles.
This avoids the observed workspace-link override bug documented by npm:
https://github.com/npm/cli/issues/9659

Run `npm ci` at the repository root and `npm ci --prefix frontend` for the app. The
PowerShell setup script performs both installations. API contracts remain shared.
