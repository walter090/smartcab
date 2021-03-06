import random
import math
import decay
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator


class LearningAgent(Agent):
    """ An agent that learns to drive in the Smartcab world.
        This is the object you will be modifying. """

    def __init__(self, env, decay_function, learning=False, epsilon=1.0, alpha=0.5):
        super(LearningAgent, self).__init__(env)  # Set the agent in the evironment
        self.planner = RoutePlanner(self.env, self)  # Create a route planner
        self.valid_actions = self.env.valid_actions  # The set of valid actions

        # Set parameters of the learning agent
        self.learning = learning  # Whether the agent is expected to learn
        self.Q = dict()  # Create a Q-table which will be a dictionary of tuples
        self.epsilon = epsilon  # Random exploration factor
        self.alpha = alpha  # Learning factor
        self.decay_function = decay_function  # decay function

        ###########
        ## TO DO ##
        ###########
        # Set any additional class parameters as needed
        self.t = 1

    def reset(self, destination=None, testing=False):
        """ The reset function is called at the beginning of each trial.
            'testing' is set to True if testing trials are being used
            once training trials have completed. """

        # Select the destination as the new location to route to
        self.planner.route_to(destination)

        ########### 
        ## TO DO ##
        ###########
        # Update epsilon using a decay function of your choice
        # Update additional class parameters as needed
        # If 'testing' is True, set epsilon and alpha to 0
        option = {
            'linear': decay.linear(self.epsilon, 0.005, self.t),
            'exponential': decay.exponential(0.95, self.t - 1),
            'quadratic': decay.quadratic(self.t),
            'e_ex': decay.e_ex(0.05, self.t - 1),
            'cosine': decay.cosine(0.01, self.t - 1),
        }

        self.epsilon = option[self.decay_function]
        self.t += 1

        if testing:
            self.epsilon = 0
            self.alpha = 0

        return None

    def build_state(self):
        """ The build_state function is called when the agent requests data from the 
            environment. The next waypoint, the intersection inputs, and the deadline 
            are all features available to the agent. """

        # Collect data about the environment
        waypoint = self.planner.next_waypoint()  # The next waypoint
        inputs = self.env.sense(self)  # Visual input - intersection light and traffic
        # deadline = self.env.get_deadline(self)  # Remaining deadline

        ########### 
        ## TO DO ##
        ###########
        # Set 'state' as a tuple of relevant data for the agent        
        state = (waypoint, inputs['light'], inputs['oncoming'])

        return state

    def get_maxQ(self, state):
        """ The get_max_Q function is called when the agent is asked to find the
            maximum Q-value of all actions based on the 'state' the smartcab is in. """

        ########### 
        ## TO DO ##
        ###########
        # Calculate the maximum Q-value of all actions for a given state
        maxQ = max(self.Q[state].values())

        return maxQ

    def createQ(self, state):
        """ The createQ function is called when a state is generated by the agent. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, check if the 'state' is not in the Q-table
        # If it is not, create a new dictionary for that state
        #   Then, for each action available, set the initial Q-value to 0.0
        if self.learning:
            if state not in self.Q.keys():
                stateQ = dict()
                for action in self.valid_actions:
                    stateQ[action] = 0.0
                self.Q[state] = stateQ
        return

    def choose_action(self, state):
        """ The choose_action function is called when the agent is asked to choose
            which action to take, based on the 'state' the smartcab is in. """

        # Set the agent state and default action
        self.state = state
        self.next_waypoint = self.planner.next_waypoint()

        ########### 
        ## TO DO ##
        ###########
        # When not learning, choose a random action
        # When learning, choose a random action with 'epsilon' probability
        # Otherwise, choose an action with the highest Q-value for the current state
        if not self.learning:
            action = self.valid_actions[random.randint(0, 3)]
        else:
            if random.random() < self.epsilon:
                action = self.valid_actions[random.randint(0, 3)]
            else:
                maxs = []
                maxQ = -1.0
                max_action = None
                for state_action, stateQ in self.Q[state].iteritems():
                    if stateQ > maxQ:
                        maxQ = stateQ
                        max_action = state_action
                        del maxs[:]
                        maxs.append(max_action)
                    elif stateQ == maxQ:
                        maxs.append(state_action)

                if len(maxs) > 1:
                    action = maxs[random.randint(0, len(maxs)-1)]
                else:
                    action = max_action

        return action

    def learn(self, state, action, reward):
        """ The learn function is called after the agent completes an action and
            receives an award. This function does not consider future rewards 
            when conducting learning. """

        ########### 
        ## TO DO ##
        ###########
        # When learning, implement the value iteration update rule
        #   Use only the learning rate 'alpha' (do not use the discount factor 'gamma')
        if self.learning:
            self.Q[state][action] = (1 - self.alpha) * self.Q[state][action] + self.alpha * reward

        return

    def update(self):
        """ The update function is called when a time step is completed in the 
            environment for a given trial. This function will build the agent
            state, choose an action, receive a reward, and learn if enabled. """

        state = self.build_state()  # Get current state
        self.createQ(state)  # Create 'state' in Q-table
        action = self.choose_action(state)  # Choose an action
        reward = self.env.act(self, action)  # Receive a reward
        if self.learning:
            self.learn(state, action, reward)  # Q-learn

        return


def run(args):
    """
    Driving function for running the simulation.
    Press ESC to close the simulation, or [SPACE] to pause the simulation.
    """
    print args

    ##############
    # Create the environment
    # Flags:
    #   verbose     - set to True to display additional output from the simulation
    #   num_dummies - discrete number of dummy agents in the environment, default is 100
    #   grid_size   - discrete number of intersections (columns, rows), default is (8, 6)
    env = Environment(verbose=args['verbose'], num_dummies=args['num_dummies'], grid_size=args['grid_size'])

    ##############
    # Create the driving agent
    # Flags:
    #   learning          - set to True to force the driving agent to use Q-learning
    #    * epsilon        - continuous value for the exploration factor, default is 1
    #    * alpha          - continuous value for the learning rate, default is 0.5
    #    * decay_function - decay function for epsilon: 'linear', 'quadratic', 'exponential', 'e_ex', 'cosine'
    agent = env.create_agent(LearningAgent, learning=args['learning'],
                             epsilon=args['epsilon'], alpha=args['alpha'],
                             decay_function=args['decay_function'])

    ##############
    # Follow the driving agent
    # Flags:
    #   enforce_deadline - set to True to enforce a deadline metric
    env.set_primary_agent(agent, enforce_deadline=args['deadline'])

    ##############
    # Create the simulation
    # Flags:
    #   update_delay - continuous time (in seconds) between actions, default is 2.0 seconds
    #   display      - set to False to disable the GUI if PyGame is enabled
    #   log_metrics  - set to True to log trial and simulation results to /logs
    #   optimized    - set to True to change the default log file name
    sim = Simulator(env, display=args['display'], update_delay=args['update_delay'],
                    log_metrics=args['log_metrics'], optimized=args['optimized'])

    ##############
    # Run the simulator
    # Flags:
    #   tolerance  - epsilon tolerance before beginning testing, default is 0.05
    #   n_test     - discrete number of testing trials to perform, default is 0
    #   show_text  - set to True to show status on terminal ## added
    sim.run(tolerance=args['tolerance'], n_test=args['n_test'])


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()

    # Environment constructor flags
    verbose_parser = parser.add_mutually_exclusive_group()
    verbose_parser.add_argument('--verbose', dest='verbose', action='store_true')
    verbose_parser.add_argument('--no-verbose', dest='verbose', action='store_false')
    parser.add_argument('--num-dummies', dest='num_dummies', type=int, default=100)
    parser.add_argument('--grid-size', dest='grid_size', type=tuple, default=(8, 6))

    # create_agent() flags
    learning_parser = parser.add_argument_group()
    learning_parser.add_argument('--learning', dest='learning', action='store_true')
    learning_parser.add_argument('--no-learning', dest='learning', action='store_false')
    parser.add_argument('--epsilon', type=float, default=1)
    parser.add_argument('--alpha', type=float, default=0.5)
    parser.add_argument('--decay-function', dest='decay_function', default='linear')  # added argument

    # set_primary_target() flag
    deadline_parser = parser.add_mutually_exclusive_group()
    deadline_parser.add_argument('--deadline', dest='deadline', action='store_true')
    deadline_parser.add_argument('--no-deadline', dest='deadline', action='store_false')

    # Simulator constructor flags
    display_parser = parser.add_mutually_exclusive_group()
    display_parser.add_argument('--display', dest='display', action='store_true')
    display_parser.add_argument('--no-display', dest='display', action='store_false')
    log_parser = parser.add_mutually_exclusive_group()
    log_parser.add_argument('--log-metrics', dest='log_metrics', action='store_true')
    log_parser.add_argument('--no-log-metrics', dest='log_metrics', action='store_false')
    optimized_parser = parser.add_mutually_exclusive_group()
    optimized_parser.add_argument('--optimized', dest='optimized', action='store_true')
    optimized_parser.add_argument('--no-optimized', dest='optimized', action='store_false')
    parser.add_argument('--update-delay', dest='update_delay', type=float, default=2)

    # Simulator run() flags
    parser.add_argument('--tolerance', type=float, default=0.05)
    parser.add_argument('--n-test', dest='n_test', type=int, default=0)
    text_parser = parser.add_mutually_exclusive_group()
    text_parser.add_argument('--text', dest='show_text', action='store_true')
    text_parser.add_argument('--no-text', dest='show_text', action='store_true')

    parser.set_defaults(verbose=False, display=True, learning=False, deadline=False, show_text=True)

    arguments = parser.parse_args().__dict__

    run(arguments)
