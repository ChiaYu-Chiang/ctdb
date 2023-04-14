document.addEventListener("DOMContentLoaded", function() {
    var select = document.querySelector("#id_isps");
    select.addEventListener("change", function() {
        var options = select.options;
        var loa = document.querySelector("#id_form_row_loa");
        for (var i = 0; i < options.length; i++) {
            if (options[i].selected && options[i].textContent.includes("HiNet")) {
                loa.style.display = "";
                return;
            }
        }
        loa.style.display = "none";
    });
});
  
