class SearchProblem:
    """
    Abstract base class for search problems.
    """

    def __init__(self, initial_state, goal_state):
        self.initial_state = initial_state
        self.goal_state = goal_state

    def get_initial_state(self):
        return self.initial_state

    def is_goal(self, state):
        return state == self.goal_state

    def get_actions(self, state):
        raise NotImplementedError("Subclasses must implement get_actions")

    def get_result(self, state, action):
        raise NotImplementedError("Subclasses must implement get_result")

    def get_cost(self, state, action, next_state):
        return 1  # Default uniform cost
