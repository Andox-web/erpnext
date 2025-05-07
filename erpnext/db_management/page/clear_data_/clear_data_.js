frappe.pages['clear-data-'].on_page_load = function(wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Clear Data Test',
		single_column: true
	});

	// Injecter le HTML dans la section principale
	$(wrapper).find('.layout-main-section').html(`
		<div class="section-body">
		  <div class="frappe-card" style="max-width: 600px; margin: 0 auto;">
			<div class="card-body">
			  <h3 class="mb-3">Réinitialisation des données</h3>
			  <p class="text-muted mb-4">
				Cliquez sur le bouton ci-dessous pour vider les données personnalisées. Cette action est irréversible.
			  </p>
			  <button id="reset-data-btn" class="btn btn-danger">
				<i class="fa fa-exclamation-triangle mr-1"></i>
				Réinitialiser
			  </button>
			</div>
		  </div>
		</div>
	  `);
	  

	// Gestion du clic
	$('#reset-data-btn').on('click', function() {
		frappe.confirm(
			'Êtes-vous sûr de vouloir réinitialiser les données ? Cette action est irréversible.',
			() => {
				frappe.call({
					method: 'erpnext.db_management.page.clear_data_.clear_data_.reset_all_data',
					callback: (r) => {
						if (r.message) {
							frappe.msgprint({
								title: 'Terminé',
								message: r.message,
								indicator: 'green'
							});
						}
					}
				});
			}
		);
	});
};