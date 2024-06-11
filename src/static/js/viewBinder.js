document.addEventListener("headerUpdated", function() {
  const mobileBreakpoint = 600;
  const screenWidth = window.innerWidth;
  const isMobile = screenWidth < mobileBreakpoint;

  const tableDownloadIcon = document.getElementById("dl-label");
  if (tableDownloadIcon) {
    tableDownloadIcon.innerHTML = isMobile ? '<span class="material-symbols-outlined">download</span>' : 'Download'; 
  };
  console.log("screen size: ", screenWidth);
});

document.addEventListener("DOMContentLoaded", function() {
  binderView = document.getElementById("binder-view");
  if (binderView) { addSortListeners() };
});

function addSortListeners() {
  const titleSortIcon = document.getElementById("title-sort");
  const authorSortIcon = document.getElementById("author-sort");
  const createdSortIcon = document.getElementById("created_on-sort");

  titleSortIcon.addEventListener("click", handleSort.bind(null, "title"));
  authorSortIcon.addEventListener("click", handleSort.bind(null, "author"));
  createdSortIcon.addEventListener("click", handleSort.bind(null, "created_on"));
};

let sortColumn = "created";
let sortDescending = false;

function handleSort(column) {

  const sortIcons = document.querySelectorAll(".binder-table-header .material-symbols-outlined");
  if (column === sortColumn) {
    sortDescending = !sortDescending;
  } else {
    sortColumn = column;
  };

  sortIcons.forEach(icon => {
    const columnName = icon.parentElement.id.replace("-sort", "");
    icon.textContent = (columnName === sortColumn) ? "swap_vert" : "sort";
  });

  fetchSortedData();
};

function fetchSortedData() {
  const data = { "column": sortColumn, "sort_descending": sortDescending };

  fetch("/sort-binders", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  })
  .then(response => response.json())
  .then(data => {
    const tableRows = document.querySelectorAll(".binder-table .table-rows .binder-row");
    tableRows.forEach((row, index) => {
      const binder = data[index];
      const cells = row.querySelectorAll(".binder-info");
      cells[0].textContent = binder.title;
      cells[1].textContent = binder.author;
      cells[2].textContent = binder.created_on;
      const downloadCell = cells[3];
      downloadCell.innerHTML = binder.signed_url !== "Please check again later" ? `<a href="${binder.signed_url}" target="_blank"><span class="material-symbols-outlined">download</span></a>`
      : `<span class="material-symbols-outlined">pending</span>`;
    });
  })
  .catch(error => {
    const message = `Error sorting data: ${error}`;
    const status = "error";
    handleAPIResponse({ "message": message, "status": status });
  });
}
