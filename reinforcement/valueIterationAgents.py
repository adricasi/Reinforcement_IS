# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections
import queue

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        # Write value iteration code here
        "*** YOUR CODE HERE ***"
        for _ in range(self.iterations):
            values = util.Counter()
            for state in self.mdp.getStates():
                QValueForAction = util.Counter() # Keys are actions, values are q-values
                # Compute all q-values
                for action in self.mdp.getPossibleActions(state):
                    QValueForAction[action] = self.computeQValueFromValues(state, action)
                values[state] = QValueForAction[QValueForAction.argMax()]
            # update self.values
            self.values = values


    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        "*** YOUR CODE HERE ***"
        QValue = 0
        for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
            QValue += prob*(self.mdp.getReward(state,action,nextState) + self.discount*self.values[nextState])
        return QValue

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        "*** YOUR CODE HERE ***"
        if self.mdp.isTerminal(state): return None
        
        QValueForAction = util.Counter() # Keys are actions, values are q-values
        # Compute all q-values
        for action in self.mdp.getPossibleActions(state):
            QValueForAction[action] = self.computeQValueFromValues(state, action)
        return QValueForAction.argMax()

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        states =  self.mdp.getStates()
        index_state_update = 0

        for _ in range(self.iterations):
            state = states[int(index_state_update % len(states))]
            
            QValueForAction = util.Counter() # Keys are actions, values are q-values
            # Compute all q-values
            for action in self.mdp.getPossibleActions(state):
                QValueForAction[action] = self.computeQValueFromValues(state, action)
            # update self.values
            self.values[state] = QValueForAction[QValueForAction.argMax()]
            index_state_update += 1

        '''
        for _ in range(self.iterations):
            values = util.Counter()
            state_to_update = states[int(index_state_update % len(states))]
            for state in self.mdp.getStates():
                QValueForAction = util.Counter() # Keys are actions, values are q-values
                # Compute all q-values
                for action in self.mdp.getPossibleActions(state):
                    QValueForAction[action] = self.computeQValueFromValues(state, action)
                values[state] = QValueForAction[QValueForAction.argMax()]
            # update self.values
            self.values[state_to_update] = values[state_to_update]
            index_state_update += 1'''
            

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        "*** YOUR CODE HERE ***"
        #Compute predecessors of all states.
        predecessors  = util.Counter()
        for state in self.mdp.getStates():
            for action in self.mdp.getPossibleActions(state):
                for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
                    #Make sure to store predecessors in a set, not a list, to avoid duplicates.
                    if nextState in predecessors:
                        predecessors[nextState].add(state)
                    else:
                        predecessors[nextState] = {state}

        #The priority queue is a min heap
        p_queue = queue.PriorityQueue()

        values = util.Counter()
        for state in self.mdp.getStates():
            if not self.mdp.isTerminal(state):
                maxQValue = self.getMaxQValue(state)
                # Save value
                values[state] = maxQValue
                # diff will be the priority
                diff = abs(self.values[state]-maxQValue)
                p_queue.put((-diff, state))
        
        for _ in range(self.iterations):
            if p_queue.empty(): return
            state = p_queue.get()[1]
            # update self.values
            self.values[state] = values[state]

            for nextState in predecessors[state]:
                maxQValue = self.getMaxQValue(nextState)
                # Save value
                values[nextState] = maxQValue
                # diff will be the priority
                diff = abs(self.values[nextState]-maxQValue)
                if diff > self.theta:
                    p_queue.put((-diff, nextState))

    def getMaxQValue(self,state):
        QValueForAction = util.Counter() # Keys are actions, values are q-values
        # Compute all q-values
        for action in self.mdp.getPossibleActions(state):
            QValueForAction[action] = self.computeQValueFromValues(state, action)
        # return max q-values
        return QValueForAction[QValueForAction.argMax()]
                
