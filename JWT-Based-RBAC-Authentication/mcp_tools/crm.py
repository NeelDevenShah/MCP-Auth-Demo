import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider
from datetime import datetime, timedelta
import uuid
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# Load public key from file
with open("mcp_auth/public.pem", "r") as f:
    public_key = f.read()

auth = BearerAuthProvider(
    public_key=public_key,
    issuer="https://dev-issuer.com",
    audience="my-mcp-server",
)

mcp = FastMCP(name="CRMMCP", auth=auth)

# Data structures for customer relationship management
@dataclass
class CustomerProfile:
    customer_id: str
    company_name: str
    contact_person: str
    email_address: str
    phone_number: str
    industry: str
    company_size: str
    annual_revenue: float
    lead_source: str
    status: str  # prospect, active, inactive, churned
    created_date: datetime
    last_contact_date: datetime
    notes: str

@dataclass
class InteractionRecord:
    interaction_id: str
    customer_id: str
    interaction_type: str  # call, email, meeting, demo, proposal
    subject: str
    description: str
    outcome: str  # positive, negative, neutral, follow_up
    next_action: str
    interaction_date: datetime
    created_by: str
    duration_minutes: Optional[int]
    notes: str

@dataclass
class SalesOpportunity:
    opportunity_id: str
    customer_id: str
    opportunity_name: str
    description: str
    value: float
    probability: float  # 0-100
    stage: str  # prospecting, qualification, proposal, negotiation, closed_won, closed_lost
    expected_close_date: datetime
    created_date: datetime
    assigned_to: str
    lead_source: str
    notes: str

@dataclass
class DealPipeline:
    deal_id: str
    opportunity_id: str
    deal_value: float
    deal_stage: str  # initial_contact, needs_analysis, proposal, negotiation, closed
    probability_percentage: float
    expected_revenue: float
    close_date: datetime
    created_date: datetime
    last_updated: datetime
    notes: str

# Sample data
CUSTOMER_PROFILES = {
    "CUST-001": CustomerProfile(
        customer_id="CUST-001",
        company_name="TechCorp Solutions",
        contact_person="John Smith",
        email_address="john.smith@techcorp.com",
        phone_number="+1-555-0123",
        industry="Technology",
        company_size="100-500 employees",
        annual_revenue=5000000.0,
        lead_source="Website",
        status="active",
        created_date=datetime(2023, 6, 15),
        last_contact_date=datetime(2024, 1, 20),
        notes="Interested in enterprise software solutions"
    ),
    "CUST-002": CustomerProfile(
        customer_id="CUST-002",
        company_name="Global Manufacturing Inc",
        contact_person="Sarah Johnson",
        email_address="sarah.johnson@gmi.com",
        phone_number="+1-555-0456",
        industry="Manufacturing",
        company_size="500-1000 employees",
        annual_revenue=25000000.0,
        lead_source="Trade Show",
        status="prospect",
        created_date=datetime(2024, 1, 10),
        last_contact_date=datetime(2024, 1, 25),
        notes="Looking for automation solutions"
    ),
    "CUST-003": CustomerProfile(
        customer_id="CUST-003",
        company_name="StartupXYZ",
        contact_person="Mike Chen",
        email_address="mike.chen@startupxyz.com",
        phone_number="+1-555-0789",
        industry="SaaS",
        company_size="10-50 employees",
        annual_revenue=500000.0,
        lead_source="Referral",
        status="active",
        created_date=datetime(2023, 9, 20),
        last_contact_date=datetime(2024, 1, 28),
        notes="Growing rapidly, needs scalable solutions"
    )
}

