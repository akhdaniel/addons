import json
import logging
import werkzeug
import werkzeug.utils
from datetime import datetime
from math import ceil

from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT as DTF, ustr
import openerp.addons.survey.controllers.main as main


_logger = logging.getLogger(__name__)

class WebsiteSurvey2(main.WebsiteSurvey):

    # AJAX submission of a page
    @http.route(['/survey/submit/<model("survey.survey"):survey>'],
                type='http', methods=['POST'], auth='public', website=True)
    def submit(self, survey, **post):
        res = super(WebsiteSurvey2, self).submit(survey, **post)

        _logger.info('editable Incoming data: %s', post)
        page_id = int(post['page_id'])
        cr, uid, context = request.cr, request.uid, request.context
        questions_obj = request.registry['survey.question']
        user_input_obj = request.registry['survey.user_input']

        questions_ids = questions_obj.search(cr, uid, [('page_id', '=', page_id)], context=context)
        questions = questions_obj.browse(cr, uid, questions_ids, context=context)

        # Answer validation
        for question in questions:
            answer_tag = "%s_%s_%s" % (survey.id, page_id, question.id)
            for label in question.labels_ids:
                if label.value.strip().startswith("I do not want to receive information from"):
                    label_id = label.id
                    answer_tag = answer_tag + '_' + str(label_id)
                    break

        if answer_tag in post:
            user_input_id = user_input_obj.search(cr, SUPERUSER_ID, [('token', '=', post['token'])], context=context)[0]
            user_input = user_input_obj.browse(cr, SUPERUSER_ID, user_input_id, context=context)
            partner_id = user_input.partner_id.id
            request.registry['res.partner'].write(cr, SUPERUSER_ID, partner_id, {'opt_out':True}, context=context)


        return res
