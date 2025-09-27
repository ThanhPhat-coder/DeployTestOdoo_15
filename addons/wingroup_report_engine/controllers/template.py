# -*- coding: utf-8 -*-
import base64

from odoo import http
from odoo.http import request
import json
from pprint import pprint


class APIAll(http.Controller):
    # https://tlt2.wgroup.vn/download/template/template_code
    @http.route('/download/template/<string:template_code>', type='http', auth='public')
    def download_file(self, template_code=None):
        record = request.env['wg.report.template.odt'].sudo().search([('code', '=', template_code)])
        binary_data = base64.b64decode(record.inv_template_data)
        filename = record.inv_template_filename
        if binary_data:
            headers = [('Content-Disposition', 'attachment; filename=%s' % filename)]
            return request.make_response(binary_data, headers=headers)
        else:
            return request.not_found()

    @http.route('/api/change-state/template', auth='public', csrf=False, type='json')
    def api_change_state_template(self, **kwargs):
        try:
            Authorization = request.httprequest.headers.environ.get("HTTP_AUTHORIZATION")
            user = request.env['res.users'].sudo().get_api_rest_user(Authorization.replace('Bearer ', ''))
            if not user:
                return {
                    'status': 'Fail',
                    'message': 'Xác thực không chính xác',
                }
            data = {key: request.jsonrequest.get(key) for key in request.jsonrequest}
            template_code = data.get('template_code')
            state = data.get('state')
            result = request.env['wg.report.template.odt'].with_user(user).tvan_change_state_template(template_code,state)
            return {
                'status': 'Success',
                'state': result,
            }
        except Exception as e:
            print (e)

    @http.route('/api/create/template', auth='public', csrf=False, type="json")
    def api_get_template(self, **kwargs):
        try:
            Authorization = request.httprequest.headers.environ.get("HTTP_AUTHORIZATION")
            user = request.env['res.users'].sudo().get_api_rest_user(Authorization.replace('Bearer ', ''))
            if not user:
                return {
                    'status': 'Fail',
                    'message': 'Xác thực không chính xác',
                }

            ReportObj = request.env['wg.report.template.odt']
            data = {key: request.jsonrequest.get(key) for key in request.jsonrequest}
            template_code = data.get('template_code')
            record = ReportObj.with_user(user).search([('code', '=', template_code)], limit=1)
            if not record:
                return {
                    'status': 'Fail',
                    'message': 'Không có mẫu!'
                }
            report_data = data.get('data', {})
            report_data['inv_template_data'] = record.inv_template_data
            report = ReportObj.with_user(user).create(report_data)
            return {
                'status': 'Success',
                'message': 'Tạo mẫu thành công!',
                'template_code': report.code
            }
        except Exception as e:
            return {
                'status': 'Fail',
                'Error': e,
            }
            raise e
        
        
    @http.route('/api/print/template', auth='public', csrf=False, type="json")
    def api_print_template(self, **kwargs):
        try:
            Authorization = request.httprequest.headers.environ.get("HTTP_AUTHORIZATION")
            user = request.env['res.users'].sudo().get_api_rest_user(Authorization.replace('Bearer ', ''))
            if not user:
                return {
                    'status': 'Fail',
                    'message': 'Xác thực không chính xác',
                }

            ReportObj = request.env['wg.report.template.odt']
            data = {key: request.jsonrequest.get(key) for key in request.jsonrequest}
            template_code = data.get('template_code')
            data_json = data.get('data_json')
            record = ReportObj.with_user(user).search([('code', '=', template_code)], limit=1)
            if not record:
                return {
                    'status': 'Fail',
                    'message': 'Không có mẫu!'
                }
            report = ReportObj.with_user(user).action_print(template_code, data_json)
            return {
                'status': 'Success',
                'message': 'In mẫu thành công!',
                'result': report
            }
        except Exception as e:
            return {
                'status': 'Fail',
                'Error': e,
            }
            raise e
        
        
        