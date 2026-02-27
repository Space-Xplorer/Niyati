"""
Test Neo4j connection and query
"""
import os
from dotenv import load_dotenv
from utils.db_connection import get_neo4j_connection

load_dotenv()

def test_connection():
    print("Testing Neo4j connection...")
    print(f"URI: {os.getenv('NEO4J_URI')}")
    print(f"User: {os.getenv('NEO4J_USER')}")
    print(f"Password: {'*' * len(os.getenv('NEO4J_PASSWORD', ''))}")
    
    try:
        neo4j_conn = get_neo4j_connection()
        print("✓ Neo4j connection object created")
        
        neo4j_conn.connect()
        print("✓ Connected to Neo4j successfully")
        
        # Test query
        query = """
        MATCH (t:Taxpayer)
        RETURN count(t) as taxpayer_count
        """
        result = neo4j_conn.execute_query(query, {})
        print(f"✓ Query executed successfully")
        print(f"  Total taxpayers in Neo4j: {result[0].get('taxpayer_count', 0)}")
        
        # Test detailed query
        query2 = """
        MATCH (t:Taxpayer)
        RETURN 
            t.gstin as gstin,
            t.business_name as business_name,
            t.risk_level as risk_level,
            t.risk_probability as risk_probability
        LIMIT 5
        """
        result2 = neo4j_conn.execute_query(query2, {})
        print(f"✓ Detailed query executed successfully")
        print(f"  Sample records: {len(result2)}")
        for i, record in enumerate(result2[:3]):
            print(f"    {i+1}. GSTIN: {record.get('gstin')}, Risk: {record.get('risk_level')}")
        
        neo4j_conn.close()
        print("✓ Connection closed")
        print("\n✅ All tests passed! Neo4j is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_connection()
