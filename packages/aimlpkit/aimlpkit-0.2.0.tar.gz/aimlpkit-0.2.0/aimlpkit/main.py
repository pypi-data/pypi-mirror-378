def disp() -> str:
    print(
        """
        disp_1 - Design an Expert System using AIML Tool.
        disp_2 - Implement Bayes Theorem using Python.
        disp_3 - Implement Conditional Probability and Joint Probability using Python.
        disp_4 - Create a simple Rule Based System in Prolog for diagnosing a common illness based on symptoms.
        disp_5 - Design Fuzzy Based Application using Python.
        disp_6 - Simulate Artificial Neural Network Model with both Feed-forward and Back-propagation approach.
        disp_7 - Genetic Algorithm.
        disp_8 - Inteliigent Agent.
        disp_9 - Sementic Network.
        disp_10 - NLP Parser.
        """
    )


def disp_1() -> str:
    return """
# Conversation.aiml

<?xml version="1.0" encoding="ISO-8859-1"?>
<aiml version="1.0">
    <meta name="language" content="en"/>
    <category>
        <pattern> HELLO * </pattern>
        <template>
            Hello User!
        </template>
    </category>
</aiml>

# LearningFileList.aiml

<aiml version="1.0">
    <category>
        <pattern>LEARN AIML</pattern>
        <template>
            <learn>conversation.aiml</learn>
        </template>
    </category>
</aiml>

# main.py

import os
import aiml

BRAIN_FILE = "brain.dump"
k = aiml.Kernel()

if os.path.exists(BRAIN_FILE):
    print("Loading from brain file: " + BRAIN_FILE)
    k.loadBrain(BRAIN_FILE)
else:
    k.bootstrap(learnFiles="learningFileList.aiml", commands="LEARN AIML")
    print("Saving brain file: " + BRAIN_FILE)
    k.saveBrain(BRAIN_FILE)

while True:
    input_text = input("USER > ")
    response = k.respond(input_text)
    print(response)
    """


def disp_2() -> str:
    return """
class BayesTheorem:
    def __init__(self):
        pass

    def calculate_evidence(self, prior, likelihood, prior_complement, likelihood_complement):
        return (prior * likelihood) + ((1 - prior) * likelihood_complement)

    def calculate_posterior(self, prior, likelihood, evidence=None, likelihood_complement=None):
        if evidence is None:
            if likelihood_complement is None:
                raise ValueError("Either evidence or likelihood_complement must be provided")
            evidence = self.calculate_evidence(prior, likelihood, prior, likelihood_complement)
        return (prior * likelihood) / evidence

    def update_belief(self, current_belief, new_likelihood, new_evidence=None, new_likelihood_complement=None):
        return self.calculate_posterior(current_belief, new_likelihood, new_evidence, new_likelihood_complement)

def medical_diagnosis_example():
    bayes = BayesTheorem()
    prior = 0.01
    sensitivity = 0.95
    specificity = 0.90
    false_positive = 1 - specificity
    posterior = bayes.calculate_posterior(
        prior=prior,
        likelihood=sensitivity,
        likelihood_complement=false_positive
    )
    print("Medical Diagnosis Example:")
    print(f"Prior probability of disease: {prior:.3f}")
    print(f"Test sensitivity: {sensitivity:.3f}")
    print(f"Test specificity: {specificity:.3f}")
    print(f"Probability of disease given positive test: {posterior:.3f}")
    print(f"That's only {posterior*100:.1f}% chance despite 95% accurate test!")
    return posterior

if __name__ == "__main__":
    print("Basic Bayes Theorem Example:")
    bayes = BayesTheorem()
    result = bayes.calculate_posterior(prior=0.3, likelihood=0.8, likelihood_complement=0.5)
    print(f"P(H|E) = {result:.3f}")
    medical_diagnosis_example()
    print("\\n")
    """


