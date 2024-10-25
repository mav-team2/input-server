# import logging
# from collections import namedtuple
# from collections.abc import Iterable
# from itertools import chain
# from typing import List, Annotated, Union
#
# from fastapi import Query, Depends
# from pycparser.ply.yacc import string_types
# from pydantic import constr, Json
# from sqlalchemy import func, or_, desc, and_, not_, orm
#
# from src.api.database.database import DbSession, get_class_by_tablename, Base
#
# log = logging.getLogger(__file__)
#
# # allows only printable characters
# QueryStr = constr(pattern=r"^[ -~]+$", min_length=1)
# BooleanFunction = namedtuple("BooleanFunction", ("key", "sqlalchemy_fn", "only_one_arg"))
# BOOLEAN_FUNCTIONS = [
#     BooleanFunction("or", or_, False),
#     BooleanFunction("and", and_, False),
#     BooleanFunction("not", not_, True),
# ]
#
#
# # def common_parameters(
# #         db_session: DbSession,
# #         page: int = Query(1, gt=0, lt=2147483647),
# #         items_per_page: int = Query(5, alias="itemsPerPage", gt=-2, lt=2147483647),
# #         query_str: QueryStr = Query(None, alias="q"),
# #         filter_spec: Json = Query([], alias="filter"),
# #         sort_by: List[str] = Query([], alias="sortBy[]"),
# #         descending: List[bool] = Query([], alias="descending[]")
# # ):
# #     return {
# #         "db_session": db_session,
# #         "page": page,
# #         "items_per_page": items_per_page,
# #         "query_str": query_str,
# #         "filter_spec": filter_spec,
# #         "sort_by": sort_by,
# #         "descending": descending,
# #     }
#
#
# # CommonParameters = Annotated[
# #     dict[str, Union[int, DbSession, QueryStr, Json, List[str], List[bool]]],
# #     Depends(common_parameters),
# # ]
#
#
# def _is_iterable_filter(filter_spec):
#     """`filter_spec` may be a list of nested filter specs, or a dict."""
#     return isinstance(filter_spec, Iterable) and not isinstance(filter_spec, (string_types, dict))
#
#
# def build_filters(filter_spec):
#     """Recursively process `filter_spec`"""
#     if _is_iterable_filter(filter_spec):
#         return list(chain.from_iterable(build_filters(item) for item in filter_spec))
#
#     if isinstance(filter_spec, dict):
#         # Check if filter spec defines a boolean function.
#         for boolean_function in BOOLEAN_FUNCTIONS:
#             if boolean_function.key in filter_spec:
#                 # The filter spec is for a boolean-function
#                 # Get the function argument definitions and validate
#                 fn_args = filter_spec[boolean_function.key]
#
#                 if not _is_iterable_filter(fn_args):
#                     raise BadFilterFormat(
#                         "`{}` value must be an iterable across the function "
#                         "arguments".format(boolean_function.key)
#                     )
#                 if boolean_function.only_one_arg and len(fn_args) != 1:
#                     raise BadFilterFormat(
#                         "`{}` must have one argument".format(boolean_function.key)
#                     )
#                 if not boolean_function.only_one_arg and len(fn_args) < 1:
#                     raise BadFilterFormat(
#                         "`{}` must have one or more arguments".format(boolean_function.key)
#                     )
#                 return [BooleanFilter(boolean_function.sqlalchemy_fn, *build_filters(fn_args))]
#
#     return [Filter(filter_spec)]
#
#
# def search(*, query_str: str, query: Query, model: str, sort=False):
#     """Perform a search based on the query."""
#     search_model = get_class_by_tablename(model)
#
#     if not query_str.strip():
#         return query
#
#     search = []
#     if hasattr(search_model, "search_vector"):
#         vector = search_model.search_vector
#         search.append(vector.op("@@")(func.tsq_parse(query_str)))
#
#     if hasattr(search_model, "name"):
#         search.append(
#             search_model.name.ilike(f"%{query_str}%"),
#         )
#         search.append(search_model.name == query_str)
#
#     if not search:
#         raise Exception(f"Search not supported for model: {model}")
#
#     query = query.filter(or_(*search))
#
#     if sort:
#         query = query.order_by(desc(func.ts_rank_cd(vector, func.tsq_parse(query_str))))
#
#     return query.params(term=query_str)
#
#
#
# def apply_filters(query, filter_spec, model_cls=None, do_auto_join=True):
#     """Apply filters to a SQLAlchemy query.
#
#     :param query:
#         A :class:`sqlalchemy.orm.Query` instance.
#
#     :param filter_spec:
#         A dict or an iterable of dicts, where each one includes
#         the necessary information to create a filter to be applied to the
#         query.
#
#         Example::
#
#             filter_spec = [
#                 {'model': 'Foo', 'field': 'name', 'op': '==', 'value': 'foo'},
#             ]
#
#         If the query being modified refers to a single model, the `model` key
#         may be omitted from the filter spec.
#
#         Filters may be combined using boolean functions.
#
#         Example:
#
#             filter_spec = {
#                 'or': [
#                     {'model': 'Foo', 'field': 'id', 'op': '==', 'value': '1'},
#                     {'model': 'Bar', 'field': 'id', 'op': '==', 'value': '2'},
#                 ]
#             }
#
#     :returns:
#         The :class:`sqlalchemy.orm.Query` instance after all the filters
#         have been applied.
#     """
#     default_model = get_default_model(query)
#     if not default_model:
#         default_model = model_cls
#
#     filters = build_filters(filter_spec)
#     filter_models = get_named_models(filters)
#
#     if do_auto_join:
#         query = auto_join(query, filter_models)
#
#     sqlalchemy_filters = [filter.format_for_sqlalchemy(query, default_model) for filter in filters]
#
#     if sqlalchemy_filters:
#         query = query.filter(*sqlalchemy_filters)
#
#     return query
#
#
# def apply_filter_specific_joins(model: Base, filter_spec: dict, query: orm.query):
#     """Applies any model specific implicitly joins."""
#     # this is required because by default sqlalchemy-filter's auto-join
#     # knows nothing about how to join many-many relationships.
#     filters = build_filters(filter_spec)
#
#     # Replace mapping if looking for commander
#     if "Commander" in str(filter_spec):
#         model_map.update({(Incident, "IndividualContact"): (Incident.commander, True)})
#     if "Assignee" in str(filter_spec):
#         model_map.update({(Case, "IndividualContact"): (Case.assignee, True)})
#
#     filter_models = get_named_models(filters)
#     joined_models = []
#     for filter_model in filter_models:
#         if model_map.get((model, filter_model)):
#             joined_model, is_outer = model_map[(model, filter_model)]
#             try:
#                 if joined_model not in joined_models:
#                     query = query.join(joined_model, isouter=is_outer)
#                     joined_models.append(joined_model)
#             except Exception as e:
#                 log.exception(e)
#
#     return query
#
#
# def search_filter_sort_paginate(
#         db_session,
#         model,
#         query_str: str = None,
#         filter_spec: List[dict] = None,
#         page: int = 1,
#         items_per_page: int = 5,
#         sort_by: List[str] = None,
#         descending: List[bool] = None
# ):
#     """Common functionality for searching, filtering, sorting, and pagination."""
#     model_cls = get_class_by_tablename(model)
#
#     try:
#         query = db_session.query(model_cls)
#
#         if query_str:
#             sort = False if sort_by else True
#             query = search(query_str=query_str, query=query, model=model, sort=sort)
#
#         query_restricted = apply_model_specific_filters(model_cls, query)
#
#         tag_all_filters = []
#         if filter_spec:
#             query = apply_filter_specific_joins(model_cls, filter_spec, query)
#             # if the filter_spec has the TagAll filter, we need to split the query up
#             # and intersect all of the results
#             if has_tag_all(filter_spec):
#                 new_filter_spec, tag_all_spec = rebuild_filter_spec_without_tag_all(filter_spec)
#                 if new_filter_spec:
#                     query = apply_filters(query, new_filter_spec, model_cls)
#                 for tag_filter in tag_all_spec:
#                     tag_all_filters.append(apply_filters(query, tag_filter, model_cls))
#             else:
#                 query = apply_filters(query, filter_spec, model_cls)
#
#         if model == "Incident":
#             query = query.intersect(query_restricted)
#             for filter in tag_all_filters:
#                 query = query.intersect(filter)
#
#         if model == "Case":
#             query = query.intersect(query_restricted)
#             for filter in tag_all_filters:
#                 query = query.intersect(filter)
#
#         if sort_by:
#             sort_spec = create_sort_spec(model, sort_by, descending)
#             query = apply_sort(query, sort_spec)
#
#     except FieldNotFound as e:
#         raise ValidationError(
#             [
#                 ErrorWrapper(FieldNotFoundError(msg=str(e)), loc="filter"),
#             ],
#             model=BaseModel,
#         ) from None
#     except BadFilterFormat as e:
#         raise ValidationError(
#             [ErrorWrapper(InvalidFilterError(msg=str(e)), loc="filter")], model=BaseModel
#         ) from None
#
#     if items_per_page == -1:
#         items_per_page = None
#
#     # sometimes we get bad input for the search function
#     # TODO investigate moving to a different way to parsing queries that won't through errors
#     # e.g. websearch_to_tsquery
#     # https://www.postgresql.org/docs/current/textsearch-controls.html
#     try:
#         query, pagination = apply_pagination(query, page_number=page, page_size=items_per_page)
#     except ProgrammingError as e:
#         log.debug(e)
#         return {
#             "items": [],
#             "itemsPerPage": items_per_page,
#             "page": page,
#             "total": 0,
#         }
#
#     return {
#         "items": query.all(),
#         "itemsPerPage": pagination.page_size,
#         "page": pagination.page_number,
#         "total": pagination.total_results,
#     }
# import logging
# from collections import namedtuple
# from collections.abc import Iterable
# from itertools import chain
# from typing import List, Annotated, Union
#
# from fastapi import Query, Depends
# from pycparser.ply.yacc import string_types
# from pydantic import constr, Json
# from sqlalchemy import func, or_, desc, and_, not_, orm
#
# from src.api.database.database import DbSession, get_class_by_tablename, Base
#
# log = logging.getLogger(__file__)
#
# # allows only printable characters
# QueryStr = constr(pattern=r"^[ -~]+$", min_length=1)
# BooleanFunction = namedtuple("BooleanFunction", ("key", "sqlalchemy_fn", "only_one_arg"))
# BOOLEAN_FUNCTIONS = [
#     BooleanFunction("or", or_, False),
#     BooleanFunction("and", and_, False),
#     BooleanFunction("not", not_, True),
# ]
#
#
# # def common_parameters(
# #         db_session: DbSession,
# #         page: int = Query(1, gt=0, lt=2147483647),
# #         items_per_page: int = Query(5, alias="itemsPerPage", gt=-2, lt=2147483647),
# #         query_str: QueryStr = Query(None, alias="q"),
# #         filter_spec: Json = Query([], alias="filter"),
# #         sort_by: List[str] = Query([], alias="sortBy[]"),
# #         descending: List[bool] = Query([], alias="descending[]")
# # ):
# #     return {
# #         "db_session": db_session,
# #         "page": page,
# #         "items_per_page": items_per_page,
# #         "query_str": query_str,
# #         "filter_spec": filter_spec,
# #         "sort_by": sort_by,
# #         "descending": descending,
# #     }
#
#
# # CommonParameters = Annotated[
# #     dict[str, Union[int, DbSession, QueryStr, Json, List[str], List[bool]]],
# #     Depends(common_parameters),
# # ]
#
#
# def _is_iterable_filter(filter_spec):
#     """`filter_spec` may be a list of nested filter specs, or a dict."""
#     return isinstance(filter_spec, Iterable) and not isinstance(filter_spec, (string_types, dict))
#
#
# def build_filters(filter_spec):
#     """Recursively process `filter_spec`"""
#     if _is_iterable_filter(filter_spec):
#         return list(chain.from_iterable(build_filters(item) for item in filter_spec))
#
#     if isinstance(filter_spec, dict):
#         # Check if filter spec defines a boolean function.
#         for boolean_function in BOOLEAN_FUNCTIONS:
#             if boolean_function.key in filter_spec:
#                 # The filter spec is for a boolean-function
#                 # Get the function argument definitions and validate
#                 fn_args = filter_spec[boolean_function.key]
#
#                 if not _is_iterable_filter(fn_args):
#                     raise BadFilterFormat(
#                         "`{}` value must be an iterable across the function "
#                         "arguments".format(boolean_function.key)
#                     )
#                 if boolean_function.only_one_arg and len(fn_args) != 1:
#                     raise BadFilterFormat(
#                         "`{}` must have one argument".format(boolean_function.key)
#                     )
#                 if not boolean_function.only_one_arg and len(fn_args) < 1:
#                     raise BadFilterFormat(
#                         "`{}` must have one or more arguments".format(boolean_function.key)
#                     )
#                 return [BooleanFilter(boolean_function.sqlalchemy_fn, *build_filters(fn_args))]
#
#     return [Filter(filter_spec)]
#
#
# def search(*, query_str: str, query: Query, model: str, sort=False):
#     """Perform a search based on the query."""
#     search_model = get_class_by_tablename(model)
#
#     if not query_str.strip():
#         return query
#
#     search = []
#     if hasattr(search_model, "search_vector"):
#         vector = search_model.search_vector
#         search.append(vector.op("@@")(func.tsq_parse(query_str)))
#
#     if hasattr(search_model, "name"):
#         search.append(
#             search_model.name.ilike(f"%{query_str}%"),
#         )
#         search.append(search_model.name == query_str)
#
#     if not search:
#         raise Exception(f"Search not supported for model: {model}")
#
#     query = query.filter(or_(*search))
#
#     if sort:
#         query = query.order_by(desc(func.ts_rank_cd(vector, func.tsq_parse(query_str))))
#
#     return query.params(term=query_str)
#
#
#
# def apply_filters(query, filter_spec, model_cls=None, do_auto_join=True):
#     """Apply filters to a SQLAlchemy query.
#
#     :param query:
#         A :class:`sqlalchemy.orm.Query` instance.
#
#     :param filter_spec:
#         A dict or an iterable of dicts, where each one includes
#         the necessary information to create a filter to be applied to the
#         query.
#
#         Example::
#
#             filter_spec = [
#                 {'model': 'Foo', 'field': 'name', 'op': '==', 'value': 'foo'},
#             ]
#
#         If the query being modified refers to a single model, the `model` key
#         may be omitted from the filter spec.
#
#         Filters may be combined using boolean functions.
#
#         Example:
#
#             filter_spec = {
#                 'or': [
#                     {'model': 'Foo', 'field': 'id', 'op': '==', 'value': '1'},
#                     {'model': 'Bar', 'field': 'id', 'op': '==', 'value': '2'},
#                 ]
#             }
#
#     :returns:
#         The :class:`sqlalchemy.orm.Query` instance after all the filters
#         have been applied.
#     """
#     default_model = get_default_model(query)
#     if not default_model:
#         default_model = model_cls
#
#     filters = build_filters(filter_spec)
#     filter_models = get_named_models(filters)
#
#     if do_auto_join:
#         query = auto_join(query, filter_models)
#
#     sqlalchemy_filters = [filter.format_for_sqlalchemy(query, default_model) for filter in filters]
#
#     if sqlalchemy_filters:
#         query = query.filter(*sqlalchemy_filters)
#
#     return query
#
#
# def apply_filter_specific_joins(model: Base, filter_spec: dict, query: orm.query):
#     """Applies any model specific implicitly joins."""
#     # this is required because by default sqlalchemy-filter's auto-join
#     # knows nothing about how to join many-many relationships.
#     filters = build_filters(filter_spec)
#
#     # Replace mapping if looking for commander
#     if "Commander" in str(filter_spec):
#         model_map.update({(Incident, "IndividualContact"): (Incident.commander, True)})
#     if "Assignee" in str(filter_spec):
#         model_map.update({(Case, "IndividualContact"): (Case.assignee, True)})
#
#     filter_models = get_named_models(filters)
#     joined_models = []
#     for filter_model in filter_models:
#         if model_map.get((model, filter_model)):
#             joined_model, is_outer = model_map[(model, filter_model)]
#             try:
#                 if joined_model not in joined_models:
#                     query = query.join(joined_model, isouter=is_outer)
#                     joined_models.append(joined_model)
#             except Exception as e:
#                 log.exception(e)
#
#     return query
#
#
# def search_filter_sort_paginate(
#         db_session,
#         model,
#         query_str: str = None,
#         filter_spec: List[dict] = None,
#         page: int = 1,
#         items_per_page: int = 5,
#         sort_by: List[str] = None,
#         descending: List[bool] = None
# ):
#     """Common functionality for searching, filtering, sorting, and pagination."""
#     model_cls = get_class_by_tablename(model)
#
#     try:
#         query = db_session.query(model_cls)
#
#         if query_str:
#             sort = False if sort_by else True
#             query = search(query_str=query_str, query=query, model=model, sort=sort)
#
#         query_restricted = apply_model_specific_filters(model_cls, query)
#
#         tag_all_filters = []
#         if filter_spec:
#             query = apply_filter_specific_joins(model_cls, filter_spec, query)
#             # if the filter_spec has the TagAll filter, we need to split the query up
#             # and intersect all of the results
#             if has_tag_all(filter_spec):
#                 new_filter_spec, tag_all_spec = rebuild_filter_spec_without_tag_all(filter_spec)
#                 if new_filter_spec:
#                     query = apply_filters(query, new_filter_spec, model_cls)
#                 for tag_filter in tag_all_spec:
#                     tag_all_filters.append(apply_filters(query, tag_filter, model_cls))
#             else:
#                 query = apply_filters(query, filter_spec, model_cls)
#
#         if model == "Incident":
#             query = query.intersect(query_restricted)
#             for filter in tag_all_filters:
#                 query = query.intersect(filter)
#
#         if model == "Case":
#             query = query.intersect(query_restricted)
#             for filter in tag_all_filters:
#                 query = query.intersect(filter)
#
#         if sort_by:
#             sort_spec = create_sort_spec(model, sort_by, descending)
#             query = apply_sort(query, sort_spec)
#
#     except FieldNotFound as e:
#         raise ValidationError(
#             [
#                 ErrorWrapper(FieldNotFoundError(msg=str(e)), loc="filter"),
#             ],
#             model=BaseModel,
#         ) from None
#     except BadFilterFormat as e:
#         raise ValidationError(
#             [ErrorWrapper(InvalidFilterError(msg=str(e)), loc="filter")], model=BaseModel
#         ) from None
#
#     if items_per_page == -1:
#         items_per_page = None
#
#     # sometimes we get bad input for the search function
#     # TODO investigate moving to a different way to parsing queries that won't through errors
#     # e.g. websearch_to_tsquery
#     # https://www.postgresql.org/docs/current/textsearch-controls.html
#     try:
#         query, pagination = apply_pagination(query, page_number=page, page_size=items_per_page)
#     except ProgrammingError as e:
#         log.debug(e)
#         return {
#             "items": [],
#             "itemsPerPage": items_per_page,
#             "page": page,
#             "total": 0,
#         }
#
#     return {
#         "items": query.all(),
#         "itemsPerPage": pagination.page_size,
#         "page": pagination.page_number,
#         "total": pagination.total_results,
#     }
