{
    "name": "Meta Profit and Loss Report With Group Feature",
    "category": 'Accounting',
    "summary": """Apps will create a profit and loss report with multi-level group features.""",
    "description": """Apps will create a profit and loss report with multi-level grouping of different account.""",
    "sequence": 1,
    "version": '1.0',
    "author": "Metamorphosis",
    'company': 'Metamorphosis Limited',
    'website': 'metamorphosis.com.bd',
    "depends": ['account','custom_report','account_group_menu'],
    "data": [
        'views/balance_sheet_report_wizard.xml',
        'views/balance_sheet_report.xml',
    ],
    'icon': "/meta_profit_loss_with_group/static/description/icon.png",
    "images": ["static/description/banner.png"],
    "installable": True,
    "application": True,
    "auto_install": False,
}
