function openReportModal() {
  var reportModal = document.getElementById("reportModal");
  reportModal.style.display = "block";
}

window.onload = function() {
  var reportModal = document.getElementById("reportModal");
  var reportSpan = document.getElementsByClassName("close-report")[0];

  reportSpan.onclick = function() {
    reportModal.style.display = "none";
  }
}