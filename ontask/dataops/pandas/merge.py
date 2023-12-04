"""Functions to do data frame merging."""
from typing import Dict, Optional

from django.utils.translation import gettext
import pandas as pd

from ontask.dataops import pandas


def _perform_non_overlapping_column_merge(
    dst_df: pd.DataFrame,
    src_df_no_overlap: pd.DataFrame,
    merge_info: Dict,
    dst_key: str,
    src_key: str,
) -> pd.DataFrame:
    """Merge the non overlapping columns of the new data frame.

    :param dst_df: Existing data frame
    :param src_df_no_overlap: portion of the src_df with no overlap
    :param merge_info: Information about how to merge
    :param dst_key: key column in dst_frame
    :param src_key: key column in src_frame
    :return: Modified data frame
    """
    # Step A. Perform the merge of non-overlapping columns
    new_df = dst_df
    if len(src_df_no_overlap.columns) > 1:
        new_df = pd.merge(
            new_df,
            src_df_no_overlap,
            how=merge_info['how_merge'],
            left_on=dst_key,
            right_on=src_key)

        # VERY special case: The key used for the merge in src_df can have an
        # identical column in dst_df, but it is not the one used for the
        # merge. For example: DST has columns C1(key), C2, C3, SRC has
        # columns C2(key) and C4. The merge is done matching C1 in DST with
        # C2 in SRC, but this will produce two columns C2_x and C2_y. In this
        # case we drop C2_y because C2_x has been properly updated with the
        # values from C2_y in the previous step (Step A).
        if src_key != dst_key and src_key in dst_df.columns:
            # Drop column_y
            new_df.drop([src_key + '_y'], axis=1, inplace=True)
            # Rename column_x
            new_df = new_df.rename(columns={src_key + '_x': src_key})

    return new_df


def _perform_overlap_update(
    dst_df: pd.DataFrame,
    src_df: pd.DataFrame,
    dst_key: str,
    src_key: str,
    how_merge: str,
) -> pd.DataFrame:
    """Perform the updat of the columns that overlap with the data_frame.

    :param dst_df: Left data frame with all the columns
    :param src_df: Right data frame with the overlapping columns
    :param dst_key: Left key column
    :param src_key: Right key column
    :param how_merge: Merge version: inner, outer, left or right
    :return: Returns the updated data frame depending on the type of merge
    variant requested.

    For this function the 'update' and 'append' functions in Pandas will be
    used.

    The 'update' function will be used for those rows for
    which there is a corresponding key in src_df. This means that the data in
    dst_df_tmp1 will only be updated if the value is not NaN.

    The 'append' function will be used for those rows in src_df that are not
    present in dst_df.

    There are four possible cases for this STEP depending on the type of
    merge (inner, outer, left, right). Here is the pseudocode used for each
    of these cases:

    - left: Simplest case because this is exactly how the function 'update'
    behaves. So, in this case dst_df_tmp1.update(src_df[OVERLAP]) is the
    result.

    - inner: First obtain the subset dst_df_tmp1 with intersection of
    dst_df_tmp1 and src_df keys (result in dst_df_tmp2) and then update
    dst_df_tmp2 with src_df[OVERLAP]

    - outer: First apply the update operation in the left case, that is
    dst_df_tmp1.update(src_df[OVERLAP], select from src_df[OVERLAP] the rows
    that are not part of dst_df_tmp1, and then append these to dst_df_tmp1 to
    create the result dst_df_tmp2

    - right: This is the most complex. It requires first to subset
    dst_df_tmp1 with the intersection of the two keys (src and dst). Then,
    dst_df_tmp1 is updated with the content of src_df[OVERLAP]. Finally,
    the rows only in the src_df need to be appended to the dataframe.
    """
    # If the src data frame has a single column (they key), there is no need
    # to do any operation
    if len(src_df.columns) <= 1:
        return dst_df

    dst_df_tmp1 = dst_df.set_index(dst_key, drop=False)
    src_df_tmp1 = src_df.set_index(src_key, drop=False)
    if how_merge == 'inner':
        # Subset of dst_df_tmp1 with the keys in both DFs
        overlap_df = dst_df_tmp1.loc[
            dst_df_tmp1.index.intersection(src_df_tmp1.index)
        ].copy()
        # Update the subset with the values in the right
        overlap_df.update(src_df_tmp1)
    elif how_merge == 'outer':
        # Update
        overlap_df = dst_df_tmp1
        overlap_df.update(src_df_tmp1)
        # Append the missing rows
        tmp1 = src_df_tmp1.loc[
            src_df_tmp1.index.difference(dst_df_tmp1.index)
        ].copy()
        if not tmp1.empty:
            # Append only if the tmp1 data frame is not empty (otherwise it
            # looses the name of the index column
            overlap_df = pd.concat([overlap_df, tmp1], sort=True)
    elif how_merge == 'left':
        overlap_df = dst_df_tmp1
        overlap_df.update(src_df_tmp1)
    else:
        # Right merge
        # Subset of dst_df_tmp1 with the keys in both DFs
        overlap_df = dst_df_tmp1.loc[
            dst_df_tmp1.index.intersection(src_df_tmp1.index)
        ].copy()
        # Update with the right DF
        overlap_df.update(src_df_tmp1)
        # Append the rows that are in right and not in left
        tmp2 = src_df_tmp1.loc[
            src_df_tmp1.index.difference(dst_df_tmp1.index)
        ].copy()
        if not tmp2.empty:
            # Append only if it is not empty
            overlap_df = pd.concat([overlap_df, tmp2], sort=True)

    # Return result
    return overlap_df.reset_index(drop=True)


