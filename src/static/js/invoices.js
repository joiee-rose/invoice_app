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

    //#region FUNCTIONS
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
    //#endregion FUNCTIONS
});