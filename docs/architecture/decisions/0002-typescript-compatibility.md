# TypeScript compatibility

The frontend pins TypeScript 5.9.3 so the Nuxt/Vue and ESLint tooling share a compatible
JavaScript compiler API. The current ESLint dependency chain failed when given the
TypeScript 7 package. Upgrade the compiler together with the tools that consume it,
and verify linting, Nuxt type checking, tests and the production build.
