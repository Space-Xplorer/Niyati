"""
Test fraud pattern detection queries
"""
from dotenv import load_dotenv
from utils.db_connection import get_neo4j_connection

load_dotenv()

def test_fraud_patterns():
    print("Testing fraud pattern detection...")
    
    try:
        neo4j_conn = get_neo4j_connection()
        neo4j_conn.connect()
        
        # 1. Circular Trade
        print("\n1. Testing Circular Trade Detection:")
        circular_query = """
        MATCH path = (t1:Taxpayer)-[:ISSUED]->(:Invoice)-[:TO]->(t2:Taxpayer)-[:ISSUED]->(:Invoice)-[:TO]->(t1)
        WHERE t1 <> t2
        RETURN count(DISTINCT t1) as circular_count
        LIMIT 1
        """
        result = neo4j_conn.execute_query(circular_query, {})
        print(f"   Circular trade entities: {result[0].get('circular_count', 0) if result else 0}")
        
        # 2. Ghost Invoices
        print("\n2. Testing Ghost Invoice Detection:")
        ghost_query = """
        MATCH (i:Invoice)
        WHERE NOT (i)-[:BACKED_BY]->(:EwayBill)
        RETURN count(i) as ghost_count
        LIMIT 1
        """
        result = neo4j_conn.execute_query(ghost_query, {})
        print(f"   Ghost invoices: {result[0].get('ghost_count', 0) if result else 0}")
        
        # 3. Spider Web Networks
        print("\n3. Testing Spider Web Detection:")
        spider_query = """
        MATCH (t1:Taxpayer)-[:SHARED_CONTACT]->(t2:Taxpayer)
        WITH t1, count(DISTINCT t2) as shared_count
        WHERE shared_count > 5
        RETURN count(t1) as spider_count
        LIMIT 1
        """
        result = neo4j_conn.execute_query(spider_query, {})
        print(f"   Spider web entities: {result[0].get('spider_count', 0) if result else 0}")
        
        # Additional stats
        print("\n4. Additional Statistics:")
        
        # Total invoices
        query = "MATCH (i:Invoice) RETURN count(i) as total"
        result = neo4j_conn.execute_query(query, {})
        print(f"   Total invoices: {result[0].get('total', 0) if result else 0}")
        
        # Invoices with e-way bills
        query = "MATCH (i:Invoice)-[:BACKED_BY]->(:EwayBill) RETURN count(i) as backed"
        result = neo4j_conn.execute_query(query, {})
        print(f"   Invoices with e-way bills: {result[0].get('backed', 0) if result else 0}")
        
        # Shared contact stats
        query = """
        MATCH (t:Taxpayer)-[:SHARED_CONTACT]->(other:Taxpayer)
        WITH t, count(DISTINCT other) as shared_count
        RETURN 
            min(shared_count) as min_shared,
            max(shared_count) as max_shared,
            avg(shared_count) as avg_shared
        """
        result = neo4j_conn.execute_query(query, {})
        if result:
            print(f"   Shared contacts - Min: {result[0].get('min_shared', 0)}, Max: {result[0].get('max_shared', 0)}, Avg: {result[0].get('avg_shared', 0):.2f}")
        
        neo4j_conn.close()
        print("\n✅ Fraud pattern tests completed!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_fraud_patterns()
