document.addEventListener("DOMContentLoaded", function() {
  const select = document.querySelector("#id_isps");
  const groupSelect = document.querySelector("#id_isp_groups");
  const loa = document.querySelector("#id_form_row_loa");
  const loa_remark = document.querySelector("#id_form_row_loa_remark");
  const extra_file = document.querySelector("#id_form_row_extra_file");
  const ispgroups = JSON.parse(
    document.getElementById("ispgroups").textContent
  );

  function updateVisibility() {
    const selectedISPs = getSelectedISPs();
    const showElements = selectedISPs.some((isp) => isp.name.includes("HiNet"));
    [loa, loa_remark, extra_file].forEach(
      (el) => (el.style.display = showElements ? "" : "none")
    );
  }

  function getSelectedISPs() {
    const selectedISPs = new Set();

    // Add ISPs from direct selection
    Array.from(select.selectedOptions).forEach((option) =>
      selectedISPs.add(option.value.toString())
    );

    // Add ISPs from selected groups
    Array.from(groupSelect.selectedOptions).forEach((option) => {
      const group = option.value;
      if (ispgroups[group]) {
        ispgroups[group].forEach((isp) => selectedISPs.add(isp.toString()));
      }
    });

    // Convert Set to Array of objects
    return Array.from(selectedISPs).map((id) => {
      const option = select.querySelector(`option[value="${id}"]`);
      return {
        id: id,
        name: option ? option.textContent : `ISP ${id}`, // Fallback name if option not found
      };
    });
  }

  function updateSelectedFiles(fileId, selectedFilesDivId) {
    const selectedFilesDiv = document.getElementById(selectedFilesDivId);
    selectedFilesDiv.innerHTML = "";
    const files = document.getElementById(fileId).files;
    const fileList = document.createElement("ul");

    Array.from(files).forEach((file, i) => {
      const fileItem = document.createElement("li");
      const fileInfo = document.createElement("p");
      fileInfo.textContent = file.name;
      fileItem.appendChild(fileInfo);

      const ispList = document.createElement("ul");
      const selectedISPs = getSelectedISPs();

      if (selectedISPs.length > 0) {
        selectedISPs.forEach((isp) => {
          const ispItem = document.createElement("li");
          const input = document.createElement("input");
          input.type = "checkbox";
          input.name = `selectedISP_${fileId}_${i}`;
          input.value = isp.id;

          const label = document.createElement("label");
          label.appendChild(input);
          label.appendChild(document.createTextNode(isp.name));

          ispItem.appendChild(label);
          ispList.appendChild(ispItem);
        });
      } else {
        const noIspItem = document.createElement("li");
        noIspItem.textContent = "No ISPs selected";
        ispList.appendChild(noIspItem);
      }

      fileItem.appendChild(ispList);
      fileList.appendChild(fileItem);
    });

    selectedFilesDiv.appendChild(fileList);
  }

  function updateAllFiles() {
    ["id_roa", "id_loa", "id_extra_file"].forEach((id) =>
      updateSelectedFiles(id, `selected${id.slice(3)}Files`)
    );
  }

  function updateAll() {
    updateVisibility();
    updateAllFiles();
  }

  updateAll();

  select.addEventListener("change", updateAll);
  groupSelect.addEventListener("change", updateAll);

  ["id_roa", "id_loa", "id_extra_file"].forEach((id) => {
    document
      .getElementById(id)
      .addEventListener("change", () =>
        updateSelectedFiles(id, `selected${id.slice(3)}Files`)
      );
  });
});
