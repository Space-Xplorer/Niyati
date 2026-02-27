"""
Database Connection Utilities

Provides connection management for PostgreSQL and Neo4j databases.

Requirements: Database connectivity
"""

import os
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


class PostgreSQLConnection:
    """PostgreSQL connection manager using psycopg2."""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to PostgreSQL."""
        try:
            # Try DATABASE_URL first
            database_url = os.getenv('DATABASE_URL')
            if database_url:
                self.conn = psycopg2.connect(database_url)
            else:
                # Fall back to individual parameters
                self.conn = psycopg2.connect(
                    user=os.getenv('PG_USER', 'postgres'),
                    password=os.getenv('PG_PASSWORD'),
                    host=os.getenv('PG_HOST', 'localhost'),
                    port=os.getenv('PG_PORT', '5432'),
                    database=os.getenv('DB_NAME', 'postgres')
                )
            
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            return self
        except Exception as e:
            raise Exception(f"Failed to connect to PostgreSQL: {str(e)}")
    
    def execute(self, query: str, params: Optional[tuple] = None):
        """Execute a query."""
        if not self.cursor:
            raise Exception("Not connected to database")
        
        self.cursor.execute(query, params)
        return self.cursor
    
    def fetchall(self):
        """Fetch all results from last query."""
        if not self.cursor:
            raise Exception("Not connected to database")
        return self.cursor.fetchall()
    
    def fetchone(self):
        """Fetch one result from last query."""
        if not self.cursor:
            raise Exception("Not connected to database")
        return self.cursor.fetchone()
    
    def commit(self):
        """Commit transaction."""
        if self.conn:
            self.conn.commit()
    
    def rollback(self):
        """Rollback transaction."""
        if self.conn:
            self.conn.rollback()
    
    def close(self):
        """Close connection."""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()


class Neo4jConnection:
    """Neo4j connection manager using official driver."""
    
    def __init__(self):
        self.driver = None
        self.uri = os.getenv('NEO4J_URI')
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD')
        
        if not self.uri or not self.password:
            raise Exception("Neo4j credentials not configured in .env file")
    
    def connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            return self
        except Exception as e:
            raise Exception(f"Failed to connect to Neo4j: {str(e)}")
    
    def close(self):
        """Close connection."""
        if self.driver:
            self.driver.close()
    
    def execute_query(self, query: str, parameters: Optional[dict] = None):
        """Execute a Cypher query and return results."""
        if not self.driver:
            raise Exception("Not connected to Neo4j")
        
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(self, query: str, parameters: Optional[dict] = None):
        """Execute a write transaction."""
        if not self.driver:
            raise Exception("Not connected to Neo4j")
        
        with self.driver.session() as session:
            return session.write_transaction(
                lambda tx: tx.run(query, parameters or {}).data()
            )
    
    def __enter__(self):
        """Context manager entry."""
        return self.connect()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def get_postgres_connection() -> PostgreSQLConnection:
    """Get a PostgreSQL connection instance."""
    return PostgreSQLConnection()


def get_neo4j_connection() -> Neo4jConnection:
    """Get a Neo4j connection instance."""
    return Neo4jConnection()
