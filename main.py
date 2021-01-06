from statementPreProcessing import *
from statementManipulations import *
from statementCheckers import *

import json
from uuid import uuid4
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField
from flask_bootstrap import Bootstrap
import pandas as pd

app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = 'bdd9761c62d68ea530872f8848107c21'
userData = {}
capacity = 500


def genNewUser(userID=None):
    global userData
    global capacity
    if userID is None:
        userID = str(uuid4())
    userData[userID] = {}
    userData[userID]['Q#'] = 0
    userData[userID]['SQ#'] = 1
    if len(userData) >= capacity:
        userData.pop(next(iter(userData)))
    return userID


def getUserData(key, default_return=None):
    global userData
    userID = request.args.get("userID")
    if userID is None:
        return default_return
    if userID not in userData:
        genNewUser(userID)
    else:
        userData[userID] = userData.pop(userID)
    if key == 'userID':
        return userID
    elif key in userData[userID]:
        return userData[userID][key]
    else:
        return default_return


def setUserData(key, value):
    userID = getUserData('userID')
    if userID is None:
        return None
    global userData
    userData[userID][key] = value
    return 'set'


def rd(link, code=None):
    userID = getUserData('userID')
    if userID is None:
        userID = genNewUser()
    link += '?userID=' + str(userID)
    if code is None:
        return redirect(link)
    else:
        return redirect(link, code)


def updateStats(stats, difficulty, correctness):
    diffmap = {10: 'very easy', 5: 'easy', 0: 'medium', -5: 'hard', -10: 'very hard'}
    stats[diffmap[difficulty]][correctness] += 1
    with open('stats.json', 'w') as f:
        json.dump(stats, f)


def getSubQ(astTree):
    stmt = gen_stmt(astTree)
    noN = rmN(astTree)
    if gen_stmt(noN) != stmt:
        return 1, ['Remove redundant negation(s) from:', stmt], noN
    if '?' in stmt:
        return 2, ['Remove Ternary operator(s) from:', stmt], rmTO(astTree)
    if '⊕' in stmt:
        return 3, ['Remove ⊕ from:', stmt], rmXOR(astTree)
    if '↔' in stmt:
        return 4, ['Remove ↔ from:', stmt], rmDI(astTree)
    if '→' in stmt:
        return 5, ['Remove → from:', stmt], rmSI(astTree)
    noB = rmB(astTree)
    if gen_stmt(noB) != stmt:
        return 6, ['Move ¬ inwards in all brackets:', stmt], noB
    if not isCNF(astTree):
        return 7, ['Convert the following to CNF:', stmt], convertToCNF(astTree, True)
    return 8, [], ''


class HomeForm(FlaskForm):
    submit = SubmitField('Analyse Statements')
    ques = SubmitField('Answer Questions')
    chp = SubmitField('Inf1a Course Page')


class statementForm(FlaskForm):
    #  Set up buttons and text boxes
    input = StringField(' ')
    submit = SubmitField('Display Truth Table')
    genRan = SubmitField('Generate Random Statement')
    conCNF = SubmitField('Convert to CNF')
    goHome = SubmitField('Return to Homepage')


class QuestionsForm(FlaskForm):
    #  Set up buttons and text boxes
    input = StringField(' ')
    nextq_hidden = StringField(' ')
    submit = SubmitField('Enter')
    next = SubmitField('Next Question')
    see = SubmitField('See sample solution')
    change = SubmitField('Change Difficulty')
    goHome = SubmitField('Return to Homepage')


class QuestionsDifficultyForm(FlaskForm):
    #  Set up buttons and text boxes
    e1 = SubmitField('Very Easy')
    e2 = SubmitField('Easy')
    submit = SubmitField('Medium')
    h1 = SubmitField('Hard')
    h2 = SubmitField('Very Hard')
    goHome = SubmitField('Return to Homepage')


class LessonsHomeForm(FlaskForm):
    l1 = SubmitField('Lesson 1: Atoms')
    submit = SubmitField('Return to Homepage')