INTERACTION_RECORDS = {
    "INT-001": InteractionRecord(
        interaction_id="INT-001",
        customer_id="CUST-001",
        interaction_type="meeting",
        subject="Product Demo",
        description="Demonstrated our enterprise software platform to the IT team",
        outcome="positive",
        next_action="Send proposal",
        interaction_date=datetime(2024, 1, 20),
        created_by="sales_rep_1",
        duration_minutes=60,
        notes="Team was impressed with the features"
    ),
    "INT-002": InteractionRecord(
        interaction_id="INT-002",
        customer_id="CUST-002",
        interaction_type="call",
        subject="Initial Contact",
        description="Cold call to introduce our services",
        outcome="neutral",
        next_action="Follow up with email",
        interaction_date=datetime(2024, 1, 25),
        created_by="sales_rep_2",
        duration_minutes=15,
        notes="Contact person was busy, will try again next week"
    ),
    "INT-003": InteractionRecord(
        interaction_id="INT-003",
        customer_id="CUST-003",
        interaction_type="email",
        subject="Pricing Inquiry",
        description="Responded to pricing questions about our SaaS platform",
        outcome="positive",
        next_action="Schedule technical review",
        interaction_date=datetime(2024, 1, 28),
        created_by="sales_rep_1",
        duration_minutes=None,
        notes="Customer is ready to move forward"
    )
}

SALES_OPPORTUNITIES = {
    "OPP-001": SalesOpportunity(
        opportunity_id="OPP-001",
        customer_id="CUST-001",
        opportunity_name="Enterprise Software License",
        description="Multi-year enterprise software license for 500 users",
        value=250000.0,
        probability=75.0,
        stage="negotiation",
        expected_close_date=datetime(2024, 3, 15),
        created_date=datetime(2023, 12, 1),
        assigned_to="sales_rep_1",
        lead_source="Website",
        notes="High priority deal, executive sponsor identified"
    ),
    "OPP-002": SalesOpportunity(
        opportunity_id="OPP-002",
        customer_id="CUST-002",
        opportunity_name="Automation Solution",
        description="Manufacturing automation software implementation",
        value=180000.0,
        probability=40.0,
        stage="qualification",
        expected_close_date=datetime(2024, 4, 30),
        created_date=datetime(2024, 1, 15),
        assigned_to="sales_rep_2",
        lead_source="Trade Show",
        notes="Need to understand technical requirements better"
    ),
    "OPP-003": SalesOpportunity(
        opportunity_id="OPP-003",
        customer_id="CUST-003",
        opportunity_name="SaaS Platform Subscription",
        description="Annual subscription for our SaaS platform",
        value=50000.0,
        probability=90.0,
        stage="proposal",
        expected_close_date=datetime(2024, 2, 15),
        created_date=datetime(2024, 1, 20),
        assigned_to="sales_rep_1",
        lead_source="Referral",
        notes="Ready to sign, just waiting for budget approval"
    )
}

DEAL_PIPELINE = {
    "DEAL-001": DealPipeline(
        deal_id="DEAL-001",
        opportunity_id="OPP-001",
        deal_value=250000.0,
        deal_stage="negotiation",
        probability_percentage=75.0,
        expected_revenue=187500.0,
        close_date=datetime(2024, 3, 15),
        created_date=datetime(2023, 12, 1),
        last_updated=datetime(2024, 1, 20),
        notes="Contract terms being finalized"
    ),
    "DEAL-002": DealPipeline(
        deal_id="DEAL-002",
        opportunity_id="OPP-002",
        deal_value=180000.0,
        deal_stage="qualification",
        probability_percentage=40.0,
        expected_revenue=72000.0,
        close_date=datetime(2024, 4, 30),
        created_date=datetime(2024, 1, 15),
        last_updated=datetime(2024, 1, 25),
        notes="Technical requirements gathering in progress"
    )
}

