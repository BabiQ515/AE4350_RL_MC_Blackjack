# -*- coding: utf-8 -*-
"""
Created on Thu Aug  5 16:35:28 2021

@author: wardb
"""

import matplotlib.pyplot as plt
import pandas as pd
import random
import numpy as np 
import enum 
import gym 
from gym import error, spaces, utils 
from gym.utils import seeding

##############################################################################
# Set up cards and deck functionalities
##############################################################################

#ranks are the values associated to specific cards. In blackjack, everything
#above a 10 has a value of 10, except for the ace, which has a value of either
#1 or 11
ranks = {
    "two"   : 2, 
    "three" : 3,
    "four"  : 4, 
    "five"  : 5, 
    "six"   : 6, 
    "seven" : 7,
    "eight" : 8, 
    "nine"  : 9,
    "ten"   : 10, 
    "jack"  : 10, 
    "queen" : 10, 
    "king"  : 10, 
    "ace"   : (1,11)
    }

#define a class for the suits
class Suit(enum.Enum): 
    spades   = "spades"
    clubs    = "clubs"
    diamonds = "diamonds"
    hearts   = "hearts"
    
#define a class for a card, a deck is made up out of multiple cards (52 of course)
class Card:
    def __init__(self, suit, rank, value):
        self.suit = suit
        self.rank = rank
        self.value = value
        
    def __str__(self):
        return self.rank + " of " + self.suit.value

#define the deck class, which has functionality to shullfe, deal, peek at the 
#top card and to add a card to the bottom of the deck 
class Deck: 
    def __init__(self,num_decks=1):
        self.cards = []
        for i in range(num_decks): 
            for suit in Suit: 
                for rank, value in ranks.items(): 
                    self.cards.append(Card(suit, rank, value))
    
    #deal one card
    def deal(self): 
        return self.cards.pop(0)
    
    #shuffle the deck 
    def shuffle(self): 
        random.shuffle(self.cards)
        
    #add a card to the bottom of the deck 
    def add_to_bottom(self, card): 
        self.cards.append(card)

    #return all cards still in the deck 
    def __str__(self): 
        res = ""; 
        for card in self.cards: 
            res += card.str(card) + "\n"
        return res
    
    #return the amount of cards still in the deck 
    def __len__(self): 
        return len(self.cards)


#some card class testing
#keys = list(ranks.keys())
#values = list(ranks.values())
#kaart = Card(Suit("clubs"), keys[6], values[6])


##############################################################################
# Implement blackjack rules + create functions to evaluate hands of dealer 
# and player 
##############################################################################

def dealer_eval(dealer_hand): 
    number_aces = 0     #number of aces in the hand
    using_ace_one = 0   #value of hand when we use an ace as a value of 1
    
    #determine the value of the hand when we see the aces as 1
    for card in dealer_hand: 
        if card.rank =="ace": 
            number_aces += 1 
            using_ace_one += card.value[0] #value of 1 for the ace
        else: 
            using_ace_one += card.value 
    
    #if the dealer has an ace, see if using 11 as a value would bring the
    #dealer's hand value closer to [17,21]
    if number_aces > 0: 
        num_aces = 0 
        while num_aces < number_aces: 
            #using_ace_eleven: value of dealer's hand when using a value of 11
            #for aces
            using_ace_eleven = using_ace_one + 10 
            
            if using_ace_eleven > 21: 
                return using_ace_one   #dealer would be bust if using 11 for an ace value
            
            elif using_ace_eleven >= 17 and using_ace_eleven <= 21: 
                return using_ace_eleven 
            
            else: 
                #using an ace as 11 does not bring the total to 17 or higher
                #so if we have another ace, we can try using that as 11 as well   
                using_ace_one = using_ace_eleven
                
            num_aces += 1 
            
        return using_ace_one
    
    else: 
        return using_ace_one

  
    
