"""
Get sample GSTINs from Neo4j
"""
from utils.db_connection import get_neo4j_connection

conn = get_neo4j_connection()
conn.connect()

result = conn.execute_query('MATCH (t:Taxpayer) RETURN t.gstin as gstin LIMIT 10', {})

print('Sample GSTINs in Neo4j:')
for r in result:
    print(f'  - {r["gstin"]}')

conn.close()
