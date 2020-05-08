# -*- coding: utf-8 -*-

"""Functions to compare objects."""
import pandas as pd


def compare_workflows(w1, w2):
    """Compare two workflows."""
    assert w1.user == w2.user
    assert w1.description_text == w2.description_text
    assert w1.ncols == w2.ncols
    assert w1.nrows == w2.nrows
    assert w1.attributes == w2.attributes
    assert w1.data_frame_table_name == w1.df_table_prefix.format(w1.id)
    assert w2.data_frame_table_name == w2.df_table_prefix.format(w2.id)
    assert w1.query_builder_ops == w2.query_builder_ops
    assert w1.nrows == w2.nrows
    assert list(w1.shared.all()) == list(w2.shared.all())

    for c1, c2 in zip(w1.columns.all(), w2.columns.all()):
        compare_columns(c1, c2)

    for a1, a2 in zip(w1.actions.all(), w2.actions.all()):
        compare_actions(a1, a2)

    for v1, v2 in zip(w1.views.all(), w2.views.all()):
        compare_views(v1, v2)


def compare_columns(c1, c2):
    """Compare two columns."""
    assert c1.name == c2.name
    assert c1.description_text == c2.description_text
    assert c1.data_type == c2.data_type
    assert c1.is_key == c2.is_key
    assert c1.position == c2.position
    assert c1.categories == c2.categories
    assert c1.active_from == c2.active_from
    assert c1.active_to == c2.active_to


def compare_actions(a1, a2):
    """Compare two actions."""
    assert a1.name == a2.name
    assert a1.description_text == a2.description_text
    assert a1.action_type == a2.action_type
    assert a1.serve_enabled == a2.serve_enabled
    assert a1.active_from == a2.active_from
    assert a1.active_to == a2.active_to
    assert a1.rows_all_false == a2.rows_all_false
    assert a1.text_content == a2.text_content
    assert a1.target_url == a2.target_url
    assert a1.shuffle == a2.shuffle

    for c1, c2 in zip(a1.conditions.all(), a2.conditions.all()):
        compare_conditions(c1, c2)

    for t1, t2 in zip(
        a1.column_condition_pair.all(),
        a2.column_condition_pair.all(),
    ):
        compare_tuples(t1, t2)


def compare_conditions(c1, c2):
    """Compare two conditions."""
    assert c1.name == c2.name
    assert c1.description_text == c2.description_text
    assert c1.formula == c2.formula
    assert c1.columns.count() == c2.columns.count()
    assert c1.n_rows_selected == c2.n_rows_selected
    assert c1.is_filter == c2.is_filter

    for cl1, cl2 in zip(c1.columns.all(), c2.columns.all()):
        assert cl1.name == cl2.name


def compare_views(v1, v2):
    """Compare two views."""
    assert v1.name == v2.name
    assert v1.description_text == v2.description_text
    assert v1.formula == v2.formula
    assert v1.nrows == v2.nrows


def compare_tuples(t1, t2):
    """Compare action, condition, column tuples."""
    assert t1.action.name == t2.action.name
    assert(
        t1.condition == t2.condition
        or t1.condition.name == t2.condition.name)
    assert t1.column.name == t2.column.name


def are_identical_dataframes(m1: pd.DataFrame, m2: pd.DataFrame):
    """Compare two pandas data frames.

    :param m1: Pandas data frame
    :param m2: Pandas data frame
    :return: Nothing if they are correct, exception if incorrect.
    """
    # If both are empty, done.
    if m2 is None and m1 is None:
        return

    # Assert that the number of columns are identical
    assert len(list(m1.columns)) == len(list(m2.columns))

    # The names of the columns have to be identical
    assert set(list(m1.columns)) == set(list(m2.columns))

    # Check the values of every column
    for cname in list(m1.columns):
        jvals = m1[cname].values
        dfvals = m2[cname].values

        # Compare removing the NaN, otherwise, the comparison breaks.
        assert(
            [jval for jval in list(jvals) if not pd.isnull(jval)]
            == [dfval for dfval in list(dfvals) if not pd.isnull(dfval)])
