from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from algorithm import G
from database import SessionLocal, create_tables, engine, Base
from models import Node, Workflow  
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

app = FastAPI(title='Workflow')

# Event handler for application startup
@app.on_event("startup")
async def startup_event():
    # Create database tables on startup
    await create_tables()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()  

# Pydantic models for request and response data
class WorkflowCreate(BaseModel):
    id: int
    name: str

class NodeCreate(BaseModel):
    id: int
    type: str
    status: str
    message_text: str
    outgoing_edge: str
    yes_edge: str
    no_edge: str
    workflow_id: int

# Create a new workflow
@app.post("/workflows")
async def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_db)):
    # Create a new Workflow object from request data
    db_workflow = Workflow(**workflow.dict())  
    # Add the new Workflow object to the database session
    db.add(db_workflow)
    # Commit the transaction
    await db.commit()
    # Refresh the object to reflect changes made in the database
    await db.refresh(db_workflow)
    return db_workflow

# Get a workflow by ID
@app.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: int, db: AsyncSession = Depends(get_db)):
    # Execute a select query to fetch the Workflow object by ID
    result = await db.execute(select(Workflow).filter(Workflow.id == workflow_id))
    # Fetch the first row
    workflow = result.fetchone()
    # If no workflow found, raise HTTPException
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    # Convert the Workflow object to a dictionary and return
    return workflow._asdict()

# Update a workflow
@app.put("/workflows/{workflow_id}")
async def update_workflow(workflow_id: int, workflow: WorkflowCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workflow).filter(Workflow.id == workflow_id))
    db_workflow = result.scalars().first()
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    for key, value in workflow.dict().items():
        setattr(db_workflow, key, value)
    await db.commit()
    await db.refresh(db_workflow)
    return db_workflow

# Delete a workflow
@app.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Workflow).filter(Workflow.id == workflow_id))
    db_workflow = result.scalars().first()
    if db_workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(db_workflow)
    await db.commit()
    return {"message": "Workflow deleted successfully"}

# Start a workflow and return the detailed path
@app.post("/workflows/{workflow_id}/start", response_model=list[str])
async def start_workflow(workflow_id: int, db: AsyncSession = Depends(get_db)):
    workflow = await db.execute(select(Workflow).filter(Workflow.id == workflow_id))
    workflow = workflow.scalars().first()
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    detailed_path = []
    current_node = "Start Node"
    detailed_path.append(current_node)

    while current_node != "End Node":
        outgoing_edges = list(G.successors(current_node))

        if len(outgoing_edges) == 1:
            next_node = outgoing_edges[0]
        else:
            if current_node == "ConditionNode1":
                last_message_status = await get_last_message_status(db, workflow_id)
                if last_message_status == "Sent":
                    next_node = "MessageNode2"
                else:
                    next_node = "ConditionNode2"
            elif current_node == "ConditionNode2":
                last_message_status = await get_last_message_status(db, workflow_id)
                if last_message_status == "Open":
                    next_node = "MessageNode3"
                else:
                    next_node = "MessageNode4"
            else:
                next_node = outgoing_edges[0]

        detailed_path.append(next_node)
        current_node = next_node

    return detailed_path

# Get the status of the last message node in the workflow
async def get_last_message_status(db: AsyncSession, workflow_id: int):
    last_message_node = await db.execute(select(Node).filter(Node.workflow_id == workflow_id, Node.type == "Message Node").order_by(Node.id.desc()))
    last_message_node = last_message_node.scalars().first()
    if last_message_node is None:
        raise HTTPException(status_code=404, detail="Message Node not found")
    return last_message_node.status

# Create a new node
@app.post("/nodes")
async def create_node(node: NodeCreate, db: AsyncSession = Depends(get_db)):
    # Validate node type and properties
    if node.type == "Start Node":
        if node.outgoing_edge is None:
            raise HTTPException(status_code=400, detail="Start Node must have an outgoing edge")
        if node.yes_edge is not None or node.no_edge is not None:
            raise HTTPException(status_code=400, detail="Start Node cannot have incoming edges")

    elif node.type == "Message Node":
        valid_statuses = ["pending", "sent", "opened"]
        if node.status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status for Message Node")
        if not node.message_text:
            raise HTTPException(status_code=400, detail="Message Node must have message text")
        if node.outgoing_edge is None:
            raise HTTPException(status_code=400, detail="Message Node must have an outgoing edge")

    elif node.type == "Condition Node":
        if node.yes_edge is None or node.no_edge is None:
            raise HTTPException(status_code=400, detail="Condition Node must have both 'Yes' and 'No' edges")
        if not node.yes_edge and not node.no_edge:
            raise HTTPException(status_code=400, detail="Condition Node must have incoming edges")

    elif node.type == "End Node":
        if not node.yes_edge and not node.no_edge:
            raise HTTPException(status_code=400, detail="End Node must have incoming edges")
        if node.outgoing_edge is not None:
            raise HTTPException(status_code=400, detail="End Node cannot have outgoing edge")

    else:
        raise HTTPException(status_code=400, detail="Invalid node type")

    # Create a new Node object from request data
    db_node = Node(**node.dict())
    # Add the new Node object to the database session
    db.add(db_node)
    # Commit the transaction
    await db.commit()
    # Refresh the object to reflect changes made in the database
    await db.refresh(db_node)
    return db_node

# Get a node by ID
@app.get("/nodes/{node_id}")
async def get_node(node_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Node).filter(Node.id == node_id))
    node = result.scalars().first()
    if node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

# Update a node
@app.put("/nodes/{node_id}")
async def update_node(node_id: int, node: NodeCreate, db: AsyncSession = Depends(get_db)):
    db_node = await db.get(Node, node_id)
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")

    # Validate node type and properties
    if node.type == "Start Node":
        if node.outgoing_edge is None:
            raise HTTPException(status_code=400, detail="Start Node must have an outgoing edge")
        if node.yes_edge is not None or node.no_edge is not None:
            raise HTTPException(status_code=400, detail="Start Node cannot have incoming edges")

    elif node.type == "Message Node":
        if not node.message_text:
            raise HTTPException(status_code=400, detail="Message Node must have message text")
        if node.outgoing_edge is None:
            raise HTTPException(status_code=400, detail="Message Node must have an outgoing edge")
        valid_statuses = ["pending", "sent", "opened"]
        if node.status not in valid_statuses:
            raise HTTPException(status_code=400, detail="Invalid status for Message Node")

    elif node.type == "Condition Node":
        if node.yes_edge is None or node.no_edge is None:
            raise HTTPException(status_code=400, detail="Condition Node must have both 'Yes' and 'No' edges")
        if not node.yes_edge and not node.no_edge:
            raise HTTPException(status_code=400, detail="Condition Node must have incoming edges")

    elif node.type == "End Node":
        if not node.yes_edge and not node.no_edge:
            raise HTTPException(status_code=400, detail="End Node must have incoming edges")
        if node.outgoing_edge is not None:
            raise HTTPException(status_code=400, detail="End Node cannot have outgoing edge")

    else:
        raise HTTPException(status_code=400, detail="Invalid node type")

    for field, value in node.dict().items():
        setattr(db_node, field, value)

    await db.commit()
    await db.refresh(db_node)
    return db_node

# Delete a node
@app.delete("/nodes/{node_id}")
async def delete_node(node_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Node).filter(Node.id == node_id))
    db_node = result.scalars().first()
    if db_node is None:
        raise HTTPException(status_code=404, detail="Node not found")
    db.delete(db_node)
    await db.commit()
    return {"message": "Node deleted successfully"}


