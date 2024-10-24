from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import streamlit as st
import json

# Define the agent's state structure
class AgentState(TypedDict):
    student_data: str
    learning_materials: List[str]
    personalized_path: str
    feedback: str
    revision_number: int
    max_revisions: int

# Define node functions for the adaptive learning agent
def analyze_student_data_node(state: AgentState):
    # Analyze student data and update the student_data field
    analysis = f"Analyzed data: {state['student_data']}."
    state["student_data"] += " | Analysis complete"
    return {
        "student_data": state["student_data"],  # Ensure update to prevent error
        "personalized_path": state["personalized_path"]
    }

def retrieve_learning_materials_node(state: AgentState):
    # Mock retrieval of learning materials
    learning_materials = [
        "Video on Linear Algebra",
        "PDF on Matrix Algebra",
        "Exercises on Abstract Algebra"
    ]
    return {
        "learning_materials": learning_materials,  # Ensure update to prevent error
        "student_data": state["student_data"]
    }

def build_learning_path_node(state: AgentState):
    # Build the learning path based on student data
    learning_path = "Linear Algebra -> Matrix Algebra -> Abstract Algebra"
    return {
        "personalized_path": learning_path,  # Ensure update to prevent error
        "learning_materials": state["learning_materials"]
    }

def collect_feedback_node(state: AgentState):
    # Mock feedback based on personalized path
    feedback = "Focus more on Abstract Algebra."
    return {
        "feedback": feedback,  # Ensure update to prevent error
        "revision_number": state["revision_number"] + 1  # Increment revision
    }

# Setup LangGraph workflow
def setup_langgraph_workflow():
    builder = StateGraph(AgentState)
    builder.add_node("analyze_student_data", analyze_student_data_node)
    builder.add_node("retrieve_learning_materials", retrieve_learning_materials_node)
    builder.add_node("build_learning_path", build_learning_path_node)
    builder.add_node("collect_feedback", collect_feedback_node)

    builder.add_edge("analyze_student_data", "retrieve_learning_materials")
    builder.add_edge("retrieve_learning_materials", "build_learning_path")
    builder.add_edge("build_learning_path", "collect_feedback")

    builder.set_entry_point("analyze_student_data")
    return builder.compile()

# Adaptive Learning Agent Interface
def adaptive_learning_agent_interface():
    st.header("Adaptive Learning Agent")

    # Input for student data
    student_data = st.text_area(
        "Enter student performance data:",
        placeholder="Provide plain text or JSON-like format for student performance data."
    )

    # Example input for testing
    example_input = {
        "student_data": "Strong in Linear Algebra and Matrix Algebra. Weak in Abstract Algebra.",
        "learning_materials": [],
        "personalized_path": "",
        "feedback": "",
        "revision_number": 1,
        "max_revisions": 2
    }

    if st.button("Use Example Input"):
        student_data = json.dumps(example_input)

    if st.button("Start Adaptive Learning") and student_data:
        try:
            # Convert string input to dictionary if in JSON format
            if student_data.startswith("{"):
                initial_state = json.loads(student_data)
            else:
                initial_state = {
                    "student_data": student_data,
                    "learning_materials": [],
                    "personalized_path": "",
                    "feedback": "",
                    "revision_number": 1,
                    "max_revisions": 2,
                }

            # Ensure required fields are present
            for key in AgentState.__annotations__.keys():
                if key not in initial_state:
                    initial_state[key] = "" if isinstance(initial_state[key], str) else []

            # Setup and run the workflow
            graph = setup_langgraph_workflow()
            final_state = None

            for state in graph.stream(initial_state):
                st.write(state)
                final_state = state

            if final_state and "personalized_path" in final_state:
                st.subheader("Personalized Learning Path")
                st.write(final_state["personalized_path"])

        except Exception as e:
            st.error(f"Error: {e}")

# Main function to run the Streamlit app
def main():
    st.title("Edulga Adaptive Learning Agent")
    adaptive_learning_agent_interface()

if __name__ == "__main__":
    main()
