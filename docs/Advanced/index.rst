.. _advanced_features:

=================
Advanced Features
=================

OnTask is built in `Python <https://www.python.org/>`_ using the web framework `Django <https://www.djangoproject.com/>`_ in combination with some additional libraries such as `Django REST Framework <http://www.django-rest-framework.org/>`_, `Pandas <https://pandas.pydata.org/>`_, etc. The application is available as `open source <https://github.com/abelardopardo/ontask_b>`_ with `MIT License <https://github.com/abelardopardo/ontask_b/blob/master/LICENSE>`_. This means that the advanced users can get a copy of the source code and modify it to suite their needs using the already existing models and functions.

The API (Application Programming Interface)
-------------------------------------------

OnTask is a platform that facilitates the connection between data and the
provision of personalised learner support actions. The higher the quality of
the data the higher number of possible effective support actions. This means
that OnTask should facilitate the connection with already existing data
sources so that it can combine data sets and create a comprehensive view of
how a learning experience is evolving.

The API is documented online through the URL suffix ``apidoc``. The page
contains the description of every entry point available with the required
parameters.

When manipulating the elements in the table there are two versions of the
basic operations (create a table, update a table, merge).

1. Pandas Version. This version handles the encoding of data frames using the
   pandas pickle encoding. This encoding has the advantage that maintains the
   elements of the dataframe intact. In other words, when the data frame is
   decoded from the pandas pickle format back to a regular dataframe, the same
   initial dataframe is obtained.

2. JSON Version. This version encodes the dataframes in JSON. The problem
   with this format is that values such as NaN and NaT (not a time) are not
   allowed by JSON, and they are substituted by empty strings. This change
   may have significant effects on the dataframe, specially on the types of
   the columns. If there is a dataframe with a column of type datetime and
   with any element with value NaT and it is first extracted through the JSON
   interface, and then uploaded again, the NaT value is transformed into an
   empty string, and Pandas will no longer recognise that column as
   datetime, but instead it will render the column of type string. This my
   have also an effect on how rules and actions are evaluated.

