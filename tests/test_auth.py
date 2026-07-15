from multiprocessing import Value

import pytest
import requests

from IServAPI.auth import AuthClient
from os import getenv


@pytest.fixture(scope="class")
def auth():
    client = AuthClient(getenv("username"), getenv("password"), "gymsf.de")
    return client


class TestAuth:

    def test_SAT(self, auth):
        assert auth._IServSAT is not None

    def test_SATId(self, auth):
        assert auth._IServSATId is not None

    def test_Session(self, auth):
        assert auth._IServSession is not None

    def test_wrongCredentials(self):

        with pytest.raises(ValueError, match="Login failed! Probably wrong password."):
            AuthClient(
                "ThisUserWillNeverExist1234",
                "NotTheCorrectPassword",
                getenv("iserv_url"),
            )
