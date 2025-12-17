# services/rl_feedback_service.py
class RLFeedbackAgent:
    def __init__(self):
        self.q_table = {}  # state → action (threshold) → reward (rep_quality)
        self.epsilon = 0.1  # Exploration
    
    def select_action(self, current_rules, session_data):
        state = hash_rules(current_rules + patient_profile)
        
        if random.random() < self.epsilon:
            return mutate_rules(current_rules)  # Explore
        else:
            return self.q_table.get(state, current_rules)  # Exploit
    
    def update(self, action_rules, reward_reps_detected_quality):
        # Q-Learning update
        state = hash_rules(action_rules)
        self.q_table[state] = (1 - alpha) * self.q_table.get(state, 0) + alpha * reward
