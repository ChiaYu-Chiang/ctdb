{
    let selectOption = document.querySelector("#selectOption");
    selectOption.addEventListener("change",changetablebyoption)
    document.addEventListener("DOMContentLoaded", changetablebyoption)
    
    function changetablebyoption() {
        let inputValue, trs, tds, textValue, includeText;
        inputValue = document.querySelector("#selectOption").value;
        trs = document.querySelectorAll("#searchTable tbody tr");
        for (tr of trs) {
            tds = tr.querySelectorAll("td");
            textValue = ""
            for (td of tds) {
                textValue += td.textContent;
            }
            includeText = (textValue.toLowerCase().indexOf(inputValue.toLowerCase()) > -1);
            tr.style.display = includeText ? "" : "none";
        }
    }
}