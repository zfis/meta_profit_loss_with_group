import re
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, tools, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
from odoo.osv import expression
from odoo.tools import float_compare, pycompat
from odoo.addons import decimal_precision as dp


class ProfitLossGroupReportData(models.TransientModel):
    _name = 'profit.loss.group.report.data.meta'
    # _order = 'priority asc,layer asc,id asc'
    _order = 'priority asc,id asc'

    date = fields.Date('Date')
    account_id = fields.Many2one('account.account','Account')
    group_id = fields.Many2one('account.group','Account group')
    credit = fields.Float('Credit')
    debit = fields.Float('Debit')
    balance = fields.Float('Balance')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id.id)

    account_name = fields.Char('Account Name')
    group_name = fields.Char('Group Name')
    account_type_name = fields.Char('Account type')
    layer = fields.Integer('Layer')
    layer_limit = fields.Integer('Layer Limit')
    priority = fields.Integer('Layer')
    
    start_date = fields.Date('start date')
    end_date = fields.Date('start date')
    display_debit_credit = fields.Boolean("Display Debit/Credit")
