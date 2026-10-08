document.addEventListener('DOMContentLoaded', () => {
  const filterInput = document.getElementById('filter-input');
  const projectCards = Array.from(document.querySelectorAll('.card'));
  const projectCount = document.getElementById('project-count');

  if (!filterInput || !projectCount || projectCards.length === 0) {
    return;
  }

  const updateProjectList = () => {
    const filterText = filterInput.value.trim().toLowerCase();
    let visibleCount = 0;

    projectCards.forEach((card) => {
      const cardText = card.textContent.toLowerCase();
      const isVisible = filterText === '' || cardText.includes(filterText);

      card.classList.toggle('is-hidden', !isVisible);

      if (isVisible) {
        visibleCount += 1;
      }
    });

    projectCount.textContent = `Showing ${visibleCount} of ${projectCards.length} projects`;
  };

  filterInput.addEventListener('input', updateProjectList);
  updateProjectList();
});
