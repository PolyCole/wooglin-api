from django.test import TestCase
from restapi.models.members import Member
from django.contrib.auth.models import User


class BasicTests(TestCase):
    def setUp(self):
        user_account = User.objects.create_user("pparker", "peter@avengers.com", "totallyNotSpiderman")

        Member.objects.create(
            user=user_account,
            name="Pete Parker",
            first_name="Pete",
            last_name="Parker",
            legal_name="Peter Parker",
            address="123 Spiderman Street",
            email="peter@avengers.com",
            phone="123.456.7890",
            rollnumber="1",
            member_score="45.5",
            inactive_flag=False,
            abroad_flag=False,
            present=5,
            position="Member"
        )

    def test_duplicate_user_accounts(self):
        """
        Checking to make sure that one user account belongs to exactly one member account.
        """

        self.assertEqual(User.objects.count(), 1)
        user_account = User.objects.get(username='pparker')

        flag = False
        try:
            self.assertEqual(Member.objects.count(), 1)
            Member.objects.create(
                user=user_account,
                name="Tony Stark",
                first_name="Tony",
                last_name="Stark",
                legal_name="Anthony Stark",
                address="123 Avengers Tower",
                email="ironman@avengers.com",
                phone="123.456.7898",
                rollnumber="2",
                member_score="2323",
                inactive_flag=False,
                abroad_flag=False,
                present=5,
                position="Member"
            )
        except:
            flag = True

        self.assertTrue(flag)
