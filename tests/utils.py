from dataclasses import asdict
from typing import Union

import pandas as pd
from forloop_common_structures.core.edge import Edge
from forloop_common_structures.core.node import Node
from forloop_common_structures.core.pipeline import Pipeline
from forloop_common_structures.core.project import Project
from forloop_common_structures.core.session import Session
from forloop_common_structures.core.trigger import Trigger
from forloop_common_structures.core.user import User
from forloop_common_structures.core.variable import Variable

from src.database_models import (
    cast_edge_types_to_db,
    cast_node_types_to_db,
    cast_pipeline_types_to_db,
    cast_project_types_to_db,
    cast_trigger_types_to_db,
    # cast_user_types_to_db,
    cast_variable_types_to_db,
    extract_last_id,
    table_dict,
)

nodes_table = table_dict['nodes']
pipelines_table = table_dict['pipelines']
projects_table = table_dict['projects']
triggers_table = table_dict['triggers']
users_table = table_dict['users']
variables_table = table_dict['variables']
edges_table = table_dict['edges']


class TestError(Exception):
    pass


class DbEntityFactory:
    """
    Helper class, simplifies generation of DB model instances for test cases. Instead of
    manually instantiating models, simply call 'create_*' method exposed by this class to generate a
    model with generic values, where they are not necessary to be specified directly. Unique
    arguments which the user must provide should be provided as arguments.
    """

    def __init__(self) -> None:
        self.MAX_INSTANCES = 5
        self.count = {Pipeline.__name__: 0, Project.__name__: 0, User.__name__: 0}
        self.int_map = {1: 'One', 2: 'Two', 3: 'Three', 4: 'Four', 5: 'Five'}

    def create_user(self) -> User:
        self._increment_count(User)

        user = User(
            email=f'email{self.count[User.__name__]}@gmail.com',
            auth0_subject_id=f'id{self.count[User.__name__]}',
            given_name=f'first{self.int_map[self.count[User.__name__]]}',
            family_name=f'last{self.int_map[self.count[User.__name__]]}',
            picture_url=f'picture{self.count[User.__name__]}',
        )
        return user

    def create_project(self, user: User) -> Project:
        self._increment_count(Project)
        self.count[Project.__name__] += 1
        return Project(
            project_name=f'project{self.count[User.__name__]}',
            project_key=user.email.replace('@', 'at'),
        )

    def create_pipeline(self, project: Project) -> Pipeline:
        self._increment_count(Pipeline)
        self.count[Pipeline.__name__] += 1
        return Pipeline(
            name=f'pipeline{self.count[User.__name__]}', project_uid=project.uid
        )

    def _increment_count(
        self, model: Union[type[Pipeline], type[Project], type[User], type[Session]]
    ) -> None:
        if self.count[model.__name__] > self.MAX_INSTANCES:
            raise TestError(f'Maximum number of {model.__name__} instances reached')
        self.count[User.__name__] += 1


def save_and_update_user(user: User) -> User:
    df_users = pd.DataFrame([asdict(user)])

    # TODO: commented due to disabled function cast_user_types_to_db
    # df_db_users = cast_user_types_to_db(df_users)
    users_df = df_users.drop('uid', axis=1)
    users_table.insert_from_df(users_df)
    user.uid = extract_last_id(users_table)
    return user


def save_and_update_project(project: Project) -> Project:
    df_projects = pd.DataFrame([asdict(project)])
    df_db_projects = cast_project_types_to_db(df_projects)
    projects_table.insert_from_df(df_db_projects)
    project.uid = extract_last_id(projects_table)
    return project


def save_and_update_pipeline(pipeline: Pipeline) -> Pipeline:
    df_pipelines = pd.DataFrame([asdict(pipeline)])
    df_db_pipelines = cast_pipeline_types_to_db(df_pipelines)
    pipelines_table.insert_from_df(df_db_pipelines)
    pipeline.uid = extract_last_id(pipelines_table)
    return pipeline


def save_and_update_node(node: Node) -> Node:
    df_nodes = pd.DataFrame([asdict(node)])
    df_db_nodes = cast_node_types_to_db(df_nodes)
    nodes_table.insert_from_df(df_db_nodes)
    node.uid = extract_last_id(nodes_table)
    return node


def save_and_update_edge(edge: Edge) -> Edge:
    df_edges = pd.DataFrame([asdict(edge)])
    df_db_edges = cast_edge_types_to_db(df_edges)
    edges_table.insert_from_df(df_db_edges)
    edge.uid = extract_last_id(edges_table)
    return edge


def save_and_update_variable(variable: Variable) -> Variable:
    df_variables = pd.DataFrame([asdict(variable)])
    df_db_variables = cast_variable_types_to_db(df_variables)
    variables_table.insert_from_df(df_db_variables)
    variable.uid = extract_last_id(variables_table)
    return variable


def save_and_update_trigger(trigger: Trigger) -> Trigger:
    triggers_df = pd.DataFrame([asdict(trigger)])
    db_triggers_df = cast_trigger_types_to_db(triggers_df)
    triggers_table.insert_from_df(db_triggers_df)
    trigger.uid = extract_last_id(triggers_table)
    return trigger
