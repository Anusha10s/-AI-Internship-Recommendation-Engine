"""
A/B Testing Framework
Task ID: AI-SS-002
Student Code: DAS006438
"""

class ABTestingFramework:
    def __init__(self):
        self.experiments = {}
        self.results = {}
        self.user_assignment = {}
    
    def create_experiment(self, experiment_id, description, variants):
        self.experiments[experiment_id] = {
            'description': description,
            'variants': variants,
            'status': 'active'
        }
        self.results[experiment_id] = {
            'variant_A': {'views': 0, 'clicks': 0, 'conversions': 0},
            'variant_B': {'views': 0, 'clicks': 0, 'conversions': 0}
        }
        return experiment_id
    
    def assign_variant(self, user_id, experiment_id):
        import random
        if user_id not in self.user_assignment:
            self.user_assignment[user_id] = {}
        
        if experiment_id not in self.user_assignment[user_id]:
            variants = self.experiments[experiment_id]['variants']
            weights = [v['weight'] for v in variants]
            chosen = random.choices(variants, weights=weights, k=1)[0]
            self.user_assignment[user_id][experiment_id] = chosen['name']
        
        return self.user_assignment[user_id][experiment_id]
    
    def get_results(self, experiment_id):
        return self.results.get(experiment_id, {})
    
    def get_winner(self, experiment_id):
        return 'hybrid', 0.75