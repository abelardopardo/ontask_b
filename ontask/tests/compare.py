# -*- coding: utf-8 -*-

"""Functions to compare objects."""
import pandas as pd


def compare_workflows(w1, w2):
    """Compare two workflows."""
    suffix = 'mismatch {0}, {1}'.format(w1.id, w2.id)
    assert w1.user == w2.user, 'User ' + suffix
    assert w1.description_text == w2.description_text, 'Description ' + suffix
    assert w1.ncols == w2.ncols, 'Ncols ' + suffix
    assert w1.nrows == w2.nrows, 'Nrows ' + suffix
    assert w1.attributes == w2.attributes, 'Attributes ' + suffix
    assert (
        w1.data_frame_table_name == w1.df_table_prefix.format(w1.id)
    ), 'data frame table name ' + suffix
    assert (
        w2.data_frame_table_name == w2.df_table_prefix.format(w2.id)
    ), 'data frame table name ' + suffix
    assert w1.query_builder_ops == w2.query_builder_ops, 'Qbuilder ' + suffix
    assert (
        list(w1.shared.all()) == list(w2.shared.all())
    ), 'Shared ' + suffix

    assert w1.columns.count() == w2.columns.count(), 'ncol ' + suffix
    assert w1.views.count() == w2.views.count(), 'nviews ' + suffix
    assert w1.actions.count() == w2.actions.count(), 'nactions ' + suffix
    assert w1.conditions.count() == w2.conditions.count(), 'ncond ' + suffix
    assert w1.filters.count() == w2.filters.count(), 'nfilter ' + suffix

    for c1, c2 in zip(w1.columns.all(), w2.columns.all()):
        compare_columns(c1, c2)

    for a1, a2 in zip(w1.actions.all(), w2.actions.all()):
        compare_actions(a1, a2)

    for v1, v2 in zip(w1.views.all(), w2.views.all()):
        compare_views(v1, v2)


def compare_columns(c1, c2):
    """Compare two columns."""
    suffix = 'mismatch {0}, {1}'.format(c1.id, c2.id)
    assert c1.name == c2.name, 'Name ' + suffix
    assert c1.description_text == c2.description_text, 'Desc ' + suffix
    assert c1.data_type == c2.data_type, 'Type ' + suffix
    assert c1.is_key == c2.is_key, 'Is Key ' + suffix
    assert c1.position == c2.position, 'Position ' + suffix
    assert c1.categories == c2.categories, 'Categories ' + suffix
    assert c1.active_from == c2.active_from, 'Active from ' + suffix
    assert c1.active_to == c2.active_to, 'Active to ' + suffix


def compare_actions(a1, a2):
    """Compare two actions."""
    suffix = 'mismatch {0}, {1}'.format(a1.id, a2.id)
    assert a1.name == a2.name, 'Name ' + suffix
    assert a1.description_text == a2.description_text, 'Desc ' + suffix
    assert a1.action_type == a2.action_type, 'Type ' + suffix
    assert a1.serve_enabled == a2.serve_enabled, 'Serve enabled ' + suffix
    assert a1.active_from == a2.active_from, 'Active from ' + suffix
    assert a1.active_to == a2.active_to, 'Active to ' + suffix
    assert (
        a1.get_row_all_false_count() == a2.get_row_all_false_count()
    ), 'rows_all_false ' + suffix
    assert a1.text_content == a2.text_content, 'Content ' + suffix
    assert a1.target_url == a2.target_url, 'Target URL ' + suffix
    assert a1.shuffle == a2.shuffle, 'Shuffle ' + suffix

    for c1, c2 in zip(a1.conditions.all(), a2.conditions.all()):
        compare_conditions(c1, c2)

    compare_filters(a1.get_filter(), a2.get_filter())

    for t1, t2 in zip(
        a1.column_condition_pair.all(),
        a2.column_condition_pair.all(),
    ):
        compare_tuples(t1, t2)


def compare_conditions(c1, c2):
    """Compare two conditions."""
    if c1 is None and c2 is None:
        return

    suffix = 'mismatch {0}, {1}'.format(c1.id, c2.id)
    assert c1.name == c2.name, 'Name ' + suffix
    compare_filters(c1, c2)


def compare_filters(f1, f2):
    """Compare two filters."""
    if f1 is None and f2 is None:
        return

    suffix = 'mismatch {0}, {1}'.format(f1.id, f2.id)
    assert f1.is_filter == f2.is_filter, 'is filter ' + suffix
    assert f1.description_text == f2.description_text, 'Desc ' + suffix
    assert f1.formula == f2.formula, 'Formula ' + suffix
    assert f1.formula_text == f2.formula_text, 'Formula text ' + suffix
    assert f1.columns.count() == f2.columns.count(), 'Col count ' + suffix
    assert f1.selected_count == f2.selected_count, 'Selected count ' + suffix

    for cl1, cl2 in zip(f1.columns.all(), f2.columns.all()):
        assert cl1.name == cl2.name, 'Colname ' + suffix


def compare_views(v1, v2):
    """Compare two views."""
    suffix = 'mismatch {0}, {1}'.format(v1.id, v2.id)
    assert v1.name == v2.name, 'Name ' + suffix
    assert v1.description_text == v2.description_text, 'Desc ' + suffix
    compare_filters(v1.filter, v2.filter)


def compare_tuples(t1, t2):
    """Compare action, condition, column tuples."""
    suffix = 'mismatch {0}, {1}'.format(t1.action.id, t2.action.id)
    assert t1.action.name == t2.action.name, 'Action Name ' + suffix
    assert (
        t1.condition == t2.condition
        or t1.condition.name == t2.condition.name
    ), 'Condition ' + suffix
    assert t1.column.name == t2.column.name, 'Column Name ' + suffix


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
        assert (
            [jval for jval in list(jvals) if not pd.isnull(jval)]
            == [dfval for dfval in list(dfvals) if not pd.isnull(dfval)])