def player_eval(player_hand): 
    number_aces = 0     #number of aces in the hand
    using_ace_one = 0   #value of hand when we use an ace as a value of 1
    
    #determine the value of the hand when we see the aces as 1
    for card in player_hand: 
        if card.rank =="ace": 
            number_aces += 1 
            using_ace_one += card.value[0] #value of 1 for the ace
        else: 
            using_ace_one += card.value
    
    #if the player has an ace, see if using 11 as a value would bring the
    #dealer's hand value closer to [17,21]
    if number_aces > 0: 
        num_aces = 0 
        while num_aces < number_aces: 
            #using_ace_eleven: value of dealer's hand when using a value of 11
            #for aces
            using_ace_eleven = using_ace_one + 10 
            if using_ace_eleven <= 4: 
                print('ace eleven: ' + str(using_ace_eleven))
            
            if using_ace_eleven > 21: 
                return using_ace_one   #dealer would be bust if using 11 for an ace value
            
            elif using_ace_eleven >= 17 and using_ace_eleven <= 21: 
                return using_ace_eleven 
            
            else: 
                #using an ace as 11 does not bring the total to 17 or higher
                #so if we have another ace, we can try using that as 11 as well   
                using_ace_one = using_ace_eleven
                
            num_aces += 1 
        
        if using_ace_one <= 4: 
            print('ace one: ' + str(using_ace_one))
            print(player_hand)
        return using_ace_one
    
    else: 
        if using_ace_one <= 4: 
            print('ace one: ' + str(using_ace_one))
            hand_str = ''
            for card in player_hand: 
                hand_str = hand_str + card.__str__()
            print(hand_str)
        return using_ace_one


##############################################################################
# define the dealer policy. This is fixed according to some strict casino rules
# where the dealer keeps on hitting until his hand value is larger or equal than
# 17
##############################################################################

def dealer_turn(dealer_hand, deck): 
    hand_value = dealer_eval(dealer_hand)
    
    while hand_value < 17: 
        dealer_hand.append(deck.deal())
        hand_value = dealer_eval(dealer_hand)
        
    return hand_value, dealer_hand, deck 


##############################################################################
# Define OpenAI Gym environment 
##############################################################################

STARTING_CAPITAL = 1000
AMOUNT_DECKS = 6

