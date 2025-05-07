frappe.pages['import-csv'].on_page_load = function(wrapper) {
    // Création de la page
    frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Import CSV',
        single_column: true
    });

    // HTML et CSS
    const html = `
    <style>
        /* Conteneur principal */
        .import-container {
            margin: 1rem auto;
            max-width: 600px;
        }
        /* Card ERPNext-like */
        .import-card {
            background: var(--background);
            border: 1px solid var(--border);
            border-radius: 4px;
        }
        .import-card .card-body {
            padding: 1.5rem;
        }
        .import-card .card-title {
            font-size: 1.125rem;
            font-weight: 500;
            margin-bottom: 1.5rem;
            color: var(--text-heading);
        }
        /* Form layout */
        .import-form {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }
        .import-form .form-group {
            display: flex;
            flex-direction: column;
        }
        .import-form .full-width {
            grid-column: span 2;
        }
        .import-form label {
            margin-bottom: 0.25rem;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }
        .import-form input[type="file"] {
            padding: 0.5rem;
            font-size: 0.875rem;
            border: 1px solid var(--border);
            border-radius: 4px;
            background: var(--background-secondary);
        }
        /* Bouton */
        .import-actions {
            margin-top: 1.5rem;
            text-align: right;
        }
        .btn-import {
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
            font-weight: 500;
            color: var(--btn-primary-text);
            background-color: var(--btn-primary-bg);
            border: 1px solid var(--btn-primary-bg);
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.2s;
        }
        .btn-import:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .btn-import:hover:not(:disabled) {
            background-color: var(--btn-primary-bg-hover);
            border-color: var(--btn-primary-bg-hover);
        }
        /* Message */
        #messageA {
            margin-top: 0.75rem;
            font-size: 0.875rem;
        }
    </style>

    <div class="import-container">
        <div class="import-card">
            <div class="card-body">
                <h5 class="card-title">Importation de fichiers CSV</h5>
                <form id="import-form" class="import-form">
                    <div class="form-group">
                        <label for="items_file">Items (CSV)</label>
                        <input type="file" id="items_file" accept=".csv" />
                    </div>
                    <div class="form-group">
                        <label for="suppliers_file">Suppliers (CSV)</label>
                        <input type="file" id="suppliers_file" accept=".csv" />
                    </div>
                    <div class="form-group full-width">
                        <label for="quotations_file">Quotations (CSV)</label>
                        <input type="file" id="quotations_file" accept=".csv" />
                    </div>
                    <div class="import-actions full-width">
                        <button type="submit" id="import-btn" class="btn-import">Importer</button>
                    </div>
                </form>
                <div id="messageA"></div>
            </div>
        </div>
    </div>`;

    $(wrapper).find('.layout-main-section').html(html);

    // Logique JS
    const form = wrapper.querySelector('#import-form');
    const messageEl = wrapper.querySelector('#messageA');
    const importBtn = wrapper.querySelector('#import-btn');

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        messageEl.innerText = '';

        const files = ['items_file', 'suppliers_file', 'quotations_file'].map(id => wrapper.querySelector(`#${id}`).files[0]);
        if (files.some(f => !f)) {
            messageEl.style.color = getComputedStyle(document.documentElement).getPropertyValue('--text-danger');
            messageEl.innerText = 'Veuillez sélectionner tous les fichiers.';
            return;
        }

        importBtn.disabled = true;
        importBtn.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Importation...`;

        const readFile = file => new Promise((res, rej) => {
            const r = new FileReader();
            r.onload = e => res(e.target.result);
            r.onerror = e => rej(e);
            r.readAsText(file);
        });

        Promise.all(files.map(readFile)).then(contents => {
			frappe.call({
				method: 'erpnext.db_management.page.import_csv.import_csv.import_all',
				args: {
					item_file_content: contents[0],
					supplier_file_content: contents[1],
					quotation_file_content: contents[2]
				},
				callback: resp => {
					importBtn.disabled = false;
					importBtn.innerText = 'Importer';
					if (!resp.exc) {
						frappe.msgprint({
							title: __('Succès'),
							message: resp.message,
							indicator: 'green'
						});
					} else {
						frappe.msgprint({
							title: __('Erreur d\'importation'),
							message: resp.message,
							indicator: 'red'
						});
					}
				},
				error: err => {
					importBtn.disabled = false;
					importBtn.innerText = 'Importer';
					frappe.msgprint({
						title: __('Erreur'),
						message: __('Erreur lors de l\'appel au serveur.'),
						indicator: 'red'
					});
					console.error(err);
				}
			});
		}).catch(err => {
			importBtn.disabled = false;
			importBtn.innerText = 'Importer';
			frappe.msgprint({
				title: __('Erreur'),
				message: `Une erreur est survenue : ${err.message}`,
				indicator: 'red'
			});
			console.error(err);
		});
    });
};
