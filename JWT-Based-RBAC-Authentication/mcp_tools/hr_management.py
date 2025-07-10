import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider
from datetime import datetime, timedelta
import uuid
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# Load public key from file
with open("mcp_auth/public.pem", "r") as f:
    public_key = f.read()

auth = BearerAuthProvider(
    public_key=public_key,
    issuer="https://dev-issuer.com",
    audience="my-mcp-server",
)

mcp = FastMCP(name="HRManagementMCP", auth=auth)

# Enums for HR management
class EmploymentStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    ON_LEAVE = "on_leave"
    PROBATION = "probation"

class LeaveType(Enum):
    ANNUAL = "annual"
    SICK = "sick"
    PERSONAL = "personal"
    MATERNITY = "maternity"
    PATERNITY = "paternity"
    UNPAID = "unpaid"

class LeaveStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"

class PerformanceRating(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    AVERAGE = "average"
    BELOW_AVERAGE = "below_average"
    POOR = "poor"

# Data structures for HR management
@dataclass
class EmployeeRecord:
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    department: str
    position: str
    hire_date: datetime
    salary: float
    employment_status: EmploymentStatus
    manager_id: Optional[str]
    location: str
    emergency_contact: str
    emergency_phone: str
    notes: str

@dataclass
class LeaveRequest:
    leave_id: str
    employee_id: str
    leave_type: LeaveType
    start_date: datetime
    end_date: datetime
    total_days: float
    reason: str
    status: LeaveStatus
    approved_by: Optional[str]
    approval_date: Optional[datetime]
    notes: str
    created_date: datetime

@dataclass
class PerformanceReview:
    review_id: str
    employee_id: str
    reviewer_id: str
    review_period: str
    review_date: datetime
    overall_rating: PerformanceRating
    technical_skills: int
    communication: int
    teamwork: int
    leadership: int
    goals_achieved: List[str]
    areas_for_improvement: List[str]
    next_period_goals: List[str]
    comments: str

# Sample data
EMPLOYEE_RECORDS = {
    "EMP-001": EmployeeRecord(
        employee_id="EMP-001",
        first_name="John",
        last_name="Smith",
        email="john.smith@company.com",
        phone="+1-555-0101",
        department="Engineering",
        position="Senior Software Engineer",
        hire_date=datetime(2022, 3, 15),
        salary=85000.0,
        employment_status=EmploymentStatus.ACTIVE,
        manager_id="EMP-005",
        location="San Francisco",
        emergency_contact="Jane Smith",
        emergency_phone="+1-555-0102",
        notes="Excellent team player"
    ),
    "EMP-002": EmployeeRecord(
        employee_id="EMP-002",
        first_name="Sarah",
        last_name="Johnson",
        email="sarah.johnson@company.com",
        phone="+1-555-0201",
        department="Marketing",
        position="Marketing Manager",
        hire_date=datetime(2021, 8, 10),
        salary=75000.0,
        employment_status=EmploymentStatus.ACTIVE,
        manager_id="EMP-006",
        location="New York",
        emergency_contact="Mike Johnson",
        emergency_phone="+1-555-0202",
        notes="Creative and results-driven"
    )
}

LEAVE_REQUESTS = {
    "LEAVE-001": LeaveRequest(
        leave_id="LEAVE-001",
        employee_id="EMP-001",
        leave_type=LeaveType.ANNUAL,
        start_date=datetime(2024, 2, 15),
        end_date=datetime(2024, 2, 20),
        total_days=5.0,
        reason="Family vacation",
        status=LeaveStatus.APPROVED,
        approved_by="EMP-005",
        approval_date=datetime(2024, 1, 25),
        notes="Approved - good timing",
        created_date=datetime(2024, 1, 20)
    )
}

PERFORMANCE_REVIEWS = {
    "REVIEW-001": PerformanceReview(
        review_id="REVIEW-001",
        employee_id="EMP-001",
        reviewer_id="EMP-005",
        review_period="Q4 2023",
        review_date=datetime(2024, 1, 15),
        overall_rating=PerformanceRating.EXCELLENT,
        technical_skills=5,
        communication=4,
        teamwork=5,
        leadership=4,
        goals_achieved=["Led successful project delivery"],
        areas_for_improvement=["Could improve documentation"],
        next_period_goals=["Lead architectural decisions"],
        comments="Outstanding performance"
    )
}

@mcp.tool()
async def add_employee_record(first_name: str = None, last_name: str = None, email: str = None,
                            phone: str = None, department: str = None, position: str = None,
                            hire_date: str = None, salary: float = None, manager_id: Optional[str] = None,
                            location: str = None, emergency_contact: str = None, emergency_phone: str = None,
                            notes: str = "") -> str:
    """Add a new employee record to the HR system.
    
    Args:
        first_name: Employee's first name (REQUIRED)
        last_name: Employee's last name (REQUIRED)
        email: Employee's email address (REQUIRED)
        phone: Employee's phone number (REQUIRED)
        department: Employee's department (REQUIRED)
        position: Employee's job position (REQUIRED)
        hire_date: Employee's hire date (YYYY-MM-DD) (REQUIRED)
        salary: Employee's annual salary (REQUIRED)
        manager_id: ID of the employee's manager (optional)
        location: Employee's work location (REQUIRED)
        emergency_contact: Emergency contact name (REQUIRED)
        emergency_phone: Emergency contact phone (REQUIRED)
        notes: Additional notes
        
    Returns:
        Employee ID and confirmation message, or list of missing required fields
    """
    # Validate required fields
    missing_fields = []
    
    if not first_name or first_name.strip() == "":
        missing_fields.append("first_name")
    
    if not last_name or last_name.strip() == "":
        missing_fields.append("last_name")
    
    if not email or email.strip() == "":
        missing_fields.append("email")
    
    if not phone or phone.strip() == "":
        missing_fields.append("phone")
    
    if not department or department.strip() == "":
        missing_fields.append("department")
    
    if not position or position.strip() == "":
        missing_fields.append("position")
    
    if not hire_date or hire_date.strip() == "":
        missing_fields.append("hire_date")
    
    if salary is None or salary <= 0:
        missing_fields.append("salary (must be > 0)")
    
    if not location or location.strip() == "":
        missing_fields.append("location")
    
    if not emergency_contact or emergency_contact.strip() == "":
        missing_fields.append("emergency_contact")
    
    if not emergency_phone or emergency_phone.strip() == "":
        missing_fields.append("emergency_phone")
    
    # If there are missing fields, return detailed feedback
    if missing_fields:
        missing_list = ", ".join(missing_fields)
        return f"❌ EMPLOYEE RECORD CREATION FAILED: Missing required information.\n\nMissing fields: {missing_list}\n\nPlease provide all required information and try again. Required fields are:\n- first_name: Employee's first name\n- last_name: Employee's last name\n- email: Employee's email address\n- phone: Employee's phone number\n- department: Employee's department\n- position: Employee's job position\n- hire_date: Employee's hire date (YYYY-MM-DD format)\n- salary: Employee's annual salary (must be > 0)\n- location: Employee's work location\n- emergency_contact: Emergency contact name\n- emergency_phone: Emergency contact phone"
    
    # Validate date format
    try:
        hire_date_obj = datetime.strptime(hire_date, "%Y-%m-%d")
    except ValueError:
        return "❌ EMPLOYEE RECORD CREATION FAILED: Invalid hire_date format. Please use YYYY-MM-DD format (e.g., 2024-01-15)"
    
    # Check if manager exists if provided
    if manager_id and manager_id not in EMPLOYEE_RECORDS:
        return f"❌ EMPLOYEE RECORD CREATION FAILED: Manager {manager_id} not found"
    
    # Check if email already exists
    for employee in EMPLOYEE_RECORDS.values():
        if employee.email.lower() == email.lower():
            return f"❌ EMPLOYEE RECORD CREATION FAILED: Employee with email {email} already exists"
    
    # Create the employee record
    employee_id = f"EMP-{str(uuid.uuid4())[:8].upper()}"
    
    EMPLOYEE_RECORDS[employee_id] = EmployeeRecord(
        employee_id=employee_id,
        first_name=first_name.strip(),
        last_name=last_name.strip(),
        email=email.strip(),
        phone=phone.strip(),
        department=department.strip(),
        position=position.strip(),
        hire_date=hire_date_obj,
        salary=salary,
        employment_status=EmploymentStatus.ACTIVE,
        manager_id=manager_id,
        location=location.strip(),
        emergency_contact=emergency_contact.strip(),
        emergency_phone=emergency_phone.strip(),
        notes=notes
    )
    
    return f"✅ Employee record {employee_id} successfully created for {first_name} {last_name}"

@mcp.tool()
async def get_employee_records(employee_id: Optional[str] = None, department: Optional[str] = None,
                             status: Optional[str] = None) -> Dict:
    """Get employee records with optional filtering.
    
    Args:
        employee_id: Optional employee ID to filter
        department: Optional department to filter
        status: Optional employment status to filter
        
    Returns:
        Dictionary containing employee information
    """
    if employee_id:
        if employee_id in EMPLOYEE_RECORDS:
            return {"employees": [asdict(EMPLOYEE_RECORDS[employee_id])]}
        else:
            return {"employees": [], "message": f"Employee {employee_id} not found"}
    
    filtered_employees = []
    for employee in EMPLOYEE_RECORDS.values():
        if department and employee.department != department:
            continue
        if status and employee.employment_status.value != status:
            continue
        filtered_employees.append(employee)
    
    return {"employees": [asdict(employee) for employee in filtered_employees]}

@mcp.tool()
async def create_leave_request(employee_id: str = None, leave_type: str = None, start_date: str = None,
                             end_date: str = None, reason: str = None, notes: str = "") -> str:
    """Create a new leave request.
    
    Args:
        employee_id: Employee ID (REQUIRED)
        leave_type: Type of leave (annual, sick, personal, maternity, paternity, unpaid) (REQUIRED)
        start_date: Start date (YYYY-MM-DD) (REQUIRED)
        end_date: End date (YYYY-MM-DD) (REQUIRED)
        reason: Reason for leave (REQUIRED)
        notes: Additional notes
        
    Returns:
        Leave request ID and confirmation message, or list of missing required fields
    """
    # Validate required fields
    missing_fields = []
    
    if not employee_id or employee_id.strip() == "":
        missing_fields.append("employee_id")
    elif employee_id not in EMPLOYEE_RECORDS:
        return f"❌ LEAVE REQUEST CREATION FAILED: Employee {employee_id} not found"
    
    if not leave_type or leave_type.strip() == "":
        missing_fields.append("leave_type")
    
    if not start_date or start_date.strip() == "":
        missing_fields.append("start_date")
    
    if not end_date or end_date.strip() == "":
        missing_fields.append("end_date")
    
    if not reason or reason.strip() == "":
        missing_fields.append("reason")
    
    # If there are missing fields, return detailed feedback
    if missing_fields:
        missing_list = ", ".join(missing_fields)
        return f"❌ LEAVE REQUEST CREATION FAILED: Missing required information.\n\nMissing fields: {missing_list}\n\nPlease provide all required information and try again. Required fields are:\n- employee_id: Employee ID\n- leave_type: Type of leave (annual, sick, personal, maternity, paternity, unpaid)\n- start_date: Start date (YYYY-MM-DD format)\n- end_date: End date (YYYY-MM-DD format)\n- reason: Reason for leave"
    
    # Validate leave type
    valid_leave_types = ["annual", "sick", "personal", "maternity", "paternity", "unpaid"]
    if leave_type not in valid_leave_types:
        return f"❌ LEAVE REQUEST CREATION FAILED: Invalid leave_type. Valid options: {valid_leave_types}"
    
    # Validate date formats
    try:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return "❌ LEAVE REQUEST CREATION FAILED: Invalid date format. Please use YYYY-MM-DD format (e.g., 2024-12-31)"
    
    # Validate that end date is after start date
    if end_date_obj <= start_date_obj:
        return "❌ LEAVE REQUEST CREATION FAILED: End date must be after start date"
    
    # Calculate total days
    total_days = (end_date_obj - start_date_obj).days + 1
    
    # Create the leave request
    leave_id = f"LEAVE-{str(uuid.uuid4())[:8].upper()}"
    
    LEAVE_REQUESTS[leave_id] = LeaveRequest(
        leave_id=leave_id,
        employee_id=employee_id.strip(),
        leave_type=LeaveType(leave_type),
        start_date=start_date_obj,
        end_date=end_date_obj,
        total_days=total_days,
        reason=reason.strip(),
        status=LeaveStatus.PENDING,
        approved_by=None,
        approval_date=None,
        notes=notes,
        created_date=datetime.now()
    )
    
    return f"✅ Leave request {leave_id} successfully created for {total_days} days"

@mcp.tool()
async def get_hr_summary() -> Dict:
    """Get a summary of HR activities.
        
    Returns:
        Dictionary containing HR summary statistics
    """
    total_employees = len(EMPLOYEE_RECORDS)
    active_employees = len([e for e in EMPLOYEE_RECORDS.values() if e.employment_status == EmploymentStatus.ACTIVE])
    
    total_leave_requests = len(LEAVE_REQUESTS)
    pending_leave_requests = len([l for l in LEAVE_REQUESTS.values() if l.status == LeaveStatus.PENDING])
    approved_leave_requests = len([l for l in LEAVE_REQUESTS.values() if l.status == LeaveStatus.APPROVED])
    
    total_reviews = len(PERFORMANCE_REVIEWS)
    excellent_reviews = len([r for r in PERFORMANCE_REVIEWS.values() if r.overall_rating == PerformanceRating.EXCELLENT])
    
    return {
        "summary": {
            "total_employees": total_employees,
            "active_employees": active_employees,
            "total_leave_requests": total_leave_requests,
            "pending_leave_requests": pending_leave_requests,
            "approved_leave_requests": approved_leave_requests,
            "total_reviews": total_reviews,
            "excellent_reviews": excellent_reviews
        }
    }

if __name__ == "__main__":
    mcp.run(transport="sse", port=8001)
