#!/usr/bin/python2.7
#
# Script to generate data set for the workshop.
#
from __future__ import print_function

import random
import string
import sys

from numpy.random import choice
import pandas as pd

# Initial file fields
#
# - N: Number between 1 and 500
# - RAND: Random number between 0 and 1 (uniform distribution)
# - SID: Random but unique number
# - Gender: Two possible values 'M', 'F' (50% gender balance)
# - GivenName: First name
# - MiddleInitial:
# - Surname: Last name
# - Course Code: Single value ELON3609
# - Course Name: Course name, single value "Translational Science"
# - Program: Four values: ENG, SCI, MED, AAS (Equal balance)
#

# Initialize the random number to guarantee the same results.
random.seed(2016)

#
# Initial file
#
initial_student_file = 'FakeNameGenerator.com_adbc811b.csv'

#
# Information to generate the student_list.csv file
#
student_list_name = 'student_list.csv'
student_list_fields = ['SID',
                       'Identifier',
                       'email',
                       'Surname',
                       'GivenName',
                       'MiddleInitial',
                       'Full name',
                       'Gender',
                       'Course Code']

student_program = ('Program',
                   ['FSCI', 'SMED', 'FEIT', 'FASS'],
                   [25, 25, 25, 25])
student_enrolment = ('Enrolment Type',
                     ['Local', 'HECS', 'International'],
                     [16, 50, 34])
student_attendance = ('Attendance', ['Full Time', 'Part Time'], [90, 10])
additional_columns = [student_program, student_enrolment, student_attendance]

#
# Information to generate the midterm_answers.csv file
#
midterm_answers_name = 'midterm_answers.csv'
midterm_results_name = 'midterm_results.csv'
midterm_answers_fields = ['SID',
                          'email',
                          'Last Name',
                          'First Name',
                          'AQ01',
                          'AQ02',
                          'AQ03',
                          'AQ04',
                          'AQ05',
                          'AQ06',
                          'AQ07',
                          'AQ08',
                          'AQ09',
                          'AQ10',
                          'Total']

# Drop out rate depending on the value of "Enrolment Type"
midterm_dropout_rates = list(zip(student_enrolment[1], [0.05, 0.05, 0.15]))

# Midterm score averages depending on the program
midterm_score_average = dict(list(zip(
    student_program[1],
    [(75, 10), (70, 15), (65, 20), (55, 35)]
)))

forum_name = 'forum_participation.csv'
forum_fields = ['SID',
                'Days online 2',
                'Views 2',
                'Contributions 2',
                'Questions 2',
                'Days online 3',
                'Views 3',
                'Contributions 3',
                'Questions 3',
                'Days online 4',
                'Views 4',
                'Contributions 4',
                'Questions 4',
                'Days online 5',
                'Views 5',
                'Contributions 5',
                'Questions 5',
                'Days online',
                'Views',
                'Contributions',
                'Questions']

project_name = 'project_rubric.csv'
project_fields = ['SID', 'Structure', 'Presentation']

blended_name = 'blended_participation.csv'
blended_fields = ['SID',
                  'Video_1_W2',
                  'Questions_1_W2',
                  'Correct_1_W2',
                  'Video_2_W2',
                  'Questions_2_W2',
                  'Correct_2_W2',
                  'Video_1_W3',
                  'Questions_1_W3',
                  'Correct_1_W3',
                  'Video_2_W3',
                  'Questions_2_W3',
                  'Correct_2_W3',
                  'Video_1_W4',
                  'Questions_1_W4',
                  'Correct_1_W4',
                  'Video_2_W4',
                  'Questions_2_W4',
                  'Correct_2_W4',
                  'Video_1_W5',
                  'Questions_1_W5',
                  'Correct_1_W5',
                  'Video_2_W5',
                  'Questions_2_W5',
                  'Correct_2_W5'
                  ]


