import frappe
from frappe import _
from frappe.utils import nowdate, getdate
import pycountry


@frappe.whitelist()
def import_all(item_file_content, supplier_file_content, quotation_file_content):
    try:
        # Parse CSV contents
        items_data = frappe.utils.csvutils.read_csv_content(item_file_content)
        suppliers_data = frappe.utils.csvutils.read_csv_content(supplier_file_content)
        quotations_data = frappe.utils.csvutils.read_csv_content(quotation_file_content)

        item_headers, item_rows = items_data[0], items_data[1:]
        sup_headers, sup_rows = suppliers_data[0], suppliers_data[1:]
        quo_headers, quo_rows = quotations_data[0], quotations_data[1:]

        frappe.db.begin()
        create_warehouses(item_rows, item_headers)
        create_countries(sup_rows, sup_headers)
        create_suppliers(sup_rows, sup_headers)
        create_item_groups(item_rows, item_headers)
        create_items(item_rows, item_headers)
        material_data = group_items_by_ref(item_rows, item_headers)
        material_requests = create_material_requests(material_data)
        create_rfq_and_quotations(quo_rows, quo_headers, material_requests)

        frappe.db.commit()
        return _('Import successful.')

    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), 'Import Error')
        return _('Error: {0}').format(str(e))


def create_countries(sup_rows, sup_headers):
    countries = set([row[sup_headers.index('country')] for row in sup_rows])
    for country in countries:
        if not frappe.db.exists("Country", {"country_name": country}):
            try:
                country_info = pycountry.countries.search_fuzzy(country)[0]
                frappe.get_doc({
                    "doctype": "Country",
                    "country_name": country,
                    "code": country_info.alpha_2
                }).insert(ignore_permissions=True)
            except Exception:
                frappe.log_error(f"Failed to create country: {country}")


def create_suppliers(sup_rows, sup_headers):
    for row in sup_rows:
        vals = dict(zip(sup_headers, row))
        name = vals.get('supplier_name')
        if name and not frappe.db.exists("Supplier", name):
            frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": name,
                "country": vals.get('country'),
                "supplier_type": vals.get('type')
            }).insert(ignore_permissions=True)


def create_item_groups(item_rows, item_headers):
    groups = set([row[item_headers.index('item_groupe')] for row in item_rows])
    for group in groups:
        if not frappe.db.exists("Item Group", group):
            frappe.get_doc({
                "doctype": "Item Group",
                "item_group_name": group,
                "parent_item_group": "All Item Groups",
                "is_group": 0
            }).insert(ignore_permissions=True)


def create_items(item_rows, item_headers):
    for row in item_rows:
        vals = dict(zip(item_headers, row))
        code = vals.get('item_name')
        if code and not frappe.db.exists("Item", code):
            frappe.get_doc({
                "doctype": "Item",
                "item_code": code,
                "item_name": code,
                "description": vals.get('description', _('Auto generated item')),
                "item_group": vals.get('item_groupe') or 'Consumable',
                "stock_uom": 'Nos',
                "is_stock_item": 1,
                "maintain_stock": 1,
                "is_purchase_item": 1,
                "is_sales_item": 0,
            }).insert(ignore_permissions=True)

def create_warehouses(item_rows, item_headers):
    warehouses = set([row[item_headers.index('target_warehouse')] for row in item_rows])
    company = frappe.defaults.get_user_default('Company')
    abbr = frappe.db.get_value('Company', company, 'abbr')
    for warehouse in warehouses:
        if not frappe.db.exists("Warehouse", warehouse):
            frappe.get_doc({
                "doctype": "Warehouse",
                "warehouse_name": warehouse,
                "company": company,
                "is_group": 0,
                "parent_warehouse": None,
                "group_or_warehouse": 1
            }).insert(ignore_permissions=True)
            