# class LessonForm(FlaskForm):


@app.route('/', methods=['POST', 'GET'])
def home():
    form = HomeForm()  # Set up the form features for homepage

    # If a button has been clicked
    if form.validate_on_submit():

        if form.ques.data:  # If its Questions button, redirect the user
            return rd('/choose_question_difficulty')
        elif form.chp.data:
            return redirect('https://course.inf.ed.ac.uk/inf1a')
        else:
            return rd('/statement_analyser')

    return render_template('home.html', form=form)  # Return the home page but with the new data generated


@app.route('/statement_analyser', methods=['POST', 'GET'])
def statementAnalyser():
    form = statementForm()  # Set up the form features for homepage

    # Make every form output initially empty
    error = desc = ""
    table = steps = None

    # If a button has been clicked
    if form.validate_on_submit():

        try:
            if form.goHome.data:  # Go back to home page if this button clicked
                return rd("/", code=302)
            if form.genRan.data:  # If its the random statement gen button
                astTree = genRanTree(0)  # Get a random tree
                form.input.data = gen_stmt(astTree)  # Set the textbox to that random statement

            tokens = tokenize(form.input.data)  # Make a list of tokens based on textbox input
            if len(tokens) == 0:
                raise Exception("Input Field is empty")
            parser = Parser(tokens)
            tree = parser.parse()  # Make a tree from the tokens list

            if form.conCNF.data:  # If the convert to CNF button is clicked
                steps = convertToCNF(tree)

            # Generate a truth table
            curAST = ast(tree)
            output = curAST.printTruthTable()

            # Check whether statement is satisfiable, tautology or unsatisfiable
            if 1 in output['Result']:
                if 0 in output['Result']:
                    desc = "Statement is satisfiable"
                else:
                    desc = "Statement is a tautology"
            else:
                desc = "Statement is inconsistent"

            # Check if print truth table button is clicked
            if form.submit.data:
                result = gen_stmt(tree)
                output[result] = output.pop('Result')
                pdTable = pd.DataFrame(output)  # Create a table data structure from truth table dictionary

                table = pdTable.head(len(output[result])).to_html(col_space=50, classes='Table')  # Generate HTML
                # code for tables
            else:
                table = None
        except Exception as inst:
            error = str(inst)  # Set error message from exceptions caught

            table = None

    return render_template('statementAnalyser.html', form=form, table=table, error=error, desc=desc,
                           steps=steps)  # Return the home page but with the new data generated


@app.route('/choose_question_difficulty', methods=['POST', 'GET'])
def questionsDifficulty():
    form = QuestionsDifficultyForm()  # Set the form objects
    if form.validate_on_submit():  # If a button has been clicked
        if form.goHome.data:  # Go back to home page if this button clicked
            return rd("/", code=302)
        difficulty = 0  # Default difficulty (for Medium difficulty)
        if form.e1.data:  # If very easy clicked
            difficulty = 10
        elif form.e2.data:  # If easy clicked
            difficulty = 5
        elif form.h1.data:  # If hard clicked
            difficulty = -5
        elif form.h2.data:  # If very hard clicked
            difficulty = -10

        setUserData('cur_question', genQuestion(difficulty))
        setUserData('Q#', getUserData('Q#', 0) + 1)
        setUserData('SQ#', 1)
        setUserData('difficulty', difficulty)
        return rd('/q')
    return render_template('questionsDifficulty.html', form=form)


