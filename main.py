import requests
import datetime
import re
import html
import sqlite3
import json
import argparse

def main():

    db = sqlite3.connect('superquiz.db')
    cur = db.cursor()
    subject = None
    consecutive_fails = 0
    successes = 0
    level = 0
    answers = []
    question_re = re.compile('([0-9]+)\\.[\\s]*(.*)')

    # Create table
    try:
        cur.execute('CREATE TABLE quizzes (date text UNIQUE, subject text, questions text)')
    except Exception as e:
        print("db error:", e)

    # Start with tomorrow, since superquiz is usually put out a day in advance
    #date1 = datetime.date.today() + datetime.timedelta(days=1)
    date1 = datetime.date(2021,5,22)

    while successes < 10:
    #for i in range(0, 8):

        # check to see if quiz for date already in DB, if so we don't do HTTP get on it
        if ( cur.execute('SELECT date FROM quizzes WHERE date = "%s"' % date1).fetchone() != None ):
            print(date1, "already exists in DB")
            date1 -= datetime.timedelta(days=1)
            continue

        url = date1.strftime(
            '''http://cdn.kingfeatures.com/rss/v1/lib/drawfeature.php?clientID=seattletimes&contentID=Superquiz&pubdate=%Y%m%d&element=body''')
        #http://cdn.kingfeatures.com/rss/content_xml/Superquiz/%04d/Superquiz_%04d%02d%02d.xml
        response = requests.request("GET", url)
        text = html.unescape(response.text)
        text = text.replace('</p><p>', '<p>')
        paragraphs = text.split('<p>')
        questions = []

        for para in paragraphs:
            if para.lower().startswith('subject:'):
                subject = para[8:].strip()
            elif para.startswith('FRESHMAN LEVEL'):
                level = 1
            elif para.startswith('GRADUATE LEVEL'):
                level = 2
            elif para.startswith('PH.D. LEVEL'):
                level = 3
            elif m := question_re.match(para):
                questions.append([m.group(2), level])
            elif para.lower().startswith('answers:'):
                answers = parse_answers(para)

        quiz = []
        if (subject != None):
            print(date1.strftime("%A, %Y-%m-%d"), subject)
            for i in range(0,len(questions)):
                quiz.append((questions[i][0], questions[i][1], answers[i]))
                #print ( json.dumps( (questions[i][0], questions[i][1], answers[i])))

            print(json.dumps(quiz))

            cur.execute('INSERT INTO quizzes VALUES (?, ?, ?)', (date1, subject, json.dumps(quiz)))
            consecutive_fails = 0
            successes += 1
        else:
            consecutive_fails += 1

        if (consecutive_fails > 10):
            break

        date1 -= datetime.timedelta(days=1)
        subject = None

    db.commit()
# end main


def parse_answers(answer_text):

    answer_text += ' ##'
    answers = []
    for i in range(1,20):
        answer_re = re.compile("%d+. (.*?) (%d.|##)" % (i, i+1))
        try:
            x = answer_re.search(answer_text)
            answers.append(x.group(1))
        except:
            break

    return answers


parser = argparse.ArgumentParser()
parser.add_argument('-s', '--search')
args = parser.parse_args()

if (args.search):
    print(args.search)
    exit(0)

if __name__ == "__main__":
    main()
