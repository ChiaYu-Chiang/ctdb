document.addEventListener("DOMContentLoaded", function() {
    const select = document.querySelector("#id_isps");
    const loa = document.querySelector("#id_form_row_loa");
    const loa_remark = document.querySelector("#id_form_row_loa_remark");
    loa.style.display = "none";
    loa_remark.style.display = "none";
    for (let i = 0; i < select.options.length; i++) {
        if (select.options[i].selected && select.options[i].textContent.includes("HiNet")) {
            loa.style.display = "";
            loa_remark.style.display = "";
            break;
        }
    }
    select.addEventListener("change", function() {
        for (let i = 0; i < select.options.length; i++) {
            if (select.options[i].selected && select.options[i].textContent.includes("HiNet")) {
                loa.style.display = "";
                loa_remark.style.display = "";
                return;
            }
        }
        loa.style.display = "none";
        loa_remark.style.display = "none";
    });
});