def weighted_choice(items):
    """items is a list of tuples in the form (item, weight)"""
    weight_total = sum((item[1] for item in items))
    n = random.uniform(0, weight_total)
    item = None
    for item, weight in items:
        if n < weight:
            return item
        n = n - weight
    return item


def add_sid(all_students, field_name, from_value):
    all_students[field_name] = \
        [from_value + x
         for x in random.sample(list(range(100000000)), len(all_students))]


def add_email(all_students):
    population = random.sample(list(range(9000)), len(all_students))
    all_students['email'] = \
        [''.join(random.choice(string.ascii_lowercase) for _ in range(4)) +
         str(1000 + x) + '@bogus.com'
         for x in population]


def add_identifier(all_students, field_name):
    all_students[field_name] = \
        ['Participant {0}'.format(idx + 1) for idx in range(len(all_students))]


def add_column(all_students, col_name, values, probabilities):
    if len(values) != len(probabilities):
        raise Exception('Two last parameters have different lengths')

    if len(probabilities) == 1:
        all_students[col_name] = values[0]
        return

    all_students[col_name] = \
        [weighted_choice(list(zip(values, probabilities)))
         for __ in range(len(all_students))]


def read_initial_file(file_name, num_students=500):
    all_students = pd.read_csv(file_name)

    max_l = len(all_students)
    if num_students < max_l:
        # Trim the result
        all_students = all_students.drop(
            random.sample(range(len(all_students)),
                max_l - num_students),
            axis=0)

    all_students['Full name'] = (
        all_students['GivenName'] + ' ' + all_students['Surname'])
    return all_students


def generate_csv_file(data_list, file_name, fields, sort_by):
    data_list[fields].sort_values(sort_by).to_csv(file_name, index=False)


def create_midterm_data(all_students):
    """
    Create the midterm data set

    Ten questions, two from each topic, a percentage of students did not
    show up, use it as an example of merge

    Rules:
    - International students have a 10% drop out rate
    - Performance changes by PROGRAM!


    :param all_students:
    :return: dictionary with the midterm answers
    """
    midterm_choices = ['A', 'B', 'C', 'D']
    midterm_solution = []
    for _ in range(0, 10):
        midterm_solution.append(random.choice(midterm_choices))

    # Insert the solution row
    midterm_answers = pd.DataFrame(
        [[0, '', 'SOLUTION', 'SOLUTION'] + midterm_solution + ['100']],
        columns=midterm_answers_fields)

    for idx, student_info in all_students.iterrows():

        midterm_score = {}
        # Detect if a student has to be dropped
        skip = False
        for enrolment, rate in midterm_dropout_rates:
            # print random.random(), rate
            if student_info['Enrolment Type'] == enrolment and \
                random.random() <= rate:
                skip = True
        if skip:
            continue

        midterm_score['SID'] = student_info['SID']
        midterm_score['email'] = student_info['email']
        midterm_score['Last Name'] = student_info['Surname']
        midterm_score['First Name'] = student_info['GivenName']

        # Select the score based on the program
        prg = student_info['Program']
        score = int(round(random.normalvariate(
            midterm_score_average[prg][0] / 10,
            midterm_score_average[prg][1] / 10)))
        if score > 10:
            score = 10
        if score < 0:
            score = 0

        # Score contains the number of questions that are correct
        text_score = str(10 * score)
        midterm_score['Total'] = text_score

        # Add the score also to the all_student database for further reference
        student_info['MIDTERM_SCORE'] = text_score

        # Generate the set of answers for the midterm
        correct_answers = random.sample(list(range(0, 10)), score)

        for x in range(0, 10):
            field = midterm_answers_fields[x + 4]
            if x in correct_answers:
                answer = midterm_solution[x]
                score = 1
            else:
                incorrect = list(midterm_choices)
                incorrect.remove(midterm_solution[x])
                answer = random.choice(incorrect)
                score = 0

            midterm_score[field] = answer
            midterm_score[field[1:]] = score

        midterm_answers = midterm_answers.append(midterm_score,
            ignore_index=True)

    return midterm_answers


