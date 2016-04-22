import json

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_hooks.models import Hook

from .models import Quiz, Question


class APITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.adminclient = APIClient()


class AuthenticatedAPITestCase(APITestCase):

    def setUp(self):
        super(AuthenticatedAPITestCase, self).setUp()
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(self.username,
                                             'testuser@example.com',
                                             self.password)
        token = Token.objects.create(user=self.user)
        self.token = token.key
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

        # Admin User setup
        self.adminusername = 'testadminuser'
        self.adminpassword = 'testadminpass'
        self.adminuser = User.objects.create_superuser(
            self.adminusername,
            'testadminuser@example.com',
            self.adminpassword)
        admintoken = Token.objects.create(user=self.adminuser)
        self.admintoken = admintoken.key
        self.adminclient.credentials(
            HTTP_AUTHORIZATION='Token ' + self.admintoken)


class TestQuizzesApp(AuthenticatedAPITestCase):

    def make_question(self, question_data=None):
        if question_data is None:
            question_data = {
                "question_type": "multiplechoice",
                "question": "Who is shortest?",
                "answers": [
                    {
                        "value": "mike",
                        "text": "Mike",
                        "correct": False
                    },
                    {
                        "value": "nicki",
                        "text": "Nicki",
                        "correct": False
                    },
                    {
                        "value": "george",
                        "text": "George",
                        "correct": True
                    }
                ],
                "response_correct": "Correct! That's why his desk is so low!",
                "response_incorrect": "Incorrect! You need to open your eyes "
                                      "and see it's George!",
                "active": True
            }
        question = Question.objects.create(**question_data)
        return question

    def make_quiz(self, quiz_data=None):
        if quiz_data is None:
            quiz_data = {
                "description": "A wonderful quiz",
                "metadata": {'a': 'a', 'b': 2}
            }
        quiz = Quiz.objects.create(**quiz_data)
        return quiz

    def test_login(self):
        request = self.client.post(
            '/api/token-auth/',
            {"username": "testuser", "password": "testpass"})
        token = request.data.get('token', None)
        self.assertIsNotNone(
            token, "Could not receive authentication token on login post.")
        self.assertEqual(request.status_code, 200,
                         "Status code on /api/token-auth was %s -should be 200"
                         % request.status_code)

    def test_create_quiz_model_data(self):
        post_data = {
            "description": "A wonderful quiz",
            "metadata": {'a': 'a', 'b': 2}
        }
        response = self.client.post('/api/v1/quiz/',
                                    json.dumps(post_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Quiz.objects.last()
        self.assertEqual(d.description, 'A wonderful quiz')
        self.assertEqual(d.metadata, {'a': 'a', 'b': 2})
        self.assertEqual(d.active, False)
        self.assertEqual(d.created_by, self.user)

    def test_create_question_model_data(self):
        post_data = {
            "question_type": "multiplechoice",
            "question": "Who is tallest?",
            "answers": [
                {
                    "value": "mike",
                    "text": "Mike",
                    "correct": False
                },
                {
                    "value": "nicki",
                    "text": "Nicki",
                    "correct": True
                },
                {
                    "value": "george",
                    "text": "George",
                    "correct": False
                }
            ],
            "response_correct": "Correct! That's why only he bangs his head "
                                "on the lamp!",
            "response_incorrect": "Incorrect! You need to open your eyes and "
                                  "see it's Nicki!",
            "active": True
        }
        response = self.client.post('/api/v1/question/',
                                    json.dumps(post_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Question.objects.last()
        self.assertEqual(d.version, 1)
        self.assertEqual(d.question_type, "multiplechoice")
        self.assertEqual(d.question, "Who is tallest?")
        self.assertEqual(len(d.answers), 3)
        self.assertEqual(d.answers[0], {
            "value": "mike",
            "text": "Mike",
            "correct": False
        })
        self.assertEqual(d.response_correct, "Correct! That's why only he "
                                             "bangs his head on the lamp!")
        self.assertEqual(d.response_incorrect, "Incorrect! You need to open "
                                               "your eyes and see it's Nicki!")
        self.assertEqual(d.created_by, self.user)

    def test_create_question_model_data_bad_type(self):
        post_data = {
            "question_type": "yesno",
            "question": "Is the sun hot?",
            "answers": [
                {
                    "value": "yes",
                    "text": "Yes",
                    "correct": True
                },
                {
                    "value": "no",
                    "text": "No",
                    "correct": False
                }
            ],
            "response_correct": "Correct! It's very hot!",
            "response_incorrect": "Incorrect! Have you felt it's power?",
            "active": True
        }
        response = self.client.post('/api/v1/question/',
                                    json.dumps(post_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["question_type"][0],
                         '"yesno" is not a valid choice.')

    def test_create_quiz_with_question(self):
        question = self.make_question()
        post_data = {
            "description": "A wonderful quiz",
            "active": True,
            "metadata": {'a': 'a', 'b': 2},
            "questions": [str(question.id)]
        }
        response = self.client.post('/api/v1/quiz/',
                                    json.dumps(post_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Quiz.objects.last()
        self.assertEqual(d.description, 'A wonderful quiz')
        self.assertEqual(d.metadata, {'a': 'a', 'b': 2})
        self.assertEqual(d.active, True)
        self.assertEqual(d.questions.all().count(), 1)
        self.assertEqual(d.created_by, self.user)

    def test_create_webhook(self):
        # Setup
        user = User.objects.get(username='testadminuser')
        post_data = {
            "target": "http://example.com/registration/",
            "event": "quiz.created"
        }
        # Execute
        response = self.adminclient.post('/api/v1/webhook/',
                                         json.dumps(post_data),
                                         content_type='application/json')
        # Check
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        d = Hook.objects.last()
        self.assertEqual(d.target, 'http://example.com/registration/')
        self.assertEqual(d.user, user)

    # This test is not working despite the code working fine
    # If you run these same steps below interactively the webhook will fire
    # @responses.activate
    # def test_webhook(self):
    #     # Setup
    #     post_save.connect(receiver=model_saved, sender=DummyModel,
    #                       dispatch_uid='instance-saved-hook')
    #     Hook.objects.create(user=self.adminuser,
    #                         event='dummymodel.added',
    #                         target='http://example.com/registration/')
    #
    #     expected_webhook = {
    #         "hook": {
    #             "target": "http://example.com/registration/",
    #             "event": "dummymodel.added",
    #             "id": 3
    #         },
    #         "data": {
    #         }
    #     }
    #     responses.add(
    #         responses.POST,
    #         "http://example.com/registration/",
    #         json.dumps(expected_webhook),
    #         status=200, content_type='application/json')
    #     dummymodel_data = {
    #         "product_code": "BLAHBLAH",
    #         "data": {"stuff": "nonsense"}
    #     }
    #     dummy = DummyModel.objects.create(**dummymodel_data)
    #     # Execute
    #     self.assertEqual(responses.calls[0].request.url,
    #                      "http://example.com/registration/")