def disp_3() -> str:
    return """
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('/content/student dropout.csv')

joint_probability_pivot = pd.pivot_table(
    df,
    values='School',
    index=['Attended_Nursery'],
    columns=['Dropped_Out'],
    aggfunc='count',
    fill_value=0
)
joint_probability_pivot = joint_probability_pivot / joint_probability_pivot.sum().sum()

print("Joint Probability Pivot Table:")
display(joint_probability_pivot)

marginal_prob_dropped_out_true = joint_probability_pivot[True].sum()
joint_prob_no_nursery_and_dropped_out_true = joint_probability_pivot.loc['no', True]
conditional_probability = joint_prob_no_nursery_and_dropped_out_true / marginal_prob_dropped_out_true
print((f"Conditional probability P(Attended_Nursery= no | dropped_out = true): {conditional_probability}"))
    """


def disp_4() -> str:
    return """
:- dynamic symptom/1.
:- dynamic illness/1.
:- dynamic ask/1.

illness(cold) :-
    symptom(runny_nose),
    symptom(sneezing),
    symptom(sore_throat).

illness(flu) :-
    symptom(fever),
    symptom(headache),
    symptom(body_ache),
    symptom(chills).

illness(allergy) :-
    symptom(runny_nose),
    symptom(sneezing),
    symptom(itchy_eyes).

illness(covid19) :-
    symptom(fever),
    symptom(cough),
    symptom(loss_of_taste_smell).

diagnose :-
    writeln('--- Medical Diagnosis System ---'),
    writeln('Answer yes/no for each symptom.'),
    retractall(symptom(_)),
    ask(runny_nose),
    ask(sneezing),
    ask(sore_throat),
    ask(fever),
    ask(headache),
    ask(body_ache),
    ask(chills),
    ask(itchy_eyes),
    ask(cough),
    ask(loss_of_taste_smell),
    findall(Disease, illness(Disease), Diseases),
    ( Diseases \\= []
    -> format('Possible diagnosis: ~w~n', [Diseases])
    ; writeln('No clear diagnosis. Please consult a doctor.')
    ).

ask(Symptom) :-
    format('Do you have ~w? (yes/no): ', [Symptom]),
    read(Reply),
    (Reply == yes -> assertz(symptom(Symptom)) ; true).
    """


def disp_5() -> str:
    return """
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

attendance = ctrl.Antecedent(np.arange(0, 101, 1), 'attendance')
internal = ctrl.Antecedent(np.arange(0, 31, 1), 'internal')
assignment = ctrl.Antecedent(np.arange(0, 11, 1), 'assignment')
performance = ctrl.Consequent(np.arange(0, 101, 1), 'performance')

attendance['low'] = fuzz.trimf(attendance.universe, [0, 0, 50])
attendance['medium'] = fuzz.trimf(attendance.universe, [30, 60, 80])
attendance['high'] = fuzz.trimf(attendance.universe, [70, 100, 100])

internal['low'] = fuzz.trimf(internal.universe, [0, 0, 15])
internal['medium'] = fuzz.trimf(internal.universe, [10, 15, 25])
internal['high'] = fuzz.trimf(internal.universe, [20, 30, 30])

assignment['low'] = fuzz.trimf(assignment.universe, [0, 0, 5])
assignment['medium'] = fuzz.trimf(assignment.universe, [3, 5, 8])
assignment['high'] = fuzz.trimf(assignment.universe, [7, 10, 10])

performance['poor'] = fuzz.trimf(performance.universe, [0, 0, 40])
performance['average'] = fuzz.trimf(performance.universe, [30, 45, 60])
performance['good'] = fuzz.trimf(performance.universe, [50, 65, 80])
performance['excellent'] = fuzz.trimf(performance.universe, [75, 100, 100])

rule1 = ctrl.Rule(attendance['low'] & internal['low'] & assignment['low'], performance['poor'])
rule2 = ctrl.Rule(attendance['low'] & internal['medium'] & assignment['low'], performance['poor'])
rule3 = ctrl.Rule(attendance['low'] & internal['high'] & assignment['low'], performance['average'])
rule4 = ctrl.Rule(attendance['medium'] & internal['low'] & assignment['low'], performance['poor'])
rule5 = ctrl.Rule(attendance['medium'] & internal['medium'] & assignment['medium'], performance['average'])
rule6 = ctrl.Rule(attendance['medium'] & internal['high'] & assignment['medium'], performance['good'])
rule7 = ctrl.Rule(attendance['high'] & internal['low'] & assignment['medium'], performance['average'])
rule8 = ctrl.Rule(attendance['high'] & internal['medium'] & assignment['low'], performance['average'])
rule9 = ctrl.Rule(attendance['high'] & internal['medium'] & assignment['high'], performance['good'])
rule10 = ctrl.Rule(attendance['high'] & internal['high'] & assignment['medium'], performance['good'])
rule11 = ctrl.Rule(attendance['high'] & internal['high'] & assignment['high'], performance['excellent'])
rule12 = ctrl.Rule(attendance['medium'] & internal['high'] & assignment['high'], performance['excellent'])
rule13 = ctrl.Rule(attendance['low'] & internal['high'] & assignment['high'], performance['good'])
rule14 = ctrl.Rule(attendance['medium'] & internal['medium'] & assignment['high'], performance['good'])

performance_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14])

performance_eval = ctrl.ControlSystemSimulation(performance_ctrl)
performance_eval.input['attendance'] = int(input("Enter Attendance Percentage: "))
performance_eval.input['internal'] = int(input("Enter internal Percentage: "))
performance_eval.input['assignment'] = int(input("Enter assginment Percentage: "))
performance_eval.compute()

print("Predicted Performance Score:", performance_eval.output['performance'])

score = performance_eval.output['performance']
if score < 40:
    category = "Poor"
elif score < 60:
    category = "Average"
elif score < 80:
    category = "Good"
else:
    category = "Excellent"

print("Performance Category:", category)
    """


