import random
from rich.console import Console
from rich.markdown import Markdown

def init():

    global console, md_text

    console = Console()
    md_text = """
    # PyLaugh  
    A Python module that delivers **programming jokes and puns**! 🤖😆  
    Perfect for developers who need a laugh while debugging.  

    ## 🎉 Features  
    ✅ Random programming jokes  
    ✅ Tech-related puns  
    ✅ Simple & lightweight Python module  
    ✅ Easy to integrate into any project  

    ## 🛠 Installation  
    To install PyLaugh, run:  `pip install pylaugh`.\
    Now you're ready to generate some humor!  

    ## 📌 Usage  
    Import PyLaugh and fetch a joke or pun:  
    ```python
    import pylaugh

    number_of_jokes = 2
    number_of_puns = 2

    tell_jokes(number_of_jokes)  # Get a random joke
    pylaugh.generate_puns(number_of_puns) # Get a programming pun
    # You can also generate this doc by doing

    pylaugh.generate_docs()

    ```
    """
    
    """Initialize joke and pun lists"""
    global jokes, puns  
    jokes = [
    "Why don’t programmers like nature? It has too many bugs.",
    "Why do Python programmers prefer snake_case? Because camelCase spits on their syntax.",
    "How do you comfort a JavaScript developer? You console them!",
    "Why did the C++ developer break up? Because their partner kept casting them into the wrong type!",
    "Why do Java developers wear glasses? Because they don’t C#!",
    "How does a programmer confuse a robot? By using infinite loops in a CAPTCHA test!",
    "Why did the developer go broke? Because he used up all his cache!",
    "Why do programmers prefer iOS development? Because Android throws too many exceptions!",
    "What’s a programmer’s favorite type of music? Algo-rhythm!"
    ]

    puns = [
    "My code has too many bugs... guess I should call an exterminator function.",
    "I tried to write an AI joke, but it couldn’t pass the Turing test.",
    "Debugging is like being a detective in a crime movie… where you are also the murderer.",
    "I wrote a program to calculate emotions... but it kept throwing exceptions.",
    "My code is like a joke—sometimes it works, sometimes it just crashes.",
    "I tried debugging my code... turns out the real bug was me.",
    "I tried to write clean code, but my comments kept getting messy.",
    "My Python script was feeling lazy, so I gave it some async motivation.",
    "The cloud engineer wanted to move to a new house, but kept saying, 'I’ll deploy later.'"
    ]

def tell_jokes(number) :
    for i in range(number) :
        print(random.choice(jokes))


def generate_puns(number) :
    for i in range(number):
        print(random.choice(puns))

def generate_docs() :
    console.print(Markdown(md_text))
