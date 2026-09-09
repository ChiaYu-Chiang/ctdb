document.addEventListener('DOMContentLoaded', function () {
    const formsetRoot = document.querySelector('#workHoursFormset');
    const container = document.querySelector('#workHoursRows');
    const addButton = document.querySelector('#addWorkHoursRow');
    const emptyFormTemplate = document.querySelector('#workHoursEmptyForm');
    // Django's inline formset prefix defaults to the FK's related_name (here: "work_hours"),
    // not the generic "form" prefix — so look the TOTAL_FORMS input up by suffix instead
    // of hardcoding a prefix that could drift if the model's related_name ever changes.
    const totalFormsInput = formsetRoot ? formsetRoot.querySelector('input[name$="-TOTAL_FORMS"]') : null;

    if (!container || !addButton || !emptyFormTemplate || !totalFormsInput) {
        return;
    }

    addButton.addEventListener('click', function () {
        const formIndex = parseInt(totalFormsInput.value, 10);
        const newRowHtml = emptyFormTemplate.innerHTML.trim().replace(/__prefix__/g, formIndex);
        const wrapper = document.createElement('div');
        wrapper.innerHTML = newRowHtml;
        container.appendChild(wrapper.firstElementChild);
        totalFormsInput.value = formIndex + 1;
    });

    container.addEventListener('click', function (e) {
        if (!e.target.classList.contains('removeWorkHoursRow')) {
            return;
        }
        const row = e.target.closest('.work-hours-row');
        const deleteCheckbox = row.querySelector('input[type="checkbox"][name$="-DELETE"]');
        if (deleteCheckbox) {
            // Existing row (has a pk): mark for deletion so Django's formset
            // actually deletes the DiaryWorkHour row on save, and hide it.
            deleteCheckbox.checked = true;
            row.style.display = 'none';
        } else {
            // Newly-added, never-saved row: just drop it from the DOM.
            row.remove();
        }
    });
});