def disp_6() -> str:
    return """
import numpy as np

class SimpleNN:
    def __init__(self, input_size, hidden_size, output_size, lr=0.5):
        self.lr = lr
        self.w1 = np.random.uniform(-1, 1, (input_size, hidden_size))
        self.b1 = np.zeros((1, hidden_size))
        self.w2 = np.random.uniform(-1, 1, (hidden_size, output_size))
        self.b2 = np.zeros((1, output_size))

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        return x * (1 - x)

    def forward(self, X):
        self.z1 = np.dot(X, self.w1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.w2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        return self.a2

    def backward(self, X, y, output):
        output_error = y - output
        output_delta = output_error * self.sigmoid_derivative(output)

        hidden_error = output_delta.dot(self.w2.T)
        hidden_delta = hidden_error * self.sigmoid_derivative(self.a1)

        self.w2 += self.a1.T.dot(output_delta) * self.lr
        self.b2 += np.sum(output_delta, axis=0, keepdims=True) * self.lr
        self.w1 += X.T.dot(hidden_delta) * self.lr
        self.b1 += np.sum(hidden_delta, axis=0, keepdims=True) * self.lr

    def train(self, X, y, epochs=10000):
        for epoch in range(epochs):
            output = self.forward(X)
            self.backward(X, y, output)
            if (epoch % 1000 == 0):
                loss = np.mean(np.square(y - output))
                print(f"Epoch {epoch}, Loss: {loss:.4f}")

    def predict(self, X):
        output = self.forward(X)
        return (output > 0.5).astype(int)

X = np.array([[0,0],
              [0,1],
              [1,0],
              [1,1]])

y_xor = np.array([[0],
                  [1],
                  [1],
                  [0]])

y_xnor = 1 - y_xor

print("Training on XOR:")
nn_xor = SimpleNN(input_size=2, hidden_size=2, output_size=1, lr=0.5)
nn_xor.train(X, y_xor, epochs=80000)
print("XOR predictions:")
print(nn_xor.predict(X))

print("\\nTraining on XNOR:")
nn_xnor = SimpleNN(input_size=2, hidden_size=2, output_size=1, lr=0.5)
nn_xnor.train(X, y_xnor, epochs=80000)
print("XNOR predictions:")
print(nn_xnor.predict(X))
    """


def disp_7() -> str:
    return """
import random

def fitness(x):
    return x**2

population = [random.randint(0, 31) for _ in range(6)]
generations = 10

for g in range(generations):
    scores = [(x, fitness(x)) for x in population]
    scores.sort(key=lambda s: s[1], reverse=True)
    print(f"Gen {g+1}: Best = {scores[0]}")
    total_fitness = sum([s[1] for s in scores])
    parent_indices = random.choices(range(len(population)), weights=[s[1] for s in scores], k=2)
    parents = [population[i] for i in parent_indices]
    children = []
    for _ in range(len(population)-2):
        child = (parents[0] + parents[1]) // 2
        if random.random() < 0.5:
            child = random.randint(0, 31)
        children.append(child)
    population = parents + children

print("\\nFinal best:", max(population, key=fitness))
    """


