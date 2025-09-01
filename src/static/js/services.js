document.addEventListener("DOMContentLoaded", function() {
    //#region SERVICE FORM
    const serviceFormDialog = document.getElementById("dialog_service-form");
    const serviceForm = document.getElementById("form_service-form");

    // Open the "Add New Service" form (click event listener)
    document.getElementById("btn_show-new-service-form").addEventListener("click", () => {
        // Set form header, button text, and form action
        document.getElementById("h2_service-form-header").innerText = "Create New Service";
        document.getElementById("btn_submit-service-form").innerText = "Add Service";
        serviceForm.action = "/services/add_service";

        openFormDialog(serviceFormDialog);
    });

    // Open the "Edit Service" form (click event listener)
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

    // Submit the Service Form (submit event listener)
    serviceForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
    
        try {
            const response = await fetch(serviceForm.action, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                data = await response.json();
                // Close the form dialog
                closeFormDialog(serviceFormDialog);
                // Either add the new service to the all services table or update the existing service in the all services table
                if (serviceForm.action.endsWith("add_service")) {
                    AddServiceToAllServicesTable(data.service);
                }
                else if (serviceForm.action.endsWith("edit_service")) {
                    EditServiceInAllServicesTable(data.service);
                }
                // Show success toast notification
                showToast("success", data.detail);
            } else {
                data = await response.json();
                if (response.status == 422) {
                    showToast("error", data.detail || "Unprocessable Entity Error");
                }
                else if(response.status == 404) {
                    closeFormDialog(serviceFormDialog);
                    showToast("error", data.detail || "Service Not Found");
                }
                else if (response.status == 500) {
                    closeFormDialog(serviceFormDialog);
                    showToast("error", data.detail || "Internal Server Error");
                }
            }
        } catch (error) {
            closeFormDialog(serviceFormDialog);
            showToast("error", error.message || "Unexpected Error");
        }
    });

    // Close the Service Form (click event listener)
    document.getElementById("btn_hide-service-form").addEventListener("click", () => {
        closeFormDialog(serviceFormDialog);
    });

    // Validate the Service Form's Unit Price Input (blur/focus lost event listener)
    // If input is NaN, show custom validation message. Otherwise, format input value to 2 decimal places.
    document.getElementById("input_service-form_unit-price").addEventListener("blur", function() {
        const value = this.value.trim();
    
        if (this.value === "") {
            this.setCustomValidity("");
            return;
        }
    
        if (isNaN(value)) {
            this.setCustomValidity("Please enter a valid number.");
            this.reportValidity();
        } else {
            this.setCustomValidity("");
            (this.value) && (this.value = Number(this.value).toFixed(2));
        }
    });
    //#endregion SERVICE FORM

    //#region REMOVE SERVICE FORM
    const removeServiceFormDialog = document.getElementById("dialog_remove-service-form");
    const removeServiceForm = document.getElementById("form_remove-service-form");

    // Open the "Remove Service" form (click event listener)
    document.querySelectorAll('[id^="btn_show-remove-service-form-"]').forEach((btn) => {
        btn.addEventListener("click", () => {
            // Populate the form with the service to remove's data
            document.getElementById("p_remove-service-form_name-placeholder").innerText = btn.dataset.name;
            document.getElementById("p_remove-service-form_description-placeholder").innerText = btn.dataset.description;
            document.getElementById("input_remove-service-form_service-id").value = btn.dataset.serviceId;

            openFormDialog(removeServiceFormDialog);
        })
    });

    // Close the "Remove Service" Form (click event listener)
    document.getElementById("btn_hide-remove-service-form").addEventListener("click", () => {
        closeFormDialog(removeServiceFormDialog);
    });

    // Submit the "Remove Service" form (submit event listener)
    removeServiceForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
    
        try {
            const response = await fetch(removeServiceForm.action, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                data = await response.json();
                // Close the form dialog, remove the service from the all services table, and show a success toast notification
                closeFormDialog(removeServiceFormDialog);
                RemoveServiceFromAllServicesTable(data.service);
                showToast("success", data.detail);
            } else {
                data = await response.json();
                if (response.status == 500) {
                    closeFormDialog(removeServiceFormDialog);
                    showToast("error", data.detail || "Internal Server Error");
                }
            }
        } catch (error) {
            closeFormDialog(removeServiceFormDialog);
            showToast("error", error.message || "Unexpected Error");
        }
    });
    //#endregion REMOVE SERVICE FORM

    //#region HELPER FUNCTIONS
    /**
     * Open a form dialog.
     * @param {HTMLDialogElement} formDialog - The form dialog to open.
     * @returns {void}
     */
    function openFormDialog(formDialog) {
        formDialog.removeAttribute("hidden");
        formDialog.showModal();
    }

    /**
     * Close a form dialog and reset its input fields.
     * @param {HTMLDialogElement} formDialog - The form dialog to close.
     * @returns {void}
     */
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

    /**
     * Show a toast notification.
     * @param {string} toastType - The type of toast notification to show (options: "success", "error").
     * @param {string} message - The message to display in the toast notification.
     * @returns {void}
     */
    function showToast(toastType, message) {
        const toast = document.getElementById(`toast-${toastType}`);
        const toastText = document.getElementById(`p_toast-${toastType}`);
    
        // Set the toast notification message text
        toastText.textContent = message;

        // Show the toast (slide in)
        toast.classList.remove("show", "hide");
        toast.classList.add("show");
    
        // Wait 3s (plus transition time), then hide the toast (slide out)
        setTimeout(() => {
            toast.classList.remove("show");
            toast.classList.add("hide");
        }, 3800);
    }

    /**
     * Add a service to the all services table.
     * @param {{ id: number, name: string, description: string, unit_price: string}} service - The service as a JSON object containing the unique ID, name, description, and unit price of the new service.
     * @returns {void}
     */
    function AddServiceToAllServicesTable(service) {
        const allServicesTableBody = document.getElementById("tbody_all-services");
        const iconHoverColor = serviceForm.dataset.iconHoverColor;

        // Icons
        const newEditIconOutlined = `
            <svg width="1.25rem", height="1.25rem" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
            </svg>
        `;
        const newEditIconSolid = `
            <svg width="1.25rem", height="1.25rem" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${iconHoverColor}">
                <path d="M21.731 2.269a2.625 2.625 0 0 0-3.712 0l-1.157 1.157 3.712 3.712 1.157-1.157a2.625 2.625 0 0 0 0-3.712ZM19.513 8.199l-3.712-3.712-12.15 12.15a5.25 5.25 0 0 0-1.32 2.214l-.8 2.685a.75.75 0 0 0 .933.933l2.685-.8a5.25 5.25 0 0 0 2.214-1.32L19.513 8.2Z" />
            </svg>
        `;
        const newDeleteIconOutlined = `
            <svg width="1.25rem", height="1.25rem" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
        `;
        const newDeleteIconSolid = `
            <svg width="1.25rem", height="1.25rem" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${iconHoverColor}">
                <path fill-rule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 0 1 3.878.512.75.75 0 1 1-.256 1.478l-.209-.035-1.005 13.07a3 3 0 0 1-2.991 2.77H8.084a3 3 0 0 1-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 0 1-.256-1.478A48.567 48.567 0 0 1 7.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 0 1 3.369 0c1.603.051 2.815 1.387 2.815 2.951Zm-6.136-1.452a51.196 51.196 0 0 1 3.273 0C14.39 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 0 0-6 0v-.113c0-.794.609-1.428 1.364-1.452Zm-.355 5.945a.75.75 0 1 0-1.5.058l.347 9a.75.75 0 1 0 1.499-.058l-.346-9Zm5.48.058a.75.75 0 1 0-1.498-.058l-.347 9a.75.75 0 0 0 1.5.058l.345-9Z" clip-rule="evenodd" />
            </svg>
        `;

        // Create a new <tr> element and set its id and inner HTML
        const newRow = document.createElement("tr");
        newRow.id = `tr_service-${service.id}`;
        newRow.innerHTML = `
            <td class="p-4">${service.name}</td>
            <td class="p-4">${service.description}</td>
            <td class="p-4 text-center">$${Number(service.unit_price).toFixed(2)}</td>
            <td class="flex flex-row gap-4 p-4">
                <!-- Edit Service Buttons -->
                <button
                    id="btn_show-edit-service-form-${service.id}"
                    data-name="${service.name}"
                    data-description="${service.description}"
                    data-unit-price="${service.unit_price}"
                    data-service-id="${service.id}"
                    class="cursor-pointer group"
                >
                    <div class="icon-wrapper overflow-hidden flex-shrink-0">
                        <span class="icon outline">${newEditIconOutlined}</span>
                        <span class="icon solid">${newEditIconSolid}</span>
                    </div>
                </button>
                <!-- Remove Service Buttons -->
                <button
                    id="btn_show-remove-service-form-${service.id}"
                    data-name="${service.name}"
                    data-description="${service.description}"
                    data-service-id="${service.id}"
                    class="cursor-pointer group"
                >
                    <div class="icon-wrapper overflow-hidden flex-shrink-0">
                        <span class="icon outline">${newDeleteIconOutlined}</span>
                        <span class="icon solid">${newDeleteIconSolid}</span>
                    </div>
                </button>
            </td>
        `;

        // Append the new <tr> element to the table body
        allServicesTableBody.appendChild(newRow);

        // Open the "Edit Service" form (click event listener)
        document.getElementById(`btn_show-edit-service-form-${service.id}`).addEventListener("click", (e) => {
            // Set form header, button text, and form action
            document.getElementById("h2_service-form-header").innerText = "Edit Service Details";
            document.getElementById("btn_submit-service-form").innerText = "Update";
            serviceForm.action = "/services/edit_service";

            // Populate form with the service to edit's data
            document.getElementById("input_service-form_name").value = e.currentTarget.dataset.name;
            document.getElementById("input_service-form_unit-price").value = Number(e.currentTarget.dataset.unitPrice).toFixed(2);
            document.getElementById("textarea_service-form_description").value = e.currentTarget.dataset.description;
            document.getElementById("input_service-form_service-id").value = e.currentTarget.dataset.serviceId;

            openFormDialog(serviceFormDialog);
        });

        // Open the "Remove Service" form (click event listener)
        document.getElementById(`btn_show-remove-service-form-${service.id}`).addEventListener("click", (e) => {
            // Populate the form with the service to remove's data
            document.getElementById("p_remove-service-form_name-placeholder").innerText = e.currentTarget.dataset.name;
            document.getElementById("p_remove-service-form_description-placeholder").innerText = e.currentTarget.dataset.description;
            document.getElementById("input_remove-service-form_service-id").value = e.currentTarget.dataset.serviceId;

            openFormDialog(removeServiceFormDialog);
        });
    }

    /**
     * Edit a service in the all services table.
     * @param {{ id: number, name: string, description: string, unit_price: string}} service - The service as a JSON object containing the unique ID, name, description, and unit price of the updated service.
     * @returns {void}
     */
    function EditServiceInAllServicesTable(service) {
        const serviceRow = document.getElementById(`tr_service-${service.id}`);

        serviceRow.getElementsByTagName("td")[0].innerText = service.name;
        serviceRow.getElementsByTagName("td")[1].innerText = service.description;
        serviceRow.getElementsByTagName("td")[2].innerText = `$${Number(service.unit_price).toFixed(2)}`;
    }

    /**
     * Remove a service from the all services table.
     * @param {{ id: number }} service - The service as a JSON object containing the unique ID of the removed service.
     * @returns {void}
     */
    function RemoveServiceFromAllServicesTable(service) {
        document.getElementById(`tr_service-${service.id}`).remove();
    }
    //#endregion HELPER FUNCTIONS
});