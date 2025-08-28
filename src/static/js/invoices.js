document.addEventListener('DOMContentLoaded', function() {
    // #region SELECT CLIENTS
    const dialogSelectClientsForm = document.getElementById("dialog-select-clients-form");
    const formSelectClientsForm = document.getElementById("form-select-clients-form");

    // Open form 
    const btnShowSelectClientsForm = document.getElementById("btn-show-select-clients-form");
    btnShowSelectClientsForm.addEventListener("click", function() {
        dialogSelectClientsForm.removeAttribute("hidden");
        dialogSelectClientsForm.showModal();
    });

    // Close form
    const btnHideSelectClientsForm = document.getElementById("btn-hide-select-clients-form");
    btnHideSelectClientsForm.addEventListener("click", function() {
        dialogSelectClientsForm.setAttribute("hidden", "true");
        dialogSelectClientsForm.close();
    });
    // #endregion SELECT CLIENTS
});