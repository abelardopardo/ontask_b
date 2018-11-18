var qbuilder_options = {
  plugins: ['bt-tooltip-errors', 'not-group'],
  operators: ['equal', 'not_equal', 'less', 'less_or_equal',
              'greater', 'greater_or_equal', 'between', 'not_between',
              'begins_with', 'not_begins_with', 'contains', 'not_contains',
              'ends_with', 'not_ends_with', 'is_empty', 'is_not_empty',
              'is_null', 'is_not_null'],
  allow_empty: {{ allow_empty }},
  filters: {{ query_builder_ops|safe }},
};
