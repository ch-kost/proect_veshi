"use strict";

document.querySelectorAll("[data-current-year]").forEach((element) => {
  element.textContent = String(new Date().getFullYear());
});

const searchField = document.querySelector("#item-search");
if (searchField) {
  searchField.addEventListener("input", () => {
    searchField.setAttribute("data-has-value", String(searchField.value.length > 0));
  });
}
