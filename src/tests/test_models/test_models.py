import unittest

from fastapi import HTTPException

from src.api.models.models import (
    create_take_over_access_token,
    create_user,
    delete_user,
    get_app_by_deploy_token,
    get_app_deployment_token,
    get_user,
    get_user_by_access_token,
    get_users,
    update_user,
)
from src.tests.mock import MockUser, mock_all_models


class TestDatabaseModels(unittest.IsolatedAsyncioTestCase):

    @mock_all_models
    async def test_get_user(self, **kwargs):
        result = await get_user(MockUser.email)
        self.assertEqual(result.email, MockUser.email)

    @mock_all_models
    async def test_get_user_not_found(self, **kwargs):
        with self.assertRaises(HTTPException) as context:
            await get_user("notfound@example.com")
        self.assertEqual(context.exception.status_code, 404)
        self.assertEqual(context.exception.detail, "User not found")

    @mock_all_models
    async def test_get_users(self, **kwargs):
        result = await get_users()
        self.assertIn(MockUser.email, result)

    @mock_all_models
    async def test_get_user_by_access_token(self, **kwargs):
        result = await get_user_by_access_token(MockUser.access_token)
        self.assertEqual(result.email, MockUser.email)

    @mock_all_models
    async def test_get_user_by_access_token_invalid(self, mock_session, **kwargs):
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        with self.assertRaises(HTTPException) as context:
            await get_user_by_access_token("invalidtoken")
        self.assertEqual(context.exception.status_code, 401)

    @mock_all_models
    async def test_create_user_already_exists(self, mock_session, **kwargs):
        with self.assertRaises(HTTPException) as context:
            await create_user(MockUser.email, MockUser.access_token)
        self.assertEqual(context.exception.status_code, 400)

    @mock_all_models
    async def test_update_user(self, user, **kwargs):
        new_user = MockUser.copy(update={"email": "new_email@gmail.com"})
        self.assertNotEqual(user.email, new_user.email)

        await update_user(MockUser.email, new_user)
        self.assertEqual(user.email, new_user.email)

    @mock_all_models
    async def test_delete_user(self, **kwargs):
        await delete_user(MockUser.email)

    @mock_all_models
    async def test_get_app_by_deploy_token(self, app, **kwargs):
        result_app, result_user = await get_app_by_deploy_token(app.deploy_token)
        self.assertEqual(result_app.name, app.name)
        self.assertEqual(result_user.email, MockUser.email)

    @mock_all_models
    async def test_get_app_by_deploy_token_not_found(self, mock_session, **kwargs):
        mock_session.execute.return_value.scalar_one_or_none.return_value = None
        with self.assertRaises(HTTPException) as context:
            await get_app_by_deploy_token("invalid_token")
        self.assertEqual(context.exception.status_code, 404)

    @mock_all_models
    async def test_get_app_deployment_token(self, app, **kwargs):
        token = await get_app_deployment_token(app.name)
        self.assertEqual(token, app.deploy_token)

    @mock_all_models
    async def test_create_take_over_access_token(self, user, **kwargs):
        self.assertIsNone(user.take_over_access_token)
        self.assertIsNone(user.take_over_access_token_expiration)

        token = await create_take_over_access_token(user.email)

        self.assertIsNotNone(token)
        self.assertTrue(isinstance(token, str))

        self.assertIsNotNone(user.take_over_access_token)
        self.assertIsNotNone(user.take_over_access_token_expiration)
