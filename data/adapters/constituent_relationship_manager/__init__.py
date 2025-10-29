#  Potential Use Cases

#   1. Funder Identity & Contact Info
#   # Use case: "I have a Bernie Number, give me contact details"
#   funder = get_funder_contact_info('BN000095')
#   # Returns: name, email, phone, address, engagement_score

#   2. Grant History Analysis
#   # Use case: "Show me all past grants with this funder"
#   history = get_grant_history('BN000095')
#   # Returns: List of past grants with amounts, dates, statuses

#   3. Relationship Context
#   # Use case: "What's our relationship with this funder?"
#   relationship = get_funder_relationship('BN000095')
#   # Returns: Engagement score, interaction count, years active, success rate

#   4. Active Grant Tracking
#   # Use case: "What CRM notes exist for active grants?"
#   active_grants = get_CRM_active_grants()
#   # Returns: Notes with status != "Awarded-Closed"

#   Questions to Help You Decide

#   Before designing the API, let's clarify:

#   Question 1: Primary vs Secondary Data Source

#   Is CRM:
#   - Primary source for grant data? (truth about current grants)
#   - Secondary source for enrichment? (contact info, history)
#   - Archive for closed grants? (historical reference only)


#   Question 2: Read-Only vs Read-Write

#   Will the new system:
#   - Only read from CRM? (display data)
#   - Write back to CRM? (update notes when grants close)


#   Question 3: Real-Time vs Cached

#   Do you need:
#   - Fresh data from CRM API every time?
#   - Cached data from the database (faster, less API calls)?

#   Current system uses database-first with refresh_funder_crm_data() for updates.

#   Question 4: Bulk vs Individual

#   Will you typically:
#   - Get one funder at a time? (detail page)
#   - Get all funders in bulk? (dashboard, reports)

#   Both probably needed.