def create_forum_data(all_students):
    """Create the data for the forum.

    Fields:
       - Days on line
       - Views
       - Contributions
       - questions
       - answers

    All these fields are replicated from week 2 to week 5 (four weeks)

    Rules:
       - International students have less participation, but higher views.
       - Part time attendance has way bigger in contributions
       - Number of answers correlates with midterm score!!!
    """
    forum_participation = pd.DataFrame()

    # Number of contributions in the forum
    week_contributions = [random.randint(20, 80) for _ in range(2, 6)]

    # Loop for all the students
    for idx, student_info in all_students.iterrows():

        forum_student_data = {'SID': student_info['SID']}

        midterm_score = int(student_info.get('MIDTERM_SCORE', 0)) / 10

        # Loop over the weeks
        days_online_acc = 0
        views_acc = 0
        contributions_acc = 0
        questions_acc = 0

        for week_n in range(2, 6):

            #
            # International or part time have many days online
            #
            if student_info['Enrolment Type'] == 'International' or \
                student_info['Attendance'] == 'Part Time':
                days_online = \
                    int(round(random.normalvariate(midterm_score * 7 / 10,
                                                   6 - week_n)))
            else:
                days_online = \
                    int(round(random.normalvariate(midterm_score * 7 / 10,
                                                   10 - week_n)))
            if days_online > 7:
                days_online = 7
            if days_online < 0:
                days_online = 0

            # Insert the value in the student forum data
            forum_student_data['Days online ' + str(week_n)] = days_online

            # Accumulate for the final field
            days_online_acc += days_online

            if days_online == 0:
                # If days online is zero, there is nothing else to do!
                forum_student_data['Views ' + str(week_n)] = 0
                forum_student_data['Contributions ' + str(week_n)] = 0
                forum_student_data['Questions ' + str(week_n)] = 0
                continue

            # Number of maximum items for this week
            max_items = week_contributions[week_n - 2]

            #
            # Contributions
            #
            # International students almost null
            # Part time, high
            # High score, much higher!
            # Rest, modest.
            if student_info['Enrolment Type'] == 'International':
                contr = int(round(random.normalvariate(0, 0.5)))
            elif student_info['Attendance'] == 'Part Time':
                contr = int(round(random.normalvariate(2, 1)))
            elif midterm_score > 6:
                contr = int(round(random.normalvariate(4, 0.5)))
            else:
                contr = int(round(random.normalvariate(1, 0.5)))
            if contr > max_items:
                contr = max_items
            if contr < 0:
                contr = 0

            # Insert the value in the student forum data
            forum_student_data['Contributions ' + str(week_n)] = contr

            # Accumulate for the final field
            contributions_acc += contr

            #
            # Answers
            # Calculated with respect to contributions (the rest are posts)
            #
            if contr == 0:
                questions = 0
            else:
                # Only makes sense if a student made a contribution
                if midterm_score > 6:
                    answers = random.randint(0, contr)
                else:
                    answers = random.randint(0, 1)
                if answers > contr:
                    answers = contr

                questions = contr - answers

            # Insert the value in the student forum data
            forum_student_data['Questions ' + str(week_n)] = questions

            # Accumulate for the final field
            questions_acc += questions

            #
            # Views
            #
            # International students very high
            # Part time, high
            # Rest, normal
            #
            # All of them correlate with the midterm score
            #
            if student_info['Enrolment Type'] == 'International':
                views = \
                    int(round(random.normalvariate(max_items *
                                                   midterm_score / 10,
                                                   max_items * 0.3)))
            elif student_info['Attendance'] == 'Part Time':
                views = \
                    int(round(random.normalvariate(max_items * 0.8 *
                                                   midterm_score / 10,
                                                   max_items * 0.2)))
            else:
                views = \
                    int(round(random.normalvariate(max_items * 0.5 *
                                                   midterm_score / 10,
                                                   max_items * 0.15)))
            if views > max_items:
                views = max_items
            if views < 0:
                views = 0

            # Make sure "views" is not less than contr or quesitons
            if views < contr or views < questions:
                views = max(contr, questions)

            # Insert the value in the student forum data
            forum_student_data['Views ' + str(week_n)] = views

            # Accumulate for the final field
            views_acc += views

        forum_student_data['Days online'] = days_online_acc
        forum_student_data['Views'] = views_acc
        forum_student_data['Contributions'] = contributions_acc
        forum_student_data['Questions'] = questions_acc

        forum_participation = forum_participation.append(forum_student_data,
            ignore_index=True)

    return forum_participation


