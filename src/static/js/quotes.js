document.addEventListener("DOMContentLoaded", async function() {
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

    //#region BATCH QUOTES FORM
    const batchQuotesFormDialog = document.getElementById("dialog_batch-quotes-form");
    const batchQuotesForm = document.getElementById("form_batch-quotes-form");
    const allClientsTableBody = document.getElementById("tbody_all-clients");

    ////////////////////////
    /* Open/Close Events */
    //////////////////////

        // Open the Batch Quotes Form
        document.getElementById("btn_show-batch-quotes-form").addEventListener("click", () => {
            openFormDialog(batchQuotesFormDialog);
        });

        // Close the Batch Quotes Form
        document.getElementById("btn_hide-batch-quotes-form").addEventListener("click", () => {
            closeFormDialog(batchQuotesFormDialog);
        });

        // "Open" (Show) the Client Quote Profile for the selected client
        document.querySelectorAll('[id^="tr_client-"]').forEach((row) => {
            row.addEventListener("click", async (e) => {
                // If the click originated from a checkbox, ignore it
                if (e.target.tagName === "INPUT" && e.target.type === "checkbox") { return; }

                // Highlight the selected client row
                const tableRowHoverColorAsOklch = e.currentTarget.dataset.tableRowHoverColorAsOklch;
                document.querySelectorAll('[id^="tr_client-"]').forEach((row) => {
                    row.style.backgroundColor = "#fff";
                });
                e.currentTarget.style.backgroundColor = tableRowHoverColorAsOklch;

                // Show the selected client's quote profile
                showClientQuoteProfile(e.currentTarget);
            });
        });

    //////////////////////
    /* Form Submission */
    ////////////////////

        // Submit the Batch Quotes Form
        batchQuotesFormDialog.addEventListener("submit", async(e) => {
            e.preventDefault();

            // Get a list of the selected clients' ids
            let clientIds = [];
            document.querySelectorAll('[id^="chkbx_add-client-to-batch-quote_client-"]').forEach((checkbox) => {
                if (checkbox.checked) {
                    clientIds.push(checkbox.dataset.clientId);
                }
            });

            try {
                const response = await fetch(batchQuotesForm.action, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        "client_ids": clientIds
                    })
                });

                if (response.ok) {
                    data = await response.json();
                    // Close the form dialog
                    closeFormDialog(batchQuotesFormDialog);
                    // Store toast message before reload
                    localStorage.setItem("toastType", "success");
                    localStorage.setItem("toastMessage", data.detail);
                    // Reload the page according to the redirect url provided in the JSON response body
                    window.location.href = data.redirect_to;
                }
            } catch (error) {
                closeFormDialog(batchQuotesFormDialog);
                showToast("error", error.message || "Unexpected Error");
            }
        });

    //end#region BATCH QUOTES FORM

    //#region FUNCTIONS
    /**
     * Open a form dialog.
     * @param {HTMLDialogElement} formDialog - The form dialog to open.
     * @returns {void}
     */
    function openFormDialog(formDialog) {
        const firstRow = document.querySelector('[id^="tr_client-"]');
        if (firstRow) { firstRow.click(); }

        formDialog.removeAttribute("hidden");
        formDialog.showModal();
    }

    /**
     * Close a form dialog and reset its input fields.
     * @param {HTMLDialogElement} formDialog - The form dialog to close.
     * @returns {void}
     */
    function closeFormDialog(formDialog) {
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
     * Show a client's quote profile in the Batch Quotes Form.
     * @param {HTMLElement} eventElement - The row in the all clients table that was clicked.
     * @returns {void}
     */
    function showClientQuoteProfile(eventElement) {
        const clientId = eventElement.dataset.clientId;

        // Hide all client quote profile divs, then show only the selected client's quote profile div
        batchQuotesForm.querySelectorAll('[id^="div_client-quote-profile_client-"]').forEach((div) => {
            div.style.display = "none";
        });
        document.getElementById(`div_client-quote-profile_client-${clientId}`).style.display = "block";

        // Populate placeholders with the selected client's data
        document.getElementById("p_batch-quotes-form_name-placeholder").innerText = eventElement.dataset.name;
        document.getElementById("p_batch-quotes-form_business-name-placeholder").innerText = eventElement.dataset.businessName;
        document.getElementById("p_batch-quotes-form_billing-address-1-placeholder").innerText = eventElement.dataset.streetAddress;
        document.getElementById("p_batch-quotes-form_billing-address-2-placeholder").innerText = `${eventElement.dataset.city}, ${eventElement.dataset.state} ${eventElement.dataset.zipCode}`;

        fetch("/quotes/get_temp_client_quote_profile", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ "client_id": clientId })
        })
        .then(response => {
            if (response.status === 200) {
                return response.json();
            }
            else {
                // Add an empty service row to the Client Quote Profile Form
                addRowToClientQuoteProfileServicesTable(clientId);
                return null;
            }
        })
        .then(data => {
            if (data) {
                // Populate the client quote profile div with the client's existing quote profile data
                populateTempClientQuoteProfile(data);
            }
        });
    }

    /**
     * Populate the Client Quote Profile services table with existing data.
     * @param {void} data 
     */
    function populateTempClientQuoteProfile(data) {
        const servicesTable = document.getElementById(`tbody_batch-quotes-form_client-quote-profile-services_client-${data.temp_quote_profile.client_id}`);
        servicesTable.innerHTML = "";
        
        // Populate the minimum monthly charge
        document.getElementById(`input_batch-quotes-form_client-quote-profile_min-monthly-charge_client-${data.temp_quote_profile.client_id}`).value = Number(data.temp_quote_profile.min_monthly_charge).toFixed(2);
        // Populate the premium salt upcharge cost
        document.getElementById(`input_batch-quotes-form_client-quote-profile_premium-salt-upcharge_client-${data.temp_quote_profile.client_id}`).value = Number(data.temp_quote_profile.premium_salt_upcharge).toFixed(2);
        // Add and populate a service row for each existing service in the client's temp quote profile
        for (let i = 0; i < data.temp_quote_profile.services.length; ++i) {
            addRowToClientQuoteProfileServicesTable(data.temp_quote_profile.client_id);
            const newRow = servicesTable.lastElementChild;
            newRow.getElementsByTagName("select")[0].value = data.temp_quote_profile.services[i].service_name;
            newRow.getElementsByTagName("input")[0].value = data.temp_quote_profile.services[i].quantity;
            newRow.getElementsByTagName("select")[1].value = data.temp_quote_profile.services[i].per_unit;
            newRow.getElementsByTagName("input")[1].value = Number(data.temp_quote_profile.services[i].unit_price).toFixed(2);
            newRow.getElementsByTagName("input")[2].value = Number(data.temp_quote_profile.services[i].tax).toFixed(2);
            newRow.getElementsByTagName("p")[0].innerText = Number(data.temp_quote_profile.services[i].total_price).toFixed(2);
            newRow.getElementsByTagName("input")[3].value = Number(data.temp_quote_profile.services[i].total_price).toFixed(2);
        }
    }    

    /**
     * Add a service row to the Client Quote Profile services table.
     * @returns {void}
     */
    function addRowToClientQuoteProfileServicesTable(clientId) {
        const tableIconHoverColor = batchQuotesForm.dataset.tableIconHoverColor;

        // Icons
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
        newRow.classList.add(`h-[2rem]`);
        // Set the inner HTML of the new element
        newRow.innerHTML = `
            <!-- Service ("select"[0]) -->
            <td class="p-2">
                <select name="service" class="w-full cursor-pointer">
                    <option value="-1" selected>--</option>
                </select>
            </td>
            <!-- Quantity ("input"[0]) -->
            <td class="p-2">
                <input type="number" name="quantity" size="3" min="1" step="1" value="1" class="h-[2rem] p-2 border rounded-md text-base">
            </td>
            <!-- Per Unit ("select"[1]) -->
            <td class="p-2">
                <select name="per-unit" class="cursor-pointer">
                    <option value="-1" selected>--</option>
                    <option value="per-visit">per visit</option>
                    <option value="per-push">per push</option>
                </select>
            </td>
            <!-- Unit Price ("input"[1]) -->
            <td class="p-2">
                <input type="text" name="unit-price" class="h-[2rem] p-2 border rounded-md text-base">
            </td>
            <!-- Tax ("input"[2]) -->
            <td class="p-2">
                <input type="text" name="tax" size="5" class="h-[2rem] p-2 border rounded-md text-base">
            </td>
            <!-- Total Price ("p"[0]) -->
            <td class="p-2">
                <p name="p_total-price" class="p-2"></p>
                <!-- hidden input storing Total Price ("input"[3]) -->
                <input type="text" name="total-price" hidden>
            </td>
            <!-- Remove Service Button -->
            <td class="p-2">
                <button
                    id=""
                    type="button"
                    name="btn_remove-service"
                    class="cursor-pointer"
                >
                    <div class="icon-wrapper overflow-hidden flex-shrink-0">
                        <span class="icon outline">${newDeleteIconOutlined}</span>
                        <span class="icon solid">${newDeleteIconSolid}</span>
                    </div>
                </button>
            </td>
        `;
        // Append the new element to the table body
        document.getElementById(`tbody_batch-quotes-form_client-quote-profile-services_client-${clientId}`).appendChild(newRow);
        // Create a new <option> element for each service and append to the new row's service <select> element
        Array.from(allServices).forEach((service) => {
            const option = document.createElement("option");
            option.value = service.name;
            option.innerText = service.name;
            option.dataset.unitPrice = service.unit_price;
            newRow.getElementsByTagName("select")[0].appendChild(option);
        });

        // Add event listeners to the new row
        newRow.addEventListener("change", (e) => {
            saveTempClientQuoteProfile(e.currentTarget, clientId);
        });
        newRow.getElementsByTagName("button")[0].addEventListener("click", (e) => {
            // Remove a service row from the Client Quote Profile services table
            removeServiceFromClientQuoteProfileServicesTable(e.currentTarget);
        });
        newRow.getElementsByTagName("select")[0].addEventListener("change", () => {
            // Populate unit price based on selected service
            const unitPrice = newRow.getElementsByTagName("select")[0].options[newRow.getElementsByTagName("select")[0].selectedIndex].dataset.unitPrice;
            newRow.getElementsByTagName("input")[1].value = Number(unitPrice).toFixed(2);
        });
        newRow.addEventListener("change", (e) => {
            // Update total price based on quantity, unit price, and tax
            // Base price = quantity * unit price
            const basePrice = Number(newRow.getElementsByTagName("input")[0].value) * Number(newRow.getElementsByTagName("input")[1].value);
            // Tax amount = (tax / 100) * base price
            const taxAmount = (Number(newRow.getElementsByTagName("input")[2].value) / 100.00) * basePrice;
            // Total price = base price + tax amount
            newRow.getElementsByTagName("p")[0].innerText = Number(basePrice + taxAmount).toFixed(2);
            newRow.getElementsByTagName("input")[3].value = Number(basePrice + taxAmount);
        });
    }

    function saveTempClientQuoteProfile(eventElement, clientId) {
        minMonthlyCharge = Number(document.getElementById(`input_batch-quotes-form_client-quote-profile_min-monthly-charge_client-${clientId}`).value);
        premiumSaltUpcharge = Number(document.getElementById(`input_batch-quotes-form_client-quote-profile_premium-salt-upcharge_client-${clientId}`).value);

        // Extract the list of services
        let services = [];
        let grandTotal = 0;
        document.getElementById(`tbody_batch-quotes-form_client-quote-profile-services_client-${clientId}`).querySelectorAll("tr").forEach((row) => {
            services.push({
                "service_name": row.getElementsByTagName("select")[0].value,
                "quantity": row.getElementsByTagName("input")[0].value,
                "per_unit": row.getElementsByTagName("select")[1].value, //? row.getElementsByTagName("input")[1].value != "-1" : "--",
                "unit_price": row.getElementsByTagName("input")[1].value,
                "tax": row.getElementsByTagName("input")[2].value,
                "total_price": row.getElementsByTagName("input")[3].value
            });
            grandTotal += Number(row.getElementsByTagName("input")[3].value);
        });

        fetch("/quotes/save_temp_client_quote_profile", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                "client_id": clientId,
                "min_monthly_charge": minMonthlyCharge,
                "premium_salt_upcharge": premiumSaltUpcharge,
                "services": services,
                "grand_total": grandTotal
            })
        })
    }
    //#endregion FUNCTIONS
});