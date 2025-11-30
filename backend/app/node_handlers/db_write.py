"""Database write node handler"""
import logging
from typing import Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.node_handlers.base import NodeHandler
from app.core.dependencies import get_db
from app.exceptions import HandlerExecutionError

logger = logging.getLogger(__name__)


class DBWriteHandler(NodeHandler):
    """Handler for database write operations"""
    
    ALLOWED_OPERATIONS = ["INSERT", "UPDATE", "DELETE", "SELECT"]
    
    async def execute(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute database write operation.
        
        Expected config:
            - operation: SQL operation (INSERT, UPDATE, DELETE, SELECT)
            - table: Table name (required)
            - values: Dict of column:value pairs for INSERT/UPDATE (supports templating)
            - where: Dict of column:value pairs for WHERE clause (optional, supports templating)
            - returning: Columns to return (optional, for INSERT/UPDATE)
            - raw_sql: Raw SQL query (alternative to table/values approach)
        
        Args:
            config: Node configuration
            inputs: Input data from workflow
        
        Returns:
            Dict with operation result
        """
        try:
            # Check if using raw SQL or structured approach
            if "raw_sql" in config:
                return await self._execute_raw_sql(config, inputs)
            else:
                return await self._execute_structured(config, inputs)
            
        except HandlerExecutionError:
            raise
        except Exception as e:
            logger.error(f"Database operation failed: {str(e)}")
            raise HandlerExecutionError(
                "DBWriteHandler",
                f"Database operation failed: {str(e)}",
                original_error=e
            )
    
    async def _execute_structured(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute structured database operation (INSERT/UPDATE/DELETE/SELECT)"""
        # Validate required config
        if "operation" not in config:
            raise HandlerExecutionError(
                "DBWriteHandler",
                "Missing required config field: 'operation'"
            )
        
        if "table" not in config:
            raise HandlerExecutionError(
                "DBWriteHandler",
                "Missing required config field: 'table'"
            )
        
        operation = config["operation"].upper()
        if operation not in self.ALLOWED_OPERATIONS:
            raise HandlerExecutionError(
                "DBWriteHandler",
                f"Invalid operation: {operation}. Allowed: {self.ALLOWED_OPERATIONS}"
            )
        
        table = config["table"]
        
        # Prepare template context
        template_context = self._prepare_template_context(inputs)
        
        # Render templated values
        values = self._render_dict_template(config.get("values", {}), template_context)
        where = self._render_dict_template(config.get("where", {}), template_context)
        
        logger.info(f"Executing {operation} on table '{table}'")
        
        # Build and execute query based on operation
        if operation == "INSERT":
            return await self._execute_insert(table, values, config.get("returning"))
        elif operation == "UPDATE":
            return await self._execute_update(table, values, where, config.get("returning"))
        elif operation == "DELETE":
            return await self._execute_delete(table, where)
        elif operation == "SELECT":
            return await self._execute_select(table, where, config.get("columns"))
        else:
            raise HandlerExecutionError(
                "DBWriteHandler",
                f"Operation {operation} not implemented"
            )
    
    async def _execute_insert(
        self,
        table: str,
        values: Dict[str, Any],
        returning: Optional[list] = None
    ) -> Dict[str, Any]:
        """Execute INSERT operation"""
        if not values:
            raise HandlerExecutionError(
                "DBWriteHandler",
                "INSERT requires 'values' in config"
            )
        
        # Build INSERT query
        columns = ", ".join(values.keys())
        placeholders = ", ".join([f":{key}" for key in values.keys()])
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        if returning:
            query += f" RETURNING {', '.join(returning)}"
        
        logger.debug(f"INSERT query: {query}")
        logger.debug(f"Values: {values}")
        
        # Execute using a new database session
        from app.db.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                result = await db.execute(text(query), values)
                await db.commit()
                
                # Get returned values if specified
                returned_data = None
                if returning:
                    row = result.fetchone()
                    if row:
                        returned_data = dict(row._mapping)
                
                rows_affected = result.rowcount
                
                logger.info(f"INSERT successful. Rows affected: {rows_affected}")
                
                return {
                    "operation": "INSERT",
                    "table": table,
                    "rows_affected": rows_affected,
                    "returned": returned_data,
                    "status": "success"
                }
                
            except Exception as e:
                await db.rollback()
                logger.error(f"INSERT failed: {str(e)}")
                raise
    
    async def _execute_update(
        self,
        table: str,
        values: Dict[str, Any],
        where: Dict[str, Any],
        returning: Optional[list] = None
    ) -> Dict[str, Any]:
        """Execute UPDATE operation"""
        if not values:
            raise HandlerExecutionError(
                "DBWriteHandler",
                "UPDATE requires 'values' in config"
            )
        
        # Build UPDATE query
        set_clause = ", ".join([f"{key} = :{key}" for key in values.keys()])
        query = f"UPDATE {table} SET {set_clause}"
        
        # Add WHERE clause
        params = values.copy()
        if where:
            where_clause = " AND ".join([f"{key} = :where_{key}" for key in where.keys()])
            query += f" WHERE {where_clause}"
            # Prefix where params to avoid collision
            for key, value in where.items():
                params[f"where_{key}"] = value
        
        if returning:
            query += f" RETURNING {', '.join(returning)}"
        
        logger.debug(f"UPDATE query: {query}")
        logger.debug(f"Params: {params}")
        
        from app.db.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                result = await db.execute(text(query), params)
                await db.commit()
                
                # Get returned values if specified
                returned_data = None
                if returning:
                    rows = result.fetchall()
                    if rows:
                        returned_data = [dict(row._mapping) for row in rows]
                
                rows_affected = result.rowcount
                
                logger.info(f"UPDATE successful. Rows affected: {rows_affected}")
                
                return {
                    "operation": "UPDATE",
                    "table": table,
                    "rows_affected": rows_affected,
                    "returned": returned_data,
                    "status": "success"
                }
                
            except Exception as e:
                await db.rollback()
                logger.error(f"UPDATE failed: {str(e)}")
                raise
    
    async def _execute_delete(self, table: str, where: Dict[str, Any]) -> Dict[str, Any]:
        """Execute DELETE operation"""
        # Build DELETE query
        query = f"DELETE FROM {table}"
        
        params = {}
        if where:
            where_clause = " AND ".join([f"{key} = :{key}" for key in where.keys()])
            query += f" WHERE {where_clause}"
            params = where
        else:
            logger.warning("DELETE without WHERE clause - will delete all rows!")
        
        logger.debug(f"DELETE query: {query}")
        logger.debug(f"Params: {params}")
        
        from app.db.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                result = await db.execute(text(query), params)
                await db.commit()
                
                rows_affected = result.rowcount
                
                logger.info(f"DELETE successful. Rows affected: {rows_affected}")
                
                return {
                    "operation": "DELETE",
                    "table": table,
                    "rows_affected": rows_affected,
                    "status": "success"
                }
                
            except Exception as e:
                await db.rollback()
                logger.error(f"DELETE failed: {str(e)}")
                raise
    
    async def _execute_select(
        self,
        table: str,
        where: Optional[Dict[str, Any]],
        columns: Optional[list] = None
    ) -> Dict[str, Any]:
        """Execute SELECT operation"""
        # Build SELECT query
        select_columns = ", ".join(columns) if columns else "*"
        query = f"SELECT {select_columns} FROM {table}"
        
        params = {}
        if where:
            where_clause = " AND ".join([f"{key} = :{key}" for key in where.keys()])
            query += f" WHERE {where_clause}"
            params = where
        
        logger.debug(f"SELECT query: {query}")
        logger.debug(f"Params: {params}")
        
        from app.db.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                result = await db.execute(text(query), params)
                rows = result.fetchall()
                
                # Convert rows to dicts
                data = [dict(row._mapping) for row in rows]
                
                logger.info(f"SELECT successful. Rows returned: {len(data)}")
                
                return {
                    "operation": "SELECT",
                    "table": table,
                    "rows_returned": len(data),
                    "data": data,
                    "status": "success"
                }
                
            except Exception as e:
                logger.error(f"SELECT failed: {str(e)}")
                raise
    
    async def _execute_raw_sql(self, config: Dict[str, Any], inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute raw SQL query"""
        raw_sql = config.get("raw_sql")
        if not raw_sql:
            raise HandlerExecutionError(
                "DBWriteHandler",
                "Missing 'raw_sql' in config"
            )
        
        # Prepare template context
        template_context = self._prepare_template_context(inputs)
        
        # Render SQL template
        query = self._render_template(raw_sql, template_context)
        
        # Get params if any
        params = config.get("params", {})
        params = self._render_dict_template(params, template_context)
        
        logger.info("Executing raw SQL query")
        logger.debug(f"Query: {query}")
        
        from app.db.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            try:
                result = await db.execute(text(query), params)
                await db.commit()
                
                # Try to fetch results
                try:
                    rows = result.fetchall()
                    data = [dict(row._mapping) for row in rows]
                    
                    return {
                        "operation": "RAW_SQL",
                        "rows_returned": len(data),
                        "data": data,
                        "status": "success"
                    }
                except Exception:
                    # No results to fetch (INSERT/UPDATE/DELETE)
                    return {
                        "operation": "RAW_SQL",
                        "rows_affected": result.rowcount,
                        "status": "success"
                    }
                
            except Exception as e:
                await db.rollback()
                logger.error(f"Raw SQL execution failed: {str(e)}")
                raise
    
    def _prepare_template_context(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for template rendering"""
        context = {}
        
        # Add workflow input
        workflow_input = inputs.get("workflow_input", {})
        if isinstance(workflow_input, dict):
            context.update(workflow_input)
        
        # Add previous outputs
        previous_outputs = inputs.get("previous_outputs", {})
        if isinstance(previous_outputs, dict):
            context["outputs"] = previous_outputs
            # Flatten for easier access
            for node_id, output in previous_outputs.items():
                if isinstance(output, dict):
                    for key, value in output.items():
                        context[f"{node_id}_{key}"] = value
        
        return context
    
    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """Render a string template"""
        if not isinstance(template, str):
            return str(template)
        
        try:
            return template.format(**context)
        except KeyError as e:
            logger.warning(f"Template variable not found: {e}. Using original.")
            return template
    
    def _render_dict_template(self, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Render templates in dictionary values"""
        if not isinstance(data, dict):
            return {}
        
        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self._render_template(value, context)
            else:
                result[key] = value
        
        return result
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate node configuration"""
        # Check if using raw SQL or structured
        if "raw_sql" in config:
            if not isinstance(config["raw_sql"], str):
                raise ValueError("raw_sql must be a string")
            return True
        
        # Structured approach validation
        if "operation" not in config:
            raise ValueError("Missing required field: operation (or use raw_sql)")
        
        if "table" not in config:
            raise ValueError("Missing required field: table")
        
        operation = config["operation"].upper()
        if operation not in self.ALLOWED_OPERATIONS:
            raise ValueError(f"Invalid operation: {operation}. Allowed: {self.ALLOWED_OPERATIONS}")
        
        if operation in ["INSERT", "UPDATE"] and "values" not in config:
            raise ValueError(f"{operation} requires 'values' field")
        
        return True
