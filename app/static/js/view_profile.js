function openMessageModal() {
  var messageModal = document.getElementById("messageModal");
  messageModal.style.display = "block";
}

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

  var messageModal = document.getElementById("messageModal");
  var messageSpan = document.getElementsByClassName("close-message")[0];

  messageSpan.onclick = function() {
    messageModal.style.display = "none";
  }
}