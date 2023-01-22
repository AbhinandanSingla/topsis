from pathlib import Path

from flask import Flask, render_template, request
import pandas as pd
import smtplib

app = Flask(__name__)


def vector_normalize(dataset, ncol, df):
    for i in range(1, ncol):
        y = 0
        for j in range(len(dataset)):
            print(df.iloc[j, i])
            y = y + df.iloc[j, i] ** 2
        y = y ** 0.5
        for j in range(len(df)):
            dataset.iat[j, i] = (dataset.iloc[j, i] / y)
    return dataset


"""**Step 3:Weight Assignment**"""


def weight(df, ncol, weights):
    weights = list(map(int, weights.split(',')))
    print(weights)
    for i in range(1, ncol):
        for j in range(len(df)):
            df.iat[j, i] = df.iloc[j, i] * weights[i - 1]
    return df


"""**Step 4:Finding ideal best and ideal worst**"""


def Calc_ideal_Values(df, nCol, impact):
    # calculating ideal best and ideal worst
    ideal_positive_value = (df.max().values)[
                           1:]  # positive value i.e if impact is + then maximum will be our ideal positive value
    ideal_negative_value = (df.min().values)[
                           1:]  # negative value i.e if impact is + then minimum will be our ideal negative value
    # now we need to check when our impact is negative
    # now we will run our loop from 1 to last column and check if our impact is negative or not if it is then we need to interchange the ideal postive and ideal negative

    for i in range(1, nCol):
        if impact[i - 1] == '-':
            ideal_positive_value[i - 1], ideal_negative_value[i - 1] = ideal_negative_value[i - 1], \
                                                                       ideal_positive_value[i - 1]
    return ideal_positive_value, ideal_negative_value


"""**Step 5:Calculate Euclidean Distance ,score and Rank**"""

import math


def euclidean_distance(dataset, ncol, weights, impact, df1):
    # first of all normalize the vector
    dataset = vector_normalize(dataset, ncol, df1)
    # second:weight assignment
    dataset1 = weight(dataset, ncol, weights)

    # ideal postive and ideal negtaive values calculation
    ideal_p, ideal_n = Calc_ideal_Values(dataset1, ncol, impact)

    # calculating the euclidean distance
    perf_score = []
    for i in range(len(dataset1)):
        s_positive, s_negative = 0.0, 0.0
        for j in range(1, ncol):
            s_positive = s_positive + (ideal_p[j - 1] - dataset1.iloc[i, j]) ** 2
            s_negative = s_negative + (ideal_n[j - 1] - dataset1.iloc[i, j]) ** 2

        s_positive = math.sqrt(s_positive)
        s_negative = math.sqrt(s_negative)

        perf_score.append(s_negative / (s_negative + s_positive))
        # print(perf_score)
        # Score
    df1['Topsis Score'] = perf_score
    # #Rank
    df1['Rank'] = (df1['Topsis Score'].rank(method='max', ascending=False))
    df1 = df1.astype({"Rank": int})

    df1.to_csv('102003466-result.csv', index=False)
    return df1


import sys
import os


# dataset, ncol, weights, impact, df1
# def main():
#         euclidean_distance(data1, len(data1.columns), weights, impact, data)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/topics', methods=['POST'])
def topics():  # put application's code here
    res = request.values.to_dict()
    file = request.files['file']
    file.save(file.filename)
    print(file.name)
    ex_df = pd.read_excel(os.path.abspath(file.filename), engine='openpyxl',
                          )
    print(os.path.abspath(file.filename))
    ex_df.to_csv(f'{Path(file.filename).stem}.csv')
    print(os.path.dirname(os.path.abspath(file.filename)))
    df = pd.DataFrame(pd.read_csv(f'{os.path.dirname(os.path.abspath(file.filename))}/{Path(file.filename).stem}.csv'))
    weights = str(res['weights'])
    impacts = str(res['impacts'])
    df1 = df.copy()
    df.drop('Fund Name', inplace=True, axis=1)
    result = euclidean_distance(df, len(df.columns), weights,
                                impacts,
                                df.copy())
    result['Fund Name'] = df1['Fund Name']
    gmail_user = 'sahilkadiyan9817@gmail.com'
    gmail_password = 'sdmsywzqwtqbzbre'

    sent_from = gmail_user
    to = [res['email']]
    subject = 'Lorem ipsum dolor sit amet'
    body = result

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)

    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print("Email sent successfully!")
    except Exception as ex:
        print("Something went wrong….", ex)

    return 'success'
    # return "success"