def _update_is_key_field(merge_info: Dict, workflow):
    """Traverse the list of columns and reset the key property.

    :param merge_info: dictionary with the lists of columns to upload, rename
    and keep as key
    :param workflow: current workflow (to access columns)
    :result: None
    """
    # Update the value of is_key based on "keep_key_column"
    for to_upload, cname, keep_key in zip(
        merge_info['columns_to_upload'],
        merge_info['rename_column_names'],
        merge_info['keep_key_column'],
    ):
        if not to_upload:
            # Column is not uploaded, nothing to process
            continue

        col = workflow.columns.get(name=cname)

        # Process the is_key property. The is_key property has been
        # recalculated during the store, now it needs to be updated looking at
        # the keep_key value.
        col.is_key = col.is_key and keep_key
        col.save(update_fields=['is_key'])


def validate_merge_parameters(
    dst_df: pd.DataFrame,
    src_df: pd.DataFrame,
    how_merge: str,
    left_on: str,
    right_on: str,
) -> Optional[str]:
    """Verify that the merge parameters are correct

    :return: Error message, or none if everything is correct
    """
    # Check that the parameters are correct
    if not how_merge or how_merge not in ['left', 'right', 'outer', 'inner']:
        return gettext('Merge method must be one of '
                       'left, right, outer or inner')

    if left_on not in list(dst_df.columns):
        return gettext(
            'Column {0} not found in current data frame').format(left_on)

    if not pandas.is_unique_series(dst_df[left_on]):
        return gettext('Column {0} is not a unique key.').format(left_on)

    if right_on not in list(src_df.columns):
        return gettext(
            'Column {0} not found in new data frame').format(right_on)

    if not pandas.is_unique_series(src_df[right_on]):
        return gettext(
            'Column {0} is not a unique key.').format(right_on)

    return None


