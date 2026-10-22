document.addEventListener('DOMContentLoaded', () => {
  const filterInput = document.getElementById('filter-input');
  const projectCards = Array.from(document.querySelectorAll('.card'));
  const projectCount = document.getElementById('project-count');

  if (!filterInput || !projectCount || projectCards.length === 0) {
    return;
  }

  const updateProjectList = () => {
    const filterText = filterInput.value.trim().toLowerCase(); // Hand edited by LEA
    let visibleCount = 0;
    const visibleTitles = [];

    projectCards.forEach((card) => {
      const cardText = card.textContent.toLowerCase(); // Hand edited by LEA
      const isVisible = filterText === '' || cardText.includes(filterText);

      card.classList.toggle('hidden', !isVisible);

      if (isVisible) {
        visibleCount += 1;
        const titleElement = card.querySelector('h3');

        if (titleElement) {
          visibleTitles.push(titleElement.textContent.trim());
        }
      }
    });

    console.log(visibleTitles);
    projectCount.textContent = `Showing ${visibleCount} of ${projectCards.length} projects`;
  };

  filterInput.addEventListener('input', updateProjectList);
  updateProjectList();

  projectCards.forEach((card) => {
    const upvoteButton = card.querySelector('.upvote-btn');
    const likeCount = card.querySelector('.like-count');

    if (!upvoteButton || !likeCount) {
      return;
    }

    upvoteButton.addEventListener('click', async () => {
      upvoteButton.disabled = true;

      try {
        const response = await fetch(
          `/api/projects/${card.dataset.projectId}/upvote`,
          { method: 'POST' },
        );

        if (!response.ok) {
          throw new Error(`Upvote failed with status ${response.status}`);
        }

        const project = await response.json();
        if (!Number.isInteger(project.likes)) {
          throw new Error('Upvote response did not include a valid like count');
        }

        likeCount.textContent = project.likes;

        if (project.likes > 10 && !card.querySelector('.trending-badge')) {
          const badge = document.createElement('span');
          badge.className = 'trending-badge';
          badge.textContent = 'Trending';
          card.querySelector('.project-card-heading').append(badge);
        }
      } catch (error) {
        console.error(error);
      } finally {
        upvoteButton.disabled = false;
      }
    });
  });
});
