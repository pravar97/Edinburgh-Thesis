from expressionPreProcessing import *
from generators import *
import json
from uuid import uuid4
from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField
from flask_bootstrap import Bootstrap
import pandas as pd
import datetime

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
    appendLogs(str(len(userData)) + ' Unique Users')
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


def appendLogs(input_line):
    with open('logs.txt', 'a') as file:
        file.write('[' + str(datetime.datetime.now()) + '] ' + str(input_line) + '\n')


def getSubQ(astTree):
    stmt = tree2str(astTree)
    noN = rmN(astTree)
    if tree2str(noN) != stmt:
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
    if tree2str(noB) != stmt:
        return 6, ['Move ¬ inwards in all brackets:', stmt], noB
    if not is_in_form('CNF', astTree) and not is_in_form('DNF', astTree):
        f = getUserData('f', random.choice(['CNF', 'DNF']))
        setUserData('f', f)
        return 7, ['Convert the following to ' + f + ':', stmt], \
               convertTo(f, astTree, do_presteps=False, return_tree_and_steps=True)

    return 8, [], ''


class HomeForm(FlaskForm):
    submit = SubmitField('Analyse Expressions')
    ques = SubmitField('Answer Questions')
    chp = SubmitField('Inf1a Course Page')


class expressionForm(FlaskForm):
    #  Set up buttons and text boxes
    input = StringField(' ', render_kw={"placeholder": "For example: (a or b) and (c -> d)"})
    submit = SubmitField('Display Truth Table')
    genRan = SubmitField('Generate Random Expression')
    conCNF = SubmitField('Convert to CNF')
    conDNF = SubmitField('Convert to DNF')
    getKmap = SubmitField('Display Karnaugh Map')
    goHome = SubmitField('Return to Homepage')


class QuestionsForm(FlaskForm):
    #  Set up buttons and text boxes
    input = StringField(' ')
    submit = SubmitField('Enter')
    see = SubmitField('See sample solution')
    next = SubmitField('Next Question')
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
            return rd('/expression_analyser')

    return render_template('home.html', form=form)  # Return the home page but with the new data generated


