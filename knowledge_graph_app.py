import os
import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components
from urllib.parse import unquote
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
from openai import OpenAI

# Set page configuration
st.set_page_config(layout="wide")

# Fetch the OpenAI API key from Streamlit secrets
api_key = st.secrets["OPENAI_API_KEY"]

# Create the OpenAI client using the secret API key
client = OpenAI(api_key=api_key)

# api_key = "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"

# Create the OpenAI client using the API key
client = OpenAI(api_key=api_key)

# Initialize session state for graph data
if 'nodes' not in st.session_state:
    st.session_state['nodes'] = []
    st.session_state['edges'] = []

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

if 'highlighted_path' not in st.session_state:
    st.session_state['highlighted_path'] = []

# Define subjects, subfields, and relationships
fields = {
    'Algebra': ['Linear Algebra', 'Matrix Algebra', 'Abstract Algebra', 
                'Commutative Algebra', 'Algebraic Number Theory', 
                'Algebraic Geometry', 'Differential Algebra', 
                'Homological Algebra', 'Boolean Algebra'],
    'Calculus': ['Differential Calculus', 'Integral Calculus', 'Multivariable Calculus', 
                 'Limits', 'Derivatives', 'Integrals'],
    'Statistics': ['Descriptive Statistics', 'Inferential Statistics', 'Probability Theory', 
                   'Hypothesis Testing', 'Regression Analysis'],
    'Computer Science': ['Data Structures', 'Algorithms', 'Databases', 
                         'Machine Learning', 'Networks', 'Operating Systems'],
    'Deep Learning': ['Neural Networks', 'Convolutional Networks', 'Recurrent Networks', 
                      'Transformers', 'Generative Models']
}

# Define relationships between fields
relationships = {
    ('Algebra', 'Calculus'): 'Foundational',
    ('Calculus', 'Statistics'): 'Analytical',
    ('Statistics', 'Machine Learning'): 'Core Concept',
    ('Computer Science', 'Deep Learning'): 'Application',
    ('Algebra', 'Computer Science'): 'Data Structures',
}

# Function to create the "Brain" knowledge network with subjects, subfields, and relationships
def add_brain_network(net, learning_path=None):
    for field, subfields in fields.items():
        net.add_node(field, label=field, color="#fe4880", size=30)

        for subfield in subfields:
            node_color = "#ffa500" if learning_path and subfield in learning_path else "#ffca7d"
            node_size = 40 if learning_path and subfield in learning_path else 20
            net.add_node(subfield, label=subfield, color=node_color, size=node_size)
            net.add_edge(field, subfield)

    for (src, dst), rel_label in relationships.items():
        net.add_edge(src, dst, label=rel_label, color="#3b76e2", width=2)

# Function to extract suggested nodes from GPT-4 response
def extract_suggested_nodes(response):
    all_subfields = [sub for subs in fields.values() for sub in subs]
    suggested_nodes = [node for node in all_subfields if node in response]
    return suggested_nodes

# Function to render the Pyvis graph in Streamlit with a highlighted learning path
def display_network():
    net = Network(notebook=False, height="600px", width="100%", bgcolor="#f0f0f0", font_color="black")
    add_brain_network(net, learning_path=st.session_state['highlighted_path'])
    net.save_graph('pyvis_graph.html')
    HtmlFile = open('pyvis_graph.html', 'r', encoding='utf-8')
    source_code = HtmlFile.read()
    components.html(source_code, height=600)

# Define the agent's state structure
class AgentState(TypedDict):
    student_data: str
    learning_materials: List[str]
    personalized_path: str
    feedback: str
    revision_number: int
    max_revisions: int

# LangGraph workflow setup
def setup_langgraph_workflow():
    builder = StateGraph(AgentState)
    builder.add_node("analyze_student_data", analyze_student_data_node)
    builder.add_node("retrieve_learning_materials", retrieve_learning_materials_node)
    builder.add_node("build_learning_path", build_learning_path_node)
    builder.add_edge("analyze_student_data", "retrieve_learning_materials")
    builder.add_edge("retrieve_learning_materials", "build_learning_path")
    builder.set_entry_point("analyze_student_data")
    return builder.compile()

