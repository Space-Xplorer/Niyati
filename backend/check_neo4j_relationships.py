"""
Check what relationships exist in Neo4j
"""
from dotenv import load_dotenv
from utils.db_connection import get_neo4j_connection

load_dotenv()

def check_relationships():
    print("Checking Neo4j relationships...")
    
    try:
        neo4j_conn = get_neo4j_connection()
        neo4j_conn.connect()
        
        # Get relationship types
        query1 = """
        CALL db.relationshipTypes()
        """
        result1 = neo4j_conn.execute_query(query1, {})
        
        print(f"\n✓ Relationship types in database:")
        for record in result1:
            print(f"  - {record.get('relationshipType')}")
        
        # Count relationships
        query2 = """
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
        """
        result2 = neo4j_conn.execute_query(query2, {})
        
        print(f"\n✓ Relationship counts:")
        for record in result2:
            print(f"  - {record.get('rel_type')}: {record.get('count')}")
        
        # Sample relationships
        query3 = """
        MATCH (a)-[r]->(b)
        RETURN labels(a)[0] as source_label, type(r) as rel_type, labels(b)[0] as target_label
        LIMIT 10
        """
        result3 = neo4j_conn.execute_query(query3, {})
        
        print(f"\n✓ Sample relationships:")
        for record in result3:
            print(f"  - ({record.get('source_label')})-[{record.get('rel_type')}]->({record.get('target_label')})")
        
        # Check for potential circular patterns
        query4 = """
        MATCH (t1:Taxpayer)-[r1]->(t2:Taxpayer)-[r2]->(t3:Taxpayer)
        WHERE t1 = t3
        RETURN count(*) as circular_2hop
        LIMIT 1
        """
        result4 = neo4j_conn.execute_query(query4, {})
        
        print(f"\n✓ Circular patterns (2-hop):")
        print(f"  - Count: {result4[0].get('circular_2hop', 0) if result4 else 0}")
        
        # Check for any Taxpayer-to-Taxpayer connections
        query5 = """
        MATCH (t1:Taxpayer)-[r]->(t2:Taxpayer)
        RETURN count(r) as taxpayer_connections
        LIMIT 1
        """
        result5 = neo4j_conn.execute_query(query5, {})
        
        print(f"\n✓ Direct Taxpayer-to-Taxpayer connections:")
        print(f"  - Count: {result5[0].get('taxpayer_connections', 0) if result5 else 0}")
        
        neo4j_conn.close()
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_relationships()
