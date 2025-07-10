import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP, Context
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.server.auth.providers.bearer import RSAKeyPair
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
from typing import List, Dict, Optional
from enum import Enum

# Load public key from file
with open("mcp_auth/public.pem", "r") as f:
    public_key = f.read()

auth = BearerAuthProvider(
    public_key=public_key,
    issuer="https://dev-issuer.com",
    audience="my-mcp-server",
)

mcp = FastMCP(name="ProjectManagementMCP", auth=auth)

# Enums for project management
class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskState(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProjectPhase(Enum):
    PLANNING = "planning"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MAINTENANCE = "maintenance"

# Data structures for project management
@dataclass
class ProjectTask:
    task_id: str
    project_id: str
    task_name: str
    description: str
    assigned_to: str
    assignee_name: str
    priority: TaskPriority
    state: TaskState
    estimated_hours: float
    actual_hours: float
    start_date: datetime
    due_date: datetime
    dependencies: List[str]
    tags: List[str]
    progress_percentage: float
    notes: str

@dataclass
class ProjectMilestone:
    milestone_id: str
    project_id: str
    milestone_name: str
    description: str
    target_date: datetime
    achieved_date: Optional[datetime]
    status: str  # pending, achieved, delayed
    deliverables: List[str]
    notes: str

@dataclass
class TeamMember:
    member_id: str
    name: str
    role: str
    email: str
    skills: List[str]
    availability_hours: float
    current_projects: List[str]
    join_date: datetime

# Sample data
PROJECT_TASKS = {
    "TASK-001": ProjectTask(
        task_id="TASK-001",
        project_id="PROJ-001",
        task_name="Database Schema Design",
        description="Design and implement the core database schema for the e-commerce platform",
        assigned_to="DEV-001",
        assignee_name="Sarah Johnson",
        priority=TaskPriority.HIGH,
        state=TaskState.COMPLETED,
        estimated_hours=16.0,
        actual_hours=14.5,
        start_date=datetime(2024, 1, 10),
        due_date=datetime(2024, 1, 20),
        dependencies=[],
        tags=["database", "backend"],
        progress_percentage=100.0,
        notes="Completed ahead of schedule"
    ),
    "TASK-002": ProjectTask(
        task_id="TASK-002",
        project_id="PROJ-001",
        task_name="User Authentication API",
        description="Implement JWT-based authentication system with role-based access control",
        assigned_to="DEV-002",
        assignee_name="Mike Chen",
        priority=TaskPriority.CRITICAL,
        state=TaskState.IN_PROGRESS,
        estimated_hours=24.0,
        actual_hours=18.0,
        start_date=datetime(2024, 1, 15),
        due_date=datetime(2024, 1, 30),
        dependencies=["TASK-001"],
        tags=["api", "security", "backend"],
        progress_percentage=75.0,
        notes="Core functionality complete, working on edge cases"
    ),
    "TASK-003": ProjectTask(
        task_id="TASK-003",
        project_id="PROJ-002",
        task_name="Frontend Dashboard Design",
        description="Create responsive dashboard UI with React components",
        assigned_to="DEV-003",
        assignee_name="Emily Rodriguez",
        priority=TaskPriority.MEDIUM,
        state=TaskState.TODO,
        estimated_hours=20.0,
        actual_hours=0.0,
        start_date=datetime(2024, 2, 1),
        due_date=datetime(2024, 2, 15),
        dependencies=[],
        tags=["frontend", "ui", "react"],
        progress_percentage=0.0,
        notes="Waiting for design mockups"
    )
}

PROJECT_MILESTONES = {
    "MIL-001": ProjectMilestone(
        milestone_id="MIL-001",
        project_id="PROJ-001",
        milestone_name="Backend Foundation Complete",
        description="Core backend services and database are operational",
        target_date=datetime(2024, 1, 25),
        achieved_date=datetime(2024, 1, 23),
        status="achieved",
        deliverables=["Database Schema", "Authentication API", "User Management"],
        notes="Completed 2 days ahead of schedule"
    ),
    "MIL-002": ProjectMilestone(
        milestone_id="MIL-002",
        project_id="PROJ-001",
        milestone_name="API Integration Complete",
        description="All backend APIs are integrated and tested",
        target_date=datetime(2024, 2, 10),
        achieved_date=None,
        status="pending",
        deliverables=["Product API", "Order API", "Payment API"],
        notes="On track for completion"
    )
}

TEAM_MEMBERS = {
    "DEV-001": TeamMember(
        member_id="DEV-001",
        name="Sarah Johnson",
        role="Senior Backend Developer",
        email="sarah.johnson@company.com",
        skills=["Python", "PostgreSQL", "Django", "Docker"],
        availability_hours=40.0,
        current_projects=["PROJ-001"],
        join_date=datetime(2023, 3, 15)
    ),
    "DEV-002": TeamMember(
        member_id="DEV-002",
        name="Mike Chen",
        role="Full Stack Developer",
        email="mike.chen@company.com",
        skills=["JavaScript", "React", "Node.js", "MongoDB"],
        availability_hours=35.0,
        current_projects=["PROJ-001", "PROJ-002"],
        join_date=datetime(2023, 6, 1)
    ),
    "DEV-003": TeamMember(
        member_id="DEV-003",
        name="Emily Rodriguez",
        role="Frontend Developer",
        email="emily.rodriguez@company.com",
        skills=["React", "TypeScript", "CSS", "Figma"],
        availability_hours=40.0,
        current_projects=["PROJ-002"],
        join_date=datetime(2023, 9, 10)
    )
}

@mcp.tool()
async def create_project_task(project_id: str = None, task_name: str = None, description: str = None,
                            assigned_to: str = None, assignee_name: str = None, priority: str = "medium",
                            estimated_hours: float = None, due_date: str = None, tags: List[str] = None,
                            notes: str = "") -> str:
    """Create a new project task.
    
    Args:
        project_id: Project identifier (REQUIRED)
        task_name: Name of the task (REQUIRED)
        description: Detailed description (REQUIRED)
        assigned_to: ID of the assigned team member (REQUIRED)
        assignee_name: Name of the assigned team member (REQUIRED)
        priority: Priority level (low, medium, high, critical) (default: medium)
        estimated_hours: Estimated hours to complete (REQUIRED)
        due_date: Due date (YYYY-MM-DD) (REQUIRED)
        tags: List of tags for categorization
        notes: Additional notes
        
    Returns:
        Task ID and confirmation message, or list of missing required fields
    """
    # Validate required fields
    missing_fields = []
    
    if not project_id or project_id.strip() == "":
        missing_fields.append("project_id")
    
    if not task_name or task_name.strip() == "":
        missing_fields.append("task_name")
    
    if not description or description.strip() == "":
        missing_fields.append("description")
    
    if not assigned_to or assigned_to.strip() == "":
        missing_fields.append("assigned_to")
    
    if not assignee_name or assignee_name.strip() == "":
        missing_fields.append("assignee_name")
    
    if estimated_hours is None or estimated_hours <= 0:
        missing_fields.append("estimated_hours (must be > 0)")
    
    if not due_date or due_date.strip() == "":
        missing_fields.append("due_date")
    
    # If there are missing fields, return detailed feedback
    if missing_fields:
        missing_list = ", ".join(missing_fields)
        return f"❌ TASK CREATION FAILED: Missing required information.\n\nMissing fields: {missing_list}\n\nPlease provide all required information and try again. Required fields are:\n- project_id: Project identifier\n- task_name: Name of the task\n- description: Detailed description\n- assigned_to: ID of the assigned team member\n- assignee_name: Name of the assigned team member\n- estimated_hours: Estimated hours to complete (must be > 0)\n- due_date: Due date (YYYY-MM-DD format)"
    
    # Validate priority level
    valid_priority_levels = ["low", "medium", "high", "critical"]
    if priority not in valid_priority_levels:
        return f"❌ TASK CREATION FAILED: Invalid priority. Valid options: {valid_priority_levels}"
    
    # Validate date format
    try:
        due_date_obj = datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        return "❌ TASK CREATION FAILED: Invalid due_date format. Please use YYYY-MM-DD format (e.g., 2024-12-31)"
    
    # Create the task
    task_id = f"TASK-{str(uuid.uuid4())[:8].upper()}"
    
    PROJECT_TASKS[task_id] = ProjectTask(
        task_id=task_id,
        project_id=project_id.strip(),
        task_name=task_name.strip(),
        description=description.strip(),
        assigned_to=assigned_to.strip(),
        assignee_name=assignee_name.strip(),
        priority=TaskPriority(priority),
        state=TaskState.TODO,
        estimated_hours=estimated_hours,
        actual_hours=0.0,
        start_date=datetime.now(),
        due_date=due_date_obj,
        dependencies=[],
        tags=tags or [],
        progress_percentage=0.0,
        notes=notes
    )
    
    return f"✅ Task {task_id} successfully created for {task_name} with {estimated_hours} estimated hours"

@mcp.tool()
async def get_project_tasks(task_id: Optional[str] = None, project_id: Optional[str] = None,
                          state: Optional[str] = None, assigned_to: Optional[str] = None) -> Dict:
    """Get project tasks with optional filtering.
    
    Args:
        task_id: Optional task ID to filter
        project_id: Optional project ID to filter
        state: Optional state to filter (todo, in_progress, review, completed, cancelled)
        assigned_to: Optional assignee ID to filter
        
    Returns:
        Dictionary containing task information
    """
    if task_id:
        if task_id in PROJECT_TASKS:
            return {"tasks": [asdict(PROJECT_TASKS[task_id])]}
        else:
            return {"tasks": [], "message": f"Task {task_id} not found"}
    
    filtered_tasks = []
    for task in PROJECT_TASKS.values():
        if project_id and task.project_id != project_id:
            continue
        if state and task.state.value != state:
            continue
        if assigned_to and task.assigned_to != assigned_to:
            continue
        filtered_tasks.append(task)
    
    return {"tasks": [asdict(task) for task in filtered_tasks]}

@mcp.tool()
async def update_task_state(task_id: str, new_state: str, actual_hours: Optional[float] = None,
                          progress_percentage: Optional[float] = None, notes: str = "") -> str:
    """Update the state of a project task.
    
    Args:
        task_id: Task ID to update
        new_state: New state (todo, in_progress, review, completed, cancelled)
        actual_hours: Optional actual hours worked
        progress_percentage: Optional progress percentage (0-100)
        notes: Optional notes about the update
        
    Returns:
        Confirmation message
    """
    if task_id not in PROJECT_TASKS:
        return f"Task {task_id} not found"
    
    try:
        state_enum = TaskState(new_state)
    except ValueError:
        return f"Invalid state. Valid options: {[s.value for s in TaskState]}"
    
    task = PROJECT_TASKS[task_id]
    old_state = task.state.value
    task.state = state_enum
    
    if actual_hours is not None:
        task.actual_hours = actual_hours
    
    if progress_percentage is not None:
        if progress_percentage < 0 or progress_percentage > 100:
            return "Progress percentage must be between 0 and 100"
        task.progress_percentage = progress_percentage
    
    if notes:
        task.notes = notes
    
    return f"✅ Task {task_id} state updated from {old_state} to {new_state}"

@mcp.tool()
async def get_task_progress(task_id: str) -> str:
    """Get the current progress of a task.
    
    Args:
        task_id: Task ID to check
        
    Returns:
        Current task progress and details
    """
    if task_id not in PROJECT_TASKS:
        return f"Task {task_id} not found"
    
    task = PROJECT_TASKS[task_id]
    
    progress_info = {
        "task_id": task_id,
        "task_name": task.task_name,
        "state": task.state.value,
        "progress_percentage": task.progress_percentage,
        "estimated_hours": task.estimated_hours,
        "actual_hours": task.actual_hours,
        "assignee": task.assignee_name,
        "due_date": task.due_date.strftime("%Y-%m-%d"),
        "priority": task.priority.value
    }
    
    return str(progress_info)

@mcp.tool()
async def get_overdue_tasks() -> Dict:
    """Get tasks that are overdue.
    
    Returns:
        Dictionary containing overdue tasks
    """
    overdue_tasks = []
    current_date = datetime.now()
    
    for task in PROJECT_TASKS.values():
        if task.due_date < current_date and task.state != TaskState.COMPLETED:
            overdue_tasks.append(asdict(task))
    
    return {
        "overdue_tasks": overdue_tasks,
        "count": len(overdue_tasks)
    }

@mcp.tool()
async def get_project_summary() -> Dict:
    """Get a summary of project activities.
    
    Returns:
        Dictionary containing project summary statistics
    """
    total_tasks = len(PROJECT_TASKS)
    completed_tasks = len([t for t in PROJECT_TASKS.values() if t.state == TaskState.COMPLETED])
    in_progress_tasks = len([t for t in PROJECT_TASKS.values() if t.state == TaskState.IN_PROGRESS])
    todo_tasks = len([t for t in PROJECT_TASKS.values() if t.state == TaskState.TODO])
    
    total_estimated_hours = sum(t.estimated_hours for t in PROJECT_TASKS.values())
    total_actual_hours = sum(t.actual_hours for t in PROJECT_TASKS.values())
    
    return {
        "summary": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "todo_tasks": todo_tasks,
            "total_estimated_hours": total_estimated_hours,
            "total_actual_hours": total_actual_hours,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
    }

if __name__ == "__main__":
    mcp.run(transport="sse", port=8002)