@app.route('/q', methods=['POST', 'GET'])
def questions():
    # Set the form data to be blank except the question
    error = wrong = right = table = ""
    steps = None

    cur_question = getUserData('cur_question')
    difficulty = getUserData('difficulty')
    sq_num = getUserData('SQ#')
    q_num = getUserData('Q#')
    if None in [q_num, sq_num, difficulty, cur_question]:
        return rd('/choose_question_difficulty')

    if type(cur_question) == tuple:
        q = ['Form a statement that satisfies this truth table:']
        table = cur_question[0]
        solution = cur_question[1]
        cur_question = solution
        stage = -1
    else:
        stage, q, solution = getSubQ(cur_question)

    q[0] = 'Q' + str(q_num) + '.' + str(sq_num) + ' ' + q[0]

    form = QuestionsForm()
    if form.validate_on_submit():
        try:

            if form.goHome.data:
                return rd("/", code=302)  # Go to home page
            if form.change.data:
                return rd('/choose_question_difficulty')  # Change the difficulty
            if form.see.data:  # See the CNF conversion solutions
                steps = 'Solution: ' + gen_stmt(solution)

            if form.submit.data:  # If enter button is clicked

                tokens = tokenize(form.input.data)  # Get tokens of user input
                if len(tokens) == 0:
                    raise Exception("Input Field is empty")
                user_parser = Parser(tokens)
                user_tree = user_parser.parse()  # Parse the user input

                pos_wrongs = {
                    -1: 'Statement is not equivalent, for example when ',
                    1: 'Entered Statement is equivalent but there are still redundant negations',
                    2: 'Entered Statement is equivalent but there are still ternary operator(s)',
                    3: 'Entered Statement is equivalent but there are still XOR operator(s)',
                    4: 'Entered Statement is equivalent but there are still double implication(s)',
                    5: 'Entered Statement is equivalent but there are still single implication(s)',
                    6: 'Entered Statement is equivalent but there are still negated brackets',
                    7: 'Entered Statement is equivalent but it is not in CNF',

                }
                with open('stats.json') as f:
                    stats = json.load(f)
                eq, trues, falses = isEQ(user_tree, cur_question, hint=True)
                if eq:  # Check if user input is equivalent to question
                    if getSubQ(user_tree)[0] != stage:
                        right = 'Well done, your answer is correct :) Please click \'Next Question\''
                        updateStats(stats, difficulty, 'right')
                        setUserData('next_question', user_tree)
                    else:
                        updateStats(stats, difficulty, 'wrong')
                        wrong = pos_wrongs[stage]
                else:
                    updateStats(stats, difficulty, 'wrong')
                    wrong = pos_wrongs[-1]
                    if trues:
                        wrong += ', '.join(trues) + ' are true'
                        if falses:
                            wrong += ' and ' + ', '.join(falses) + ' are false'
                    else:
                        wrong += ', '.join(falses) + ' are false'

                return render_template('questions.html', form=form, q=q, wrong=wrong, table=table, right=right)
            if form.next.data:  # Go to next question if next question clicked
                next_question = getUserData('next_question')
                setUserData('next_question', None)
                if isCNF(next_question) or next_question is None:
                    next_question = genQuestion(difficulty)
                    setUserData('Q#', getUserData('Q#', 0)+1)
                    setUserData('SQ#', 1)
                else:
                    setUserData('SQ#', getUserData('SQ#', 0) + 1)
                setUserData('cur_question', next_question)
                return rd('/q')

        except Exception as inst:
            error = str(inst)

    return render_template('questions.html', form=form, q=q, error=error, table=table, steps=steps)


@app.route('/lessonsHome', methods=['POST', 'GET'])
def lessonsHome():
    form = LessonsHomeForm()

    if form.validate_on_submit():
        lessons = [form.l1.data]
        for i in range(1):
            if lessons[i]:
                setUserData('L#', i+1)
                return rd("/l")

        return rd("/", code=302)  # Go to home page

    return render_template('lessonsHome.html', form=form)


@app.route('/l', methods=['POST', 'GET'])
def lesson():
    lnum = getUserData('L#')
    if lnum is None:
        return rd('/lessonsHome')
    title = 'Lesson ' + str(lnum)
    form = LessonsHomeForm()
    if form.validate_on_submit():
        if form.learn.data:
            return redirect("https://course.inf.ed.ac.uk/inf1a")
        else:
            return rd("/", code=302)  # Go to home page

    return render_template('lesson.html', title=title, form=form)


if __name__ == '__main__':
    app.run(debug=True)
