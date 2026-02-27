"""
Check what properties actually exist in Neo4j
"""
from dotenv import load_dotenv
from utils.db_connection import get_neo4j_connection

load_dotenv()

def check_schema():
    print("Checking Neo4j schema...")
    
    try:
        neo4j_conn = get_neo4j_connection()
        neo4j_conn.connect()
        
        # Get sample Taxpayer node with all properties
        query = """
        MATCH (t:Taxpayer)
        RETURN t
        LIMIT 1
        """
        result = neo4j_conn.execute_query(query, {})
        
        if result:
            taxpayer = result[0].get('t')
            print(f"\n✓ Sample Taxpayer node properties:")
            for key, value in taxpayer.items():
                print(f"  - {key}: {value}")
        
        # Get all unique property keys for Taxpayer nodes
        query2 = """
        MATCH (t:Taxpayer)
        UNWIND keys(t) as key
        RETURN DISTINCT key
        ORDER BY key
        """
        result2 = neo4j_conn.execute_query(query2, {})
        
        print(f"\n✓ All property keys on Taxpayer nodes:")
        for record in result2:
            print(f"  - {record.get('key')}")
        
        # Check other node types
        query3 = """
        CALL db.labels()
        """
        result3 = neo4j_conn.execute_query(query3, {})
        
        print(f"\n✓ All node labels in database:")
        for record in result3:
            print(f"  - {record.get('label')}")
        
        neo4j_conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_schema()
