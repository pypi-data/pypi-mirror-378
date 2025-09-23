def disp() -> str:
    print(
        """
        disp_1 - Design an Expert System using AIML Tool.
        disp_2 - Implement Bayes Theorem using Python.
        disp_3 - Implement Conditional Probability and Joint Probability using Python.
        disp_4 - Create a simple Rule Based System in Prolog for diagnosing a common illness based on symptoms.
        disp_5 - Design Fuzzy Based Application using Python.
        disp_6 - Simulate Artificial Neural Network Model with both Feed-forward and Back-propagation approach.
        disp_7 - Gentic Algorithm.
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
