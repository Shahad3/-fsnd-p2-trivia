import os
import json
import random
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, resources={r"": {"origins": "*"}})
  #@cross_origin()

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    question = [question.format() for question in selection]
    return question[start:end]

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
    categories1 = Category.query.all()
    # Get all categories
    categories = [category.format() for category in categories1]

    return jsonify({
      'success' : True,
      'categories' : categories,
    })


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    # Get all questions
    selection = Question.query.all()
    categories1 = Category.query.all()
    # Get all categories
    categories = [category.format() for category in categories1]
    # Paginate questions
    current_questions = paginate_questions(request, selection)
    # If the requested page is empty, show a not found page
    if (len(current_questions) == 0):
      abort(404)

    return jsonify({
      'success' : True,
      'questions' : current_questions,
      'categories' : categories,
      'total_questions' : len(selection)
    })
  



  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/question/<int:id>/delete', methods=['DELETE'])
  def delete_question(id):
    try:
      question = Question.query.filter_by(id=id).one_or_none()

      if question is None:
        abort(404)
        return jsonify({
        'success' : False,
      })
      else:
        question.delete()

      return jsonify({
        'success' : True,
        'deleted' : id
      })
    except Exception as e:
      print ("Error: ", e)
      
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/question', methods=['POST'])
  def post_question():
    body = request.get_json()
    new_question = body.get('question',None)
    new_answer = body.get('answer',None)
    new_category = body.get('category',None)
    new_difficulty = body.get('difficulty',None)
    if ((new_question is None) or (new_answer is None) or (new_category is None))or (new_difficulty is None):
      abort(422)
    try:
      new_question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
      new_question.insert()
      selection = Question.query.all()
      current_questions = paginate_questions(request, selection)
      return jsonify({
        'success': True,
        'created': new_question.id,
        'questions': current_questions,
        'total questions': len(selection)
      })
    except Exception as e:
      print("Error: ", e)
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_question():
    body = request.get_json()
    search_term = body.get('searchTerm',None)
    if (search_term is None):
      abort(404)
    try:
      selection = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      current_questions = paginate_questions(request, selection)
      return jsonify({
        'success': True,
        'questions': current_questions,
        'total results': len(selection)
      })
    except Exception as e:
      print("Error: ", e)
      abort(400)
  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<id>/questions')
  def get_qs_by_category(id):
    selection = Question.query.filter_by(category=id).all()
    # current question for the requsted page
    current_questions = paginate_questions(request, selection)
    current_category = Category.query.filter_by(id=id).first()
    categories1 = Category.query.all()
    # Get all categories
    categories = [category.format() for category in categories1]

    # If the requested page is empty, show a not found page
    if (len(current_questions) == 0):
      abort(404)

    return jsonify({
      'success' : True,
      'questions' : current_questions,
      'current category' : current_category.type,
      'categories' : categories,
      'total questions' : len(selection)
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/questions/play', methods=['POST'])
  def play_question():
    body = request.get_json()
    category = body.get('category',None)
    previous = body.get('previous',None)
    try:
      if (category is None):
        selection = Question.query.all()
      else:
        selection = Question.query.filter_by(category=category).all()
      random_question = random.randrange(len(selection))
      if((previous is not None) and (random_question == previous)):
        random_question = random.randrange(len(selection))
      return jsonify({
        'success' : True,
        'question' : selection[random_question].format()
      })
    except Exception as e:
      print(e)
      abort(400)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
        return jsonify({
            "success": False, 
            "code": 404,
            "message": "Page is not found"
        }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          "success": False, 
          "code": 422,
          "message": "The request is unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False, 
          "code": 400,
          "message": "bad request"
      }), 400
  
  return app

    