from custodia.domain.identity import Principal, Role


class FakePrincipal:
    """Returns a fixed staff principal — for local development and testing only."""

    def load(self) -> Principal:
        return Principal(
            subject="fake-subject-001",
            email="staff@example.com",
            roles=frozenset([Role.STAFF]),
        )
