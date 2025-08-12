{
    "name": "rif_odoo_2025_employee_part_2025",
    "summary": "Building and testing rif_odoo_employee_part_2025 to be added in the official project",
    "version": "1.0",
    "license": "LGPL-3",
    "depends": [
        #orm
        "base",
        #employee
        "hr",
        #contrat
        "hr_contract", 
            # Optional, for digital signatures
        "sign",  
        #equipements
        "maintenance",
        #skills and CV
        "hr_skills",
        "hr_skills_slides",
        "hr_skills_survey",
        # hr_attendance is the base presence module
        'hr_attendance',
        #to do list
        "hr_timesheet",
        
    ],
    "data": [
        #views
        "views/hr_department_views.xml"
    ],
    "demo": [],
    "assets": {}
}