def perform_dataframe_upload_merge(
    workflow,
    dst_df: pd.DataFrame,
    src_df: pd.DataFrame,
    merge_info: Dict,
):
    """Merge the existing data frame (dst) with a new one (src).

    It combines the two data frames dst_df and src_df and stores its content.

    The combination of dst_df and src_df assumes:

    - dst_df has a set of columns (potentially empty) that do not overlap in
      name with the ones in src_df (dst_df[NO_OVERLAP_DST])

    - dst_df and src_df have a set of columns (potentially empty) that overlap
      in name (dst_df[OVERLAP] and src_df[OVERLAP] respectively)

    - src_df has a set of columns (potentially empty) that do not overlap in
      name with the ones in dst_df (src_df[NO_OVERLAP_SRC])

    The function combines dst_df and src_df following two main steps (in both
    steps, the number of rows processed are derived from the parameter
    merge_info['how_merge']).

    STEP A: A new data frame dst_df_tmp1 is created using the pandas "merge"
    operation between dst_df and src_df[NO_OVERLAP_SRC]. This increases the
    number of columns in dst_df_tmp1 with respect to dst_df by adding the new
    columns from src_df.

    The pseudocode for this step is:

    dst_df_tmp1 = pd.merge(dst_df,
                           src_df[NO_OVERLAP_SRC],
                           how=merge['how_merge'],
                           left_on=merge_info['dst_selected_key'],
                           right_on=merge_info['src_selected_key'])

    STEP B: The data frame dst_df_tmp1 is then updated with the values in
    src_df[OVERLAP].

    :param workflow: Workflow with the data frame
    :param dst_df: Destination dataframe (already stored in DB)
    :param src_df: Source dataframe, stored in temporary table
    :param merge_info: Dictionary with merge options
           - initial_column_names: List of initial column names in src data
             frame.
           - rename_column_names: Columns that need to be renamed in src data
             frame.
           - columns_to_uplooad: Columns to be considered for the update
           - src_selected_key: Key in the source data frame
           - dst_selected_key: key in the destination (existing) data frame
           - how_merge: How to merge: inner, outer, left or right
    :return: None or Exception with anomaly in the message
    """
    # STEP 1 Rename the column names.
    src_df = src_df.rename(
        columns=dict(list(zip(
            merge_info['initial_column_names'],
            merge_info['rename_column_names']))))

    # STEP 2 Drop the columns not selected
    columns_to_upload = merge_info['columns_to_upload']
    src_df.drop(
        [
            col for idx, col in enumerate(list(src_df.columns))
            if not columns_to_upload[idx]
        ],
        axis=1,
        inplace=True)

    # If no keep_key_column value is given, initialize to True
    if 'keep_key_column' not in merge_info:
        kk_column = []
        for cname in merge_info['rename_column_names']:
            kk_column.append(pandas.is_unique_series(src_df[cname]))
        merge_info['keep_key_column'] = kk_column

    # Get the keys
    src_key = merge_info['src_selected_key']
    dst_key = merge_info['dst_selected_key']

    # STEP 3 Perform the combination
    # Separate the columns in src that overlap from those that do not
    # overlap, but include the key column in both data frames.
    overlap_names = set(dst_df.columns).intersection(src_df.columns)
    src_no_overlap_names = set(src_df.columns).difference(overlap_names)
    src_df_overlap = src_df[list(overlap_names.union({src_key}))]
    src_df_no_overlap = src_df[list(src_no_overlap_names.union({src_key}))]

    # Step A. Perform the merge of non-overlapping columns
    new_df = _perform_non_overlapping_column_merge(
        dst_df,
        src_df_no_overlap,
        merge_info,
        dst_key,
        src_key)

    # Step B. Perform the update with the overlapping columns
    new_df = _perform_overlap_update(
        new_df,
        src_df_overlap,
        dst_key,
        src_key,
        merge_info['how_merge'])

    # If the merge produced a data frame with no rows, flag it as an error to
    # prevent loosing data when there is a mistake in the key column
    if new_df.shape[0] == 0:
        raise Exception(gettext(
            'Merge operation produced a result with no rows'))

    # If the merge produced a data frame with no unique columns, flag it as an
    # error to prevent the data frame from propagating without a key column
    if not pandas.has_unique_column(new_df):
        raise Exception(gettext(
            'Merge operation produced a result without any key columns. '
            + 'Review the key columns in the data to upload.',
        ))

    # Store the result back in the DB
    pandas.store_dataframe(new_df, workflow)

    _update_is_key_field(merge_info, workflow)

    # Recompute all the values of the conditions in each of the actions
    for action in workflow.actions.all():
        action.update_selected_row_counts()
