# WorkflowApi
This project is a Workflow API built with FastAPI, networkX, pytest, Pydantic, and SQLAlchemy.

## Node Types

- **Start Node**: Can only have one outgoing edge and no incoming edges.
- **Message Node**: Can have statuses: pending, sent, opened. Must have a message text. Can only have one outgoing edge. Can have multiple incoming edges.
- **Condition Node**: Can have two outgoing edges: Yes and No. If the condition is true, the path through the Yes edge is chosen, if false – through the No edge. Can have multiple incoming edges. Can be connected to Message Node or another Condition Node, but the condition should be calculated only based on the status of the last executed Message Node.
- **End Node**: This is the final node for the workflow. Can have multiple incoming edges. Cannot have outgoing edges.

## API Features

- **Workflow CRUD**: Create, Update, Delete Workflow.
- **Node Creation**: Endpoint for adding new nodes (Start, Message, Condition, End) to the workflow.
- **Node Configuration**: Ability to change parameters for nodes or delete nodes.
- **Workflow Execution**: Endpoint for initializing and starting the selected Workflow, returning a detailed path from Start to End Node. Or an error that it is not possible to get from start to end node with a description of the reason.

## Technologies

- **networkX**: For graph construction.
- **pytest**: For writing test cases and testing the algorithm and API.
- **FastAPI**: For building the API.
- **Pydantic**: For data validation.
- **SQLAlchemy or tortoiseorm**: For database operations.

## Getting Started

1. Clone the repository:
    ```
    git clone https://github.com/trekfest/WorkflowApi.git
    ```
2. Install the dependencies:
    ```
    pip install -r requirements.txt
    ```
3. Run the application:
    ```
    uvicorn main:app --reload
    ```
4. Access the API documentation:
    ```
    http://localhost:8000/docs
    ```

5.  Run the tests:
    ```
    pytest test.py
    ```