@mcp.tool()
async def get_customer_profiles(customer_id: Optional[str] = None, status: Optional[str] = None,
                              industry: Optional[str] = None) -> Dict:
    """Get customer profiles with optional filtering.
    
    Args:
        customer_id: Optional customer ID to filter
        status: Optional status to filter (prospect, active, inactive, churned)
        industry: Optional industry to filter
        
    Returns:
        Dictionary containing customer profile information
    """
    if customer_id:
        if customer_id in CUSTOMER_PROFILES:
            return {"customers": [asdict(CUSTOMER_PROFILES[customer_id])]}
        else:
            return {"customers": [], "message": f"Customer {customer_id} not found"}
    
    filtered_customers = []
    for customer in CUSTOMER_PROFILES.values():
        if status and customer.status != status:
            continue
        if industry and customer.industry != industry:
            continue
        filtered_customers.append(customer)
    
    return {"customers": [asdict(customer) for customer in filtered_customers]}

@mcp.tool()
async def add_customer_profile(company_name: str = None, contact_person: str = None, email_address: str = None,
                             phone_number: str = None, industry: str = None, company_size: str = None,
                             annual_revenue: float = None, lead_source: str = None, notes: str = "") -> str:
    """Add a new customer profile to the CRM system.
    
    Args:
        company_name: Name of the company (REQUIRED)
        contact_person: Primary contact person (REQUIRED)
        email_address: Contact email address (REQUIRED)
        phone_number: Contact phone number (REQUIRED)
        industry: Industry sector (REQUIRED)
        company_size: Company size category (REQUIRED)
        annual_revenue: Annual revenue in USD (REQUIRED)
        lead_source: Source of the lead (REQUIRED)
        notes: Additional notes
        
    Returns:
        Customer ID and confirmation message, or list of missing required fields
    """
    # Validate required fields
    missing_fields = []
    
    if not company_name or company_name.strip() == "":
        missing_fields.append("company_name")
    
    if not contact_person or contact_person.strip() == "":
        missing_fields.append("contact_person")
    
    if not email_address or email_address.strip() == "":
        missing_fields.append("email_address")
    
    if not phone_number or phone_number.strip() == "":
        missing_fields.append("phone_number")
    
    if not industry or industry.strip() == "":
        missing_fields.append("industry")
    
    if not company_size or company_size.strip() == "":
        missing_fields.append("company_size")
    
    if annual_revenue is None or annual_revenue < 0:
        missing_fields.append("annual_revenue (must be >= 0)")
    
    if not lead_source or lead_source.strip() == "":
        missing_fields.append("lead_source")
    
    # If there are missing fields, return detailed feedback
    if missing_fields:
        missing_list = ", ".join(missing_fields)
        return f"❌ CUSTOMER PROFILE CREATION FAILED: Missing required information.\n\nMissing fields: {missing_list}\n\nPlease provide all required information and try again. Required fields are:\n- company_name: Name of the company\n- contact_person: Primary contact person\n- email_address: Contact email address\n- phone_number: Contact phone number\n- industry: Industry sector\n- company_size: Company size category\n- annual_revenue: Annual revenue in USD (must be >= 0)\n- lead_source: Source of the lead"
    
    # Check if customer already exists (by email)
    for customer in CUSTOMER_PROFILES.values():
        if customer.email_address.lower() == email_address.lower():
            return f"❌ CUSTOMER PROFILE CREATION FAILED: Customer with email {email_address} already exists"
    
    # Create the customer profile
    customer_id = f"CUST-{str(uuid.uuid4())[:8].upper()}"
    
    CUSTOMER_PROFILES[customer_id] = CustomerProfile(
        customer_id=customer_id,
        company_name=company_name.strip(),
        contact_person=contact_person.strip(),
        email_address=email_address.strip(),
        phone_number=phone_number.strip(),
        industry=industry.strip(),
        company_size=company_size.strip(),
        annual_revenue=annual_revenue,
        lead_source=lead_source.strip(),
        status="prospect",
        created_date=datetime.now(),
        last_contact_date=datetime.now(),
        notes=notes
    )
    
    return f"✅ Customer profile {customer_id} successfully created for {company_name}"

