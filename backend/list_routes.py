"""
List all registered Flask routes
"""
from app import app

print("Registered routes:")
for rule in app.url_map.iter_rules():
    methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    print(f"  {rule.endpoint:30s} {methods:20s} {rule.rule}")
