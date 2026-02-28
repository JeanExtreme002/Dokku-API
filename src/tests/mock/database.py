import datetime
import functools
from unittest.mock import AsyncMock, MagicMock, patch

from src.api.models import App, Network, Service, User
from src.api.schemas import UserSchema
from src.api.tools import hash_access_token

MockUser = UserSchema(
    id=1,
    email="test@example.com",
    access_token="abc123",
    access_token_expiration=datetime.datetime.now(datetime.timezone.utc)
    + datetime.timedelta(days=7),
    is_admin=False,
    created_at="2023-01-01T00:00:00Z",
    apps_quota=1,
    services_quota=1,
    networks_quota=1,
)

MockApp = App(name="test-app", deploy_token="deploy123", user_email=MockUser.email)
MockService = Service(name="test-service", user_email=MockUser.email)
MockNetwork = Network(name="test-network", user_email=MockUser.email)


def mock_all_models(test_func):
    @functools.wraps(test_func)
    async def wrapper(*args, **kwargs):
        with patch("src.api.models.session.AsyncSessionLocal") as mock_sessionmaker:
            mock_session = AsyncMock()
            mock_sessionmaker.return_value.__aenter__.return_value = mock_session

            user = User(
                id=MockUser.id,
                email=MockUser.email,
                access_token=hash_access_token(MockUser.access_token),
                access_token_expiration=MockUser.access_token_expiration,
                is_admin=MockUser.is_admin,
                created_at=MockUser.created_at,
                apps_quota=MockUser.apps_quota,
                services_quota=MockUser.services_quota,
                networks_quota=MockUser.networks_quota,
            )
            app = MockApp
            service = MockService
            network = MockService

            user.apps = [app]
            user.services = [service]
            user.networks = [network]

            def execute_side_effect(statement):
                mock_result = MagicMock()
                entity = None

                if hasattr(statement, "column_descriptions"):
                    entity = statement.column_descriptions[0].get("entity")

                where = getattr(statement, "_where_criteria", ())

                def iter_criteria(criteria):
                    for item in criteria:
                        clauses = getattr(item, "clauses", None)
                        if clauses is not None:
                            for clause in clauses:
                                yield clause
                        else:
                            yield item

                def get_column_and_value(crit):
                    left_name = getattr(crit.left, "name", None)
                    right_name = getattr(crit.right, "name", None)
                    left_value = getattr(crit.left, "value", None)
                    right_value = getattr(crit.right, "value", None)

                    if left_name is not None:
                        return left_name, right_value
                    if right_name is not None:
                        return right_name, left_value
                    return None, None

                if entity == User:
                    if not where:
                        mock_result.scalar_one_or_none.return_value = user
                        mock_result.scalars.return_value.all.return_value = [user]
                    else:
                        found_identity = False
                        expiration_ok = True
                        for crit in iter_criteria(where):
                            try:
                                column_name, value = get_column_and_value(crit)
                                if value in [
                                    MockUser.email,
                                    hash_access_token(MockUser.access_token),
                                ]:
                                    found_identity = True
                                if column_name == "access_token_expiration" and value:
                                    expiration_ok = (
                                        MockUser.access_token_expiration > value
                                    )
                            except Exception:
                                continue
                        if found_identity and expiration_ok:
                            mock_result.scalar_one_or_none.return_value = user
                            mock_result.scalars.return_value.all.return_value = [user]
                        else:
                            mock_result.scalar_one_or_none.return_value = None
                            mock_result.scalars.return_value.all.return_value = []
                    return mock_result

                if entity == App:
                    for crit in where:
                        try:
                            value = getattr(crit.right, "value", None)
                            if value in ["test-app", "deploy123"]:
                                mock_result.scalar_one_or_none.return_value = app
                                return mock_result
                        except Exception:
                            continue
                    mock_result.scalar_one_or_none.return_value = None
                    return mock_result

                mock_result.scalar_one_or_none.return_value = None
                mock_result.scalars.return_value.all.return_value = []
                return mock_result

            mock_session.execute.side_effect = execute_side_effect

            return await test_func(
                *args,
                user=user,
                app=app,
                service=service,
                network=network,
                mock_session=mock_session,
                mock_sessionmaker=mock_sessionmaker,
                **kwargs,
            )

    return wrapper