class BlackjackEnv(gym.Env): 
    metadata = {'render.modes': ['human']}
    
    def __init__(self): 
        super(BlackjackEnv, self).__init__()
        
        #initalize deck and hands of dealer and player 
        self.player_hand = []
        self.dealer_hand = []
        self.deck = Deck(AMOUNT_DECKS)
        
        #define the rewards, 100 for winngin, 0 for a tie and -100 for losing 
        self.reward_options = {"win" : 100, "lose" : -100, "tie" : 0}
        
        #define the possible actions: 0 = hit, 1 = stand 
        self.action_space = spaces.Discrete(2)
        
        #define the observation space. It is a tuple where the first element
        #denotes the possible hand values of the player hand for which he has
        #take an action. These values range from 4 (two 2's) up until 20.
        #If the player's hand value is 21, he automaticallyt wins, so no decision has to be made.
        #The second tuple element is the dealer's up card, the value of which 
        #can range from 2 up until 11
        #The observation space also needs to account for all the possible player
        #hand values when going bust. If the agent decides to hit on 20, he can 
        #reach a max value of 30, considering the ace will be counted as 1 when
        #receiving it at a value of 20. This makes the player's possible states
        #[4-30]
        
        ####### TODO: why is 4 not an option for the player's hand value, and why is 1 not an option for the dealer's hand value
        self.observation_space = spaces.Tuple((spaces.Discrete(27), spaces.Discrete(10)))
        
        #initialze the 'done' return from 'step' function to be false 
        self.done = False
        
    def _take_action(self, action): 
        if action == 0: #hit 
            self.player_hand.append(self.deck.deal())
        
        #evaluate player's hand value after taking the action 
        self.player_value = player_eval(self.player_hand)
        
    def step(self, action): 
        self._take_action(action)
        
        #end the game if it's done => when player hand is >= 21 or player stands
        if action ==1 or self.player_value >= 21: 
            self.done = True
        else: 
            self.done = False
            
        #initialize and calculate reward for this step
        reward = 0
        
        if self.done:   #so stand or player value above 21 
            #calculate reward/loss 
            if self.player_value == 21:     #blackjack, automatic win
                reward = self.reward_options["win"]
            elif self.player_value > 21:    #burnt, automatic lose
                reward = self.reward_options["lose"]
            else:                           #player stands
                #now it's not clear whether the player has won or lost. For this
                #the dealer has to play first in order to be able to compare their hands
                
                dealer_value, self.dealer_hand, self.deck = dealer_turn(self.dealer_hand, self.deck)
                
                if dealer_value < self.player_value or dealer_value > 21: 
                    reward = self.reward_options["win"]
                elif dealer_value == 21 or dealer_value > self.player_value : ## TODO: shouldn't the dealer's turn be done first to check whether he has blackjack? 
                                          # this only gets checked when the player stands. Both people could have blackjack
                    reward = self.reward_options["lose"]
                else: 
                    reward = self.reward_options["tie"]
                    
        self.capital += reward
        
        #determine the next state to return 
        #state is player's hand value -4 to fit in the [0,22] range used to specify
        #the observation space 
        #the other part of the state is the dealer's up card, with a value of [1,10], 
        #subtracted by -1 to fit the [0,9] range in the observation space definition
        
        #index for player hand value 
        obs_index_player = self.player_value - 4 
        
        #index for dealer's upcard 
        obs_index_dealer = dealer_eval([self.upcard]) - 2 
        
        state = np.array([obs_index_player, obs_index_dealer])
        
        #return state, reward and whether the game is done
        return state, reward, self.done, {}
        
 
    #reset game. The player and dealer hands will be put back in the deck and
    #it will be shuffled. After, the player is dealt 2 cards and the dealer's 
    #upcard is shown/dealt. The starting capital of the player is reset to 
    #STARTING_CAPITAL. The function returns an initial state
    def reset(self):
        self.deck.cards += self.player_hand + self.dealer_hand
        self.deck.shuffle()
        
        self.done = False 
        
        self.capital = STARTING_CAPITAL
        
        #deal the player's hand 
        self.player_hand = [self.deck.deal(), self.deck.deal()]
        #deal the dealer's hand 
        self.dealer_hand = [self.deck.deal(), self.deck.deal()]
        
        self.player_value = player_eval(self.player_hand)
        obs_index_player = self.player_value - 4    #convert [2-20] range to [0-18] range
        
        self.upcard = self.dealer_hand[0]
        obs_index_dealer = dealer_eval([self.upcard]) - 2 #convert [1-10] to [0-9]
        
        state = np.array([obs_index_player, obs_index_dealer])
        
        #print('player_value: ' + str(self.player_value))
        #print('upcard value: ' + str(self.upcard.value))
        
        return state
     
    #render the game. It shows player balance, player hand, player value
    #dealer's upcard and whether the episode is done
    def render(self, mode='human', close=False): 
        player_hand_ranks = []
        for card in self.player_hand: 
            player_hand_ranks.append(card.rank)
        
        #upcard = dealer_eval([self.upcard])
        
        print('PLayer capital: ' + str(self.capital))
        print('Player hand: ' + str(player_hand_ranks))
        print('Dealer upcard: ' + str(self.upcard.rank))
        print('Done?: ' + str(self.done))
             
        


##############################################################################
# Initialize first-visit MC algorithm 
##############################################################################

def init_mc(env): 
    #initialize policy to be evaluated. The policy is stochastic. In each state
    #a probability to either hit or stick is determined. Initially these 
    #probabilities are set to 50% for each action
    policy_map = [[[0.5 for k in range(env.action_space.n)]for j in range(env.observation_space[1].n)] for l in range(env.observation_space[0].n)]
    
    #initialize the state-action pair value table. This denotes the (discounted)
    #exected rewards when taking action a in state s. Initially, all these values
    #are set to zero 
    Q_table = [[[0 for k in range(env.action_space.n)] for j in range(env.observation_space[1].n)] for l in range(env.observation_space[0].n)]
    
    #initialize returns array for all the state-action pairs. These are all set
    #to 0 as well 
    returns = Q_table 
    
    #initialize learning rate. Defines the weight of new state-action values
    #int the Q_table after each episode. Small learning_rate denotes exploratory 
    #behaviour 
    learning_rate = 0.001
    
    #initialize the probability learning rate epsilon. This rate is analogous to
    #the learning rate, but for the probability table. It determines the weight
    #for adjusting the probability that a certain action is to be taken. A high
    #epsilon yields a smaller increase/decrease for the probability corresponding
    #to the state-action pair
    epsilon = 1
    
    #???epsilon_decay denotes by which factor epsilon is decayed. With decreasing
    #epsilon over the episodes, the agent starts to exploit more than explore.
    epsilon_decay = 0.99999
    
    #epsilon cannot go below a certain bound in order to still guarantee some
    #exploration at any time 
    epsilon_min = 0.9
    
    #the discount rate determines in what way the actions prior to a received
    #reward (thus in the same episode) contribute to this reward being received.
    #If the discount rate is 1, no attention is given to the previous actions, 
    #except for the last action which invoked the reward
    discount_rate = 0.8
    
    return policy_map, Q_table, returns
  