def disp_8() -> str:
    return """
import random

class Agent:
    def act(self, p): return 'clean' if p=='dirty' else random.choice(['up','down','left','right'])

bot = Agent()
print(bot.act('dirty'))

class IntelligentAgent:
    def __init__(self, environment_size=(10, 10)):
        self.environment_size = environment_size
        self.location = (random.randint(0, environment_size[0]-1), random.randint(0, environment_size[1]-1))
        self.knowledge = {}

    def act(self, perception):
        if 'dirt' in perception and perception['dirt'] == 'present':
            return 'clean'
        elif 'obstacle' in perception and perception['obstacle'] == 'present':
            return random.choice(['up', 'down', 'left', 'right'])
        else:
            return random.choice(['up', 'down', 'left', 'right', 'stay'])

    def move(self, action):
        x, y = self.location
        if action == 'up': y = max(0, y - 1)
        elif action == 'down': y = min(self.environment_size[1] - 1, y + 1)
        elif action == 'left': x = max(0, x - 1)
        elif action == 'right': x = min(self.environment_size[0] - 1, x + 1)
        self.location = (x, y)
        return self.location

    def perceive(self, environment):
        return environment.get(self.location, {})

class SimpleEnvironment:
    def __init__(self, size=(10, 10)):
        self.size = size
        self.state = {}
        self.state[(2, 3)] = {'dirt': 'present'}
        self.state[(5, 5)] = {'obstacle': 'present'}
        self.state[(8, 1)] = {'dirt': 'present'}

    def get(self, location, default={}):
        return self.state.get(location, default)

    def update(self, location, action):
        if action == 'clean' and location in self.state and 'dirt' in self.state[location]:
            del self.state[location]['dirt']
            if not self.state[location]:
                del self.state[location]

env = SimpleEnvironment()
bot = IntelligentAgent(environment_size=env.size)

for _ in range(20):
    perception = bot.perceive(env)
    action = bot.act(perception)
    print(f"Agent at {bot.location} perceives {perception} and decides to {action}")
    if action == 'clean':
        env.update(bot.location, action)
    else:
        bot.move(action)

print("\\nFinal environment state:", env.state)

class SmartNetAgent:
    def __init__(self):
        self.solutions = {
            'ping_fail': ['check_cables', 'restart_router', 'renew_dhcp'],
            'slow_speed': ['close_apps', 'reset_modem', 'check_bandwidth'],
            'no_connect': ['reboot_device', 'check_wifi', 'update_drivers']
        }
        self.success_rate = {sol: 0 for sol in sum(self.solutions.values(), [])}

    def fix(self, problem, success=True):
        solution = random.choice(self.solutions[problem])
        if success: self.success_rate[solution] += 1
        return solution

agent = SmartNetAgent()
print(agent.fix(input("")))
    """


def disp_9() -> str:
    return """
import networkx as nx
import matplotlib.pyplot as plt

G = nx.DiGraph()
G.add_edge("Dog", "Mammal", relation="is-a")
G.add_edge("Mammal", "Animal", relation="is-a")
G.add_edge("Dog", "has fur", relation="has")

pos = nx.spring_layout(G)
edge_labels = nx.get_edge_attributes(G, 'relation')
nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2500)
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
plt.show()
    """


def disp_10() -> str:
    return """
import nltk
from nltk.parse.chart import ChartParser
from nltk import CFG

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

grammar = CFG.fromstring(\\"\\"\\"
S -> NP VP
NP -> DT N | DT ADJ N | PRP
VP -> V NP | V NP PP | V
PP -> P NP

DT -> 'the' | 'a'
N -> 'cat' | 'dog' | 'mat' | 'mouse'
ADJ -> 'black' | 'lazy' | 'small'
V -> 'chased' | 'sat' | 'ate' | 'saw'
P -> 'on' | 'under' | 'with'
PRP -> 'he' | 'she'
\\"\\"\\")
 
parser = ChartParser(grammar)

sentence = "the black cat chased the small mouse"
tokens = sentence.split()

for tree in parser.parse(tokens):
    print(tree)
    tree.pretty_print()
    """
