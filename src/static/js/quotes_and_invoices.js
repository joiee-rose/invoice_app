document.addEventListener("DOMContentLoaded", function() {
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
        const selectedClients = getSelectedClients();
        populateClientQuoteProfiles(selectedClients);

        switchFrames(invoiceFormFrame2, invoiceFormFrame1);
    });

    // Click event listener to show frame 1 of the invoice form, from frame 2
    document.getElementById("btn_invoice-form_show-frame-1").addEventListener("click", () => {
        switchFrames(invoiceFormFrame1, invoiceFormFrame2);
    });

    // Click event listener to close the invoice form
    document.getElementById("btn_hide-invoice-form").addEventListener("click", () => {
        // TODO - switch back to frame 1
        switchFrames(invoiceFormFrame1, invoiceFormFrame2);
        closeFormDialog(invoiceFormDialog); 
    });

    function populateClientQuoteProfiles(clients) {
        Object.keys(clients).forEach((id) => {
            const newDiv = document.createElement("div");
            newDiv.innerHTML = `
                <p class="text-base">Client Name: ${clients[id]}</p>
            `;
            document.getElementById("invoice-form_client-quote-profiles-container").appendChild(newDiv);
        });
    }

    function getSelectedClients() {
        const selectedClients = {};
        document.querySelectorAll('[id^="input_invoice-form_client-id-"]').forEach((checkbox) => {
            if (checkbox.checked) {
                selectedClients[checkbox.dataset.clientId] = checkbox.dataset.clientName;
            }
        });
        return selectedClients;
    }
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
    //#endregion HELPER FUNCTIONS
});