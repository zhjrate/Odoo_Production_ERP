# -*- coding: utf-8 -*-
from odoo import api, fields, models,  _
import time
from odoo.exceptions import UserError
from ast import literal_eval
# import json
import xlwt
from io import StringIO
import base64
import platform

class LowStockreportXls(models.Model):
    _name = 'low.stockreport.xls'
    _description = 'Low Stock Report'

    name_data = fields.Char('Name', size=256)
    file_name = fields.Binary('Click to download', readonly=True)
    
class ProductLowStockReport(models.AbstractModel):
    _name = 'report.ip_product_low_stock_notification.report_stock_menu'
    _description = "product low stock report"

    def get_low_stock_products(self, data):
        domain = []
        product_list = []
        product_list2 = []
        product_list3 =[]
        product_list4 =[]
        return_list = {}
        StockQuantObj = self.env['stock.quant']
        stock_notification_type = data['form']['stock_notification']
        min_qty = data['form']['minimum_qty']
        company_ids = data['form']['company_ids']
        location_ids = data['form']['stock_lctn_id']
        if not location_ids:
            raise UserError("Please Select Location")
        return_list['type'] = stock_notification_type
        return_list['min_qty'] = min_qty
        total_qty = 0
        unreserved_qty = 0
        unreserved_qty = 0
        if company_ids and company_ids:
            domain += [('company_id', 'in', company_ids)]
        if location_ids:
            loc = location_ids[0]
            domain += ['|', ('location_id', '=', loc), ('location_id', 'child_of', loc)]
        # if stock_notification_type == 'global':
        #     product_ids = self.env['product.product'].search([('type', 'not in', ['service'])])
        #     for product_id in product_ids:
        #         product_domain = [('product_id', '=', product_id.id)]
        #         quant_ids = StockQuantObj.search(domain + product_domain)
        #         for quant_id in quant_ids:
        #             if quant_id.quantity < min_qty:
        #                 product_list.append(quant_id)
        #         return_list['quant_ids'] = product_list
        if stock_notification_type == 'individual':
            product_ids = self.env['product.product'].search([('type', 'not in', ['service'])])
            for product_id in product_ids:
                product_domain = [('product_id', '=', product_id.id)]
                quant_ids = StockQuantObj.search(domain + product_domain)
                tot_qty = sum(quant_id.quantity for quant_id in quant_ids)
                reserved_qty = sum(quant_id.reserved_quantity for quant_id in quant_ids)
                #if reserved_qty:
                unreserved_qty = tot_qty - reserved_qty
                for quant_id in quant_ids:
                    if tot_qty < product_id.minimum_qty:
                        c=quant_id.product_id.id
                        d=[quant_id.product_id.display_name,tot_qty,product_id.minimum_qty,quant_id.product_uom_id.name,unreserved_qty,quant_id.product_id.batch_size,quant_id.product_id.name,quant_id.product_id.default_code,quant_id.location_id.complete_name]
                        product_detail1 = {'id':c,'values':d}
                        product_list3.append(product_detail1)
            list_quant = product_list3
            new_v =[]
            for y in list_quant:
                if y not in new_v:
                    new_v.append(y)
            for dt in new_v:
                product_detail3 = []
                product_detail3.append(dt['values'][0])
                product_detail3.append(dt['values'][1])
                product_detail3.append(dt['values'][2])
                product_detail3.append(dt['values'][3])
                product_detail3.append(dt['values'][4])
                product_detail3.append(dt['values'][5])
                product_detail3.append(dt['values'][6])
                product_detail3.append(dt['values'][7])
                product_detail3.append(dt['values'][8])
                product_list4.append(product_detail3)
            return_list['quant_ids'] = product_list4
            return_list['location_ids'] = location_ids[1]
    
                       
                        
                # return_list['quant_ids'] = product_list
        if stock_notification_type == 'reorder':
            # raise UserError("reorder")
            # if location_ids:
            #     raise UserError(location_ids)
            reordering_rule_ids = self.env['stock.warehouse.orderpoint'].search([])
            for rule_id in reordering_rule_ids:
                product_domain = [('product_id', '=', rule_id.product_id.id)]
                quant_ids = StockQuantObj.search(domain + product_domain)
                total_qty = sum(quant_id.quantity for quant_id in quant_ids)
                reserved_qty = sum(quant_id.reserved_quantity for quant_id in quant_ids)
                # total_qty = -(total_qty)
                #if reserved_qty:
                unreserved_qty = total_qty - reserved_qty
                for quant_id in quant_ids:
                    if total_qty < rule_id.product_min_qty:
                        a=quant_id.product_id.id
                        b=[quant_id.product_id.display_name,total_qty,rule_id.product_min_qty,quant_id.product_uom_id.name,unreserved_qty,quant_id.product_id.batch_size,quant_id.product_id.name,quant_id.product_id.default_code,quant_id.location_id.complete_name]
                        product_detail = {'id':a,'values':b}
                        product_list.append(product_detail)
            list_quants = product_list
            # if product_list:
            #     raise UserError(product_list)
            new_d = []
            for x in list_quants:
                if x not in new_d:
                    new_d.append(x)

            for data in new_d:
                product_detail2 = []
                product_detail2.append(data['values'][0])
                product_detail2.append(data['values'][1])
                product_detail2.append(data['values'][2])
                product_detail2.append(data['values'][3])
                product_detail2.append(data['values'][4])
                product_detail2.append(data['values'][5])
                product_detail2.append(data['values'][6])
                product_detail2.append(data['values'][7])
                product_detail2.append(data['values'][8])
                product_list2.append(product_detail2)
            return_list['quant_ids'] = product_list2
            return_list['location_ids'] = location_ids[1]
        return return_list

    def get_low_stock_products_mail(self):
        domain = []
        product_list = []
        return_list = {}
        StockQuantObj = self.env['stock.quant']

        get_param = self.env['ir.config_parameter'].sudo().get_param
        stock_notification_type = get_param('ip_product_low_stock_notification.stock_notification')
        min_qty = float(get_param('ip_product_low_stock_notification.minimum_qty'))
        company_ids = literal_eval(get_param('ip_product_low_stock_notification.company_ids'))
        location_ids = literal_eval(get_param('ip_product_low_stock_notification.location_ids'))
        return_list['type'] = stock_notification_type
        return_list['min_qty'] = min_qty

        if company_ids and company_ids:
            domain += [('company_id', 'in', company_ids)]
        if location_ids and location_ids:
            domain += ['|', ('location_id', 'in', location_ids), ('location_id', 'child_of', location_ids)]
        # if stock_notification_type == 'global':
        #     product_ids = self.env['product.product'].search([('type', 'not in', ['service'])])
        #     for product_id in product_ids:
        #         product_domain = [('product_id', '=', product_id.id)]
        #         quant_ids = StockQuantObj.search(domain + product_domain)
        #         for quant_id in quant_ids:
        #             if quant_id.quantity < min_qty:
        #                 product_list.append(quant_id)
        #         return_list['quant_ids'] = product_list
        if stock_notification_type == 'individual':
            product_ids = self.env['product.product'].search([('type', 'not in', ['service'])])
            for product_id in product_ids:
                product_domain = [('product_id', '=', product_id.id)]
                quant_ids = StockQuantObj.search(domain + product_domain)
                for quant_id in quant_ids:
                    if quant_id.quantity < product_id.minimum_qty:
                        product_list.append(quant_id)
                return_list['quant_ids'] = product_list
        if stock_notification_type == 'reorder':
            reordering_rule_ids = self.env['stock.warehouse.orderpoint'].search([])
            for rule_id in reordering_rule_ids:
                product_domain = [('product_id', '=', rule_id.product_id.id)]
                quant_ids = StockQuantObj.search(domain + product_domain)
                for quant_id in quant_ids:
                    if quant_id.quantity < rule_id.product_min_qty:
                        product_detail = []
                        product_detail.append(quant_id.product_id.display_name)
                        product_detail.append(quant_id.location_id.display_name)
                        product_detail.append(quant_id.quantity)
                        product_detail.append(rule_id.product_min_qty)
                        product_detail.append(quant_id.product_uom_id.name)
                        product_list.append(product_detail)
        return_list['quant_ids'] = product_list
        return return_list

    @api.model
    def _get_report_values(self, docids, data=None):
        low_product = []
        if self.env.context.get('send_email', False):
            self.model = 'stock.quant'
            low_product = self.get_low_stock_products_mail()
        else:
            if not data.get('form'):
                raise UserError(_("Content is missing, this report cannot be printed."))
            self.model = self.env.context.get('active_model')
            low_product = self.get_low_stock_products(data)
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'time': time,
            'low_stock': low_product,
        }


    def print_low_stock_xls_report(self,data):
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet("Low Stock Report")
        format1 = xlwt.easyxf('font: bold 1, color white;\
                     pattern: pattern solid, fore_color black;')
        first_col = sheet.col(0)
        two_col = sheet.col(1)
        three_col = sheet.col(2)
        fourth_col = sheet.col(3)
        fifth_col = sheet.col(4)
        sixth_col = sheet.col(5)
        seventh_col = sheet.col(6)
        eight_col = sheet.col(7)
        
        sheet.write(0,0,'Item Code',format1)
        sheet.write(0,1,'Item Name',format1)
        sheet.write(0,2,'Location',format1)
        sheet.write(0,3,'Min Stock',format1)
        sheet.write(0,4,'Onhand Qty',format1)
        sheet.write(0,5,'Unreserved Qty',format1)
        sheet.write(0,6,'Batch Size',format1)
        sheet.write(0,7,'UOM',format1)
        data = self.get_low_stock_products(data)
        dt = data.get('quant_ids')
        row_number = 1
        for value in dt:
            sheet.write(row_number,0,value[7])
            sheet.write(row_number,1,value[6])
            sheet.write(row_number,2,value[8])
            sheet.write(row_number,3,value[2])
            sheet.write(row_number,4,value[1])
            sheet.write(row_number,5,value[4])
            sheet.write(row_number,6,value[5])
            sheet.write(row_number,7,value[3])
            row_number +=1
        output = StringIO()
        if platform.system() == 'Linux':
            filename = ('/tmp/Low Stock Report' +'.xls')
        else:
            filename = ('Low Stock Report' +'.xls')

        workbook.save(filename)
        fp = open(filename, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)
        # Files actions
        attach_vals = {
                'name_data': 'Low Stock Report'+ '.xls',
                'file_name': out,
        }
        act_id = self.env['low.stockreport.xls'].create(attach_vals)
        fp.close()
        return act_id


