import frappe
from frappe import _

@frappe.whitelist()
def reset_all_data():
    if frappe.session.user != "Administrator":
        frappe.throw(_("Only Administrator can perform this action."))
    # Liste des Doctypes issus de ta checkbox HTML
    doctypes = [
        # Supprimer les doctypes dépendants d'abord
        "Request for Quotation Item",
        "Supplier Quotation Item",
        "Purchase Order Item",
        "Purchase Invoice Item",
        "Purchase Receipt Item",
        "Material Request Item",
        "Stock Entry Detail",
        "GL Entry",
        "Payment Entry Reference",
        "Communication",
        "Activity Log",
        "File",
        "ToDo",
        "Workflow Action",

        # Puis les documents principaux
        "Material Request",
        "Request for Quotation",
        "Supplier Quotation",
        "Purchase Order",
        "Purchase Invoice",
        "Purchase Receipt",
        "Stock Entry",
        "Payment Entry",

        # Enfin, les entités principales
        "Item",
        "Supplier",
        "Warehouse",
        
        # Supprimer d'abord les documents dépendants
        "Salary Slip",
        "Salary Structure Assignment",
        "Salary Structure",
        "Salary Component",
        "Salary Detail",            
    	"Department",                
        "Designation",               
        "Employee"
    ]
    deleted = []
    try:
        frappe.db.sql("SET FOREIGN_KEY_CHECKS = 0")
        for doctype in doctypes:
            meta = frappe.get_meta(doctype, cached=True)
            if meta.issingle:
                continue  # ignorer les singletons
            frappe.db.delete(doctype)
            deleted.append(doctype)
        frappe.db.sql("SET FOREIGN_KEY_CHECKS = 1")
        frappe.db.commit()
        return "Reinitialisation avec succès."


    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Erreur lors de la suppression de données")
        return str(e)