def create_project_data(all_students):
    """Create the data for the project (rubric).

    Fields:
       - Structure
       - Presentation

    Rules:
    """
    project_rubric = pd.DataFrame()
    levels_of_attainment = ['High', 'Medium', 'Poor']

    # Loop for all the students
    for idx, student_info in all_students.iterrows():
        project_student_data = {'SID': student_info['SID']}

        if student_info['Enrolment Type'] == 'International':
            p_weights_structure = [.7, .2, .1]
            p_weights_prez = [.2, .5, .3]
        else:
            p_weights_structure = [.6, .3, .1]
            p_weights_prez = [.7, .2, .1]

        project_student_data['Structure'] = str(choice(
            levels_of_attainment,
            1,
            p=p_weights_structure)[0])
        project_student_data['Presentation'] = str(choice(
            levels_of_attainment,
            1,
            p=p_weights_prez)[0])

        project_rubric = project_rubric.append(
            project_student_data,
            ignore_index=True)

    return project_rubric


def create_blended_file(all_students):
    # Data about
    #
    # 2 activities: video + formative questions
    #
    # For each activity: % of video seen, % of questions attempted, % correct
    #
    # Times weeks 2-5
    #
    # Total: 24 columns (2 activites X 3 indicators X 4 weeks)
    #
    # All variables correlate with the midterm score

    blended_indicators = pd.DataFrame()

    # Loop for all the students
    for idx, student_info in all_students.iterrows():

        blended_student = {'SID': student_info['SID']}

        midterm_score = student_info.get('Total', 0)
        if pd.isna(midterm_score):
            midterm_score = 0.0
        else:
            midterm_score = int(midterm_score)

        # Loop for weeks 2 to 6
        for week_n in range(2, 6):

            # Generate random percentages
            perc = [random.normalvariate(midterm_score,
                20 - (midterm_score * 1.0) / 10)
                    for _ in range(0, 4)]
            perc = [100 if x > 100 else x for x in perc]
            perc = [0 if x < 0 else x for x in perc]

            perc[0] = int(perc[0] * 100) / 100.0
            perc[1] = int(perc[1] * 100) / 100.0
            blended_student['Video_1_W' + str(week_n)] = perc[0]
            blended_student['Video_2_W' + str(week_n)] = perc[1]
            q1 = round(perc[2] / 20)
            q2 = round(perc[3] / 20)
            blended_student['Questions_1_W' + str(week_n)] = q1
            blended_student['Questions_2_W' + str(week_n)] = q2

            # Percentage of correct questions
            value = random.normalvariate(midterm_score, 30)
            if value < 0:
                value = 0
            if value > 100:
                value = 100
            value = round(value / 20)
            if value > q1:
                value = q1
            blended_student['Correct_1_W' + str(week_n)] = value

            value = random.normalvariate(midterm_score, 30)
            if value < 0:
                value = 0
            if value > 100:
                value = 100
            value = round(value / 20)
            if value > q2:
                value = q2
            blended_student['Correct_2_W' + str(week_n)] = value

        blended_indicators = blended_indicators.append(
            blended_student,
            ignore_index=True)

    return blended_indicators


