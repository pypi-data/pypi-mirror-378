from typing import Literal, Optional

from gql import Client, gql
from gql.transport.httpx import HTTPXAsyncTransport
from graphql import GraphQLInputObjectType, GraphQLObjectType

from ..utilities.config import GRAPHQL_ENDPOINTS


class PolymarketGraphQLClient:
    def __init__(self,
                endpoint_name: Literal[
                    "activity_subgraph",
                    "fpmm_subgraph",
                    "open_interest_subgraph",
                    "orderbook_subgraph",
                    "pnl_subgraph",
                    "positions_subgraph",
                    "sports_oracle_subgraph",
                    "wallet_subgraph",
                ]):
        if endpoint_name not in GRAPHQL_ENDPOINTS:
            msg = f"Invalid endpoint name: {endpoint_name}. Must be one of {list(GRAPHQL_ENDPOINTS.keys())}"
            raise ValueError(msg)
        endpoint_url = GRAPHQL_ENDPOINTS[endpoint_name]
        self.transport = HTTPXAsyncTransport(url=endpoint_url)
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)
        self.schema = None
        self.object_types = []
        self.query_fields = []
        self.subscription_fields = []
        self.filter_input_types = []

    async def _init_schema(self):
        async with self.client as session:
            self.schema = session.schema

    async def _get_query_fields(self):
        if self.query_fields:
            return self.query_fields
        if not self.schema:
            await self._init_schema()
        self.query_fields = [field for field in self.schema.type_map["Query"].fields if not field.startswith("_")]

        return self.query_fields

    async def _get_subscription_fields(self):
        if self.subscription_fields:
            return self.subscription_fields
        if not self.schema:
            await self._init_schema()
        if "Subscription" in self.schema.type_map:
            self.subscription_fields = [field for field in self.schema.type_map["Subscription"].fields if not field.startswith("_")]
        else:
            self.subscription_fields = []
        return self.subscription_fields

    async def _get_object_types(self):
        if self.object_types:
            return self.object_types
        if not self.schema:
            await self._init_schema()
        for object_name, object in self.schema.type_map.items():
            if type(object) is GraphQLObjectType and not object_name.startswith("_"):
                self.object_types.append(object_name)
        return self.object_types

    async def _get_filter_input_types(self):
        if self.filter_input_types:
            return self.filter_input_types
        if not self.schema:
            await self._init_schema()
        for object_name, object in self.schema.type_map.items():
            if isinstance(object, GraphQLInputObjectType) and not object_name.startswith("_"):
                self.filter_input_types.append(object_name)
        return self.filter_input_types

    async def list_queries(self):
        if self.query_fields:
            return self.query_fields
        return await self._get_query_fields()

    async def list_subscriptions(self):
        if self.subscription_fields:
            return self.subscription_fields
        return await self._get_subscription_fields()

    async def list_object_types(self):
        if self.object_types:
            return self.object_types
        return await self._get_object_types()

    async def list_filter_input_types(self):
        if self.filter_input_types:
            return self.filter_input_types
        return await self._get_filter_input_types()

    async def get_fields(self, object_name: str):
        if self.schema is None:
            await self._init_schema()
        if object_name not in self.schema.type_map:
            msg = "Invalid object name"
            raise ValueError(msg)
        return list(self.schema.type_map[object_name].fields.keys())

    async def query(
        self,
        endpoint: str,
        fields: list[str],
        filters: Optional[dict] = None,
        relationships: Optional[dict] = None,
    ):
        if not self.schema:
            await self._init_schema()
        if not self.query_fields:
            await self._get_query_fields()
        if not self.object_types:
            await self._get_object_types()

        if endpoint not in self.query_fields:
            msg = f"Invalid endpoint: {endpoint}"
            raise ValueError(msg)

        endpoint_field = self.schema.type_map["Query"].fields[endpoint]
        required_args = [
            arg_name for arg_name, arg in endpoint_field.args.items()
            if arg.type.to_kwargs().get("required", False)
        ]
        missing_args = [arg for arg in required_args if not (filters and arg in filters)]
        if missing_args:
            msg = f"Missing required argument(s) for '{endpoint}': {', '.join(missing_args)}"
            raise ValueError(msg)

        def build_selection(fields, relationships):
            selections = []
            for field in fields:
                if relationships and field in relationships:
                    subfields = relationships[field]
                    selections.append(f"{field} {{ {' '.join(subfields)} }}")
                else:
                    selections.append(field)
            return " ".join(selections)

        def build_args(filters):
            """Build GraphQL arguments, handling both simple and complex where clauses."""
            if not filters:
                return ""

            arg_strs = []
            for k, v in filters.items():
                if k == "where" and isinstance(v, dict):
                    # Handle complex where clause
                    where_conditions = []
                    for where_key, where_value in v.items():
                        if isinstance(where_value, str):
                            where_conditions.append(f"{where_key}: {where_value}")
                        else:
                            where_conditions.append(f"{where_key}: {where_value}")
                    where_str = "{" + ", ".join(where_conditions) + "}"
                    arg_strs.append(f"{k}: {where_str}")
                # Handle simple key-value filters
                elif isinstance(v, str):
                    arg_strs.append(f'{k}: "{v}"')
                else:
                    arg_strs.append(f"{k}: {v}")

            return "(" + ", ".join(arg_strs) + ")"

        selection_set = build_selection(fields, relationships)
        args = build_args(filters)

        query_str = f"""
        query {{
            {endpoint}{args} {{
                {selection_set}
            }}
        }}
        """
        print(query_str)
        async with self.client as session:
            result = await session.execute(gql(query_str))
        return result
