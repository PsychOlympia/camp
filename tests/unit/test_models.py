from app.models import User, Team


def test_new_team():
    """
    GIVEN a Team model
    WHEN a new Team is created
    THEN check the name, members fields are defined correctly
    """
    team = Team(name='test_team')
    assert team.name == 'test_team'


def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the username, password_hash fields are defined correctly
    """
    user = User(username='test_user', password_hash='hashed_password')  # noqa
    assert user.username == 'test_user'
    assert user.password_hash == 'hashed_password'
    assert user.team is None


def test_new_user_with_team():
    """
    GIVEN a User model and a Team model
    WHEN a new User is created with a Team
    THEN check the team field is defined correctly and the members field is defined correctly
    """
    team = Team(name='test_team')
    user = User(username='test_user', password_hash='hashed_password', team=team)  # noqa
    assert user.team is not None
    assert user.team.name == 'test_team'
    assert user in team.members
