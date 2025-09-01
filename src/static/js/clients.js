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
                // Close the form dialog, REMOVE THE CLIENT from the all clients table, and show a success toast notification
                closeFormDialog(removeClientFormDialog);
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

    // Click event listener to open the client quote profile form
    document.querySelectorAll('[id^="btn_show-client-quote-profile-form-"]').forEach((btn) => {
        btn.addEventListener("click", () => {
            // Populate client quote form with the client's data
            document.getElementById("p_client-quote-profile-form_name-placeholder").innerText = btn.dataset.name;
            document.getElementById("p_client-quote-profile-form_business-name-placeholder").innerText = btn.dataset.businessName;
            document.getElementById("p_client-quote-profile-form_billing-address-1-placeholder").innerText = btn.dataset.streetAddress;
            document.getElementById("p_client-quote-profile-form_billing-address-2-placeholder").innerText = btn.dataset.city + ", " + btn.dataset.state + " " + btn.dataset.zipCode;
            document.getElementById("input_client-quote-profile-form_client-id").value = btn.dataset.clientId;

            // Check if client already has a quote profile
            fetch(`/clients/api/quote_profile/${btn.dataset.clientId}`)
            .then(response => (response.status === 200) ? response.json() : null)
            .then(data => {
                if (data) {
                    populateClientQuoteProfile(data);
                } else {
                    addRowToClientQuoteProfileServicesTable(0);
                    document.getElementById("input_client-quote-profile-form_services-count").value = 1;
                }
            })
            .catch(error => {
                console.log('Error fetching client quote profile:', error);
            });

            openFormDialog(clientQuoteProfileFormDialog);
        });
    });

    // Click event listener to add a service row
    document.getElementById("btn_add-client-service").addEventListener("click", () => {
        addRowToClientQuoteProfileServicesTable(document.getElementById("input_client-quote-profile-form_services-count").value);
    });

    // Click event listener to close the client quote profile form
    document.getElementById("btn_hide-client-quote-profile-form").addEventListener("click", () => {
        document.getElementById("tbody_client-quote-profile-services").innerHTML = "";
        closeFormDialog(clientQuoteProfileFormDialog);
    });

    // Function to populate the client quote profile form with existing data
    async function populateClientQuoteProfile(data) {
        for (let i = 0; i < data.services.length; ++i) {
            await addRowToClientQuoteProfileServicesTable(i);
            document.getElementById(`select_service-${i}`).value = data.services[i].service_id;
            document.getElementById(`input_quantity-${i}`).value = data.services[i].quantity;
            document.getElementById(`select_per-unit-${i}`).value = data.services[i].per_unit;
            document.getElementById(`p_unit-price-${i}`).innerText = Number(data.services[i].unit_price).toFixed(2);
            document.getElementById(`p_total-price-${i}`).innerText = Number(data.services[i].total_price).toFixed(2);

            // hidden inputs
            document.getElementById(`input_service-name-${i}`).value = data.services[i].service_name;
            document.getElementById(`input_unit-price-${i}`).value = data.services[i].unit_price;
            document.getElementById(`input_total-price-${i}`).value = data.services[i].total_price;
            /* document.getElementById(`p_unit-price-${i}`).innerText = Number(document.getElementById(`select_service-${i}`).options[document.getElementById(`select_service-${i}`).selectedIndex].dataset.unitPrice).toFixed(2);
            document.getElementById(`p_total-price-${i}`).innerText = Number(document.getElementById(`input_quantity-${i}`).value * document.getElementById(`p_unit-price-${i}`).innerText).toFixed(2); */
        }
    }

    // Function to add a new row to the client quote profile services table
    function addRowToClientQuoteProfileServicesTable(rowNumber) {
        return new Promise((resolve, reject) => {
            document.getElementById("input_client-quote-profile-form_services-count").value = Number(document.getElementById("input_client-quote-profile-form_services-count").value) + 1;

            const newRow = document.createElement("tr");

            newRow.id = `tbl_row-${rowNumber}`;
            newRow.classList.add(`h-[2rem]`);
            newRow.innerHTML = `
                <!-- Service -->
                <td class="p-2">
                    <select id="select_service-${rowNumber}" name="service-${rowNumber}" class="cursor-pointer">
                        <option value="-1" selected>--</option>
                    </select>
                    <!-- hidden input storing Service Name -->
                    <input type="text" id="input_service-name-${rowNumber}" name="service-name-${rowNumber}" hidden>
                </td>
                <!-- Quantity -->
                <td class="p-2">
                    <input type="number" id="input_quantity-${rowNumber}" name="quantity-${rowNumber}" min="1" step="1" value="1" class="h-[2rem] p-2 border rounded-md text-base">
                </td>
                <!-- Per Unit -->
                <td class="p-2">
                    <select id="select_per-unit-${rowNumber}" name="per-unit-${rowNumber}" class="cursor-pointer">
                        <option value="-1" selected>--</option>
                        <option value="per-visit">per visit</option>
                        <option value="per-push">per push</option>
                    </select>
                </td>
                <!-- Unit Price -->
                <td class="p-2">
                    <p id="p_unit-price-${rowNumber}" class="p-2"></p>
                    <!-- hidden input storing Unit Price -->
                    <input type="text" id="input_unit-price-${rowNumber}" name="unit-price-${rowNumber}" hidden>
                </td>
                <!-- Total Price -->
                <td class="p-2">
                    <p id="p_total-price-${rowNumber}" class="p-2"></p>
                    <!-- hidden input storing Total Price -->
                    <input type="text" id="input_total-price-${rowNumber}" name="total-price-${rowNumber}" hidden>
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

                    document.getElementById(`select_service-${rowNumber}`).appendChild(option);
                });
                resolve();
            })
            .catch(error => {
                console.log('Error fetching services:', error);
                reject(error);
            });

            const serviceSelect = document.getElementById(`select_service-${rowNumber}`);
            const inputQuantity = document.getElementById(`input_quantity-${rowNumber}`);
            const unitPrice = document.getElementById(`p_unit-price-${rowNumber}`);
            const totalPrice = document.getElementById(`p_total-price-${rowNumber}`);

            // Populate unit price based on selected service
            serviceSelect.addEventListener("change", () => {
                if (serviceSelect.value != -1) {
                    const serviceUnitPrice = serviceSelect.options[serviceSelect.selectedIndex].dataset.unitPrice;
                    unitPrice.innerText = Number(serviceUnitPrice).toFixed(2);

                    // Update service name and unit price hidden inputs
                    document.getElementById(`input_service-name-${rowNumber}`).value = serviceSelect.options[serviceSelect.selectedIndex].innerText;
                    document.getElementById(`input_unit-price-${rowNumber}`).value = Number(serviceUnitPrice).toFixed(2);
                } else {
                    unitPrice.innerText = "";
                    document.getElementById(`input_service-name-${rowNumber}`).value = "";
                    document.getElementById(`input_unit-price-${rowNumber}`).value = "";
                }
            });

            // Update total price based on quantity and unit price
            document.getElementById(`tbl_row-${rowNumber}`).addEventListener("change", (event) => {
                if (serviceSelect.value != -1 && inputQuantity.value != null && inputQuantity.value != "") {
                    totalPrice.innerText = Number(inputQuantity.value * unitPrice.innerText).toFixed(2);
                    document.getElementById(`input_total-price-${rowNumber}`).value = totalPrice.innerText;
                }
            });
        });
    }

    // TODO - Remove a service row
    function removeRowFromClientQuoteProfileServicesTable(rowNumber) {
        document.getElementById(`tbl_row-${rowNumber}`).remove();
        document.getElementById("input_client-quote-profile-form_services-count").value = Number(document.getElementById("input_client-quote-profile-form_services-count").value) - 1;
    }

    // Click event listener to save client quote profile to client
    document.getElementById("btn_save-client-quote-profile").addEventListener("click", () => {
        // Set the form action
        clientQuoteProfileForm.action = "/clients/save_quote_profile";
    });

    // Click event listener to generate and send an invoice from the client quote profile
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

    function formatPhoneNumber(digits) {
        // return as-is if not 10 digits, otherwise format as (XXX) XXX-XXXX
        return (!/^[0-9]{10}$/.test(digits)) ? digits : `(${digits.slice(0,3)}) ${digits.slice(3,6)}-${digits.slice(6)}`;
    }
    //#endregion HELPER FUNCTIONS
}); 