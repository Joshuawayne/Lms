# SOLID and dependency boundaries

Single responsibility: route handlers map HTTP; application use cases coordinate
workflows; domain code expresses rules; infrastructure implements external access.

Open/closed: extend block registries, rule strategies and provider adapters through
focused contracts. Avoid a central conditional containing every activity or provider.

Liskov substitution: implementations must honor the documented behavior, failures
and consistency guarantees of the interface they implement.

Interface segregation: define only the capabilities a consumer needs. Avoid a generic
repository interface requiring every module to implement unrelated CRUD operations.

Dependency inversion: application/domain code depends on suitable contracts, with
concrete adapters wired at bootstrap. Protocols and functions are appropriate; not
every function needs a class or separate interface file.

Import-linter enforces initial domain/application restrictions in `backend/pyproject.toml`.
Domain code cannot import HTTP/database libraries or application/API/infrastructure
packages. Application use cases cannot import HTTP/database libraries or concrete
API/infrastructure adapters. Add further contracts as public module interfaces evolve.

Keep shared code small and stable. Cross-module workflows should use intentional
interfaces; review dependency direction and transaction ownership explicitly.
