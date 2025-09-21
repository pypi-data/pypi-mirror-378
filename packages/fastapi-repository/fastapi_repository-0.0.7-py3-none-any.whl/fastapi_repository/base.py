from typing import Optional, List, Union, Dict, Any, Sequence
from uuid import UUID
from sqlalchemy import func, update, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, lazyload


OPERATORS = {
    # Exact match
    "exact": lambda col, val: col == val,
    "iexact": lambda col, val: col.ilike(val),
    # Partial match
    "contains": lambda col, val: col.contains(val),
    "icontains": lambda col, val: col.ilike(f"%{val}%"),
    # IN clause
    "in": lambda col, val: col.in_(val) if isinstance(val, list) else col.in_([val]),
    # Comparison operators
    "gt": lambda col, val: col > val,
    "gte": lambda col, val: col >= val,
    "lt": lambda col, val: col < val,
    "lte": lambda col, val: col <= val,
    # Starts/ends with
    "startswith": lambda col, val: col.startswith(val),
    "istartswith": lambda col, val: col.ilike(f"{val}%"),
    "endswith": lambda col, val: col.endswith(val),
    "iendswith": lambda col, val: col.ilike(f"%{val}"),
}


class BaseRepository:
    default_scope: dict = {}

    def __init__(self, session: AsyncSession, model=None):
        self.session = session
        if not model:
            raise ValueError("Model is not set for this repository.")
        self.model = model

    async def find(
        self,
        id: Union[int, UUID],
        sorted_by: Optional[str] = None,
        sorted_order: str = "asc",
        joinedload_models: Optional[List] = None,
        lazyload_models: Optional[List] = None,
        disable_default_scope: bool = False,
    ):
        """
        Find a record by its ID. Raise an exception if not found.
        """
        query = await self.__generate_query(
            limit=1,
            offset=0,
            sorted_by=sorted_by,
            sorted_order=sorted_order,
            joinedload_models=joinedload_models,
            lazyload_models=lazyload_models,
            disable_default_scope=disable_default_scope,
            id=id,
        )

        result = await self.session.execute(query)
        instance = result.scalars().first()

        if not instance:
            raise NoResultFound(f"{self.model.__name__} with id {id} not found.")

        return instance

    async def find_by(
        self,
        sorted_by: Optional[str] = None,
        sorted_order: str = "asc",
        joinedload_models: Optional[List] = None,
        lazyload_models: Optional[List] = None,
        disable_default_scope: bool = False,
        **search_params,
    ):
        """
        Find a record by given attributes. Return None if not found.
        """
        query = await self.__generate_query(
            limit=1,
            offset=0,
            sorted_by=sorted_by,
            sorted_order=sorted_order,
            joinedload_models=joinedload_models,
            lazyload_models=lazyload_models,
            disable_default_scope=disable_default_scope,
            **search_params,
        )
        result = await self.session.execute(query)
        instance = result.scalars().first()
        return instance

    async def find_by_or_raise(
        self,
        sorted_by: Optional[str] = None,
        sorted_order: str = "asc",
        joinedload_models: Optional[List] = None,
        lazyload_models: Optional[List] = None,
        disable_default_scope: bool = False,
        **search_params,
    ):
        """
        Find a record by given attributes. Raise an exception if not found.
        """
        instance = await self.find_by(
            sorted_by=sorted_by,
            sorted_order=sorted_order,
            joinedload_models=joinedload_models,
            lazyload_models=lazyload_models,
            disable_default_scope=disable_default_scope,
            **search_params,
        )
        if not instance:
            raise NoResultFound(
                f"{self.model.__name__} with attributes {search_params} not found."
            )
        return instance

    async def where(
        self,
        limit: int = 100,
        offset: int = 0,
        sorted_by: Optional[str] = None,
        sorted_order: str = "asc",
        joinedload_models: Optional[List] = None,
        lazyload_models: Optional[List] = None,
        disable_default_scope: bool = False,
        **search_params,
    ):
        """
        Find records with optional filtering, sorting, and pagination.
        """
        query = await self.__generate_query(
            limit=limit,
            offset=offset,
            sorted_by=sorted_by,
            sorted_order=sorted_order,
            joinedload_models=joinedload_models,
            lazyload_models=lazyload_models,
            disable_default_scope=disable_default_scope,
            **search_params,
        )
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def count(self, disable_default_scope: bool = False, **search_params) -> int:
        """
        Count records with optional filtering.
        """
        conditions = []
        if not disable_default_scope:
            default_conditions = await self.__get_conditions(**self.default_scope)
            if default_conditions:
                conditions.extend(default_conditions)

        conditions += await self.__get_conditions(**search_params)
        query = select(func.count("*")).select_from(self.model).where(*conditions)
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def exists(
        self, disable_default_scope: bool = False, **search_params
    ) -> bool:
        """
        Check if any record exists with the given attributes.
        """
        counted = await self.count(
            disable_default_scope=disable_default_scope, **search_params
        )
        return counted > 0

    async def __generate_query(
        self,
        limit: int = 100,
        offset: int = 0,
        sorted_by: Optional[str] = None,
        sorted_order: str = "asc",
        joinedload_models: Optional[List] = None,
        lazyload_models: Optional[List] = None,
        disable_default_scope: bool = False,
        **search_params,
    ):
        # Combine default_scope and search conditions into a single predicate
        base_pred = None
        if not disable_default_scope and self.default_scope:
            base_pred = await self.__build_condition_tree(self.default_scope)

        search_pred = await self.__build_condition_tree(search_params)

        final_pred = None
        if base_pred is not None and search_pred is not None:
            final_pred = and_(base_pred, search_pred)
        else:
            final_pred = base_pred or search_pred

        query = select(self.model)
        if final_pred is not None:
            query = query.where(final_pred)

        # Keep the existing joinedload / lazyload / order_by logic as is
        if joinedload_models:
            for spec in joinedload_models:
                query = query.options(self._build_loader_option(spec, loader="joined"))
        if lazyload_models:
            for spec in lazyload_models:
                query = query.options(self._build_loader_option(spec, loader="lazy"))
        if sorted_by:
            query = self._apply_order_by(query, sorted_by, sorted_order)

        return query.limit(limit).offset(offset)

    def _apply_order_by(self, query, sorted_by: str, sorted_order: str):
        """
        Apply ORDER BY.
        - Direct model column: "email"
        - Relationship path: Specify like "profile__company__name"
        When a path is specified, necessary OUTER JOINs are automatically added before sorting.
        """
        # No path specified: default behavior (direct model column)
        if "__" not in sorted_by:
            column = getattr(self.model, sorted_by, None)
            if column is None:
                raise AttributeError(f"{self.model.__name__} has no attribute '{sorted_by}'")
            return query.order_by(column.asc() if sorted_order.lower() == "asc" else column.desc())

        # Path specified: rel__rel2__column
        parts = [p for p in sorted_by.split("__") if p]
        if len(parts) < 2:
            raise AttributeError(
                "sorted_by requires at least 'relationship__column' when using a path"
            )

        *rel_parts, col_name = parts
        attrs = self._resolve_attr_chain(self.model, rel_parts)  # Chain of relationship attributes
        target_cls = attrs[-1].property.mapper.class_
        column = getattr(target_cls, col_name, None)
        if column is None:
            raise AttributeError(f"{target_cls.__name__} has no attribute '{col_name}'")

        # Lightly check that column is not a relationship (should be a column)
        prop = getattr(column, "property", None)
        if prop is not None and hasattr(prop, "mapper"):
            raise AttributeError(
                f"'{col_name}' on {target_cls.__name__} is a relationship, not a column"
            )

        # Add OUTER JOINs for each relationship in the path (to avoid dropping missing records in one-to-many, etc.)
        for a in attrs:
            query = query.outerjoin(a)

        # ORDER BY
        order_expr = column.asc() if sorted_order.lower() == "asc" else column.desc()
        return query.order_by(order_expr)
    def _wrap_relationship_predicate(self, attrs, predicate):
        """
        attrs: InstrumentedAttribute のリスト（親→子の順）
        最下流の述語 predicate に対して、関係の種類に応じて any()/has() を多段で包む
        """
        for a in reversed(attrs):
            uselist = getattr(a.property, "uselist", False)
            predicate = a.any(predicate) if uselist else a.has(predicate)
        return predicate

    # Added: Convert a single key (e.g., "a__b__name__icontains") into a SQLAlchemy condition
    def _parse_key_to_condition(self, key: str, value):
        # If the key is a compound path (separated by "__"), pop the last token if it's an operator
        if "__" in key:
            parts = key.split("__")
            op = "exact"
            if parts[-1] in OPERATORS:
                op = parts.pop()

            # example: foo__icontains=bar
            if len(parts) == 1:
                column = getattr(self.model, parts[0], None)
                if column is None:
                    raise AttributeError(f"{self.model.__name__} has no attribute '{parts[0]}'")
                return OPERATORS[op](column, value)

            # example: rel1__rel2__...__field__op
            *rel_parts, field_name = parts
            attrs = self._resolve_attr_chain(self.model, rel_parts)  # [rel1_attr, rel2_attr, ...]
            target_cls = attrs[-1].property.mapper.class_
            target_col = getattr(target_cls, field_name, None)
            if target_col is None:
                raise AttributeError(f"{target_cls.__name__} has no attribute '{field_name}'")
            pred = OPERATORS[op](target_col, value)
            return self._wrap_relationship_predicate(attrs, pred)
        else:
            column = getattr(self.model, key, None)
            if column is None:
                raise AttributeError(f"{self.model.__name__} has no attribute '{key}'")
            return column == value

    # Added: Recursively build a condition tree (supports _or/_and)
    async def __build_condition_tree(self, params) -> Any:
        """
        params: dict | list
          - dict: Supports standard {key: value} plus _or / _and keys
          - list: Combine each element with AND (if nested under _or, it will be wrapped with or_([...]))
        Returns: SQLAlchemy predicate (BinaryExpression) or None
        """
        if params is None:
            return None

        # Combine lists with AND (assuming the caller will pass them to or_)
        if isinstance(params, list):
            parts = [await self.__build_condition_tree(p) if isinstance(p, (dict, list))
                     else None for p in params]
            parts = [p for p in parts if p is not None]
            if not parts:
                return None
            return and_(*parts)

        if not isinstance(params, dict):
            raise TypeError("search params must be dict or list")

        or_keys = {"_or", "or_", "$or"}
        and_keys = {"_and", "and_", "$and"}

        children_and = []
        children_or_groups = []

        for k, v in params.items():
            if k in or_keys:
                if not isinstance(v, list):
                    raise TypeError(f"{k} must be a list of dicts")
                group = [await self.__build_condition_tree(item) for item in v]
                group = [g for g in group if g is not None]
                if group:
                    children_or_groups.append(or_(*group))
                continue

            if k in and_keys:
                if not isinstance(v, list):
                    raise TypeError(f"{k} must be a list of dicts")
                group = [await self.__build_condition_tree(item) for item in v]
                group = [g for g in group if g is not None]
                if group:
                    children_and.append(and_(*group))
                continue

            # Standard key=value condition
            children_and.append(self._parse_key_to_condition(k, v))

        # Combine AND conditions
        predicate = None
        if children_and:
            predicate = and_(*children_and)
        if children_or_groups:
            predicate = or_(*(children_or_groups + ([predicate] if predicate is not None else [])))

        return predicate

    async def __get_conditions(self, **search_params):
        """
        Kept for backward compatibility, but internally uses __build_condition_tree to return a single predicate.
        Returns a list to match the original callers (where(*conditions)).
        """
        pred = await self.__build_condition_tree(search_params)
        return [pred] if pred is not None else []

    async def create(self, **create_params):
        """
        Generic create method that instantiates the model,
        saves it, and returns the new instance.
        """
        instance = self.model(**create_params)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, id: Union[int, UUID], **update_params):
        """
        Update a single record by its primary key.
        Raises NoResultFound if the record doesn't exist.

        Usage:
            await repository.update(some_id, field1='value1', field2='value2')
        """
        instance = await self.find(id)
        for field, value in update_params.items():
            setattr(instance, field, value)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update_all(self, updates: Dict[str, Any], **search_params) -> int:
        """
        Update all records that match the given conditions in one query.
        Returns the number of rows that were updated.

        Usage:
            await repository.update_all(
                {"field1": "new_value", "field2": 123},
                some_field__gte=10,
                other_field="foo"
            )
        """
        conditions = await self.__get_conditions(**search_params)
        stmt = update(self.model).where(*conditions).values(**updates)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    async def destroy(self, id: Union[int, UUID]) -> None:
        """
        Destroy (delete) a single record by its primary key.
        Raises NoResultFound if the record doesn't exist.
        """
        instance = await self.find(id)  # Will raise NoResultFound if not found
        await self.session.delete(instance)
        await self.session.commit()

    async def destroy_all(self, **search_params) -> int:
        """
        Destroy (delete) all records that match the given conditions in one query.
        Returns the number of rows that were deleted.

        Usage:
            await repository.destroy_all(field1="value1", field2__gte=10)
        """
        conditions = await self.__get_conditions(**search_params)
        stmt = delete(self.model).where(*conditions)
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount

    def _resolve_attr_chain(self, start_cls, names: Sequence[str]):
        """
        Example: names = ["orders", "items", "product"]
        Traverse relationship attributes sequentially from start_cls and return a list of InstrumentedAttributes
        """
        current_cls = start_cls
        attrs = []
        for name in names:
            attr = getattr(current_cls, name, None)
            if attr is None or not hasattr(attr, "property"):
                raise AttributeError(f"{current_cls.__name__} has no relationship '{name}'")
            attrs.append(attr)
            current_cls = attr.property.mapper.class_
        return attrs

    def _build_loader_option(self, item, loader: str = "joined"):
        """
        `item` accepts any of the following:
          - String path: "orders__items__product"
          - Array/tuple of strings: ["orders", "items", "product"]
          - Single InstrumentedAttribute
          - Array/tuple of InstrumentedAttributes (multi-level)
        loader: "joined" | "lazy"
        """
        if loader not in {"joined", "lazy"}:
            raise ValueError("loader must be 'joined' or 'lazy'")

        def first_loader(attr):
            return joinedload(attr) if loader == "joined" else lazyload(attr)

        def chain_loader(opt, attr):
            return opt.joinedload(attr) if loader == "joined" else opt.lazyload(attr)

        # String ("rel__rel2__rel3")
        if isinstance(item, str):
            parts = [p for p in item.split("__") if p]
            if not parts:
                raise ValueError("empty relationship path")
            attrs = self._resolve_attr_chain(self.model, parts)
            opt = first_loader(attrs[0])
            for a in attrs[1:]:
                opt = chain_loader(opt, a)
            return opt

        # Sequence of strings (["rel", "rel2", ...])
        if isinstance(item, (list, tuple)) and all(isinstance(p, str) for p in item):
            attrs = self._resolve_attr_chain(self.model, item)
            opt = first_loader(attrs[0])
            for a in attrs[1:]:
                opt = chain_loader(opt, a)
            return opt

        # Single InstrumentedAttribute
        if hasattr(item, "property"):
            return first_loader(item)

        # Sequence of InstrumentedAttributes
        if isinstance(item, (list, tuple)) and all(hasattr(p, "property") for p in item):
            if not item:
                raise ValueError("empty attribute chain")
            opt = first_loader(item[0])
            for a in item[1:]:
                opt = chain_loader(opt, a)
            return opt

        raise TypeError(
            "joinedload_models/lazyload_models item must be a relationship attribute, "
            "a list/tuple of relationship attributes, a string path 'a__b__c', "
            "or a list/tuple of strings ['a','b','c']."
        )