document.addEventListener("DOMContentLoaded", function() {
  const select = document.querySelector("#id_isps");
  const loa = document.querySelector("#id_form_row_loa");
  const loa_remark = document.querySelector("#id_form_row_loa_remark");
  const extra_file = document.querySelector("#id_form_row_extra_file");
  loa.style.display = "none";
  loa_remark.style.display = "none";
  extra_file.style.display = "none";
  for (let i = 0; i < select.options.length; i++) {
    if (
      select.options[i].selected &&
      select.options[i].textContent.includes("HiNet")
    ) {
      loa.style.display = "";
      loa_remark.style.display = "";
      extra_file.style.display = "";
      break;
    }
  }
  select.addEventListener("change", function() {
    for (let i = 0; i < select.options.length; i++) {
      if (
        select.options[i].selected &&
        select.options[i].textContent.includes("HiNet")
      ) {
        loa.style.display = "";
        loa_remark.style.display = "";
        extra_file.style.display = "";
        return;
      }
    }
    loa.style.display = "none";
    loa_remark.style.display = "none";
    extra_file.style.display = "none";
  });
});
function showSelectedFiles(fileId, selectedFilesDivId) {
  var selectedFilesDiv = document.getElementById(selectedFilesDivId);
  selectedFilesDiv.innerHTML = "";

  var files = document.getElementById(fileId).files;
  var fileList = document.createElement("ul");

  for (var i = 0; i < files.length; i++) {
    var fileItem = document.createElement("li");

    // File info
    var fileInfo = document.createElement("p");
    fileInfo.textContent = files[i].name;
    fileItem.appendChild(fileInfo);

    // Display the selected ISPs under each file with radio buttons
    var selectElement = document.getElementById("id_isps");
    var selectedISPs = [];
    for (var j = 0; j < selectElement.options.length; j++) {
      if (selectElement.options[j].selected) {
        var ispId = selectElement.options[j].value;
        var ispName = selectElement.options[j].text;
        selectedISPs.push({ id: ispId, name: ispName });
      }
    }

    // Selected ISPs with radio buttons
    var ispList = document.createElement("ul");
    for (var k = 0; k < selectedISPs.length; k++) {
      var ispItem = document.createElement("li");
      var input = document.createElement("input");
      input.type = fileId === "id_roa" ? "radio" : "checkbox";
      input.name = "selectedISP_" + fileId + "_" + i;
      input.value = selectedISPs[k].id;

      var label = document.createElement("label");
      label.appendChild(input);
      label.appendChild(document.createTextNode(selectedISPs[k].name));

      ispItem.appendChild(label);
      ispList.appendChild(ispItem);
    }

    fileItem.appendChild(ispList);
    fileList.appendChild(fileItem);
  }

  selectedFilesDiv.appendChild(fileList);
}

document.getElementById("id_isps").addEventListener("change", function() {
  showSelectedFiles("id_roa", "selectedroaFiles");
  showSelectedFiles("id_loa", "selectedloaFiles");
  showSelectedFiles("id_extra_file", "selectedextra_fileFiles");
});

document.getElementById("id_roa").addEventListener("change", function() {
  showSelectedFiles("id_roa", "selectedroaFiles");
});

document.getElementById("id_loa").addEventListener("change", function() {
  showSelectedFiles("id_loa", "selectedloaFiles");
});

document.getElementById("id_extra_file").addEventListener("change", function() {
  showSelectedFiles("id_extra_file", "selectedextra_fileFiles");
});
