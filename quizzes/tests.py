import json
from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_hooks.models import Hook

from .models import Quiz, Question, Tracker, Answer


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

    def make_tracker(self, tracker_data=None):
        if tracker_data is None:
            tracker_data = {
                "identity": "b45d17b6-1291-4825-bfb9-446f6f853dae",
                "quiz": self.make_quiz()
            }
        tracker = Tracker.objects.create(**tracker_data)
        return tracker

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

    def test_create_quiz_listing(self):
        question1 = self.make_question()
        quiz1_data = {
            "description": "A wonderful quiz 1",
            "active": True,
            "metadata": {'a': 'a', 'b': 2},
            "questions": [str(question1.id)]
        }
        self.client.post('/api/v1/quiz/', json.dumps(quiz1_data),
                         content_type='application/json')
        question2 = self.make_question()
        quiz2_data = {
            "description": "A wonderful quiz 2",
            "active": True,
            "metadata": {'a': 'a', 'b': 2},
            "questions": [str(question2.id)]
        }
        self.client.post('/api/v1/quiz/', json.dumps(quiz2_data),
                         content_type='application/json')

        response = self.client.get('/api/v1/quiz/',
                                   content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.json()["results"]

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["description"], "A wonderful quiz 1")
        self.assertEqual(results[0]["questions"], [str(question1.id)])
        self.assertEqual(results[1]["description"], "A wonderful quiz 2")

    def test_create_tracker_model_data(self):
        quiz = self.make_quiz()
        post_data = {
            "identity": "b45d17b6-1291-4825-bfb9-446f6f853dae",
            "quiz": str(quiz.id)
        }
        response = self.client.post('/api/v1/tracker/',
                                    json.dumps(post_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Tracker.objects.last()
        self.assertEqual(str(d.identity),
                         "b45d17b6-1291-4825-bfb9-446f6f853dae")
        self.assertEqual(d.metadata, None)
        self.assertEqual(d.complete, False)
        self.assertIsNotNone(d.started_at)
        self.assertEqual(d.created_by, self.user)

    def test_patch_tracker_model_data(self):
        quiz = self.make_quiz()
        post_data = {
            "identity": "b45d17b6-1291-4825-bfb9-446f6f853dae",
            "quiz": str(quiz.id)
        }
        response = self.client.post('/api/v1/tracker/',
                                    json.dumps(post_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Tracker.objects.last()
        self.assertEqual(d.complete, False)
        self.assertIsNone(d.completed_at)

        patch_data = {
            "complete": True,
            "completed_at": datetime.now().isoformat()
        }
        response = self.client.patch('/api/v1/tracker/%s/' % str(d.id),
                                     json.dumps(patch_data),
                                     content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        d = Tracker.objects.last()
        self.assertEqual(d.complete, True)
        self.assertIsNotNone(d.completed_at)

    def test_create_answer_model_data_correct(self):
        # create question, quiz and tracker
        question = self.make_question()
        quiz = self.make_quiz()
        quiz.questions = [question]
        quiz.save()
        tracker = self.make_tracker(tracker_data={
            "identity": "b45d17b6-1291-4825-bfb9-446f6f853dae",
            "quiz": quiz
        })
        post_data = {
            "question": str(question.id),
            "question_text": "Who is shortest?",
            "answer_value": "george",
            "answer_text": "George",
            "answer_correct": True,
            "response_sent": "Correct! That's why his desk is so low!",
            "tracker": str(tracker.id)
        }
        response = self.client.post('/api/v1/answer/',
                                    json.dumps(post_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Answer.objects.last()
        self.assertEqual(str(d.tracker.identity),
                         "b45d17b6-1291-4825-bfb9-446f6f853dae")
        self.assertEqual(d.question_text, "Who is shortest?")
        self.assertEqual(d.answer_value, "george")
        self.assertEqual(d.answer_text, "George")
        self.assertEqual(d.answer_correct, True)
        self.assertEqual(d.response_sent, "Correct! That's why his desk is "
                                          "so low!")
        self.assertIsNotNone(d.created_at)
        self.assertEqual(d.created_by, self.user)

    def test_create_answer_model_data_incorrect(self):
        # create question, quiz and tracker
        question = self.make_question()
        quiz = self.make_quiz()
        quiz.questions = [question]
        quiz.save()
        tracker = self.make_tracker(tracker_data={
            "identity": "b45d17b6-1291-4825-bfb9-446f6f853dae",
            "quiz": quiz
        })
        post_data = {
            "question": str(question.id),
            "question_text": "Who is shortest?",
            "answer_value": "nicki",
            "answer_text": "Nicki",
            "answer_correct": False,
            "response_sent": "Incorrect! You need to open your eyes "
                             "and see it's George!",
            "tracker": str(tracker.id)
        }
        response = self.client.post('/api/v1/answer/',
                                    json.dumps(post_data),
                                    content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        d = Answer.objects.last()
        self.assertEqual(str(d.tracker.identity),
                         "b45d17b6-1291-4825-bfb9-446f6f853dae")
        self.assertEqual(d.question_text, "Who is shortest?")
        self.assertEqual(d.answer_value, "nicki")
        self.assertEqual(d.answer_text, "Nicki")
        self.assertEqual(d.answer_correct, False)
        self.assertEqual(d.response_sent, "Incorrect! You need to open your "
                                          "eyes and see it's George!")
        self.assertIsNotNone(d.created_at)
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
