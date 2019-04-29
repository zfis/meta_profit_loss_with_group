from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class ProfitLossGroupReportWizard(models.Model):
    _name = 'profit.loss.group.report.wizard.meta'

    from_date = fields.Date('From Date', default=lambda self: fields.datetime.now(), required=True)
    to_date = fields.Date('To Date', default=lambda self: fields.datetime.now(), required=True)

    display_debit_credit = fields.Boolean("Display Debit/Credit")
    layer_limit = fields.Selection([(100,'All Layer'),(2,'Top Layer'),(3,'Top 2 Layer'),(4,'Top 3 Layer'),(5,'Top 4 Layer'),
    (6,'Top 5 Layer'),(7,'Top 6 Layer')], "Account Group Layer", default=100, required=True)

    @api.multi
    def get_group_list(self, group_id):
        if not group_id.parent_id:
            return [group_id,]
        else:
            return self.get_group_list(group_id.parent_id) + [group_id,]
    
    @api.multi
    def data_creation(self, group_map, account_map, group_id, layer):
        if group_id.id in group_map.keys():
            group_map[group_id.id]['layer'] = layer
            # group_map[group_id.id]['balance'] = group_map[group_id.id]['debit'] - group_map[group_id.id]['credit']
            self.env['profit.loss.group.report.data.meta'].create(group_map[group_id.id])
            
            child_group_ids = self.env['account.group'].search([['parent_id','=',group_id.id]])
            for child_group_id in child_group_ids:
                self.data_creation(group_map, account_map, child_group_id, layer+1)

            for account_id in group_id.account_ids:
                if account_id.id in account_map.keys():
                    account_map[account_id.id]['layer'] = layer+1
                    self.env['profit.loss.group.report.data.meta'].create(account_map[account_id.id])


        # child_group_ids = self.env['account.group'].search([['parent_id','=',group_id.id]])
        # for child_group_id in child_group_ids:
        #     self.data_creation(group_map, account_map, child_group_id, layer+1)

    @api.multi
    def done(self):
        # raise UserError(self.number_of_layer)
        self.env.cr.execute(""" TRUNCATE TABLE test_balance_sheet_report_data_meta; """)

        # account_type_list = ["Receivable","Payable","Bank and Cash","Credit Card","Current Assets","Non-current Assets",
        # "Prepayments","Fixed Assets", "Current Liabilities", "Non-current Liabilities", "Equity", "Current Year Earnings",]

        account_type_list = ["Income","Other Income","Cost of Revenue","Expenses","Depreciation", ]
        account_type_reverse_cal = ["Income","Other Income",]

        account_type_priority = [0,1,2,3,4,5,6,7,8,9,10,11]

        group_map= dict()
        account_map= dict()
        
        all_account_ids = self.env['account.account'].search([['company_id','=',self.env.user.company_id.id]])
        for account_id in all_account_ids:
            account_type = account_id.user_type_id.name 
            if account_type in account_type_list:

                total_db = 0
                total_cr = 0
                all_filtered_journal_items = self.env['account.move.line'].search([['account_id','=',account_id.id],['date','>=',self.from_date],['date','<=',self.to_date]])
                for item in all_filtered_journal_items:
                    total_db += item.debit
                    total_cr += item.credit
                
                pr = account_type_list.index(account_id.user_type_id.name)
                balance = total_db -total_cr
                if account_type in account_type_reverse_cal:
                    balance = total_cr - total_db


                account_map[account_id.id]={
                    'account_name': account_id.name,
                    'account_id': account_id.id,
                    'display_debit_credit': self.display_debit_credit,
                    'start_date': self.from_date,
                    'end_date': self.to_date,
                    'debit': total_db,
                    'credit': total_cr,
                    'balance': balance,
                    'priority': pr,
                    'layer_limit':self.layer_limit,
                }

                if account_id.group_id:
                    group_list = self.get_group_list( account_id.group_id)
                    for group_id in group_list:
                        if group_id.id not in group_map.keys():
                            group_map[group_id.id]={
                                # 'group_name': group_id.name,
                                'group_id': group_id.id,
                                'display_debit_credit': self.display_debit_credit,
                                'start_date': self.from_date,
                                'end_date': self.to_date,
                                'debit': 0,
                                'credit': 0,
                                'balance': 0,
                                'priority':10000,
                                'layer_limit':self.layer_limit,
                            }
                        group_map[group_id.id]['debit'] += total_db
                        group_map[group_id.id]['credit'] += total_cr
                        if account_type in account_type_reverse_cal:
                            group_map[group_id.id]['balance'] = group_map[group_id.id]['credit'] - group_map[group_id.id]['debit']
                        else:
                            group_map[group_id.id]['balance'] = group_map[group_id.id]['debit'] - group_map[group_id.id]['credit']

                        if group_map[group_id.id]['priority'] > pr:
                            group_map[group_id.id]['priority'] = pr

        

        #Income Entries
        inc_group_id = self.env['account.group'].search([['code_prefix','=','4'],['level','=',1]])
        self.data_creation(group_map, account_map, inc_group_id, 1)

             

        #Cost of Good sold
        cor_group_id = self.env['account.group'].search([['code_prefix','=','5'],['level','=',1]])
        self.data_creation(group_map, account_map, cor_group_id, 1)

        tdb = group_map[inc_group_id.id]['debit'] - group_map[inc_group_id.id]['debit']
        tcr = group_map[cor_group_id.id]['credit'] - group_map[cor_group_id.id]['credit']

        gross_profit = group_map[inc_group_id.id]['balance'] - group_map[cor_group_id.id]['balance']

        values = {
            'group_name': "Gross Profit",
            'display_debit_credit': self.display_debit_credit,
            'start_date': self.from_date,
            'end_date': self.to_date,
            'debit': tdb,
            'credit': tcr,
            'balance': gross_profit,
            'layer':1,
            'layer_limit':self.layer_limit,
            'priority':2,
        }
        self.env['profit.loss.group.report.data.meta'].create(values)  

        #Expense Entires
        exp_group_id = self.env['account.group'].search([['code_prefix','=','6'],['level','=',1]])
        self.data_creation(group_map, account_map, exp_group_id, 1)
        
        tdb -= group_map[exp_group_id.id]['debit']
        tcr -= group_map[exp_group_id.id]['credit']
        net_profit = gross_profit - group_map[exp_group_id.id]['balance']

        values = {
            'group_name': "Net Profit",
            'display_debit_credit': self.display_debit_credit,
            'start_date': self.from_date,
            'end_date': self.to_date,
            'debit': tdb,
            'credit': tcr,
            'balance': net_profit,
            'layer':1,
            'layer_limit':self.layer_limit,
            'priority':10,
        }
        self.env['profit.loss.group.report.data.meta'].create(values) 
        
            
        # raise UserError(all_filtered_payment_record)
        docids = self.env['profit.loss.group.report.data.meta'].search([])
        if len(docids)>0:
            return self.env['report'].get_action(docids, 'meta_profit_loss_with_group.test_balance_sheet_report_document')
        else:
            raise UserError("No Record Found")       