def analyze_student_data_node(state: AgentState):
    response = "Analyzed student data. Strengths and weaknesses identified."
    return {"analysis": response}

def retrieve_learning_materials_node(state: AgentState):
    response = ["Video on Linear Algebra", "PDF on Matrix Algebra"]
    return {"learning_materials": response}

def build_learning_path_node(state: AgentState):
    response = "Revised learning path with more detailed topics."
    return {"personalized_path": response}

# Function to render the adaptive learning path visualization
# Function to render the adaptive learning path visualization
def render_styled_learning_path(learning_path_list):
    st.markdown(
        """
        <style>
        .learning-container {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            overflow-x: auto;
        }
        .box {
            padding: 15px;
            background-color: #2d2d2d; /* Darker background color */
            color: #ffffff; /* White text color */
            border-radius: 8px;
            font-weight: bold;
            text-align: center;
            min-width: 150px;
            white-space: nowrap;
        }
        .arrow {
            font-size: 24px;
            margin: 0 5px;
            color: #757575;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    html_content = '<div class="learning-container">'
    for i, step in enumerate(learning_path_list):
        html_content += f'<div class="box">{step}</div>'
        if i != len(learning_path_list) - 1:
            html_content += '<div class="arrow">➔</div>'
    html_content += '</div>'
    st.markdown(html_content, unsafe_allow_html=True)
def render_static_community_section():
    st.markdown(
        """
        <style>
        .community-container {
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 10px;
            max-width: 400px;
            margin: 0 auto;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }
        .community-header {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 24px;
            font-weight: bold;
            color: #333;
            margin-bottom: 20px;
        }
        .community-icon {
            width: 16px;
            height: 16px;
            background-color: #ff0077;
            border-radius: 50%;
            display: inline-block;
        }
        .community-card, .community-event {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
        }
        .community-card {
            background-color: #ffca7d;
            color: #333;
        }
        .community-event {
            background-color: #fe4880;
            color: #fff;
        }
        .community-details {
            margin-left: 10px;
        }
        </style>
        
        <div class="community-container">
            <div class="community-header">
                <span>Community</span>
                <div class="community-icon"></div>
            </div>

            <div class="community-card">
                <div>Intro to NLP</div>
                <span class="community-details">👥 40 members</span>
            </div>
            <div class="community-card">
                <div>AI enthusiasts</div>
                <span class="community-details">👥 +99 members</span>
            </div>

            <div class="community-event">
                <div>Getting into the world of NLP</div>
                <span class="community-details">📅 20th Oct 2025 - 19:30 to 21:30</span>
            </div>

            <div class="community-card">
                <div>Influential people</div>
                <span class="community-details">🌐</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# Main function to run the app
def main():
    st.title("Edulga Brain Network & Adaptive Learning Agent")

    # Use columns for side-by-side layout
    col1, col2 = st.columns([2, 1])  # Adjust the width ratio as needed

    with col1:
        # Knowledge Graph Section
        st.header("Knowledge Graph")
        display_network()

        # Adaptive Learning Path Visualization Section
        if st.session_state['highlighted_path']:
            st.subheader("Adaptive Learning Path")
            render_styled_learning_path(st.session_state['highlighted_path'])

    with col2:
        # Chat & Learning Path Generation Section
        st.header("Controls & Chat")
        user_input = st.text_input("Your question:")
        if st.button("Send"):
            if user_input:
                st.session_state['messages'].append({"role": "user", "content": user_input})
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": (
                            "You are an AI tutor within Edulga's comprehensive knowledge network. "
                            "You must suggest a learning path across the following subjects and their subfields: "
                            f"{fields}"
                        )},
                        {"role": "user", "content": user_input}
                    ]
                )
                assistant_message = response.choices[0].message.content
                st.session_state['messages'].append({"role": "assistant", "content": assistant_message})
                suggested_nodes = extract_suggested_nodes(assistant_message)
                st.session_state['highlighted_path'] = suggested_nodes
                render_styled_learning_path(suggested_nodes)



        # Display chat history
        for message in st.session_state['messages']:
            st.write(f"**{message['role'].capitalize()}**: {message['content']}")

        render_static_community_section()  
if __name__ == "__main__":
    main()
