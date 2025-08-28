document.addEventListener("DOMContentLoaded", function() {
    // #region APP SETTINGS
    // Theme (ID: 0000)
    const themeOptionsContainer = document.getElementById("theme-options");
    const themeOptions = themeOptionsContainer.querySelectorAll("span");
    const inputSelectedTheme = document.getElementById("0000");

    // Set the default theme (light)
    selectThemeOption(inputSelectedTheme.value);

    // Add click event listeners to each theme option.
    Array.from(themeOptions).forEach(themeOption => {
        themeOption.addEventListener("click", function(event) {
            // Select the clicked theme option.
            selectThemeOption(event.currentTarget.id);
        })
    });

    // Function to select a theme option.
    // This adds the "selected" class to the clicked option and removes it from all other options.
    // Then, it adds a border to the selected option for visual feedback and provides a preview of the change.
    // Finally, it sets the selected option's id as the value of the hidden input field.
    function selectThemeOption(selectedThemeId) {
        previewThemeOptionChange(inputSelectedTheme.value, selectedThemeId);

        Array.from(themeOptions).forEach(themeOption => {
            if (themeOption.id === selectedThemeId) {
                themeOption.classList.add("selected");
                themeOption.setAttribute("class", themeOption.getAttribute("class") + " border-3 border-gray-700");
            } else {
                themeOption.classList.remove("selected");
                themeOption.setAttribute("class", themeOption.getAttribute("class").replace("border-3 border-gray-700", "").trim());
            }
        });
        inputSelectedTheme.value = selectedThemeId;
    }

    function previewThemeOptionChange(oldThemeId, newThemeId) {
        
    }

    // Color Theme (ID: 0001)
    const colorThemeOptionsContainer = document.getElementById("color-theme-options");
    const colorThemeOptions = colorThemeOptionsContainer.querySelectorAll("span");
    const inputSelectedColorTheme = document.getElementById("0001");

    // Set the default color theme (blue-400)
    selectColorOption(inputSelectedColorTheme.value);

    // Add click event listeners to each color option.
    Array.from(colorThemeOptions).forEach(colorOption => {
        colorOption.addEventListener("click", function(event) {
            // Select the clicked color option.
            selectColorOption(event.target.id);
        });
    });

    // Function to select a color option.
    // This adds the "selected" class to the clicked option and removes it from all other options.
    // Then, it adds a border to the selected option for visual feedback and provides a preview of the change.
    // Finally, it sets the selected option's id as the value of the hidden input field.
    function selectColorOption(selectedColorId) {
        previewColorOptionChange(inputSelectedColorTheme.value, selectedColorId);
        
        Array.from(colorThemeOptions).forEach(colorOption => {
            if (colorOption.id === selectedColorId) {
                colorOption.classList.add("selected");
                colorOption.setAttribute("class", colorOption.getAttribute("class") + " border-3 border-gray-700");
            } else {
                colorOption.classList.remove("selected");
                colorOption.setAttribute("class", colorOption.getAttribute("class").replace("border-3 border-gray-700", "").trim());
            }
        });
        inputSelectedColorTheme.value = selectedColorId;
    }

    function previewColorOptionChange(oldColorId, newColorId) {
        document.getElementById("btn-save-settings").setAttribute("class", document.getElementById("btn-save-settings").getAttribute("class").replace(oldColorId, newColorId));
    }

    // #endregion APP SETTINGS

    // #region INVOICES SETTINGS
    // PDF Save To Path (ID: 3000)
    const inputPDFSaveToPath = document.getElementById("3000");

    // #endregion INVOICES SETTINGS
});