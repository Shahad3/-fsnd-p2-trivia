import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            "question":"How to uplaod a file?",
            "answer":"No idea",
            "category":1,
            "difficulty":2 
            }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_all_questions(self):
        test = self.client().get('/questions')
        data = json.loads(test.data)

        self.assertEqual(test.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])

    def test_error_get_all_questions(self):
        test = self.client().get('/questions?page=1000')
        data = json.loads(test.data)

        self.assertEqual(test.status_code, 404)
        self.assertEqual(data['success'], False)


    def test_get_all_cateogries(self):
        test = self.client().get('/categories')
        data = json.loads(test.data)

        self.assertEqual(test.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_error_get_all_cateogries(self):
        test = self.client().get('/category')

        self.assertEqual(test.status_code, 404)

    def test_get_questions_by_category(self):
        test = self.client().get('/categories/1/questions')
        data = json.loads(test.data)

        self.assertEqual(test.status_code, 200)

    def test_post_question(self):
        test = self.client().post('/question', json=self.new_question)
        data = json.loads(test.data)

        self.assertEqual(test.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_fail_to_post_question(self):
        test = self.client().post('/question', json={})
        self.assertEqual(test.status_code, 422)

    def test_delete_question(self):
        new_question = Question(question='New Question', answer='new_answer', category=1, difficulty=2)
        new_question.insert()
        url = '/question/{}/delete'.format(new_question.id)
        print(url)
        test = self.client().delete(url)
        deleted = Question.query.filter(Question.id == new_question.id).one_or_none()

        self.assertEqual(test.status_code, 200)
        self.assertEqual(deleted, None)


    def test_search_question(self):
        test = self.client().post('/questions/search', json={'searchTerm':'title'})
        data = json.loads(test.data)
        self.assertEqual(test.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_play(self):
        test = self.client().post('/questions/play', json={})

        self.assertEqual(test.status_code, 200)

    def test_play_by_category(self):
        test = self.client().post('/questions/play', json={'previous':'15'})
        data = json.loads(test.data)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question']['category'], '1')
        self.assertEqual(test.status_code, 200)

    
        
        



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()