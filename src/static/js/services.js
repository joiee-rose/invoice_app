document.addEventListener('DOMContentLoaded', function() {
    //#region SERVICE FORM
    const serviceFormDialog = document.getElementById("dialog_service-form");
    const serviceForm = document.getElementById("form_service-form");

    // Click event listener to open the "Add New Service" form
    document.getElementById("btn_show-new-service-form").addEventListener("click", () => {
        // Set form header, button text, and form action
        document.getElementById("h2_service-form-header").innerText = "Create New Service";
        document.getElementById("btn_submit-service-form").innerText = "Add Service";
        serviceForm.action = "/services/add_service";

        openFormDialog(serviceFormDialog);
    });

    // Click event listener to open to "Edit Service" form
    document.querySelectorAll('[id^="btn_show-edit-service-form-"]').forEach((btn) => {
        btn.addEventListener("click", () => {
            // Set form header, button text, and form action
            document.getElementById("h2_service-form-header").innerText = "Edit Service Details";
            document.getElementById("btn_submit-service-form").innerText = "Update";
            serviceForm.action = "/services/edit_service";

            // Populate form with the service to edit's data
            document.getElementById("input_service-form_name").value = btn.dataset.name;
            document.getElementById("input_service-form_unit-price").value = Number(btn.dataset.unitPrice).toFixed(2);
            document.getElementById("textarea_service-form_description").value = btn.dataset.description;
            document.getElementById("input_service-form_service-id").value = btn.dataset.serviceId;

            openFormDialog(serviceFormDialog);
        });
    });

    // Click event listener to close the service form
    document.getElementById("btn_hide-service-form").addEventListener("click", () => {
        closeFormDialog(serviceFormDialog);
    });

    // Format unit price input to 2 decimal places when focus is lost
    document.getElementById("input_service-form_unit-price").addEventListener("blur", function() {
        (this.value) && (this.value = Number(this.value).toFixed(2));
    });
    //#endregion SERVICE FORM

    //#region REMOVE SERVICE FORM
    const removeServiceFormDialog = document.getElementById("dialog_remove-service-form");

    // Click event listener to open the remove service form
    document.querySelectorAll('[id^="btn_show-remove-service-form-"]').forEach((btn) => {
        btn.addEventListener("click", () => {
            // Populate the form with the service to remove's data
            document.getElementById("p_remove-service-form_name-placeholder").innerText = btn.dataset.name;
            document.getElementById("p_remove-service-form_description-placeholder").innerText = btn.dataset.description;
            document.getElementById("input_remove-service-form_service-id").value = btn.dataset.serviceId;

            openFormDialog(removeServiceFormDialog);
        })
    });

    // Click event listener to close the remove service form
    document.getElementById("btn_hide-remove-service-form").addEventListener("click", () => {
        closeFormDialog(removeServiceFormDialog);
    });
    //#endregion REMOVE SERVICE FORM

    //#region HELPER FUNCTIONS
    function openFormDialog(formDialog) {
        formDialog.removeAttribute("hidden");
        formDialog.showModal();
    }

    function closeFormDialog(formDialog) {
        Array.from(formDialog.getElementsByTagName("input")).forEach((input) => {
            input.value = "";
        });
        Array.from(formDialog.getElementsByTagName("textarea")).forEach((textarea) => {
            textarea.value = "";
        });

        formDialog.setAttribute("hidden", "hidden");
        formDialog.close();
    }
    //#endregion HELPER FUNCTIONS
});