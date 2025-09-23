######################################################################################################
#                                 Auto-generated Metaflow stub file                                  #
# MF version: 2.18.8                                                                                 #
# Generated on 2025-09-22T21:43:14.140394                                                            #
######################################################################################################

from __future__ import annotations



SFN_DYNAMO_DB_TABLE: None

class DynamoDbClient(object, metaclass=type):
    def __init__(self):
        ...
    def save_foreach_cardinality(self, foreach_split_task_id, foreach_cardinality, ttl):
        ...
    def save_parent_task_id_for_foreach_join(self, foreach_split_task_id, foreach_join_parent_task_id):
        ...
    def get_parent_task_ids_for_foreach_join(self, foreach_split_task_id):
        ...
    ...