def group_items_by_ref(item_rows, item_headers):
    material_data = {}
    for i,row in enumerate(item_rows):
        vals = dict(zip(item_headers, row))
        ref = vals.get('ref')
        from datetime import datetime

        date_str = vals.get('date')
        required_str = vals.get('required_by')

        # ⚠️ Précise le format: jour/mois/année
        date = datetime.strptime(date_str, '%d/%m/%Y').date()
        required = datetime.strptime(required_str, '%d/%m/%Y').date()
        # ✅ Ajout de validation de date
        if required < date:
            frappe.throw(_(f"Ligne #{i+1} (ref {ref}): 'Required By' ({required})({required_str}) ne peut pas précéder la date de transaction ({date})({date_str})."))

        purpose = vals.get('purpose')
        company = frappe.defaults.get_user_default('Company')
        abbr = frappe.db.get_value('Company', company, 'abbr')
        warehouse = vals.get('target_warehouse') or 'Stores'
        wh = f"{warehouse} - {abbr}"

        quantity = float(vals.get('quantity') or 0)
        if quantity < 0:
            frappe.throw(_(f"Quantité invalide !{row}"))
        item_entry = {
            'item_code': vals.get('item_name'),
            'qty': quantity,
            'warehouse': wh,
            'schedule_date': required
        }

        if ref not in material_data:
            material_data[ref] = {
                'transaction_date': date,
                'schedule_date': required,
                'purpose': purpose,
                'items': [item_entry]
            }
        else:
            material_data[ref]['items'].append(item_entry)
    return material_data


def create_material_requests(material_data):
    material_requests = {}
    for ref, data in material_data.items():
        mr = frappe.get_doc({
            'doctype': 'Material Request',
            'naming_series': 'MAT-MR-.YYYY.-',
            'transaction_date': data['transaction_date'],
            'schedule_date': data['schedule_date'],
            'company': frappe.defaults.get_user_default('Company'),
            'material_request_type': data['purpose'],
            'items': data['items']
        })
        mr.insert()
        mr.submit()
        material_requests[str(ref)] = mr.name
    return material_requests


def create_rfq_and_quotations(quo_rows, quo_headers, material_requests):
    for row in quo_rows:
        vals = dict(zip(quo_headers, row))
        ref = str(vals.get('ref_request_quotation'))
        if ref in material_requests:
            mr_name = material_requests[ref]
            mr_doc = frappe.get_doc('Material Request', mr_name)

            rfq = frappe.get_doc({
                'doctype': 'Request for Quotation',
                'naming_series': 'PUR-RFQ-.YYYY.-',
                'company': frappe.defaults.get_user_default('Company'),
                'transaction_date': mr_doc.transaction_date,
                'status': 'Submitted',
                'message_for_supplier': vals.get('message_for_supplier') or _('Please submit your best quotation.'),
                'suppliers': [{'supplier': vals.get('supplier')}],
                'items': [{
                    'item_code': item.item_code,
                    'qty': item.qty,
                    'warehouse': item.warehouse,
                    'uom': 'Nos',
                    'conversion_factor': 1.0,
                    'schedule_date': item.schedule_date
                } for item in mr_doc.items]
            })
            rfq.insert()
            rfq.submit()
            rfq.reload()

            sq_items = []
            for i, item in enumerate(mr_doc.items):
                rfq_item = rfq.items[i]
                sq_items.append({
                    'item_code': item.item_code,
                    'qty': item.qty,
                    'warehouse': item.warehouse,
                    'uom': 'Nos',
                    'conversion_factor': 1.0,
                    'schedule_date': item.schedule_date,
                    'request_for_quotation': rfq.name,
                    'request_for_quotation_item': rfq_item.name,
                    'material_request': mr_doc.name,
                    'material_request_item': item.name
                })

            sq = frappe.get_doc({
                'doctype': 'Supplier Quotation',
                'supplier': vals.get('supplier'),
                'company': frappe.defaults.get_user_default('Company'),
                'transaction_date': mr_doc.transaction_date,
                'items': sq_items
            })
            sq.insert()
        else:
            frappe.throw(_(f"Material Request not found for reference: {ref}"))
