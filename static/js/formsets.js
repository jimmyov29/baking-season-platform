document.addEventListener("DOMContentLoaded", () => {
    const formset = document.querySelector("[data-formset]");
    if (!formset) {
        return;
    }

    const prefix = formset.dataset.formset;
    const body = formset.querySelector("[data-formset-body]");
    const template = formset.querySelector("[data-empty-form]");
    const addButton = formset.querySelector("[data-add-form]");
    const totalForms = document.querySelector(`input[name="${prefix}-TOTAL_FORMS"]`);

    if (!body || !template || !addButton || !totalForms) {
        return;
    }

    addButton.addEventListener("click", () => {
        const index = Number(totalForms.value);
        const markup = template.innerHTML.replaceAll("__prefix__", index);
        body.insertAdjacentHTML("beforeend", markup);
        totalForms.value = index + 1;
    });

    body.addEventListener("click", (event) => {
        const button = event.target.closest("[data-remove-form]");
        if (!button) {
            return;
        }

        const row = button.closest("[data-form-row]");
        const deleteInput = row.querySelector('input[name$="-DELETE"]');
        if (deleteInput) {
            deleteInput.checked = true;
            deleteInput.value = "on";
            row.hidden = true;
            return;
        }

        row.remove();
    });
});
