from odoo import http
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.addons.website.controllers.form import WebsiteForm


class CustomWebsiteHrRecruitment(WebsiteHrRecruitment):

    @http.route('''/jobs/apply/<model("hr.job"):job>''', type='http', auth="public", website=True, sitemap=True)
    def jobs_apply(self, job, **kwargs):
     
        response = super().jobs_apply(job, **kwargs)
        
    
        skills = request.env['hr.skill'].sudo().search([])
        
   
        if hasattr(response, 'qcontext'):
            response.qcontext.update({
                'skills': skills
            })
        
        return response
from odoo.addons.website.controllers.form import WebsiteForm
import logging


_logger = logging.getLogger(__name__)

class CustomWebsiteForm(WebsiteForm):
    
    
    def _get_job_required_skills(self, request, job_id):
        """Get required skills for a specific job"""
        if not job_id:
            return []
            
        try:
            job_record = request.env['hr.job'].sudo().browse(job_id)
            if job_record.exists():
                # Get skill IDs from the job record
                required_skill_ids = job_record.skill_ids.ids
                _logger.info("Job %s (%s) requires skills: %s", job_record.name, job_id, required_skill_ids)
                return required_skill_ids
            else:
                _logger.warning("Job with ID %s not found", job_id)
                return []
        except Exception as e:
            _logger.error("Error fetching job skills: %s", str(e))
            return []

    def _move_to_next_stage(self, request, values):
        """Move applicant to next stage if conditions are met"""
        if 'stage_id' not in values:
            return
            
        current_stage_id = values['stage_id']
        # Get the next stage
        current_stage = request.env['hr.recruitment.stage'].sudo().browse(current_stage_id)
        next_stage = request.env['hr.recruitment.stage'].sudo().search([
            ('sequence', '>', current_stage.sequence)
        ], order='sequence asc', limit=1)
        
        if next_stage:
            values['stage_id'] = next_stage.id
        else:
            _logger.warning("No next stage found, keeping current stage %s", current_stage.name)
    
    def insert_record(self, request, model, values, custom, meta=None):
        
        
        if model.model == 'hr.applicant':
            
            job_id = values.get('job_id')
            required_skills = self._get_job_required_skills(request, job_id)
         
            
            lines = custom.split('\n')
            skill_line = [line for line in lines if line.strip().startswith('skill_ids')][0]
            applicant_skill_ids = [int(x.strip()) for x in skill_line.split(':')[1].split(',')]
            print('applicants skill ids',applicant_skill_ids)
                    
            matching_skills = [skill for skill in applicant_skill_ids if skill in required_skills]
            should_move_to_next_stage = len(matching_skills) == len(required_skills)
            # should_move_to_next_stage = len(matching_skills) >= 2  # At least 2 skills must match
            
            if should_move_to_next_stage:
                self._move_to_next_stage(request, values)
        
        

        record_id = super().insert_record(request, model, values, custom, meta)
        
        if model.model == 'hr.applicant' and record_id:

           
            try:
                for skill_id in applicant_skill_ids:
                 
                    skill_record = request.env['hr.skill'].sudo().browse(skill_id)
                    if skill_record.exists():
                      
                        default_skill_level = request.env['hr.skill.level'].sudo().search([
                            ('skill_type_id', '=', skill_record.skill_type_id.id),
                            ('default_level', '=', True)
                        ], limit=1)
                        
                        
                        if not default_skill_level:
                            default_skill_level = request.env['hr.skill.level'].sudo().search([
                                ('skill_type_id', '=', skill_record.skill_type_id.id)
                            ], limit=1)
                        
                        skill_level_id = default_skill_level.id if default_skill_level else 1
                        
                        
                        
                        request.env['hr.candidate.skill'].sudo().create({
                            'candidate_id': record_id,
                            'skill_id': skill_id,
                            'skill_type_id': skill_record.skill_type_id.id, 
                            'skill_level_id': skill_level_id,  
                        })
                _logger.info("Added hardcoded skills %s to applicant %s", applicant_skill_ids, record_id)
                
            except Exception as e:
                _logger.error("Error adding hardcoded skills: %s", str(e))
        
        return record_id