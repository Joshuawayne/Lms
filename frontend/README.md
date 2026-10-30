# Jjenga Code frontend

Nuxt 4, Vue 3, Nuxt UI, Tailwind CSS and Pinia. The frontend owns its dependency lockfile.
The root npm package owns shared tooling. From the project root:

```powershell
npm ci
npm ci --prefix frontend
npm run postinstall --prefix frontend
npm run frontend:dev
```

The only implemented page is the development connectivity check. Portal and feature
folders are reserved for later work. There is no login or role-selection simulation.

`NUXT_PUBLIC_API_BASE_URL` configures the browser-visible API base URL. Database URLs,
authentication secrets, file-storage credentials and third-party secrets belong in
the backend environment. The API client currently omits credentials until the
authentication/session contract is decided. Frontend route middleware will be a
navigation convenience; FastAPI will enforce record-level access.

`app/stores` contains Pinia stores. Avoid global Pinia singletons, credentials in
stores, or persistence of sensitive records. Feature components and composables use
explicit imports; shared Nuxt components/composables live in their native folders.

API types in `app/api/generated/types.ts` are generated from the exported FastAPI
contract. Run `npm run contracts:generate` after intentional API changes.
