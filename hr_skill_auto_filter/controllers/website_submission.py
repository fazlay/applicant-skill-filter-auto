from odoo.addons.website.controllers.form import WebsiteForm
import logging


_logger = logging.getLogger(__name__)

class CustomWebsiteForm(WebsiteForm):
    
    def insert_record(self, request, model, values, custom, meta=None):
        print("=== CUSTOM INSERT_RECORD OVERRIDE ===")
        _logger.info("=== CUSTOM INSERT_RECORD OVERRIDE ===")
        _logger.info("Model: %s", model.model)
        _logger.info("Values: %s", values)
        _logger.info("Custom: %s", custom)
        
    
        if model.model == 'hr.applicant' and custom:
            # Extract skill_ids from custom data
            skill_match = re.search(r'skill_ids\s*:\s*([0-9,\s]+)', custom)
            if skill_match:
                skill_ids_str = skill_match.group(1).strip()
                _logger.info("Found skills in custom: %s", skill_ids_str)
                
                # Convert to list of integers
                skill_list = [int(x.strip()) for x in skill_ids_str.split(',') if x.strip()]
                
                # Add to values for proper field storage
                # Assuming you have a skill_ids field in hr.applicant
                values['skill_ids'] = [(6, 0, skill_list)]
                
                # Remove from custom to clean up the description
                custom = re.sub(r'skill_ids\s*:\s*[0-9,\s]+\n?', '', custom).strip()
                
                _logger.info("Added skill_ids to values: %s", values['skill_ids'])
                _logger.info("Cleaned custom: %s", custom)
        
     
        return super().insert_record(request, model, values, custom, meta)