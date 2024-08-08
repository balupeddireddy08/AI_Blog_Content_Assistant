from langchain_huggingface import HuggingFaceEndpoint  # Import Hugging Face endpoint class
from secret_api_keys import hugging_face_api_key # Import secret API key from separate file
from langchain.prompts import PromptTemplate  # Import PromptTemplate class from langchain

import os  # Import the 'os' module for potential system interactions
import re  # Import the 're' module for regular expressions
import streamlit as st  # Import Streamlit for web app development

# Set the Hugging Face Hub API token as an environment variable
os.environ['HUGGINGFACEHUB_API_TOKEN'] = hugging_face_api_key

# Define the Hugging Face model repository ID
repo_id = "meta-llama/Meta-Llama-3-8B-Instruct"

# Create a Hugging Face Endpoint instance
llm = HuggingFaceEndpoint(
    repo_id=repo_id,  # Specify the model repository ID
    temperature=0.6,  # Set the temperature parameter (controls randomness)
    token=hugging_face_api_key,  # Use the API key for authentication
)

# Define a PromptTemplate for title suggestions
prompt_template_for_title_suggestion = PromptTemplate(
    input_variables=['topic'],  # Specify input variables
    template =  # Define the prompt template
    '''
    I'm planning a blog post on topic : {topic}.
    The title is informative, or humorous, or persuasive. 
    The target audience is beginners, tech enthusiasts.  
    Suggest a list of ten creative and attention-grabbing titles for this blog post. 
    Don't give any explanation or overview to each title.
    '''
)

title_suggestion_chain = prompt_template_for_title_suggestion | llm # defining the title suggestion chain

# Define a PromptTemplate for blog content generation
prompt_template_for_title = PromptTemplate(
    input_variables=['title', 'keywords', 'blog_length'],  # Specify input variables
    template=  # Define the prompt template
    '''Write a high-quality, informative, and plagiarism-free blog post on the topic: "{title}". 
    Target the content towards a beginner audience. 
    Use a conversational writing style and structure the content with an introduction, body paragraphs, and a conclusion. 
    Try to incorporate these keywords: {keywords}. 
    Aim for a content length of {blog_length} words. 
    Make the content engaging and capture the reader's attention.'''
)

title_chain = prompt_template_for_title | llm # Create a chain for title generation

## Working on UI with the help of streamlit
st.title("AI Blog Content Assistant...🤖")
st.header("Create High-Quality Blog Content Without Breaking the Bank")

st.subheader('Title Generation') # Display a subheader for the title generation section
topic_expander = st.expander("Input the topic") # Create an expander for topic input

# Create a content block within the topic expander
with topic_expander:
    topic_name = st.text_input("", key="topic_name") # Get user input for the topic name
    submit_topic = st.button('Submit topic') # Button for submitting the topic

if submit_topic: # Handle button click (submit_topic)
    title_selection_text = '' # Initialize an empty string to store title suggestions
    title_suggestion_str = title_suggestion_chain.invoke({topic_name}) # Generate titles using the title suggestion chain
    for sentence in title_suggestion_str.split('\n'): 
        title_selection_text += (sentence.strip() + '\n') # Clean up each sentence and add it to the selection text
    st.text(title_selection_text) # Display the generated title suggestions


st.subheader('Blog Generation') # Display a subheader for the blog generation section
title_expander = st.expander("Input the title") # Create an expander for title input


with title_expander: # Create a content block within the title expander
    title_of_the_blog = st.text_input("", key="title_of_the_blog") # Get user input for the blog title
    num_of_words = st.slider('Number of Words', min_value=100, max_value=1000, step=50) # Slider for selecting the desired number of words


    if 'keywords' not in st.session_state: # Manage keyword list in session state
        st.session_state['keywords'] = []  # Initialize empty list on first run
    keyword_input = st.text_input("Enter a keyword:") # Input field for adding keywords
    keyword_button = st.button("Add Keyword") # Button to add keyword to the list
    if keyword_button: # Handle button click for adding keyword
        st.session_state['keywords'].append(keyword_input) # Add the keyword to the session state list
        st.session_state['keyword_input'] = "" # Clear the keyword input field after adding
        for keyword in st.session_state['keywords']:  # Display the current list of keywords
            # Inline styling for displaying keywords
            st.write(f"<div style='display: inline-block; background-color: lightgray; padding: 5px; margin: 5px;'>{keyword}</div>", unsafe_allow_html=True)

    # Button to submit the information for content generation
    submit_title = st.button('Submit Info')

if submit_title: # Handle button click for submitting information
    formatted_keywords = []
    for i in st.session_state['keywords']: # Process and format keywords
        if len(i) > 0:
            formatted_keywords.append(i.lstrip('0123456789 : ').strip('"').strip("'"))  
    formatted_keywords = ', '.join(formatted_keywords)

    st.subheader(title_of_the_blog) # Display the blog title as a subheader
    st.write(title_chain.invoke({'title': title_of_the_blog, 'keywords': formatted_keywords, 'blog_length':num_of_words})) # Generate and display the blog content using the title chain