@mcp.tool()
async def update_customer_status(customer_id: str, new_status: str, notes: str = "") -> str:
    """Update the status of a customer profile.
    
    Args:
        customer_id: Customer ID to update
        new_status: New status (prospect, active, inactive, churned)
        notes: Optional notes about the status change
        
    Returns:
        Confirmation message
    """
    if customer_id not in CUSTOMER_PROFILES:
        return f"Customer {customer_id} not found"
    
    valid_statuses = ["prospect", "active", "inactive", "churned"]
    if new_status not in valid_statuses:
        return f"Invalid status. Valid options: {valid_statuses}"
    
    customer = CUSTOMER_PROFILES[customer_id]
    old_status = customer.status
    customer.status = new_status
    
    if notes:
        customer.notes = notes
    
    customer.last_contact_date = datetime.now()
    
    return f"✅ Customer {customer_id} status updated from {old_status} to {new_status}"

@mcp.tool()
async def record_interaction(customer_id: str = None, interaction_type: str = None, subject: str = None,
                           description: str = None, outcome: str = None, next_action: str = None,
                           created_by: str = "system", duration_minutes: Optional[int] = None,
                           notes: str = "") -> str:
    """Record a customer interaction.
    
    Args:
        customer_id: Customer ID (REQUIRED)
        interaction_type: Type of interaction (call, email, meeting, demo, proposal) (REQUIRED)
        subject: Subject/title of the interaction (REQUIRED)
        description: Detailed description (REQUIRED)
        outcome: Outcome (positive, negative, neutral, follow_up) (REQUIRED)
        next_action: Next action to take (REQUIRED)
        created_by: User recording the interaction
        duration_minutes: Duration in minutes (optional)
        notes: Additional notes
        
    Returns:
        Interaction ID and confirmation message, or list of missing required fields
    """
    # Validate required fields
    missing_fields = []
    
    if not customer_id or customer_id.strip() == "":
        missing_fields.append("customer_id")
    elif customer_id not in CUSTOMER_PROFILES:
        return f"❌ INTERACTION RECORDING FAILED: Customer {customer_id} not found"
    
    if not interaction_type or interaction_type.strip() == "":
        missing_fields.append("interaction_type")
    
    if not subject or subject.strip() == "":
        missing_fields.append("subject")
    
    if not description or description.strip() == "":
        missing_fields.append("description")
    
    if not outcome or outcome.strip() == "":
        missing_fields.append("outcome")
    
    if not next_action or next_action.strip() == "":
        missing_fields.append("next_action")
    
    # If there are missing fields, return detailed feedback
    if missing_fields:
        missing_list = ", ".join(missing_fields)
        return f"❌ INTERACTION RECORDING FAILED: Missing required information.\n\nMissing fields: {missing_list}\n\nPlease provide all required information and try again. Required fields are:\n- customer_id: Customer ID\n- interaction_type: Type of interaction (call, email, meeting, demo, proposal)\n- subject: Subject/title of the interaction\n- description: Detailed description\n- outcome: Outcome (positive, negative, neutral, follow_up)\n- next_action: Next action to take"
    
    # Validate interaction type
    valid_interaction_types = ["call", "email", "meeting", "demo", "proposal"]
    if interaction_type not in valid_interaction_types:
        return f"❌ INTERACTION RECORDING FAILED: Invalid interaction_type. Valid options: {valid_interaction_types}"
    
    # Validate outcome
    valid_outcomes = ["positive", "negative", "neutral", "follow_up"]
    if outcome not in valid_outcomes:
        return f"❌ INTERACTION RECORDING FAILED: Invalid outcome. Valid options: {valid_outcomes}"
    
    # Create the interaction record
    interaction_id = f"INT-{str(uuid.uuid4())[:8].upper()}"
    
    INTERACTION_RECORDS[interaction_id] = InteractionRecord(
        interaction_id=interaction_id,
        customer_id=customer_id.strip(),
        interaction_type=interaction_type.strip(),
        subject=subject.strip(),
        description=description.strip(),
        outcome=outcome.strip(),
        next_action=next_action.strip(),
        interaction_date=datetime.now(),
        created_by=created_by,
        duration_minutes=duration_minutes,
        notes=notes
    )
    
    # Update customer's last contact date
    CUSTOMER_PROFILES[customer_id].last_contact_date = datetime.now()
    
    return f"✅ Interaction {interaction_id} successfully recorded for customer {customer_id}"

