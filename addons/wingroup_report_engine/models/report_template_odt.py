# -*- coding: utf-8 -*-
import uuid
import json
import base64
import xmltodict
from datetime import datetime
from odoo.tools.misc import formatLang, format_date

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from odoo.addons.qr_code_base.models.qr_code_base import generate_qr_code


class ReportTemplateODT(models.Model):
    _name = 'wg.report.template.odt'
    _inherit ='mail.thread'
    _description = 'Mẫu bản in (odt)'
    _order = 'create_date desc'


    @api.model
    def get_code(self, company_vat=None):
        code = company_vat + str(uuid.uuid4()).upper().replace('-', '')
        if self.sudo().search([('code', '=', code)], limit=1):
            return self.get_code()
        return code

    def name_get(self):
        return [(r.id, '{} - {}'.format(r.company_vat, r.company_name)) for r in self]

    @api.model
    def create(self, vals):
        vals['code'] = self.get_code(vals.get('company_vat'))
        return super(ReportTemplateODT, self).create(vals)
    
    def unlink(self):
        if any(self.filtered(lambda x: x.state !='cancel')):
            raise UserError('Không thể xoá mẫu in khi trong trạng thái Đang sử dụng, Nháp.')
        return super(ReportTemplateODT, self).unlink()

    code = fields.Char('Mã nhận dạng', index=1, readonly=True, states={'new': [('readonly', False)]})
    type = fields.Selection([
        ('1', 'HĐĐT giá trị gia tăng'),
        ('2', 'HĐĐT bán hàng'),
        ('3', 'HĐĐT bán tài sản công'),
        ('4', 'HĐĐT bán hàng dự trữ quốc gia'),
        ('5', 'Tem/Vé/Thẻ/Phiếu thu/Chứng từ điện tử'),
        ('6', 'PXK kiêm VC nội bộ'),
        ], 'Loại hóa đơn', required=True, readonly=True, states={'new': [('readonly', False)]})
    active = fields.Boolean('Có hiệu lực', default=True)
    company_vat = fields.Char('Mã số thuế', required=True, tracking=True, readonly=True, states={'new': [('readonly', False)]})
    company_name = fields.Char('Tên công ty', required=True, readonly=True, states={'new': [('readonly', False)]})
    company_address = fields.Char('Địa chỉ', required=True, readonly=True, states={'new': [('readonly', False)]})

    inv_template_data = fields.Binary('Mẫu hóa đơn (odt)', required=True, readonly=True, states={'new': [('readonly', False)]})
    inv_template_filename = fields.Char('Tên file mẫu', required=True, readonly=True, states={'new': [('readonly', False)]})

    image_logo = fields.Binary('Logo công ty', required=True, readonly=True, states={'new': [('readonly', False)]})
    image_background = fields.Binary('Ảnh nền', required=True, readonly=True, states={'new': [('readonly', False)]})
    image_sign = fields.Binary('Khung chữ ký', required=True, readonly=True, states={'new': [('readonly', False)]})
    sample_data = fields.Text('Dữ liệu mẫu', readonly=True, states={'new': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Công ty', readonly=True, states={'new': [('readonly', False)]})
    inv_serial = fields.Char('Ký hiệu hoá đơn', readonly=True, states={'new': [('readonly', False)]})
    inv_template_xml = fields.Binary('File XML', readonly=True, states={'new': [('readonly', False)]})
    inv_template_xml_name = fields.Char('Tên file XML mẫu', readonly=True, states={'new': [('readonly', False)]})
    state = fields.Selection([
        ('new', 'Mới khởi tạo'),
        ('use', 'Đang sử dụng'),
        ('cancel', 'Huỷ bỏ')
    ], default="new", string='Trạng thái', tracking=True)
    note = fields.Text('Ghi chú', readonly=True, states={'new': [('readonly', False)]})
    name = fields.Char('Tên', required=True, readonly=True, states={'new': [('readonly', False)]})
    config_sign_date = fields.Text('Định dạng ngày ký', default='Ký ngày %d tháng %m năm %Y', readonly=True, states={'new': [('readonly', False)]})
    print_type = fields.Selection([
        ('inv', 'Hoá đơn'),
        ('contract', 'Hợp đồng')
    ], string='Mẫu In', default="inv", tracking=True, readonly=True, states={'new': [('readonly', False)]})

    # @api.constrains('company_vat', 'inv_serial', 'type')
    # def _constrains_vat_serial_type(self):
    #     for rec in self:
    #         self.env.cr.execute("""
    #             SELECT id FROM wg_report_template_odt
    #             WHERE company_vat = %s AND state = %s AND inv_serial = %s AND type = %s AND id != %s 
    #             """, (rec.company_vat, rec.state, rec.inv_serial, rec.type, rec.id))
    #         result = self.env.cr.fetchall()
    #         if result:
    #             raise ValidationError("A record with the same VAT, serial, and type already exists.")

    def test_tmp_file(self):
        res = self.action_print(self.code, data=self.sample_data)
        return res

    def test_store_file(self):
        res = self.action_print(self.code, data=self.sample_data, storage=True)
        return res

    def action_print(self, template_code, data={}, storage=False):
        template = self.sudo().search([('code', '=', template_code)], limit=1)
        if not template:
            raise ValidationError('Không tìm thấy mẫu "{}"'.format(template_code))            
        try:
            data = json.loads(data)
            try:
                CompanyImageLogo = data['CompanyImageLogo']
                CompanyImageBackground = data['CompanyImageBackground']
                CompanyImageSign = data['CompanyImageSign']
            except Exception as e:
                CompanyImageLogo = self.image_logo.decode('utf-8')
                CompanyImageBackground = self.image_background.decode('utf-8')
                CompanyImageSign = self.image_sign.decode('utf-8')
            data.update({
                "CompanyImageLogo": CompanyImageLogo,
                "CompanyImageBackground": CompanyImageBackground,
                "CompanyImageSign": CompanyImageSign,
                "ImageQRCode": generate_qr_code('https://hoadonkhanhlinh.vn').decode('utf-8'),
            })
            print("pass")
        except Exception as e:
            print("fail")
            pass
        model_name = 'wg.report.pdf.tmp'
        if storage:
            model_name = 'wg.report.pdf.store'
        try:
            company_vat = data['CompanyVat']
            company_name = data['CompanyName']
            name = data['print_report_name']
        except Exception as e:
            company_vat = template.company_vat
            company_name = template.company_name
            name = "'Không_xác_định.pdf'"
        
        record = self.env[model_name].create({
            'template_id': template.id,
            'data': json.dumps(data),
            'company_vat': company_vat,
            'company_name': company_name,
            'name': name,
        })
        report_data = { 
            'type': 'ir.actions.report',
            'model': model_name,
            'report_type':'aeroo',
            'in_format':'oo-odt',
            'out_format': self.env['report.mimetypes'].search([('code','=', 'oo-pdf')], limit=1).id,
            'tml_source': 'database',
            'print_report_name': name,
            'report_data': template.inv_template_data,
        }
        report = self.env['ir.actions.report'].new(report_data)
        file_data, out_code, filename = report.with_context(self._context).render_aeroo([record.id], data={})
        attachment_id = record.attachment_id
        att_value = {
            'name': filename,
            'res_model': model_name,
            'res_id': record.id,
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'public': True,
        }
        if not attachment_id:
            attachment_id = self.env['ir.attachment'].create(att_value)
        else:
            attachment_id.write(att_value)
        record.write({
            'attachment_id': attachment_id.id,
        })
        return record.open_link_by_new_tab()

    def report_is_not_demo(self, data):
        try:
            data['Demo'] = "0"
        except Exception as e:
            print(e)
        return data
    
    def create_report_pdf(self, data_convert, template, model_name):
        data = self.report_is_not_demo(data_convert)
        try:
            company_vat = data['CompanyVat']
            company_name = data['CompanyName']
            name = data['print_report_name']
        except Exception as e:
            company_vat = template.company_vat
            company_name = template.company_name
            name = "'Không_xác_định.pdf'"
            
        record = self.env[model_name].create({
            'template_id': template.id,
            'data': json.dumps(data),
            'company_vat': company_vat,
            'company_name': company_name,
            'name': name
        })
        return record

    def create_attachments(self, data_convert, record, template, model_name):
        report_data = { 
            'type': 'ir.actions.report',
            'model': model_name,
            'report_type':'aeroo',
            'in_format':'oo-odt',
            'out_format': self.env['report.mimetypes'].search([('code','=', 'oo-pdf')], limit=1).id,
            'tml_source': 'database',
            'print_report_name': data_convert.get('print_report_name') or "'Không_xác_định'",
            # 'print_report_name': data_convert.get('print_report_name') or "'Không_xác_định'",
            'report_data': template.inv_template_data,
        }
        report = self.env['ir.actions.report'].new(report_data)
        file_data, out_code, filename = report.with_context(self._context).render_aeroo([record.id], data={})
        attachment_id = record.attachment_id
        att_value = {
            'name': filename,
            'res_model': model_name,
            'res_id': record.id,
            'type': 'binary',
            'datas': base64.b64encode(file_data),
            'public': True,
        }
        if not attachment_id:
            attachment_id = self.env['ir.attachment'].create(att_value)
        else:
            attachment_id.write(att_value)
        record.write({
            'attachment_id': attachment_id.id,
        })

    @api.model
    def action_print_by_xml(self, data={}, storage=False):
        data_convert, template = self.convert_xml_to_json(data)
        model_name = 'wg.report.pdf.store' if storage else 'wg.report.pdf.tmp'
        record = self.create_report_pdf(data_convert, template, model_name)
        self.create_attachments(data_convert, record, template, model_name)
        return record.open_link_by_new_tab()

    @api.model
    def get_invoice_template(self, KHHDon, KHMSHDon, MST, template_code=False):
        domain = [
                ('inv_serial', '=', KHHDon),
                ('type', '=', KHMSHDon),
                ('company_vat', '=', MST ),
        ]
        if template_code:
            domain = [('code', '=', template_code)]

        template = self.sudo().search(domain, limit=1)
        if not template:
            template = self.sudo().search([], limit=1)
        return template

    def format_date_not_in_datetimerange(self, Nlap):
        date =''
        day = ''
        month = ''
        year = ''
        try:
            date = datetime.strptime(Nlap, '%Y-%m-%d')
            day = date.day
            month = date.month
            year = date.year
        except Exception as e:
            date = Nlap
            if '/' in Nlap:
                year, month, day = Nlap.split('/')
            if '-' in Nlap:
                year, month, day = Nlap.split('-')
        return date, day, month, year
    
    def convert_to_eight_digit_string(self, number):
        return number.zfill(8)

    def convert_string_to_dict_list(self, vat):
        result = []
        for i, char in enumerate(vat):
            result.append({str(i+1): char})
        return result
    
    def convert_xml_to_json(self, data):
        json_data = xmltodict.parse(base64.b64decode(data.get("base_64")).decode('utf-8'))
        DLHDon = json_data.get('HDon', {}).get('DLHDon', {})
        TTChung = DLHDon.get('TTChung', {})
        NDHDon = DLHDon.get('NDHDon', '')
        #  get hdlq
        try:
            TCHDon = TTChung.get('TTHDLQuan', '').get('TCHDon', '')
            if TCHDon == '2':
                try:
                    type_inv = next(item['DLieu'] for item in DLHDon['TTKhac']['TTin'] if item['@Id'] == 'adjCode')
                    TCHDon = '2.2' #Điều chỉnh giảm 2.2
                    if type_inv == 'DCT':
                        TCHDon = '2.1' #Điều chỉnh tăng 2.1
                except Exception as e:
                    TCHDon == '2'
            LHDCLQuan = TTChung.get('TTHDLQuan', '').get('LHDCLQuan', '')
            KHMSHDCLQuan = TTChung.get('TTHDLQuan', '').get('KHMSHDCLQuan', '')
            KHHDCLQuan = TTChung.get('TTHDLQuan', '').get('KHHDCLQuan', '')
            SHDCLQuan = TTChung.get('TTHDLQuan', '').get('SHDCLQuan', '')
            NLHDCLQuan = TTChung.get('TTHDLQuan', '').get('NLHDCLQuan', '')
        except Exception as e:
            TCHDon = '0'
            LHDCLQuan = '0'
            KHMSHDCLQuan = '0'
            KHHDCLQuan = ''
            SHDCLQuan = '0'
            NLHDCLQuan = ''

        HDLQNKy, HDLQNKyNgay, HDLQNKyThang, HDLQNKyNam = self.format_date_not_in_datetimerange(NLHDCLQuan)
        
        try:
            TTin = DLHDon.get('TTKhac', '').get('TTin', '')
        except Exception as e:
            TTin = ''

        try:
            MCCQThue = json_data.get('HDon', {}).get('MCCQT', {}).get('#text', '')
            privateCode = [item['DLieu'] for item in TTin if item['@Id'] in ['privateCode']][0]
            cmpnKey = [item['DLieu'] for item in TTin if item['@Id'] in ['cmpnKey']][0]
        except Exception as e:
            MCCQThue = ''
            privateCode = ''
            cmpnKey = ''

        try:
            datetime_str = json_data.get('HDon', {}).get('DSCKS', {}).get('NBan', {}).get('Signature', {}).get('Object', {}).get('SignatureProperties', {}).get('SignatureProperty', {}).get('SigningTime', {})
            sign_date = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%S")
        except Exception as e:
            sign_date = ''

        date, day, month, year = self.format_date_not_in_datetimerange(TTChung.get('NLap', {}))
        template_code = data.get('template_code', False)
        template = self.get_invoice_template(TTChung.get('KHHDon'), TTChung.get('KHMSHDon'), NDHDon.get('NBan').get('MST'), template_code)
        res = {
            "TCHDon": TCHDon,
            "TCHDonName": (
                "Hóa đơn gốc" if TCHDon == "0" else
                "Điều chỉnh" if TCHDon == "2" else
                "Điều chỉnh tăng" if TCHDon == "2.1" else
                "Điều chỉnh giảm" if TCHDon == "2.2" else
                "Thay thế" if TCHDon == "1" else ""
            ),
            "HDLQKHMSHDon": KHMSHDCLQuan,
            "HDLQKHHDon": KHHDCLQuan,
            "HDLQSHDon": SHDCLQuan,
            "HDLQLoai": LHDCLQuan,
            "HDLQNKy": HDLQNKy.strftime('%d/%m/%Y') if type(HDLQNKy) is datetime else '{day}/{month}/{year}'.format(day=HDLQNKyNgay, month=HDLQNKyThang, year=HDLQNKyNam),
            "HDLQNKyNgay": str(HDLQNKy.day) if type(HDLQNKy) is datetime else HDLQNKyNgay,
            "HDLQNKyThang": str(HDLQNKy.month) if type(HDLQNKy) is datetime else HDLQNKyThang,
            "HDLQNKyNam": str(HDLQNKy.year) if type(HDLQNKy) is datetime else HDLQNKyNam,
            
            "CompanyVat": NDHDon.get('NBan', {}).get('MST', ''),
            "arrayCompanyVat": self.convert_string_to_dict_list(NDHDon.get('NBan', {}).get('MST', '')),
            "CompanyName": NDHDon.get('NBan', {}).get('Ten', ''),
            "CompanyAddress": NDHDon.get('NBan', {}).get('DChi', ''),
            "CompanyEmail": NDHDon.get('NBan', {}).get('Email', ''),
            "CompanyPhone": NDHDon.get('NBan', {}).get('SDThoai', ''),
            "CompanyWebsite": NDHDon.get('NBan', {}).get('Website', ''),
            "CompanyBankInfo": NDHDon.get('NBan', {}).get('STKNHang', ''),
            "CompanyImageLogo": template.image_logo.decode('utf-8'),
            "CompanyImageBackground": template.image_background.decode('utf-8'),
            "CompanyImageSign": template.image_sign.decode('utf-8'),
            "ImageQRCode": generate_qr_code('https://hoadonkhanhlinh.vn').decode('utf-8'),
            "KHMSHDon": TTChung.get('KHMSHDon', ''),
            "KHHDon": TTChung.get('KHHDon', ''),
            "SHDon": self.convert_to_eight_digit_string(TTChung.get('SHDon', '')),
            "NLap": str(date.strftime('%d/%m/%Y')) if type(date) is datetime else '{day}/{month}/{year}'.format(day=day, month=month, year=year),
            "NLapNgay": str(date.day) if type(date) is datetime else day,
            "NLapThang": str(date.month) if type(date) is datetime else month,
            "NLapNam": str(date.year) if type(date) is datetime else year,

            "NKy": str(sign_date.strftime('%d/%m/%Y')) if type(sign_date) is datetime else '',
            "NKyNgay": str(sign_date.day) if type(sign_date) is datetime else '',
            "NKyThang": str(sign_date.month) if type(sign_date) is datetime else '',
            "NKyNam": str(sign_date.year) if type(sign_date) is datetime else '',

            "SBKe": TTChung.get('SBKe', ''),
            "NBKe": TTChung.get('NBKe', ''),
            "DVTTe": TTChung.get('DVTTe', ''),
            "TGia": TTChung.get('TGia', ''),
            "HTTToan": TTChung.get('HTTToan', ''),

            "TenNBan": NDHDon.get('NBan', {}).get('Ten', ''),
            "MSTNBan": NDHDon.get('NBan', {}).get('MST', ''),
            "arrayMSTNBan": self.convert_string_to_dict_list(NDHDon.get('NBan', {}).get('MST', '')),
            "DChiNban": NDHDon.get('NBan', {}).get('DChi', ''),
            "DCTDTu": NDHDon.get('NBan', {}).get('DCTDTu', ''),
            "SDThoaiNBan": NDHDon.get('NBan', {}).get('SDThoai', ''),
            "STKNHang": NDHDon.get('NBan', {}).get('STKNHang', ''),
            "TNHang": NDHDon.get('NBan', {}).get('TNHang', ''),

            "TenNMua": NDHDon.get('NMua', {}).get('Ten', ''),
            "MSTNMua": NDHDon.get('NMua', {}).get('MST', ''),
            "arrayMSTNMua": self.convert_string_to_dict_list(NDHDon.get('NMua', {}).get('MST', '')),
            "DChiNMua": NDHDon.get('NMua', {}).get('DChi', ''),
            "MKHang": NDHDon.get('NMua', {}).get('MKHang', ''),
            "SDThoai": NDHDon.get('NMua', {}).get('SDThoai', ''),
            "DCTDTu": NDHDon.get('NMua', {}).get('DCTDTu', ''),
            "HVTNMHang": NDHDon.get('NMua', {}).get('HVTNMHang', ''),
            "STKNHang": NDHDon.get('NBan', {}).get('STKNHang', ''),
            "TNHang": NDHDon.get('NBan', {}).get('TNHang', ''),
            "HVTNMHang": "",

            "MCCQT": MCCQThue,
            "TgTCThue": float(NDHDon.get('TToan', {}).get('TgTCThue', 0)),
            "TgTCThueStr": formatLang(self.env, float(NDHDon.get('TToan', {}).get('TgTCThue', 0)), digits=0) or 0,
            "TgTThue": float(NDHDon.get('TToan', {}).get('TgTThue', 0)),
            "TgTThueStr": formatLang(self.env, float(NDHDon.get('TToan', {}).get('TgTThue', 0)), digits=0) or 0,
            "TgTTTBSo": float(NDHDon.get('TToan', {}).get('TgTTTBSo', 0)),
            "TgTTTBSoStr": formatLang(self.env, float(NDHDon.get('TToan', {}).get('TgTTTBSo', 0)), digits=0) or 0,
            "TongPhi": 0,
            "TongPhiStr": '',
            "TgTTTBChu": NDHDon.get('TToan', {}).get('TgTTTBChu', ''),
            "SignTitle": "CHỮ KÝ SỐ HỢP LỆ",
            "SignBy": "Ký bởi: " + NDHDon.get('NBan', {}).get('Ten', ''),
            "SignDate":  self.tvan_config_sign_date(sign_date),
            # "SignDate": "Ký " + str(sign_date.strftime('ngày %d tháng %m năm %Y')) if type(sign_date) is datetime else '',
            "TrackingLink": "https://tracuu.hoadonkhanhlinh.vn",
            "TrackingCode": "LACKUTE102",
            "ImageQRCode": generate_qr_code('https://hoadonkhanhlinh.vn').decode('utf-8'),

            "privateCode": privateCode ,
            "cmpnKey": cmpnKey,
            "Demo": "1",
            "print_report_name": "'Hoá_đơn_giá_trị_gia_tăng'",
            # "DDNKy": self.tvan_config_sign_date(sign_date),
            
        }

        res.update({
            'DSHHDVu': self.get_dshhdv(NDHDon),
            'footer_data': self.get_footer_data(NDHDon),
            'footer_data2': self.get_footer_data2(NDHDon),
        })
        return res, template
    
    def tvan_config_sign_date(self,sign_date):
        try:
            if type(sign_date) is datetime:
                return str(sign_date.strftime(self.config_sign_date))
        except Exception as e:
            return ''

    def get_dshhdv(self, NDHDon):
        try:
            DSHHDVu = []
            HHDVu = NDHDon.get('DSHHDVu').get('HHDVu')
            if type(HHDVu) != dict:
                for index, line in enumerate(HHDVu):
                    try:
                        TThueStr = next(item['DLieu'] for item in line['TTKhac']['TTin'] if item['@type'] == 'itemVatAmount')
                    except Exception as e:
                        TThueStr = '0'
                    TCongStr = float(line['ThTien']) + float(TThueStr)
                    DSHHDVu.append({
                        "STT": "" if line.get('TChat') == "" or line.get('TChat', '') == "4" else index + 1,
                        "TChat": line.get('TChat', ''),
                        "MHHDVu": line.get('MHHDVu', ''),
                        "THHDVu": line.get('THHDVu', ''),  # Bắt buộc
                        "DVTinh": line.get('DVTinh', ''),
                        "SLuong": float(line.get('SLuong', 0) or 0),
                        "SLuongStr": formatLang(self.env, float(line.get('SLuong', 0) or 0), digits=0) or 0,
                        "DGia": float(line.get('DGia', 0) or 0),
                        "DGiaStr": formatLang(self.env, float(line.get('DGia', 0) or 0), digits=0) or 0,
                        "TLCKhau": float(line.get('TLCKhau', 0) or 0),
                        "TLCKhauStr": formatLang(self.env, float(line.get('TLCKhau', 0) or 0), digits=0) or 0,
                        "STCKhau": float(line.get('STCKhau', 0) or 0),
                        "STCKhauStr": formatLang(self.env, float(line.get('STCKhau', 0) or 0), digits=0) or 0,
                        "ThTien": float(line.get('ThTien', 0) or 0),
                        "ThTienStr": formatLang(self.env, float(line.get('ThTien', 0) or 0), digits=0) or 0,
                        "TSuat": line.get('TSuat', '') or '',
                        "TThueStr": formatLang(self.env, float(TThueStr), digits=0) or 0,
                        "TCongStr": formatLang(self.env, TCongStr, digits=0) or 0
                    })
            else:
                try:
                    TThueStr = next(item['DLieu'] for item in HHDVu['TTKhac']['TTin'] if item['@type'] == 'itemVatAmount')
                except Exception as e:
                    TThueStr = '0'
                TCongStr = float(HHDVu.get('ThTien')) + float(TThueStr)
                
                DSHHDVu.append({
                    "STT": "" if HHDVu.get('TChat') == "" or HHDVu.get('TChat', '') == "4" else '1' ,
                    "Tchat": HHDVu.get('TChat', '') ,
                    "MHHDVu": HHDVu.get('MHHDVu', ''),
                    "THHDVu": HHDVu.get('THHDVu', ''),  # Bắt buộc
                    "DVTinh": HHDVu.get('DVTinh', ''),
                    "SLuong": float(HHDVu.get('SLuong', 0) or 0),
                    "SLuongStr": formatLang(self.env, float(HHDVu.get('SLuong', 0)), digits=0) or 0,
                    "DGia": float(HHDVu.get('DGia', 0) or 0),
                    "DGiaStr": formatLang(self.env, float(HHDVu.get('DGia', 0)), digits=0) or 0,
                    "TLCKhau": float(HHDVu.get('TLCKhau', 0) or 0),
                    "TLCKhauStr": formatLang(self.env, float(HHDVu.get('TLCKhau', 0)), digits=0) or 0,
                    "STCKhau": float(HHDVu.get('STCKhau', 0) or 0),
                    "STCKhauStr": formatLang(self.env, float(HHDVu.get('STCKhau', 0)), digits=0) or 0,
                    "ThTien": float(HHDVu.get('ThTien', 0) or 0),
                    "ThTienStr": formatLang(self.env, float(HHDVu.get('ThTien', 0)), digits=0) or 0,
                    "TSuat": HHDVu.get('TSuat', ''),
                    "TThueStr": formatLang(self.env, float(TThueStr), digits=0) or 0,
                    "TCongStr": formatLang(self.env, TCongStr, digits=0) or 0
                })
        except Exception as e:
            pass
        return DSHHDVu

    def get_footer_data(self, NDHDon):
        footer_data = []
        try:
            for index, line in enumerate(NDHDon.get('TToan',{}).get('THTTLTSuat',{}).get('LTSuat',{})):
                TCongStr = float(line.get('ThTien', "") or 0) + float(line.get('TThue', "") or 0)
                footer_data.append({
                    "STT": index+1,
                    "TSuat": line.get('TSuat', ""),
                    "ThTien": float(line.get('ThTien', "") or 0),
                    "ThTienStr": formatLang(self.env, float(line.get('ThTien')), digits=0) or 0,
                    "TThue": float(line.get('TThue', "") or 0),
                    "TThueStr": formatLang(self.env, float(line.get('TThue')), digits=0) or 0,
                    "TCongStr": formatLang(self.env, TCongStr, digits=0) or 0,
                })
            return footer_data
        except Exception as e:
            pass
        return footer_data 

    def get_footer_data2(self, NDHDon):
        footer_data2 = []
        try:
            for index, line in enumerate(NDHDon.get('TToan',{}).get('THTTLTSuat',{}).get('LTSuat',{})):
                TCongStr = float(line.get('ThTien', "") or 0) + float(line.get('TThue', "") or 0)
                footer_data2.append({
                    str(line.get('TSuat', "")):{
                        "TSuat": line.get('TSuat', ""),
                        "ThTien": float(line.get('ThTien', "") or 0),
                        "ThTienStr": formatLang(self.env, float(line.get('ThTien')), digits=0) or 0,
                        "TThue": float(line.get('TThue', "") or 0),
                        "TThueStr": formatLang(self.env, float(line.get('TThue')), digits=0) or 0,
                        "TCongStr": formatLang(self.env, TCongStr, digits=0) or 0,
                    }
                })
        except Exception as e:
            pass
        return footer_data2

    def tvan_contract_xml_json(self, data_xml):
        try:
            res = xmltodict.parse(base64.b64decode(data_xml.get('base_64')))
            return res
        except Exception as e:
            print(e)

    def btn_convert_xml_json(self):
        data_xml = {"base_64": self.inv_template_xml.decode('utf-8')}
        if self.print_type == "inv":
            json_inv = self.tvan_xml_to_json(data_xml)
            self.write(json_inv)
            return
        json_contract = self.tvan_contract_xml_json(data_xml)
        self.write({'sample_data': json.dumps(json_contract)})

    def tvan_xml_to_json(self, data):
        data_convert, template = self.convert_xml_to_json(data)
        data = {'sample_data': json.dumps(data_convert)}
        return data

    def action_confirm(self):
        self.write({'state': 'use'})

    def action_draft(self):
        self.write({'state': 'new'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def tvan_change_state_template(self, template_code, state):
        template = self.search([('code', '=', template_code)])
        if template:
            template.write({
                'state': state
            })
            return template.state
