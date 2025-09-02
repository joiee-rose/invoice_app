document.addEventListener("DOMContentLoaded", function() {
    //#region CLIENT FORM
    const clientFormDialog = document.getElementById("dialog_client-form");
    const clientForm = document.getElementById("form_client-form");

    // Open the "Add New Client" form (click event listener)
    document.getElementById("btn_show-new-client-form").addEventListener("click", () => {
        // Set form header, button text, and form action
        document.getElementById("h2_client-form-header").innerText = "Create New Client";
        document.getElementById("btn_submit-client-form").innerText = "Add Client";
        clientForm.action = "/clients/add_client";

        openFormDialog(clientFormDialog);
    });

    // Open the "Edit Client" form (click event listener)
    document.querySelectorAll('[id^="btn_show-edit-client-form-"]').forEach((btn) => {
        btn.addEventListener("click", () => {
            // Set form header, button text, and form action
            document.getElementById("h2_client-form-header").innerText = "Edit Client Details";
            document.getElementById("btn_submit-client-form").innerText = "Update";
            clientForm.action = "/clients/edit_client";

            // Populate form with the client to edit's data
            document.getElementById("input_client-form_name").value = btn.dataset.name;
            document.getElementById("input_client-form_business-name").value = btn.dataset.businessName;
            document.getElementById("input_client-form_street-address").value = btn.dataset.streetAddress;
            document.getElementById("input_client-form_city").value = btn.dataset.city;
            document.getElementById("input_client-form_state").value = btn.dataset.state;
            document.getElementById("input_client-form_zip-code").value = btn.dataset.zipCode;
            document.getElementById("input_client-form_email").value = btn.dataset.email;
            document.getElementById("input_client-form_phone").value = btn.dataset.phone;
            document.getElementById("input_client-form_client-id").value = btn.dataset.clientId;

            openFormDialog(clientFormDialog);
        });
    });

    // Submit the Client Form (submit event listener)
    clientForm.addEventListener("submit", async(e) => {
        e.preventDefault();
        const formData = new FormData(clientForm);

        try {
            const response = await fetch(clientForm.action, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                data = await response.json();
                // Close the form dialog
                closeFormDialog(clientFormDialog);
                // Either add the new client to the all clients table or update the existing client in the all clients table
                if (clientForm.action.endsWith("add_client")) {
                    addClientToAllClientsTable(data.client);
                }
                else if (clientForm.action.endsWith("edit_client")) {
                    editClientInAllClientsTable(data.client);
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
                    showToast("error", data.detail || "Client Not Found");
                }
                else if (response.status == 500) {
                    closeFormDialog(serviceFormDialog);
                    showToast("error", data.detail || "Internal Server Error");
                }
            }
        } catch (error) {
            closeFormDialog(clientFormDialog);
            showToast("error", error.message || "Unexpected Error");
        }
    });

    // Close the Client Form (click event listener)
    document.getElementById("btn_hide-client-form").addEventListener("click", () => {
        closeFormDialog(clientFormDialog);
    });
    //#endregion CLIENT FORM

    //#region REMOVE CLIENT FORM
    const removeClientFormDialog = document.getElementById("dialog_remove-client-form");
    const removeClientForm = document.getElementById("form_remove-client-form");

    // Open the "Remove Client" form (click event listener)
    document.querySelectorAll('[id^="btn_show-remove-client-form-"]').forEach((btn) => {
        btn.addEventListener("click", () => {
            // Populate the form with the client to remove's data
            document.getElementById("p_remove-client-form_name-placeholder").innerText = btn.dataset.name;
            document.getElementById("p_remove-client-form_business-name-placeholder").innerText = btn.dataset.businessName;
            document.getElementById("input_remove-client-form_client-id").value = btn.dataset.clientId;

            openFormDialog(removeClientFormDialog);
        });
    });
    
    // Close the "Remove Client" form (click event listener)
    document.getElementById("btn_hide-remove-client-form").addEventListener("click", () => {
        closeFormDialog(removeClientFormDialog);
    });

    // Submit the "Remove Client" form (submit event listener)
    removeClientForm.addEventListener("submit", async(e) => {
        e.preventDefault();
        const formData = new FormData(e.target);

        try {
            const response = await fetch(removeClientForm.action, {
                method: "POST",
                body: formData,
            });

            if (response.ok) {
                data = await response.json();
                // Close the form dialog, remove the client from the all clients table, and show a success toast notification
                closeFormDialog(removeClientFormDialog);
                removeClientFromAllClientsTable(data.client);
                showToast("success", data.detail);
            } else {
                data = await response.json();
                if (response.status == 500) {
                    closeFormDialog(removeClientFormDialog);
                    showToast("error", data.detail || "Internal Server Error");
                }
            }
        } catch (error) {
            closeFormDialog(removeClientFormDialog);
            showToast("error", error.message || "Unexpected Error");
        }
    });

    // Format phone number as (XXX) XXX-XXXX (blur/focus lost event listener)
    document.getElementById("input_client-form_phone").addEventListener("blur", function() {
        (this.value) && (this.value = formatPhoneNumber(this.value)); // see Helper Functions
    });
    //#endregion REMOVE CLIENT FORM

    //#region CLIENT PROFILE FORM
    const clientQuoteProfileFormDialog = document.getElementById("dialog_client-quote-profile-form");
    const clientQuoteProfileForm = document.getElementById("form_client-quote-profile-form");

    // Add Event Listener - Open the Client Quote Profile Form (click event listener)
    document.querySelectorAll('[id^="btn_show-client-quote-profile-form-"]').forEach((btn) => {
        btn.addEventListener("click", () => {
            // Populate client quote form with the client's data
            document.getElementById("p_client-quote-profile-form_name-placeholder").innerText = btn.dataset.name;
            document.getElementById("p_client-quote-profile-form_business-name-placeholder").innerText = btn.dataset.businessName;
            document.getElementById("p_client-quote-profile-form_billing-address-1-placeholder").innerText = btn.dataset.streetAddress;
            document.getElementById("p_client-quote-profile-form_billing-address-2-placeholder").innerText = `${btn.dataset.city}, ${btn.dataset.state} ${btn.dataset.zipCode}`;
            document.getElementById("input_client-quote-profile-form_client-id").value = btn.dataset.clientId;

            // Check if client already has a quote profile
            fetch(`/clients/api/quote_profile/${btn.dataset.clientId}`)
            .then(response => (response.status === 200) ? response.json() : null)
            .then(data => {
                if (data) {
                    populateClientQuoteProfile(data);
                } else {
                    addRowToClientQuoteProfileServicesTable();
                }
            })
            .catch(error => {
                console.log('Error fetching client quote profile:', error);
            });

            openFormDialog(clientQuoteProfileFormDialog);
        });
    });

    // Add a service row to the Client Quote Profile Form (click event listener)
    document.getElementById("btn_add-client-service").addEventListener("click", () => {
        addRowToClientQuoteProfileServicesTable();
    });

    // Close the Client Quote Profile Form (click event listener)
    document.getElementById("btn_hide-client-quote-profile-form").addEventListener("click", () => {
        document.getElementById("tbody_client-quote-profile-services").innerHTML = "";
        closeFormDialog(clientQuoteProfileFormDialog);
    });

    // Save the Client Quote Profile Form (click event listener)
    document.getElementById("btn_save-client-quote-profile").addEventListener("click", () => {
        // Set the form action
        clientQuoteProfileForm.action = "/clients/save_quote_profile";
    });

    // Generate & Send Quote from the Client Quote Profile Form (click event listener)
    document.getElementById("btn_send-quote").addEventListener("click", () => {
        // Set the form action
        clientQuoteProfileForm.action = "/clients/send_quote";
    });
    //#endregion CLIENT PROFILE FORM

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
     * Add a client to the all clients table.
     * @param {{ id: number, name: string, business_name: string, city: string, state: string, zip_code: string, email: string, phone: string}} client - The client as a JSON object containing the unique ID and data of the new client.
     * @returns {void}
     */
    function addClientToAllClientsTable(client) {
        const allClientsTableBody = document.getElementById("tbody_all-clients");
        const iconHoverColor = clientForm.dataset.iconHoverColor;

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
        const newClientQuoteProfileIconOutlined = `
            <svg width="1.25rem", height="1.25rem" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" fill="${iconHoverColor}">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m3.75 9v7.5m2.25-6.466a9.016 9.016 0 0 0-3.461-.203c-.536.072-.974.478-1.021 1.017a4.559 4.559 0 0 0-.018.402c0 .464.336.844.775.994l2.95 1.012c.44.15.775.53.775.994 0 .136-.006.27-.018.402-.047.539-.485.945-1.021 1.017a9.077 9.077 0 0 1-3.461-.203M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
        `;
        const newClientQuoteProfileIconSolid = `
            <svg width="1.25rem", height="1.25rem" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" fill="${iconHoverColor}">
                <path fill-rule="evenodd" d="M3.75 3.375c0-1.036.84-1.875 1.875-1.875H9a3.75 3.75 0 0 1 3.75 3.75v1.875c0 1.036.84 1.875 1.875 1.875H16.5a3.75 3.75 0 0 1 3.75 3.75v7.875c0 1.035-.84 1.875-1.875 1.875H5.625a1.875 1.875 0 0 1-1.875-1.875V3.375Zm10.5 1.875a5.23 5.23 0 0 0-1.279-3.434 9.768 9.768 0 0 1 6.963 6.963A5.23 5.23 0 0 0 16.5 7.5h-1.875a.375.375 0 0 1-.375-.375V5.25ZM12 10.5a.75.75 0 0 1 .75.75v.028a9.727 9.727 0 0 1 1.687.28.75.75 0 1 1-.374 1.452 8.207 8.207 0 0 0-1.313-.226v1.68l.969.332c.67.23 1.281.85 1.281 1.704 0 .158-.007.314-.02.468-.083.931-.83 1.582-1.669 1.695a9.776 9.776 0 0 1-.561.059v.028a.75.75 0 0 1-1.5 0v-.029a9.724 9.724 0 0 1-1.687-.278.75.75 0 0 1 .374-1.453c.425.11.864.186 1.313.226v-1.68l-.968-.332C9.612 14.974 9 14.354 9 13.5c0-.158.007-.314.02-.468.083-.931.831-1.582 1.67-1.694.185-.025.372-.045.56-.06v-.028a.75.75 0 0 1 .75-.75Zm-1.11 2.324c.119-.016.239-.03.36-.04v1.166l-.482-.165c-.208-.072-.268-.211-.268-.285 0-.113.005-.225.015-.336.013-.146.14-.309.374-.34Zm1.86 4.392V16.05l.482.165c.208.072.268.211.268.285 0 .113-.005.225-.015.336-.012.146-.14.309-.374.34-.12.016-.24.03-.361.04Z" clip-rule="evenodd" />
            </svg>
        `;

        // Create a new <tr> element and set its id and inner HTML
        const newRow = document.createElement("tr");
        newRow.id = `tr_client-${client.id}`;
        newRow.innerHTML = `
            <td class="p-4">${client.name}</td>
            <td class="p-4">${client.business_name}</td>
            <td class="p-4">${client.street_address}, ${client.city}, ${client.state} ${client.zip_code}</td>
            <td class="p-4">${client.email}</td>
            <td class="p-4">${client.phone}</td>
            <td class="flex flex-row gap-4 p-4">
                <!-- Edit Client Buttons -->
                <button
                    id="btn_show-edit-client-form-${client.id}"
                    data-name="${client.name}"
                    data-business-name="${client.business_name}"
                    data-street-address="${client.street_address}"
                    data-city="${client.city}"
                    data-state="${client.state}"
                    data-zip-code="${client.zip_code}"
                    data-email="${client.email}"
                    data-phone="${client.phone}"
                    data-client-id="${client.id}"
                    class="flex cursor-pointer"
                >
                    <div class="icon-wrapper overflow-hidden flex-shrink-0">
                        <span class="icon outline">${newEditIconOutlined}</span>
                        <span class="icon solid">${newEditIconSolid}</span>
                    </div>
                </button>
                <!-- Remove Client Buttons -->
                <button
                    id="btn_show-remove-client-form-${client.id}"
                    data-name="${client.name}"
                    data-business-name="${client.business_name}"
                    data-client-id="${client.id}"
                    class="cursor-pointer group"
                >
                    <div class="icon-wrapper overflow-hidden flex-shrink-0">
                        <span class="icon outline">${newDeleteIconOutlined}</span>
                        <span class="icon solid">${newDeleteIconSolid}</span>
                    </div>
                </button>
                <!-- Client Quote Profile Buttons -->
                <button
                    id="btn_show-client-quote-profile-form-${client.id}"
                    data-name="${client.name}"
                    data-business-name="${client.business_name}"
                    data-street-address="${client.street_address}"
                    data-city="${client.city}"
                    data-state="${client.state}"
                    data-zip-code="${client.zip_code}"
                    data-client-id="${client.id}"
                    class="cursor-pointer group"
                >
                    <div class="icon-wrapper overflow-hidden flex-shrink-0">
                        <span class="icon outline">${newClientQuoteProfileIconOutlined}</span>
                        <span class="icon solid">${newClientQuoteProfileIconSolid}</span>
                    </div>
                </button>
            </td>
        `;

        // Append the new <tr> element to the table body
        allClientsTableBody.appendChild(newRow);

        // Add Event Listener - Open the "Edit Client" form (click event listener)
        document.getElementById(`btn_show-edit-client-form-${client.id}`).addEventListener("click", (e) => {
            // Set form header, button text, and form action
            document.getElementById("h2_client-form-header").innerText = "Edit Client Details";
            document.getElementById("btn_submit-client-form").innerText = "Update";
            clientForm.action = "/clients/edit_client";

            // Populate form with the client to edit's data
            document.getElementById("input_client-form_name").value = e.currentTarget.dataset.name;
            document.getElementById("input_client-form_business-name").value = e.currentTarget.dataset.businessName;
            document.getElementById("input_client-form_street-address").value = e.currentTarget.dataset.streetAddress;
            document.getElementById("input_client-form_city").value = e.currentTarget.dataset.city;
            document.getElementById("input_client-form_state").value = e.currentTarget.dataset.state;
            document.getElementById("input_client-form_zip-code").value = e.currentTarget.dataset.zipCode;
            document.getElementById("input_client-form_email").value = e.currentTarget.dataset.email;
            document.getElementById("input_client-form_phone").value = e.currentTarget.dataset.phone;
            document.getElementById("input_client-form_client-id").value = e.currentTarget.dataset.clientId;

            openFormDialog(clientFormDialog);
        });

        // Add Event Listener - Open the "Remove Client" form (click event listener)
        document.getElementById(`btn_show-remove-client-form-${client.id}`).addEventListener("click", (e) => {
            // Populate the form with the client to remove's data
            document.getElementById("p_remove-client-form_name-placeholder").innerText = e.currentTarget.dataset.name;
            document.getElementById("p_remove-client-form_business-name-placeholder").innerText = e.currentTarget.dataset.businessName;
            document.getElementById("input_remove-client-form_client-id").value = e.currentTarget.dataset.clientId;

            openFormDialog(removeClientFormDialog);
        });

        // Add Event Listener - Open the Client Quote Profile Form (click event listener)
        document.getElementById(`btn_show-client-quote-profile-form-${client.id}`).addEventListener("click", (e) => {
            // Populate client quote form with the client's data
            document.getElementById("p_client-quote-profile-form_name-placeholder").innerText = e.currentTarget.dataset.name;
            document.getElementById("p_client-quote-profile-form_business-name-placeholder").innerText = e.currentTarget.dataset.businessName;
            document.getElementById("p_client-quote-profile-form_billing-address-1-placeholder").innerText = e.currentTarget.dataset.streetAddress;
            document.getElementById("p_client-quote-profile-form_billing-address-2-placeholder").innerText = e.currentTarget.dataset.city + ", " + e.currentTarget.dataset.state + " " + e.currentTarget.dataset.zipCode;
            document.getElementById("input_client-quote-profile-form_client-id").value = e.currentTarget.dataset.clientId;

            // Check if client already has a quote profile
            fetch(`/clients/api/quote_profile/${e.currentTarget.clientId}`)
            .then(response => (response.status === 200) ? response.json() : null)
            .then(data => {
                if (data) {
                    populateClientQuoteProfile(data);
                } else {
                    addRowToClientQuoteProfileServicesTable();
                }
            })
            .catch(error => {
                console.log('Error fetching client quote profile:', error);
            });

            openFormDialog(clientQuoteProfileFormDialog);
        });

        // Add Event Listener - Add a service row to the Client Quote Profile Form (click event listener)
        document.getElementById("btn_add-client-service").addEventListener("click", () => {
            addRowToClientQuoteProfileServicesTable();
        });
    }

    /**
     * Edit a client in the all clients table.
     * @param {{ id: number, name: string, business_name: string, city: string, state: string, zip_code: string, email: string, phone: string}} client - The client as a JSON object containing the unique ID and data of the updated client.
     * @returns {void}
     */
    function editClientInAllClientsTable(client) {
        const clientRow = document.getElementById(`tr_client-${client.id}`);

        clientRow.getElementsByTagName("td")[0].innerText = client.name;
        clientRow.getElementsByTagName("td")[1].innerText = client.business_name;
        clientRow.getElementsByTagName("td")[2].innerText = `${client.street_address}, ${client.city}, ${client.state} ${client.zip_code}`;
        clientRow.getElementsByTagName("td")[3].innerText = client.email;
        clientRow.getElementsByTagName("td")[4].innerText = client.phone;
    }

    /**
     * Remove a client from the all clients table.
     * @param {{ id: number }} client - The client as a JSON object containing the unique ID of the removed client.
     * @returns {void}
     */
    function removeClientFromAllClientsTable(client) {
        document.getElementById(`tr_client-${client.id}`).remove();
    }

    /**
     * Add a service row to the Client Quote Profile services table.
     * @returns {Promise<void>}
     */
    function addRowToClientQuoteProfileServicesTable() {
        return new Promise((resolve, reject) => {
            const newRow = document.createElement("tr");
            newRow.classList.add(`h-[2rem]`);
            newRow.innerHTML = `
                <!-- Service -->
                <td class="p-2">
                    <select name="service" class="cursor-pointer">
                        <option value="-1" selected>--</option>
                    </select>
                    <!-- hidden input storing Service Name -->
                    <input type="text" name="service-name" hidden>
                </td>
                <!-- Quantity -->
                <td class="p-2">
                    <input type="number" name="quantity" size="5" min="1" step="1" value="1" class="h-[2rem] p-2 border rounded-md text-base">
                </td>
                <!-- Per Unit -->
                <td class="p-2">
                    <select name="per-unit" class="cursor-pointer">
                        <option value="-1" selected>--</option>
                        <option value="per-visit">per visit</option>
                        <option value="per-push">per push</option>
                    </select>
                </td>
                <!-- Unit Price -->
                <td class="p-2">
                    <p name="p_unit-price" class="p-2"></p>
                    <!-- hidden input storing Unit Price -->
                    <input type="text" name="unit-price" hidden>
                </td>
                <!-- Tax -->
                <td class="p-2">
                    <input type="text" name="tax" size="5" class="h-[2rem] p-2 border rounded-md text-base">
                </td>
                <!-- Total Price -->
                <td class="p-2">
                    <p name="p_total-price" class="p-2"></p>
                    <!-- hidden input storing Total Price -->
                    <input type="text" name="total-price" hidden>
                </td>
            `;
            document.getElementById("tbody_client-quote-profile-services").appendChild(newRow);

            // Append an option for each service in the database to the service select element
            fetch("/services/api/all")
            .then(response => response.json())
            .then(data => {
                Array.from(data).forEach((service) => {
                    const option = document.createElement("option");

                    option.value = service.id;
                    option.dataset.unitPrice = service.unit_price;
                    option.innerText = service.name;

                    newRow.getElementsByTagName("select")[0].appendChild(option);
                });
                resolve();
            })
            .catch(error => {
                console.log('Error fetching services:', error);
                reject(error);
            });

            const serviceSelect = newRow.getElementsByTagName("select")[0];
            const inputQuantity = newRow.getElementsByTagName("input")[1];
            const unitPrice = newRow.getElementsByTagName("p")[0];
            const tax = newRow.getElementsByTagName("input")[3];
            const totalPrice = newRow.getElementsByTagName("p")[1];
            
            const inputServiceName = newRow.getElementsByTagName("input")[0];
            const inputUnitPrice = newRow.getElementsByTagName("input")[2];
            const inputTotalPrice = newRow.getElementsByTagName("input")[4];

            // Populate unit price based on selected service (change event listener)
            serviceSelect.addEventListener("change", () => {
                if (serviceSelect.value != -1) {
                    const serviceUnitPrice = serviceSelect.options[serviceSelect.selectedIndex].dataset.unitPrice;
                    unitPrice.innerText = Number(serviceUnitPrice).toFixed(2);

                    // Update service name and unit price hidden inputs
                    inputServiceName.value = serviceSelect.options[serviceSelect.selectedIndex].innerText;
                    inputUnitPrice.value = Number(serviceUnitPrice).toFixed(2);
                } else {
                    unitPrice.innerText = "";
                    inputServiceName.value = "";
                    inputUnitPrice.value = "";
                }
            });

            // Update total price based on quantity, unit price, and tax (change event listener)
            newRow.addEventListener("change", (event) => {
                if (serviceSelect.value != -1 && inputQuantity.value != null && inputQuantity.value != "" && tax.value != null && tax.value != "") {
                    const basePrice = Number(inputQuantity.value) * Number(unitPrice.innerText);
                    const taxAmount = Number(tax.value / 100) * basePrice;
                    totalPrice.innerText = Number(basePrice + taxAmount).toFixed(2);
                    inputTotalPrice.value = totalPrice.innerText;
                }
            });
        });
    }

    /**
     * Populate the Client Quote Profile services table with existing data.
     * @param {void} data 
     */
    async function populateClientQuoteProfile(data) {
        const servicesTable = document.getElementById("tbody_client-quote-profile-services");
        
        document.getElementById("input_client-quote-profile-form_min-monthly-charge").value = Number(data.min_monthly_charge).toFixed(2);
        
        for (let i = 0; i < data.services.length; ++i) {
            await addRowToClientQuoteProfileServicesTable();
            const newRow = servicesTable.lastElementChild;

            newRow.getElementsByTagName("select")[0].value = data.services[i].service_id;
            newRow.getElementsByTagName("input")[1].value = data.services[i].quantity;
            newRow.getElementsByTagName("select")[1].value = data.services[i].per_unit;
            newRow.getElementsByTagName("p")[0].innerText = Number(data.services[i].unit_price).toFixed(2);
            newRow.getElementsByTagName("input")[3].value = Number(data.services[i].tax).toFixed(2);
            newRow.getElementsByTagName("p")[1].innerText = Number(data.services[i].total_price).toFixed(2);

            // hidden inputs
            newRow.getElementsByTagName("input")[0].value = data.services[i].service_name;
            inputUnitPrice = newRow.getElementsByTagName("input")[2].value = data.services[i].unit_price;
            newRow.getElementsByTagName("input")[4].value = data.services[i].total_price;
        }
    }

    // TODO - Remove a service row
    function removeRowFromClientQuoteProfileServicesTable(rowNumber) {
        document.getElementById(`tbl_row-${rowNumber}`).remove();
        document.getElementById("input_client-quote-profile-form_services-count").value = Number(document.getElementById("input_client-quote-profile-form_services-count").value) - 1;
    }

    function formatPhoneNumber(digits) {
        // return as-is if not 10 digits, otherwise format as (XXX) XXX-XXXX
        return (!/^[0-9]{10}$/.test(digits)) ? digits : `(${digits.slice(0,3)}) ${digits.slice(3,6)}-${digits.slice(6)}`;
    }
    //#endregion HELPER FUNCTIONS
}); 