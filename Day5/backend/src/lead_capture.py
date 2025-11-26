"""
Lead Capture System for Razorpay SDR Agent
Manages lead data collection and storage
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import re


class LeadCapture:
    """Manages lead information collection and storage"""
    
    # Required fields for a complete lead
    REQUIRED_FIELDS = [
        'name',
        'company', 
        'email',
        'role',
        'use_case',
        'team_size',
        'timeline'
    ]
    
    def __init__(self, leads_db_path: str):
        """
        Initialize lead capture system
        
        Args:
            leads_db_path: Path to master leads database JSON file
        """
        self.leads_db_path = leads_db_path
        self.current_lead = {}
        self.timestamp = None
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure the leads database file exists"""
        os.makedirs(os.path.dirname(self.leads_db_path), exist_ok=True)
        
        if not os.path.exists(self.leads_db_path):
            initial_data = {"leads": []}
            with open(self.leads_db_path, 'w', encoding='utf-8') as f:
                json.dump(initial_data, f, indent=2)
            print(f"✅ Created leads database: {self.leads_db_path}")
    
    def start_new_lead(self):
        """Start capturing a new lead"""
        self.current_lead = {}
        self.timestamp = datetime.now().isoformat()
        print("🆕 Started new lead capture")
    
    def add_field(self, field_name: str, value: str) -> bool:
        """
        Add or update a field in the current lead
        
        Args:
            field_name: Name of the field (e.g., 'name', 'email')
            value: Value for the field
            
        Returns:
            True if field was added successfully, False otherwise
        """
        if not value or not value.strip():
            return False
        
        # Validate email if it's an email field
        if field_name == 'email':
            if not self._validate_email(value):
                print(f"⚠️ Invalid email format: {value}")
                return False
        
        self.current_lead[field_name] = value.strip()
        print(f"✅ Captured {field_name}: {value}")
        return True
    
    def _validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def get_field(self, field_name: str) -> Optional[str]:
        """Get a field value from current lead"""
        return self.current_lead.get(field_name)
    
    def has_field(self, field_name: str) -> bool:
        """Check if a field has been collected"""
        return field_name in self.current_lead and bool(self.current_lead[field_name])
    
    def get_missing_fields(self) -> List[str]:
        """Get list of fields that haven't been collected yet"""
        missing = []
        for field in self.REQUIRED_FIELDS:
            if not self.has_field(field):
                missing.append(field)
        return missing
    
    def is_complete(self) -> bool:
        """Check if all required fields have been collected"""
        return len(self.get_missing_fields()) == 0
    
    def get_completion_percentage(self) -> float:
        """Get percentage of fields collected"""
        if not self.REQUIRED_FIELDS:
            return 100.0
        collected = len(self.REQUIRED_FIELDS) - len(self.get_missing_fields())
        return (collected / len(self.REQUIRED_FIELDS)) * 100
    
    def save_to_database(self) -> bool:
        """
        Save current lead to master database
        
        Returns:
            True if saved successfully, False otherwise
        """
        if not self.current_lead:
            print("⚠️ No lead data to save")
            return False
        
        try:
            # Read existing database
            with open(self.leads_db_path, 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # Add timestamp
            lead_with_timestamp = {
                'timestamp': self.timestamp or datetime.now().isoformat(),
                **self.current_lead
            }
            
            # Append new lead
            database['leads'].append(lead_with_timestamp)
            
            # Write back to file
            with open(self.leads_db_path, 'w', encoding='utf-8') as f:
                json.dump(database, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Lead saved to database! Total leads: {len(database['leads'])}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving lead: {e}")
            return False
    
    def generate_summary(self) -> str:
        """
        Generate a verbal summary of the lead
        
        Returns:
            Human-readable summary string
        """
        if not self.current_lead:
            return "No lead information was collected."
        
        summary_parts = []
        
        # Name and company
        name = self.get_field('name')
        company = self.get_field('company')
        if name and company:
            summary_parts.append(f"I spoke with {name} from {company}")
        elif name:
            summary_parts.append(f"I spoke with {name}")
        
        # Role
        role = self.get_field('role')
        if role:
            summary_parts.append(f"who is a {role}")
        
        # Use case
        use_case = self.get_field('use_case')
        if use_case:
            summary_parts.append(f"They're looking to use Razorpay for {use_case}")
        
        # Team size
        team_size = self.get_field('team_size')
        if team_size:
            summary_parts.append(f"Their team has {team_size} members")
        
        # Timeline
        timeline = self.get_field('timeline')
        if timeline:
            timeline_text = {
                'now': 'They want to get started immediately',
                'soon': 'They\'re planning to start soon',
                'later': 'They\'re exploring options for later'
            }.get(timeline.lower(), f'Their timeline is {timeline}')
            summary_parts.append(timeline_text)
        
        # Email
        email = self.get_field('email')
        if email:
            summary_parts.append(f"I can follow up with them at {email}")
        
        # Join parts intelligently
        if len(summary_parts) == 0:
            return "I collected some basic information from the prospect."
        elif len(summary_parts) == 1:
            return summary_parts[0] + "."
        else:
            summary = ". ".join(summary_parts[:2])
            if len(summary_parts) > 2:
                summary += ". " + ". ".join(summary_parts[2:])
            return summary + "."
    
    def get_next_question_suggestion(self) -> Optional[str]:
        """
        Suggest the next question to ask based on missing fields
        
        Returns:
            Suggested question or None if all fields collected
        """
        missing = self.get_missing_fields()
        
        if not missing:
            return None
        
        # Question templates for each field
        question_templates = {
            'name': "May I have your name?",
            'company': "What company are you with?",
            'email': "What's the best email to reach you at?",
            'role': "What's your role at the company?",
            'use_case': "What would you like to use Razorpay for?",
            'team_size': "How large is your team?",
            'timeline': "When are you looking to get started? Is it urgent, or are you still exploring?"
        }
        
        next_field = missing[0]
        return question_templates.get(next_field, f"Can you tell me about your {next_field}?")
    
    def get_lead_data(self) -> Dict:
        """Get current lead data"""
        return self.current_lead.copy()


# Utility function
def create_lead_capture(leads_dir: str = None) -> LeadCapture:
    """
    Create LeadCapture instance
    
    Args:
        leads_dir: Directory for leads database
        
    Returns:
        LeadCapture instance
    """
    if leads_dir is None:
        # Default to leads directory relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        leads_dir = os.path.join(os.path.dirname(current_dir), 'leads')
    
    db_path = os.path.join(leads_dir, 'leads_database.json')
    return LeadCapture(db_path)


if __name__ == "__main__":
    # Test the lead capture system
    print("\n" + "="*60)
    print("Testing Lead Capture System")
    print("="*60)
    
    lead = create_lead_capture()
    lead.start_new_lead()
    
    # Simulate collecting lead info
    lead.add_field('name', 'Rahul Sharma')
    lead.add_field('company', 'TechStartup India')
    lead.add_field('email', 'rahul@techstartup.in')
    lead.add_field('role', 'CTO')
    lead.add_field('use_case', 'payment gateway for our SaaS product')
    lead.add_field('team_size', '15')
    lead.add_field('timeline', 'now')
    
    print(f"\n📊 Completion: {lead.get_completion_percentage()}%")
    print(f"❓ Missing fields: {lead.get_missing_fields()}")
    print(f"\n📝 Summary:\n{lead.generate_summary()}")
    
    # Save to database
    lead.save_to_database()
