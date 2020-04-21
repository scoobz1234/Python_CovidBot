#  Copyright (c) 2020. Stephen R. Ouellette

import tkinter as tk
from threading import Timer, Thread, Event
from tkinter import *
from tkinter import ttk
from chat import *

#####################################
#        GLOBAL VARIABLES           #
#####################################
INITIALIZED = False
POKETIME = 20
USERNAME = "You"
CONTEXT = {}

#####################################
#          WINDOW CREATION          #
#####################################
def close_window():
    """Function to button things up before we close"""
    poke_timer.cancel()  # free up the thread before we exit
    window.destroy()  # kill the window

# Window Creation
window = Tk()  # Create the window
window.protocol("WM_DELETE_WINDOW", close_window)  # Set up the window close function (override)
window.geometry("680x600")  # Window size (x,y)
window.title("COVID-19 Chatbot")  # Window title

# Window Styles
style = ttk.Style()  # initialize the style
style.theme_create("TabStyle", parent="alt", settings={
    "tNotebook": {"configure": {"tabmargins": [2, 5, 2, 0]}},
    "TNotebook.Tab": {"configure": {"padding": [20, 10]}, }})

style.theme_use("TabStyle")  # sets the theme to use to our above theme we created.

# Window Tabs
tabs = ttk.Notebook(window, width=200, height=200)

# Create tab and then add the tab to the notebook..
tab_one = ttk.Frame(tabs)
tabs.add(tab_one, text="Covid Chat")

tab_two = ttk.Frame(tabs)
tabs.add(tab_two, text="About")

tabs.pack(expand=True, fill=tk.BOTH)

###############################
#          CLASSES            #
###############################
class PokeTimer(object):
    """ Timer for calling poke function """

    def __init__(self, interval, f, *args, **kwargs):
        """Initialize the class object"""
        self.interval = interval
        self.f = f
        self.args = args
        self.kwargs = kwargs

        self.timer = None

    def callback(self):
        """Handles the callback function"""
        self.f(*self.args, **self.kwargs)
        self.start()

    def cancel(self):
        """Cancel function so we can clean up"""
        self.timer.cancel()

    def start(self):
        """Start function so we can actually start the thread(timer)"""
        self.timer = Timer(self.interval, self.callback)
        self.timer.start()

################################
#          FUNCTIONS           #
################################
def poke(event=None):
    """Poke event, checks if the user is still there... currently just bugs the user"""
    msg_list.insert(END, "Bot -> Are you still there?")
    CONTEXT[USERNAME] = 'here'


def init(event=None):
    """ Function to send initial message"""
    global INITIALIZED  # Gets the global variable
    if not INITIALIZED:
        msg_list.insert(END, "Bot -> Hello! How can I help you today?")
        INITIALIZED = True


def send(event=None):
    """Handles sending of the messages"""
    poke_timer.cancel()  # Cancel the poke timer
    msg = msg_input.get()  # Get the user input
    msg_list.insert(END, "You -> " + msg)  # insert user message into list
    msg_input.set("")  # clear the input
    response(msg)  # Call the bot to answer
    poke_timer.start()  # restart the poke timer


# Bot response function
def classify(sentence):
    """Classifies the users input into the tag best matched"""
    # make a prediction using the model from the user input passed into the bag of words function
    results = model.predict([bag_of_words(sentence, WORDS)])[0]  # the positional 0 here helps with threshold below
    # Filter out the weak results
    results = [[i, r] for i, r in enumerate(results) if r > THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((TAGS[r[0]], r[1]))
    # return tuple of intent and probability
    return return_list


def response(sentence, contextID="hardCodedID"):
    """Handles the response from the bot"""
    results = classify(sentence)
    # if we have a classification then find the matching intent tag
    if results:
        # loop as long as there are matches to process
        while results:
            for i in data['intents']:
                # find a tag matching the first result
                if i['tag'] == results[0][0]:
                    # set the context for this intent if necessary
                    if 'context_set' in i:
                        CONTEXT[contextID] = i['context_set']

                    # check if this intent is contextual and applies to this conversation
                    if not 'context_filter' in i or \
                            (contextID in CONTEXT and 'context_filter' in i and i['context_filter'] == CONTEXT[contextID]):
                        # a random response from the intent
                        msg_list.insert(END, "Bot ->" + random.choice(i['responses']))
            results.pop(0)
    else:
        msg_list.insert(END, "Bot -> I'm sorry, I didn't quite understand?")


""" COVID TAB """
# Chat
frame_chat = Frame(tab_one, bd=1, relief="sunken", background="black")
frame_chat.pack(padx=10, pady=10, fill=None, expand=False)
msg_input = StringVar()  # User message to bot (contains the message)
msg_input.set("")
scrollbar = Scrollbar(frame_chat)

msg_list = Listbox(
    frame_chat,
    height=25,
    width=100,
    borderwidth=0,
    highlightthickness=0,
    background=frame_chat.cget("background"),
    yscrollcommand=scrollbar)

msg_list.config(background='black', foreground='white')

scrollbar.pack(side=RIGHT, fill=Y)

msg_list.pack(padx=10, pady=10, fill=BOTH, expand=True)

msg_list.pack()
frame_chat.pack()

# Chat Input
msg_entry = Entry(tab_one, textvariable=msg_input)
msg_entry.config(background="white")
msg_entry.bind("<Return>", send)
msg_entry.pack(side=TOP, fill=X, padx=30, ipady=5)
btn_send = Button(msg_entry, text="Send", command=send, cursor="arrow")
btn_send.pack(side=RIGHT, fill=Y)

"""About Tab"""
frame = Frame(tab_two, bd=1, relief="sunken", background="white")
frame.pack(padx=10, pady=10, fill=None, expand=False)

# Labels
lbl_one = Label(tab_two, text="Created for Final Project CSC370 Artificial Intelligence")
lbl_one.pack(side=TOP, fill=X, padx=30)

lbl_two = Label(
    tab_two,
    text="This is a Graphical User Interface created and implemented with my "
         "Covid-19 Bot. This bot is contextual (new from the last version)"
         "Meaning it can retain the context of the conversation you are having"
         "within reason of course! The bot will train every time you run the program"
         "This is happening because its really fast, and it can be afforded.",
    wraplength=500)
lbl_two.pack(side=TOP, fill=X, padx=30)

lbl_three = Label(tab_two, text="Copyright© Stephen R Ouellette, 2020")
lbl_three.pack(side=BOTTOM, fill=X, padx=30)


#####################################
#                RUN                #
#####################################
init()  # sends the initial message
poke_timer = PokeTimer(POKETIME, poke)  # threaded timer for chat timing
poke_timer.start()  # start the poke timer

window.mainloop()  # main loop (starts and keeps the window open till we are ready to close)
