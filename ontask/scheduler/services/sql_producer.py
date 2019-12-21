# -*- coding: utf-8 -*-

"""Service to create a SQL update operation.."""
from typing import Dict

from ontask import models


def create_scheduled_sql_upload(
    connection: models.SQLConnection,
    sql_operation: models.ScheduledOperation,
    field_values: Dict
):
    pass