@app.route('/expression_analyser', methods=['POST', 'GET'])
def expressionAnalyser():
    form = expressionForm()  # Set up the form features for homepage

    # Make every form output initially empty
    error = desc = ""
    table = steps = None

    # If a button has been clicked
    if form.validate_on_submit():

        try:
            appendLogs('Expression Analysed: ' + form.input.data)
            if form.goHome.data:  # Go back to home page if this button clicked
                return rd("/", code=302)
            if form.genRan.data:  # If its the random expression gen button
                astTree = genRanTree(0)  # Get a random tree
                form.input.data = tree2str(astTree)  # Set the textbox to that random expression

            tokens = tokenize(form.input.data)  # Make a list of tokens based on textbox input
            if len(tokens) == 0:
                raise Exception("Input Field is empty")
            parser = Parser(tokens)
            tree = parser.parse()  # Make a tree from the tokens list

            if form.conCNF.data:  # If the convert to CNF button is clicked
                steps = convertTo('CNF', tree)

            if form.conDNF.data:  # If the convert to CNF button is clicked
                steps = convertTo('DNF', tree)

            # Generate a truth table
            curAST = ast(tree)
            output = curAST.printTruthTable()

            # Check whether expression is satisfiable, tautology or inconsistent
            if 1 in output['Result']:
                if 0 in output['Result']:
                    desc = "Expression is satisfiable"
                else:
                    desc = "Expression is a tautology"
            else:
                desc = "Expression is inconsistent"

            if form.getKmap.data:
                kmap, rowkeys, rowatoms, colatoms = curAST.printKMap()
                pdTable = pd.DataFrame(kmap, index=rowkeys)
                table = '<p style="font-size:20pt; font-width:900; position: absolute; margin-right: ' + str(
                    50 + len(kmap) * 25) + 'px; right: ' \
                                           '50vw; top: ' + str(52 + len(rowkeys) * 10.4) + 'px;">' + ''.join(
                    rowatoms) + '</p> '
                table += '<p style="font-size:20pt; font-width:900;">' + ''.join(colatoms) + '</p> '
                table += pdTable.head(len(rowkeys)).to_html(col_space=50, classes='Table', index=len(rowkeys) > 1)
                # Check if print truth table button is clicked
            elif form.submit.data:
                result = tree2str(tree)
                output[result] = output.pop('Result')
                pdTable = pd.DataFrame(output)  # Create a table data structure from truth table dictionary

                table = pdTable.head(len(output[result])).to_html(col_space=50, classes='Table')  # Generate HTML
                # code for tables
            else:
                table = None
        except Exception as inst:
            error = str(inst)  # Set error message from exceptions caught

            table = None

    return render_template('expressionAnalyser.html', form=form, table=table, error=error, desc=desc,
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
    steps = steps_table = None

    cur_question = getUserData('cur_question')
    difficulty = getUserData('difficulty')
    sq_num = getUserData('SQ#')
    q_num = getUserData('Q#')
    if None in [q_num, sq_num, difficulty, cur_question]:
        return rd('/choose_question_difficulty')

    if cur_question[-1] == 'tt':
        q = ['Form a expression that satisfies this Truth Table:']
        table = cur_question[0]
        solution = cur_question[1]
        stage = -1
    elif cur_question[-1] == 'km':
        q = ['Form a expression that satisfies this Karnaugh Map:']
        table = cur_question[0]
        solution = cur_question[1]
        stage = -1
    else:
        stage, q, solution = getSubQ(cur_question[0])
        if type(solution) == tuple:
            steps_table = solution[0]
            solution = solution[1]
    q[0] = 'Q' + str(q_num) + '.' + str(sq_num) + ' ' + q[0]

    form = QuestionsForm()
    if form.validate_on_submit():
        try:

            if form.goHome.data:
                return rd("/", code=302)  # Go to home page
            if form.change.data:
                return rd('/choose_question_difficulty')  # Change the difficulty
            if form.see.data:  # See the CNF conversion solutions
                if steps_table is None:
                    steps = 'Solution: ' + tree2str(solution)
                else:
                    steps = steps_table

            if form.next.data:  # Go to next question if next question clicked
                next_question = getUserData('next_question')
                setUserData('next_question', None)
                if next_question is not None:
                    if not is_in_form('CNF', next_question[0]) and not is_in_form('DNF', next_question[0]):
                        setUserData('SQ#', getUserData('SQ#', 0) + 1)
                        setUserData('cur_question', next_question)
                        return rd('/q')

                setUserData('Q#', getUserData('Q#', 0) + 1)
                setUserData('SQ#', 1)
                setUserData('cur_question', genQuestion(difficulty))
                setUserData('f', random.choice(['CNF', 'DNF']))
                return rd('/q')

            if form.submit.data:  # If enter button is clicked

                tokens = tokenize(form.input.data)  # Get tokens of user input
                if len(tokens) == 0:
                    raise Exception("Input Field is empty")
                user_parser = Parser(tokens)
                user_tree = user_parser.parse()  # Parse the user input
                f = getUserData('f', '')
                pos_wrongs = {
                    -1: 'Expression is not equivalent, for example when ',
                    1: 'Entered Expression is equivalent but there are redundant negations',
                    2: 'Entered Expression is equivalent but there are ternary operator(s)',
                    3: 'Entered Expression is equivalent but there are XOR operator(s)',
                    4: 'Entered Expression is equivalent but there are double implication(s)',
                    5: 'Entered Expression is equivalent but there are single implication(s)',
                    6: 'Entered Expression is equivalent but there are negated brackets',
                    7: 'Entered Expression is equivalent but it is not in ' + f,

                }
                with open('stats.json') as f:
                    stats = json.load(f)
                eq, trues, falses = isEQ(user_tree, solution, hint=True)
                if eq:  # Check if user input is equivalent to question
                    user_stage = getSubQ(user_tree)[0]
                    if user_stage != stage and stage != 7 or stage == 7 and user_stage == 8:
                        right = 'Well done, your answer is correct :) Please click \'Next Question\''
                        updateStats(stats, difficulty, 'right')
                        setUserData('next_question', (user_tree, 'sm'))
                    else:
                        updateStats(stats, difficulty, 'wrong')
                        wrong = pos_wrongs[user_stage]
                else:
                    updateStats(stats, difficulty, 'wrong')
                    wrong = pos_wrongs[-1]
                    if trues:
                        verb = ['are', 'is'][int(len(trues) == 1)]
                        wrong += ', '.join(trues) + ' ' + verb + ' true'
                        if falses:
                            verb = ['are', 'is'][int(len(falses) == 1)]
                            wrong += ' and ' + ', '.join(falses) + ' ' + verb + ' false'
                    else:
                        verb = ['are', 'is'][int(len(falses) == 1)]
                        wrong += ', '.join(falses) + ' ' + verb + ' false'

                appendLogs('Question: ' + ' '.join(q) + ', User Response: ' + form.input.data + ', Feedback: ' + wrong + right)
                return render_template('questions.html', form=form, q=q, wrong=wrong, table=table, right=right,
                                       steps=steps)

        except Exception as inst:
            error = str(inst)

    return render_template('questions.html', form=form, q=q, error=error, table=table, steps=steps)


if __name__ == '__main__':
    app.run(debug=True)
