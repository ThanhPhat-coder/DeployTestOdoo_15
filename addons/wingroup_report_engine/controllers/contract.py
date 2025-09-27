# -*- coding: utf-8 -*-
import base64

from odoo import http
from odoo.http import request
import json
from pprint import pprint

class APIAll(http.Controller):

    @http.route('/api/create-contract/pdf-by-xml', auth='public', csrf=False, type='json')
    def api_create_contract_json_by_xml(self, **kwargs):
        try:
            Authorization = request.httprequest.headers.environ.get("HTTP_AUTHORIZATION")
            user = request.env['res.users'].sudo().get_api_rest_user(Authorization.replace('Bearer ', ''))
            if not user:
                return {
                    'status': 'Fail',
                    'message': 'Xác thực không chính xác',
                }
            report_data = {key: request.jsonrequest.get(key) for key in request.jsonrequest}
            template_code = report_data.get('template_code')
            xml_data = report_data.get('xml_data')
            print(template_code)
            contract_data_json = request.env['wg.report.template.odt'].with_user(user).tvan_contract_xml_json(data_xml=xml_data)
            print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeee", contract_data_json)
            pdf = request.env['wg.report.template.odt'].with_user(user).action_print(template_code, json.dumps(contract_data_json))
            print (pdf)
            return {
                'result': pdf,
            }
        except Exception as e:
            raise e