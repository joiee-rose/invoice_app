document.addEventListener("DOMContentLoaded", function() {
    const toastType = localStorage.getItem("toastType");
    const toastMessage = localStorage.getItem("toastMessage");

    // Show stored toast message after a reload
    if (toastType && toastMessage) {
        setTimeout(() => {
            showToast(toastType, toastMessage);
            // Clear the message so it doesn't show again on next reload
            localStorage.removeItem("toastType");
            localStorage.removeItem("toastMessage");
        }, 3);
    }

    //#region SERVICE FORM
    const serviceFormDialog = document.getElementById("dialog_service-form");
    const serviceForm = document.getElementById("form_service-form");

    ////////////////////////
    /* Open/Close Events */
    //////////////////////

        // Open the "Add New Service" form
        document.getElementById("btn_show-new-service-form").addEventListener("click", () => {
            openAddNewServiceForm();
        });

        // Open the "Edit Service" form*
        document.querySelectorAll('[id^="btn_show-edit-service-form-"]').forEach((btn) => {
            btn.addEventListener("click", (e) => {
                openEditServiceForm(e.currentTarget);
            });
        });

        // Close the Service Form
        document.getElementById("btn_hide-service-form").addEventListener("click", () => {
            closeFormDialog(serviceFormDialog);
        });

    //////////////////////
    /* Form Submission */
    ////////////////////

        // Submit the Service Form
        serviceForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            try {
                // Use the current form's action (set by the button that opens the form)
                const response = await fetch(serviceForm.action, {
                    method: "POST",
                    body: formData,
                });

                if (response.ok) {
                    data = await response.json();
                    // Close the form dialog
                    closeFormDialog(serviceFormDialog);
                    // Store toast message before reload
                    localStorage.setItem("toastType", "success");
                    localStorage.setItem("toastMessage", data.detail);
                    // Reload the page according to the redirect url provided in the JSON response body
                    window.location.href = data.redirect_to;
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

    /////////////////////////////////////
    /* Input Validation and Formating */
    ///////////////////////////////////

        // Unit Price Input
        document.getElementById("input_service-form_unit-price").addEventListener("blur", (e) => {
            validateAndFormatPriceInput(e.currentTarget);
        });
    //#endregion SERVICE FORM

    //#region REMOVE SERVICE FORM
    const removeServiceFormDialog = document.getElementById("dialog_remove-service-form");
    const removeServiceForm = document.getElementById("form_remove-service-form");
    
    ////////////////////////
    /* Open/Close Events */
    //////////////////////

        // Open the "Remove Service" form*
        document.querySelectorAll('[id^="btn_show-remove-service-form-"]').forEach((btn) => {
            btn.addEventListener("click", (e) => {
                openRemoveServiceForm(e.currentTarget);
            })
        });

        // Close the "Remove Service" Form
        document.getElementById("btn_hide-remove-service-form").addEventListener("click", () => {
            closeFormDialog(removeServiceFormDialog);
        });

    //////////////////////
    /* Form Submission */
    ////////////////////

        // Submit the "Remove Service" form
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
                    // Close the form dialog
                    closeFormDialog(removeServiceFormDialog);
                    // Store toast message before reload
                    localStorage.setItem("toastType", "success");
                    localStorage.setItem("toastMessage", data.detail);
                    // Reload the page according to the redirect url provided in the JSON response body
                    window.location.href = data.redirect_to;
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

    //#region SEARCH
    const searchInput = document.getElementById("input_search");
    const searchBySelect = document.getElementById("select_search-by");

    searchInput.addEventListener("input", function(e) {
        clearAllServicesTableSearch();
        if (searchInput.value.trim() === "") return;
        searchAllServicesTable(e.currentTarget.value, searchBySelect.value);
    });

    searchBySelect.addEventListener("change", function(e) {
        clearAllServicesTableSearch();
        if (searchInput.value.trim() === "") return;
        searchAllServicesTable(searchInput.value, e.currentTarget.value);
    });
    //#endregion SEARCH

    //#region FUNCTIONS
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
     * Ensure a price input is numeric.
     * If it is, format its value to 2 decimal places. If not, show a custom validation message.
     * @param {HTMLInputElement} eventElement - The price input element to validate and format.
     * @returns {void}
     */
    function validateAndFormatPriceInput(eventElement) {
        const value = eventElement.value.trim();
    
        if (eventElement.value === "") {
            eventElement.setCustomValidity("");
            return;
        }
        else if (isNaN(value)) {
            eventElement.setCustomValidity("Please enter a valid number.");
            eventElement.reportValidity();
        } else {
            eventElement.setCustomValidity("");
            (eventElement.value) && (eventElement.value = Number(eventElement.value).toFixed(2));
        }
    }

    /**
     * Open the "Add New Service" version of the Service Form.
     * @returns {void}
     */
    function openAddNewServiceForm() {
        // Set the form header and button text
        document.getElementById("h2_service-form-header").innerText = "Create New Service";
        document.getElementById("btn_submit-service-form").innerText = "Add Service";
        // Set the form action
        serviceForm.action = "/services/add_service";
        // Open the form dialog
        openFormDialog(serviceFormDialog);
    }

    /**
     * Open the "Edit Service" version of the Service Form.
     * @param {HTMLElement} eventElement - The button element that was clicked to open the form.
     * @returns {void}
     */
    function openEditServiceForm(eventElement) {
        // Set the form header and button text
        document.getElementById("h2_service-form-header").innerText = "Edit Service Details";
        document.getElementById("btn_submit-service-form").innerText = "Update";
        // Set the form action
        serviceForm.action = "/services/edit_service";
        // Populate the form with the service to edit's data
        document.getElementById("input_service-form_name").value = eventElement.dataset.name;
        document.getElementById("input_service-form_unit-price").value = Number(eventElement.dataset.unitPrice).toFixed(2);
        document.getElementById("textarea_service-form_description").value = eventElement.dataset.description;
        document.getElementById("input_service-form_service-id").value = eventElement.dataset.serviceId;
        // Open the form dialog
        openFormDialog(serviceFormDialog);
    }

    /**
     * Open the "Remove Service" form.
     * @param {HTMLElement} eventElement - The button element that was clicked to open the form.
     * @returns {void}
     */
    function openRemoveServiceForm(eventElement) {
        // Populate the form with the service to remove's data
        document.getElementById("p_remove-service-form_name-placeholder").innerText = eventElement.dataset.name;
        document.getElementById("p_remove-service-form_description-placeholder").innerText = eventElement.dataset.description;
        document.getElementById("input_remove-service-form_service-id").value = eventElement.dataset.serviceId;
        // Open the form dialog
        openFormDialog(removeServiceFormDialog);
    }

    /**
     * Search the all services table for services matching an input search string.
     * If the number of matches found exceeds the number of rows shown per page, enable vertical scrolling for the table.
     * @param {string} searchInput - The input search string.
     * @param {string} searchBy - The field to search by.
     * @returns {void}
     */
    function searchAllServicesTable(searchInput, searchBy) {
        const tableDiv = document.getElementById("div_table");
        const tablePaginationDiv = document.getElementById("div_table-pagination");
        const allServicesTableBody = document.getElementById("tbody_all-services");
        searchInput = searchInput.toLowerCase().trim();

        // Clear the current table
        allServicesTableBody.innerHTML = "";
        // Iterate through the list of all services and add matches to the table
        let matchesFound = 0;
        allServices.forEach((service) => {
            switch (searchBy) {
                case "name":
                    if (service.name.toLowerCase().includes(searchInput)) {
                        addServiceToAllServicesTable(service);
                        ++matchesFound;
                    };
                    break;
                case "description":
                    if (service.description.toLowerCase().includes(searchInput)) {
                        addServiceToAllServicesTable(service);
                        ++matchesFound;
                    };
                    break;
                case "unit-price":
                    if (service.unit_price.toLowerCase().includes(searchInput)) {
                        addServiceToAllServicesTable(service);
                        ++matchesFound;
                    };
                    break;
            }
        });

        (matchesFound > perPage) && tableDiv.classList.add("max-h-[48rem]", "overflow-y-auto");
        tablePaginationDiv.classList.add("hidden");
    }

    /**
     * Clear any search filters applied to the all services table and restore the current page's services.
     * @returns {void}
     */
    function clearAllServicesTableSearch() {
        const tableDiv = document.getElementById("div_table");
        const tablePaginationDiv = document.getElementById("div_table-pagination");
        const allServicesTableBody = document.getElementById("tbody_all-services");

        // Clear the current table
        allServicesTableBody.innerHTML = "";
        // Add the page's services back to the table
        pageServices.forEach((service) => {
            addServiceToAllServicesTable(service);
        });

        tableDiv.classList.remove("max-h-[48rem]", "overflow-y-auto");
        tablePaginationDiv.classList.remove("hidden");
    }

    /**
     * Add a service to the all services table.
     * @param {{ id: number, name: string, description: string, unit_price: string}} service - The service as a JSON object containing the unique ID, name, description, and unit price of the new service.
     * @returns {void}
     */
    function addServiceToAllServicesTable(service) {
        const allServicesTableBody = document.getElementById("tbody_all-services");
        const tableIconHoverColor = serviceForm.dataset.tableIconHoverColor;

        // Icons
        const newEditIconOutlined = `
            <svg width="1.25rem", height="1.25rem" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125" />
            </svg>
        `;
        const newEditIconSolid = `
            <svg width="1.25rem", height="1.25rem" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${tableIconHoverColor}">
                <path d="M21.731 2.269a2.625 2.625 0 0 0-3.712 0l-1.157 1.157 3.712 3.712 1.157-1.157a2.625 2.625 0 0 0 0-3.712ZM19.513 8.199l-3.712-3.712-12.15 12.15a5.25 5.25 0 0 0-1.32 2.214l-.8 2.685a.75.75 0 0 0 .933.933l2.685-.8a5.25 5.25 0 0 0 2.214-1.32L19.513 8.2Z" />
            </svg>
        `;
        const newDeleteIconOutlined = `
            <svg width="1.25rem", height="1.25rem" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
            </svg>
        `;
        const newDeleteIconSolid = `
            <svg width="1.25rem", height="1.25rem" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="${tableIconHoverColor}">
                <path fill-rule="evenodd" d="M16.5 4.478v.227a48.816 48.816 0 0 1 3.878.512.75.75 0 1 1-.256 1.478l-.209-.035-1.005 13.07a3 3 0 0 1-2.991 2.77H8.084a3 3 0 0 1-2.991-2.77L4.087 6.66l-.209.035a.75.75 0 0 1-.256-1.478A48.567 48.567 0 0 1 7.5 4.705v-.227c0-1.564 1.213-2.9 2.816-2.951a52.662 52.662 0 0 1 3.369 0c1.603.051 2.815 1.387 2.815 2.951Zm-6.136-1.452a51.196 51.196 0 0 1 3.273 0C14.39 3.05 15 3.684 15 4.478v.113a49.488 49.488 0 0 0-6 0v-.113c0-.794.609-1.428 1.364-1.452Zm-.355 5.945a.75.75 0 1 0-1.5.058l.347 9a.75.75 0 1 0 1.499-.058l-.346-9Zm5.48.058a.75.75 0 1 0-1.498-.058l-.347 9a.75.75 0 0 0 1.5.058l.345-9Z" clip-rule="evenodd" />
            </svg>
        `;

        // Create a new <tr> element
        const newRow = document.createElement("tr");
        // Set the id attribute of the new element
        newRow.id = `tr_service-${service.id}`;
        // Set the inner HTML of the new element
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
        // Append the new element to the table body
        allServicesTableBody.appendChild(newRow);

        // Add event listeners to the new row's icon buttons
        document.getElementById(`btn_show-edit-service-form-${service.id}`).addEventListener("click", (e) => {
            // Open the "Edit Service" form
            openEditServiceForm(e.currentTarget);
        });
        document.getElementById(`btn_show-remove-service-form-${service.id}`).addEventListener("click", (e) => {
            // Open the "Remove Service" form
            openRemoveServiceForm(e.currentTarget);
        });
    }
    //#endregion FUNCTIONS

    //#region DEPRECATED FUNCTIONS
    /**
     * Remove a service from the all services table.
     * @param {{ id: number }} service - The service as a JSON object containing the unique ID of the removed service.
     * @returns {void}
     * 
     * 09/08/2025 - This function is no longer used because the page reloads after a service is removed.
     */
    /*function removeServiceFromAllServicesTable(service) {
        document.getElementById(`tr_service-${service.id}`).remove();
    }*/

    /**
     * Edit a service in the all services table.
     * @param {{ id: number, name: string, description: string, unit_price: string}} service - The service as a JSON object containing the unique ID, name, description, and unit price of the updated service.
     * @returns {void}
     * 
     * 09/08/2025 - This function is no longer used because the page reloads after a service is removed.
     */
    /*function editServiceInAllServicesTable(service) {
        const serviceRow = document.getElementById(`tr_service-${service.id}`);

        serviceRow.getElementsByTagName("td")[0].innerText = service.name;
        serviceRow.getElementsByTagName("td")[1].innerText = service.description;
        serviceRow.getElementsByTagName("td")[2].innerText = `$${Number(service.unit_price).toFixed(2)}`;
    }*/
    //#endregion DEPRECATED FUNCTIONS
});