@mcp.tool()
async def get_interaction_history(customer_id: Optional[str] = None, interaction_type: Optional[str] = None,
                                outcome: Optional[str] = None) -> Dict:
    """Get interaction history with optional filtering.
    
    Args:
        customer_id: Optional customer ID to filter
        interaction_type: Optional interaction type to filter
        outcome: Optional outcome to filter
        
    Returns:
        Dictionary containing interaction history
    """
    if customer_id:
        if customer_id not in CUSTOMER_PROFILES:
            return {"interactions": [], "message": f"Customer {customer_id} not found"}
    
    filtered_interactions = []
    for interaction in INTERACTION_RECORDS.values():
        if customer_id and interaction.customer_id != customer_id:
            continue
        if interaction_type and interaction.interaction_type != interaction_type:
            continue
        if outcome and interaction.outcome != outcome:
            continue
        filtered_interactions.append(interaction)
    
    return {"interactions": [asdict(interaction) for interaction in filtered_interactions]}

@mcp.tool()
async def create_sales_opportunity(customer_id: str = None, opportunity_name: str = None, description: str = None,
                                 value: float = None, probability: float = None, stage: str = None,
                                 expected_close_date: str = None, assigned_to: str = None, lead_source: str = None,
                                 notes: str = "") -> str:
    """Create a new sales opportunity.
    
    Args:
        customer_id: Customer ID (REQUIRED)
        opportunity_name: Name of the opportunity (REQUIRED)
        description: Detailed description (REQUIRED)
        value: Deal value in USD (REQUIRED)
        probability: Probability percentage (0-100) (REQUIRED)
        stage: Sales stage (REQUIRED)
        expected_close_date: Expected close date (YYYY-MM-DD) (REQUIRED)
        assigned_to: Assigned sales representative (REQUIRED)
        lead_source: Source of the lead (REQUIRED)
        notes: Additional notes
        
    Returns:
        Opportunity ID and confirmation message, or list of missing required fields
    """
    # Validate required fields
    missing_fields = []
    
    if not customer_id or customer_id.strip() == "":
        missing_fields.append("customer_id")
    elif customer_id not in CUSTOMER_PROFILES:
        return f"❌ OPPORTUNITY CREATION FAILED: Customer {customer_id} not found"
    
    if not opportunity_name or opportunity_name.strip() == "":
        missing_fields.append("opportunity_name")
    
    if not description or description.strip() == "":
        missing_fields.append("description")
    
    if value is None or value <= 0:
        missing_fields.append("value (must be > 0)")
    
    if probability is None or probability < 0 or probability > 100:
        missing_fields.append("probability (must be 0-100)")
    
    if not stage or stage.strip() == "":
        missing_fields.append("stage")
    
    if not expected_close_date or expected_close_date.strip() == "":
        missing_fields.append("expected_close_date")
    
    if not assigned_to or assigned_to.strip() == "":
        missing_fields.append("assigned_to")
    
    if not lead_source or lead_source.strip() == "":
        missing_fields.append("lead_source")
    
    # If there are missing fields, return detailed feedback
    if missing_fields:
        missing_list = ", ".join(missing_fields)
        return f"❌ OPPORTUNITY CREATION FAILED: Missing required information.\n\nMissing fields: {missing_list}\n\nPlease provide all required information and try again. Required fields are:\n- customer_id: Customer ID\n- opportunity_name: Name of the opportunity\n- description: Detailed description\n- value: Deal value in USD (must be > 0)\n- probability: Probability percentage (0-100)\n- stage: Sales stage\n- expected_close_date: Expected close date (YYYY-MM-DD format)\n- assigned_to: Assigned sales representative\n- lead_source: Source of the lead"
    
    # Validate stage
    valid_stages = ["prospecting", "qualification", "proposal", "negotiation", "closed_won", "closed_lost"]
    if stage not in valid_stages:
        return f"❌ OPPORTUNITY CREATION FAILED: Invalid stage. Valid options: {valid_stages}"
    
    # Validate date format
    try:
        close_date_obj = datetime.strptime(expected_close_date, "%Y-%m-%d")
    except ValueError:
        return "❌ OPPORTUNITY CREATION FAILED: Invalid expected_close_date format. Please use YYYY-MM-DD format (e.g., 2024-12-31)"
    
    # Create the opportunity
    opportunity_id = f"OPP-{str(uuid.uuid4())[:8].upper()}"
    
    SALES_OPPORTUNITIES[opportunity_id] = SalesOpportunity(
        opportunity_id=opportunity_id,
        customer_id=customer_id.strip(),
        opportunity_name=opportunity_name.strip(),
        description=description.strip(),
        value=value,
        probability=probability,
        stage=stage.strip(),
        expected_close_date=close_date_obj,
        created_date=datetime.now(),
        assigned_to=assigned_to.strip(),
        lead_source=lead_source.strip(),
        notes=notes
    )
    
    return f"✅ Opportunity {opportunity_id} successfully created for {opportunity_name} with value ${value:,.2f}"

