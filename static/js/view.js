document.addEventListener("DOMContentLoaded", () => {
  const catList = document.getElementById("catList");
  const listBtn = document.getElementById("listBtn");
  const galleryBtn = document.getElementById("galleryBtn");
  const topBtn = document.getElementById("top_btn");
  const searchInput = document.getElementById("searchInput");
  const searchTermSpan = document.getElementById("searchTerm");

  // Set default view to gallery
  catList.classList.add("gallery-view");

  // Toggle view buttons
  listBtn.addEventListener("click", () => {
    catList.classList.remove("gallery-view");
    catList.classList.add("list-view");
  });

  galleryBtn.addEventListener("click", () => {
    catList.classList.remove("list-view");
    catList.classList.add("gallery-view");
  });

  // Scroll to top button
  topBtn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });

  // Search filtering logic
  const params = new URLSearchParams(window.location.search);
  const query = params.get("q")?.toLowerCase() || "";

  if (searchTermSpan && searchInput) {
    searchTermSpan.textContent = query;
    searchInput.value = query;
  }

  const listItems = catList.querySelectorAll("li");
  listItems.forEach((li) => {
    const text = li.textContent.toLowerCase();
    if (text.includes(query)) {
      li.style.display = "";
    } else {
      li.style.display = "none";
    }
  });
});
