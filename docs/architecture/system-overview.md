# System overview

One repository contains one Nuxt frontend and one FastAPI backend. FastAPI connects
directly to Supabase PostgreSQL. Nuxt provides rendering, navigation, components and
client state; FastAPI owns LMS rules, permissions and internal API contracts.

The backend is a modular monolith. Each business module has domain, application,
API and infrastructure boundaries. The composition root supplies concrete adapters.
Background workers will reuse application use cases when durable job delivery is chosen.

The custom activity builder/player shares versioned block contracts. A registry
maps supported block types to their editor/renderer implementation. Activity
definitions, published versions, assignments and attempts are distinct concepts.

Identity/session, private object storage, durable jobs and production hosting are
pending decisions. Their reserved directories do not represent selected providers.
BigBlueButton and Gotenberg will have server-side adapters. Blockly belongs in the
activity UI; safe code execution requires a separate resource-limited execution boundary.

Only health APIs, framework composition, error handling and development connectivity
are implemented in this foundation.