##############################################################################
# Initialize learning parameters 
##############################################################################
  
#initialize learning rate. Defines the weight of new state-action values
#int the Q_table after each episode. Small learning_rate denotes exploratory 
#behaviour 
learning_rate = 0.001
    
#initialize the probability learning rate epsilon. This rate is analogous to
#the learning rate, but for the probability table. It determines the weight
#for adjusting the probability that a certain action is to be taken. A high
#epsilon yields a smaller increase/decrease for the probability corresponding
#to the state-action pair
epsilon = 1
    
#???epsilon_decay denotes by which factor epsilon is decayed. With decreasing
#epsilon over the episodes, the agent starts to exploit more than explore.
epsilon_decay = 0.99999
    
#epsilon cannot go below a certain bound in order to still guarantee some
#exploration at any time 
epsilon_min = 0.9
    
#the discount rate determines in what way the actions prior to a received
#reward (thus in the same episode) contribute to this reward being received.
#If the discount rate is 1, no attention is given to the previous actions, 
#except for the last action which invoked the reward
discount_rate = 0.8  

  

###############################################################################
# Construct main loop for first visit MC
###############################################################################
def loop_mc(env, policy_map, Q_table, returns, learning_rate, epsilon, epsilon_decay, epsilon_min, discount_rate): 
    #generate episode using the given policy
    episode_results = []
    state = env.reset() 
    
    while env.done == False: 
        print('state: ' + str(state))
        #determine probabilities to take action 0 (hit) or 1 (stand)
        actions_probs = policy_map[state[0]][state[1]]
        #determine action with highest probability 
        best_action = np.argmax(actions_probs)
        #retract its probability 
        prob_best_action = actions_probs[best_action]
        
        if random.uniform(0,1) < prob_best_action: 
            action = best_action 
        else: 
            if best_action == 1: 
                action = 0
            else: 
                action = 1
        #print('action: ' + str(action))
        #take a step in the environment with the determined action 
        next_state, reward, env.done, info = env.step(action)
        
        #print('reward: ' + str(reward))
        #print('new state: ' + str(next_state))
        
        #append the state - action pair and corresponding reward to results of
        #this episode 
        episode_results.append([state, action, reward])
        
        #start from the next state 
        state = next_state 
    
    #update the Q_table and policy map
    discount_counter = 0
    for episode in episode_results: 
        state = episode[0]
        action = episode[1]
        reward = episode[2]*(discount_rate)**discount_counter
        #update Q-value of state-action pair via learning rate 
        Q_table[state[0]][state[1]][action] += learning_rate*reward
        #update policy map (probabilities) via discounted epsilon 
        epsilon = max(epsilon*epsilon_decay, epsilon_min)
        policy_map[state[0]][state[1]][action] += (1-epsilon)
        if action == 0: 
            policy_map[state[0]][state[1]][1] = 1 - policy_map[state[0]][state[1]][action]
        else: 
            policy_map[state[0]][state[1]][1] = 1 - policy_map[state[0]][state[1]][action]
        
        discount_counter += 1
    
    return Q_table, policy_map, epsilon
        
    

###############################################################################
# test the gym environment
###############################################################################
env = BlackjackEnv()

total_reward = 0
NUM_EPISODES = 10000

policy_map, Q_table, returns = init_mc(env)

for i in range(NUM_EPISODES):
    print('--------------')
    print('Episode ' + str(i))
    
    Q_table, policy_map, epsilon = loop_mc(env, policy_map, Q_table,returns, learning_rate, epsilon, epsilon_decay, epsilon_min, discount_rate)
    

###############################################################################
# Plot results 
###############################################################################






