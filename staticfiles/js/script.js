// Show loader when clicking on a link or refreshing the page
document.addEventListener("DOMContentLoaded", function() {
    showLoader();
});

// Show loader on page load
function showLoader() {
    const loader = document.getElementById("loader");
    loader.style.display = "block";  // Show loader

    // Hide loader after 2 seconds
    setTimeout(function() {
        loader.style.display = "none";  // Hide loader
    }, 2000);
}

// Show notification after 3 seconds
setTimeout(function() {
    document.getElementById("notification").classList.add("show");
}, 3000);

// Hide notification after 5 seconds
setTimeout(function() {
    document.getElementById("notification").classList.remove("show");
}, 8000);
