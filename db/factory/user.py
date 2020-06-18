from db import connect
from db.model import User


class UserFactory:
    def get_by_email(self, email):
        """
        Get user by email

        :param str email: user email
        :return: user object
        :rtype: User
        """
        session = connect()

        try:
            return session.query(User) \
                .filter(User.email == email) \
                .first()
        finally:
            session.close()

    def save(self, user):
        """
        Save user
        :param User user: user object
        """
        session = connect()

        try:
            session.add(user)
            session.commit()
        finally:
            session.close()
