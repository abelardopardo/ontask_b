.. _bulk_user_creation:

Creating users in Bulk
**********************

OnTask offers the possibility of creating users in bulk through given the
data in a CSV file through the following steps:

1. Create a CSV file (plain text) with the initial line containing only the
   word ``email`` (name of the column). Include then one email address per
   user per line. You may check the file ``initial_learners.csv`` provided in
   the folder ``scripts``.

2. From the top level folder run the command::

     $ python3 manage.py initialize_db scripts/initial_learners.csv"

   If you have the user emails in a file with a different column name, you
   may provide the script that name (instead of the default ``email`` using
   the option ``-e``::

     $ python3 manage.py initialize_db -e your_email_column_name scripts/initial_learners.csv"

   If you want to create user accounts for instructors, you need to specify
   this with the option ``-i`` in the script::

     $ python3 manage.py initialize_db -e your_email_column_name -i scripts/initial_learners.csv"