def main(file_name=None, num_students=500):
    if file_name is None:
        print(
            'Scrip needs the name of a file with the ',
            end=' ',
            file=sys.stderr)
        print('initial data set to process', file=sys.stderr)
        sys.exit(1)

    step_num = 1

    print('Step', step_num, 'Reading initial file', file_name)
    step_num += 1
    all_students = read_initial_file(file_name, num_students=num_students)

    print('  Initial list read with', len(all_students), 'elements.')
    print('  Fields:', ','.join(list(all_students.columns)))

    #
    # Adding SID column
    #
    assert 'SID' in student_list_fields
    print('Step', step_num, 'Adding column', 'SID')
    step_num += 1
    add_sid(all_students, 'SID', 300000000)

    #
    # Adding Identifier column
    #
    assert 'Identifier in student_list_fields'
    print('Step', step_num, 'Adding column', 'Identifier')
    step_num += 1
    add_identifier(all_students, 'Identifier')

    #
    # Adding email column
    #
    assert 'email' in student_list_fields
    print('Step', step_num, 'Adding email column')
    step_num += 1
    add_email(all_students)

    #
    # Adding Course Code
    #
    assert 'Course Code' in student_list_fields
    print('Step', step_num, 'Adding column', 'Course Code')
    step_num += 1
    add_column(all_students, 'Course Code', ['ELON3509'], [100])

    #
    # Adding columns for Program, Enrolment, Attendance
    #
    for column_name, values, weights in additional_columns:
        print('Step', step_num, 'Adding column', column_name)
        step_num += 1
        add_column(all_students,
            column_name,
            values,
            weights)
        student_list_fields.append(column_name)

    # Filter the undesired columns
    all_students = all_students[student_list_fields]

    #
    # Creating midterm answers
    #
    print('Step', step_num, 'Creating', midterm_answers_name)
    step_num += 1
    midterm_answers = create_midterm_data(all_students)

    #
    # Creating midterm results
    #
    print('Step', step_num, 'Creating', midterm_results_name)
    step_num += 1
    # Change the name of the fields so that they point to the result
    result_fields = midterm_answers_fields
    for x in range(4, 14):
        result_fields[x] = result_fields[x][1:]

    # Update all data
    all_students = pd.merge(
        all_students,
        midterm_answers[1:][result_fields].drop(
            ['email', 'Last Name', 'First Name'],
            axis=1
        ),
        how='left',
        on='SID')

    #
    # Creating forum data
    #
    print('Step', step_num, 'Creating', forum_name)
    step_num += 1
    forum_participation = create_forum_data(all_students)

    # Update all data
    all_students = pd.merge(all_students,
        forum_participation[forum_fields],
        how='left',
        on='SID')

    #
    # Creating project data
    #
    print('Step', step_num, 'Creating', project_name)
    step_num += 1
    project_rubric = create_project_data(all_students)

    # Update all data
    all_students = pd.merge(all_students,
        project_rubric[project_fields],
        how='left',
        on='SID')

    #
    # Creating blended information
    #
    print('Step', step_num, 'Creating', blended_name)
    step_num += 1
    blended_indicators = create_blended_file(all_students)

    # Update all data
    all_students = pd.merge(all_students,
        blended_indicators[blended_fields],
        how='left',
        on='SID')

    print('Step', step_num, 'Creating CSV files')
    step_num += 1

    # All data
    all_students.to_csv('all_data.csv', index=False)

    # Student info file
    generate_csv_file(all_students,
        student_list_name,
        student_list_fields,
        'Surname')

    # Midterm answers
    generate_csv_file(midterm_answers, midterm_answers_name,
        midterm_answers_fields, 'SID')

    # Midterm results
    generate_csv_file(midterm_answers[1:], midterm_results_name,
        result_fields, 'SID')

    # Forum data
    generate_csv_file(forum_participation, forum_name, forum_fields, 'SID')

    # Project data
    generate_csv_file(project_rubric, project_name, project_fields, 'SID')

    # Blended data
    generate_csv_file(blended_indicators, blended_name, blended_fields, 'SID')


# Execution as script
if __name__ == "__main__":
    n_students = 500
    if len(sys.argv) > 2:
        n_students = int(sys.argv[2])

    main(sys.argv[1], n_students)