@mcp.tool()
async def get_sales_opportunities(opportunity_id: Optional[str] = None, stage: Optional[str] = None,
                                customer_id: Optional[str] = None) -> Dict:
    """Get sales opportunities with optional filtering.
    
    Args:
        opportunity_id: Optional opportunity ID to filter
        stage: Optional stage to filter
        customer_id: Optional customer ID to filter
        
    Returns:
        Dictionary containing opportunity information
    """
    if opportunity_id:
        if opportunity_id in SALES_OPPORTUNITIES:
            return {"opportunities": [asdict(SALES_OPPORTUNITIES[opportunity_id])]}
        else:
            return {"opportunities": [], "message": f"Opportunity {opportunity_id} not found"}
    
    filtered_opportunities = []
    for opportunity in SALES_OPPORTUNITIES.values():
        if stage and opportunity.stage != stage:
            continue
        if customer_id and opportunity.customer_id != customer_id:
            continue
        filtered_opportunities.append(opportunity)
    
    return {"opportunities": [asdict(opportunity) for opportunity in filtered_opportunities]}

@mcp.tool()
async def get_crm_summary() -> Dict:
    """Get a summary of CRM activities.
        
    Returns:
        Dictionary containing CRM summary statistics
    """
    total_customers = len(CUSTOMER_PROFILES)
    active_customers = len([c for c in CUSTOMER_PROFILES.values() if c.status == "active"])
    prospect_customers = len([c for c in CUSTOMER_PROFILES.values() if c.status == "prospect"])
    
    total_opportunities = len(SALES_OPPORTUNITIES)
    total_opportunity_value = sum(o.value for o in SALES_OPPORTUNITIES.values())
    weighted_pipeline_value = sum(o.value * o.probability / 100 for o in SALES_OPPORTUNITIES.values())
    
    total_interactions = len(INTERACTION_RECORDS)
    recent_interactions = len([i for i in INTERACTION_RECORDS.values() 
                             if i.interaction_date > datetime.now() - timedelta(days=30)])
    
    return {
        "summary": {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "prospect_customers": prospect_customers,
            "total_opportunities": total_opportunities,
            "total_opportunity_value": total_opportunity_value,
            "weighted_pipeline_value": weighted_pipeline_value,
            "total_interactions": total_interactions,
            "recent_interactions": recent_interactions
        }
    }

if __name__ == "__main__":
    mcp.run(transport="sse", port=8003)
