.. _tut_personalized_text_and_surveys:

Combining personalized text and surveys
=======================================

The information collected through :ref:surveys<tut_surveys>` is stored in the appropriate columns in the data table and therefore can be used in a personalized text action to select the appropriate message. For example, the information collected as answers to the question *What was the most challenging topic for you this week?* can be used to select a set of appropriate links to resources about the given topic. The answers are stored in column `Survey Q1` in the Table. Analogously, the answers to the question *What was your dedication to the course this week?* are stored in the Table in the column with name `Survey Q2`.

The values in these columns can be used to create a personalized text action that provides a text with suggestions for additional resources or techniques to adopt based, for example, on the program in which the student is enrolled and the topic they found more challenging. Additionally, the text could include some suggestions depending on the estimated number of work hours the student reported in the survey.

When using the values previously collected in a survey, special care must be taken to account for those learners that did not answer the survey (or did so partially). This can be easily achieved by adding additional conditions or simply filtering those students for which any of the columns in the survey is empty (a disjunction of the conditions *Survey Q1 is empty* or *Survey Q2 is empty*).



