document.addEventListener("DOMContentLoaded", function() {
    //#region NEW QUOTE(S)
    const quoteFormDialog = document.getElementById("dialog_quote-form");
    const quoteForm = document.getElementById("form_quote-form");
    const quoteFormFrame1 = document.getElementById("div_quote-form_frame-1");
    const quoteFormFrame2 = document.getElementById("div_quote-form_frame-2");

    // Click event listener to open frame 1 of the quote form
    document.getElementById("btn_show-quote-form").addEventListener("click", () => {
        openFormDialog(quoteFormDialog);
    });

    // Click event listener to show frame 2 of the quote form, from frame 1
    document.getElementById("btn_quote-form_show-frame-2").addEventListener("click", () => {
        // Get a list of the selected clients and populate the next frame
        // with their client quote profiles
        const selectedClients = getSelectedClients("quote");
        createClientQuoteProfileTables(selectedClients, "quote");

        switchFrames(quoteFormFrame2, quoteFormFrame1);
    });

    // Click event listener to show frame 1 of the quote form, from frame 2
    document.getElementById("btn_quote-form_show-frame-1").addEventListener("click", () => {
        switchFrames(quoteFormFrame1, quoteFormFrame2);
    });

    // Click event listener to close the quote form
    document.getElementById("btn_hide-quote-form").addEventListener("click", () => {
        switchFrames(quoteFormFrame1, quoteFormFrame2);
        closeFormDialog(quoteFormDialog); 
    });
    //#endregion NEW QUOTE(S)

    //#region NEW INVOICE
    const invoiceFormDialog = document.getElementById("dialog_invoice-form");
    const invoiceForm = document.getElementById("form_invoice-form");
    const invoiceFormFrame1 = document.getElementById("div_invoice-form_frame-1");
    const invoiceFormFrame2 = document.getElementById("div_invoice-form_frame-2");

    // Click event listener to open frame 1 of the invoice form
    document.getElementById("btn_show-invoice-form").addEventListener("click", () => {
        openFormDialog(invoiceFormDialog);
    });

    // Click event listener to show frame 2 of the invoice form, from frame 1
    document.getElementById("btn_invoice-form_show-frame-2").addEventListener("click", () => {
        // Get a list of the selected clients and populate the next frame
        // with their client quote profiles
        const selectedClients = getSelectedClients("invoice");
        createClientQuoteProfileTables(selectedClients, "invoice");

        switchFrames(invoiceFormFrame2, invoiceFormFrame1);
    });

    // Click event listener to show frame 1 of the invoice form, from frame 2
    document.getElementById("btn_invoice-form_show-frame-1").addEventListener("click", () => {
        switchFrames(invoiceFormFrame1, invoiceFormFrame2);
    });

    // Click event listener to close the invoice form
    document.getElementById("btn_hide-invoice-form").addEventListener("click", () => {
        switchFrames(invoiceFormFrame1, invoiceFormFrame2);
        closeFormDialog(invoiceFormDialog); 
    });
    //#endregion NEW INVOICE

    //#region HELPER FUNCTIONS
    function openFormDialog(formDialog) {
        formDialog.removeAttribute("hidden");
        formDialog.showModal();
    }

    function closeFormDialog(formDialog) {
        // Remove all client quote profiles from the invoice form
        document.getElementById("invoice-form_client-quote-profiles-container").innerHTML = "";
        // Reset checked clients from the invoice form
        document.querySelectorAll('[id^="input_invoice-form_client-id-"]').forEach((checkbox) => {
            if (checkbox.checked) {
                checkbox.checked = false;
            }
        });

        formDialog.setAttribute("hidden", "hidden");
        formDialog.close();
    }

    function switchFrames(frameToShow, frameToHide) {
        frameToHide.setAttribute("hidden", "hidden");
        frameToShow.removeAttribute("hidden");
    }

    // Function to create and add to the DOM client quote profiles for the selected clients in frame 2 of the invoice form
    function createClientQuoteProfileTables(clients, formType) {
        const colorTheme = invoiceForm.dataset.colorTheme;
        
        clients.forEach(client => {
            // Create and add the table to a container div
            const newDiv = document.createElement("div");
            newDiv.classList.add("flex", "flex-col", "mb-4");
            newDiv.innerHTML = `
                <!-- Client Information -->
                <div class="mb-2 flex flex-col">
                    <p class="text-base">${client.name}</p>
                    <p class="text-base">${client.business_name}</p>
                </div>
                <div class="relative w-full h-full mb-4 overflow-scroll flex flex-col bg-white shadow-md rounded-lg bg-clip-border">
                    <table class="w-full min-w-max table-auto text-left">
                        <thead>
                            <tr class="h-[1.5rem] bg-${colorTheme} border-b">
                                <th class="w-[25%] p-2">Service</th>
                                <th class="w-[5%] p-2">Quantity</th>
                                <th class="w-[25%] p-2">Per Unit</th>
                                <th class="w-[20%] p-2">Unit Price</th>
                                <th class="w-[20%] p-2">Total Price</th>
                            </tr>
                        </thead>
                        <tbody id="tbody_client-quote-profile-services_client-${client.id}">
                            <!-- rows added dynamically with JavaScript -->
                        </tbody>
                    </table>
                </div>
                <!-- Add Service Button -->
                <div class="flex justify-start">
                    <button type="button" id="btn_add-client-service_client-${client.id}" class="h-[2rem] pl-4 pr-4 bg-${colorTheme} rounded-md text-base font-semibold cursor-pointer">Add Service</button>
                </div>
                <!-- hidden input storing Services Count -->
                <input type="text" id="input_client-quote-profile_services-count_client-${client.id}" name="services-count_client-${client.id}" value="0" hidden>
            `;
            document.getElementById(`${formType}-form_client-quote-profiles-container`).appendChild(newDiv);

            // Check if client already has a quote profile
            fetch(`/clients/api/quote_profile/${client.id}`)
            .then(response => (response.status === 200) ? response.json() : null)
            .then(data => {
                if (data) {
                    populateClientQuoteProfile(data);
                } else {
                    addRowToClientQuoteProfileServicesTable(0, client.id);
                    document.getElementById(`input_client-quote-profile_services-count_client-${client.id}`).value = 1;
                }
            })
            .catch(error => {
                console.log('Error fetching client quote profile:', error);
            });

            // Add click event listener to each table's "Add Service" button
            document.getElementById(`btn_add-client-service_client-${client.id}`).addEventListener("click", () => {
                addRowToClientQuoteProfileServicesTable(Number(document.getElementById(`input_client-quote-profile_services-count_client-${client.id}`).value), client.id);
            });
        });
    }

    async function populateClientQuoteProfile(data) {
        for (let i = 0; i < data.services.length; ++i) {
            await addRowToClientQuoteProfileServicesTable(i, data.client_id);
            document.getElementById(`select_service-${i}_client-${data.client_id}`).value = data.services[i].service_id;
            document.getElementById(`input_quantity-${i}_client-${data.client_id}`).value = data.services[i].quantity;
            document.getElementById(`select_per-unit-${i}_client-${data.client_id}`).value = data.services[i].per_unit;
            document.getElementById(`p_unit-price-${i}_client-${data.client_id}`).innerText = Number(data.services[i].unit_price).toFixed(2);
            document.getElementById(`p_total-price-${i}_client-${data.client_id}`).innerText = Number(data.services[i].total_price).toFixed(2);

            // hidden inputs
            document.getElementById(`input_service-name-${i}_client-${data.client_id}`).value = data.services[i].service_name;
            document.getElementById(`input_unit-price-${i}_client-${data.client_id}`).value = data.services[i].unit_price;
            document.getElementById(`input_total-price-${i}_client-${data.client_id}`).value = data.services[i].total_price;
        }
    }

    function addRowToClientQuoteProfileServicesTable(rowNumber, clientId) {
        return new Promise((resolve, reject) => {
            document.getElementById(`input_client-quote-profile_services-count_client-${clientId}`).value = Number(document.getElementById(`input_client-quote-profile_services-count_client-${clientId}`).value) + 1;

            const newRow = document.createElement("tr");

            newRow.id = `tbl_row-${rowNumber}_client-${clientId}`;
            newRow.classList.add(`h-[2rem]`);
            newRow.innerHTML = `
                <!-- Service -->
                <td class="p-2">
                    <select id="select_service-${rowNumber}_client-${clientId}" name="service-${rowNumber}_client-${clientId}" class="cursor-pointer">
                        <option value="-1" selected>--</option>
                    </select>
                    <!-- hidden input storing Service Name -->
                    <input type="text" id="input_service-name-${rowNumber}_client-${clientId}" name="service-name-${rowNumber}_client-${clientId}" hidden>
                </td>
                <!-- Quantity -->
                <td class="p-2">
                    <input type="number" id="input_quantity-${rowNumber}_client-${clientId}" name="quantity-${rowNumber}_client-${clientId}" min="1" step="1" value="1" class="h-[2rem] p-2 border rounded-md text-base">
                </td>
                <!-- Per Unit -->
                <td class="p-2">
                    <select id="select_per-unit-${rowNumber}_client-${clientId}" name="per-unit-${rowNumber}_client-${clientId}" class="cursor-pointer">
                        <option value="-1" selected>--</option>
                        <option value="per-visit">per visit</option>
                        <option value="per-push">per push</option>
                    </select>
                </td>
                <!-- Unit Price -->
                <td class="p-2">
                    <p id="p_unit-price-${rowNumber}_client-${clientId}" class="p-2"></p>
                    <!-- hidden input storing Unit Price -->
                    <input type="text" id="input_unit-price-${rowNumber}_client-${clientId}" name="unit-price-${rowNumber}_client-${clientId}" hidden>
                </td>
                <!-- Total Price -->
                <td class="p-2">
                    <p id="p_total-price-${rowNumber}_client-${clientId}" class="p-2"></p>
                    <!-- hidden input storing Total Price -->
                    <input type="text" id="input_total-price-${rowNumber}_client-${clientId}" name="total-price-${rowNumber}_client-${clientId}" hidden>
                </td>
            `;
            document.getElementById(`tbody_client-quote-profile-services_client-${clientId}`).appendChild(newRow);

            // Append an option for each service in the database to the service select element
            fetch("/services/api/all")
            .then(response => response.json())
            .then(data => {
                Array.from(data).forEach((service) => {
                    const option = document.createElement("option");

                    option.value = service.id;
                    option.dataset.unitPrice = service.unit_price;
                    option.innerText = service.name;

                    document.getElementById(`select_service-${rowNumber}_client-${clientId}`).appendChild(option);
                });
                resolve();
            })
            .catch(error => {
                console.log('Error fetching services:', error);
                reject(error);
            });

            const serviceSelect = document.getElementById(`select_service-${rowNumber}_client-${clientId}`);
            const inputQuantity = document.getElementById(`input_quantity-${rowNumber}_client-${clientId}`);
            const unitPrice = document.getElementById(`p_unit-price-${rowNumber}_client-${clientId}`);
            const totalPrice = document.getElementById(`p_total-price-${rowNumber}_client-${clientId}`);

            // Populate unit price based on selected service
            serviceSelect.addEventListener("change", () => {
                if (serviceSelect.value != -1) {
                    const serviceUnitPrice = serviceSelect.options[serviceSelect.selectedIndex].dataset.unitPrice;
                    unitPrice.innerText = Number(serviceUnitPrice).toFixed(2);

                    // Update service name and unit price hidden inputs
                    document.getElementById(`input_service-name-${rowNumber}_client-${clientId}`).value = serviceSelect.options[serviceSelect.selectedIndex].innerText;
                    document.getElementById(`input_unit-price-${rowNumber}_client-${clientId}`).value = Number(serviceUnitPrice).toFixed(2);
                } else {
                    unitPrice.innerText = "";
                    document.getElementById(`input_service-name-${rowNumber}_client-${clientId}`).value = "";
                    document.getElementById(`input_unit-price-${rowNumber}_client-${clientId}`).value = "";
                }
            });

            // Update total price based on quantity and unit price
            document.getElementById(`tbl_row-${rowNumber}_client-${clientId}`).addEventListener("change", (event) => {
                if (serviceSelect.value != -1 && inputQuantity.value != null && inputQuantity.value != "") {
                    totalPrice.innerText = Number(inputQuantity.value * unitPrice.innerText).toFixed(2);
                    document.getElementById(`input_total-price-${rowNumber}_client-${clientId}`).value = totalPrice.innerText;
                }
            });
        });
    }

    // Function to get the selected clients from frame 1 of the invoice form and update the hidden input with the selected client IDs
    function getSelectedClients(formType) {
        const selectedClients = [];
        document.querySelectorAll(`[id^="input_${formType}-form_client-id-"]`).forEach((checkbox) => {
            if (checkbox.checked) {
                selectedClients.push({
                    id: checkbox.dataset.clientId,
                    name: checkbox.dataset.clientName,
                    business_name: checkbox.dataset.clientBusinessName
                });
            }
        });
        document.getElementById(`input_${formType}-form_client-ids`).value = selectedClients.map(client => client.id).join(";");
        return selectedClients;
    }
    //#endregion HELPER FUNCTIONS
});