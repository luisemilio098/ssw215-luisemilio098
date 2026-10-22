document.addEventListener('DOMContentLoaded', () => {
  const filterInput = document.getElementById('filter-input');
  const projectCount = document.getElementById('project-count');
  const projectsGrid = document.querySelector('.projects-grid');
  const newProjectForm = document.getElementById('new-project-form');
  const newTitleInput = document.getElementById('new-title');

  if (!filterInput || !projectCount || !projectsGrid || !newProjectForm || !newTitleInput) {
    return;
  }

  const updateProjectList = () => {
    const filterText = filterInput.value.trim().toLowerCase();
    const projectCards = Array.from(projectsGrid.querySelectorAll('.card'));
    let visibleCount = 0;
    const visibleTitles = [];

    projectCards.forEach((card) => {
      const cardText = card.textContent.toLowerCase();
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

  const addTrendingBadge = (card, likes) => {
    const heading = card.querySelector('.project-card-heading');
    if (likes > 10 && heading && !heading.querySelector('.trending-badge')) {
      const badge = document.createElement('span');
      badge.className = 'trending-badge';
      badge.textContent = 'Trending';
      heading.append(badge);
    }
  };

  const createProjectCard = (project) => {
    const card = document.createElement('article');
    card.className = 'card';
    card.dataset.projectId = project.id;

    const heading = document.createElement('div');
    heading.className = 'project-card-heading';
    const title = document.createElement('h3');
    title.className = 'project-card-title';
    title.textContent = project.title;
    heading.append(title);

    const description = document.createElement('p');
    description.className = 'project-card-description';
    description.textContent = project.description;

    const actions = document.createElement('div');
    actions.className = 'project-card-actions';
    const upvoteButton = document.createElement('button');
    upvoteButton.className = 'upvote-btn';
    upvoteButton.type = 'button';
    upvoteButton.textContent = 'Upvote';
    const likeCount = document.createElement('span');
    likeCount.className = 'like-count';
    likeCount.textContent = project.likes;
    actions.append(upvoteButton, likeCount);

    card.append(heading, description, actions);
    addTrendingBadge(card, project.likes);
    return card;
  };

  filterInput.addEventListener('input', updateProjectList);
  updateProjectList();

  projectsGrid.addEventListener('click', async (event) => {
    const upvoteButton = event.target.closest('.upvote-btn');
    if (!upvoteButton || !projectsGrid.contains(upvoteButton)) {
      return;
    }

    const card = upvoteButton.closest('.card');
    if (!card) {
      return;
    }
    const likeCount = card.querySelector('.like-count');
    if (!likeCount) {
      return;
    }

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
      addTrendingBadge(card, project.likes);
    } catch (error) {
      console.error(error);
    } finally {
      upvoteButton.disabled = false;
    }
  });

  newProjectForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const submitButton = newProjectForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;

    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: newTitleInput.value }),
      });

      if (!response.ok) {
        throw new Error(`Project creation failed with status ${response.status}`);
      }
      const project = await response.json();
      projectsGrid.append(createProjectCard(project));
      newProjectForm.reset();
      updateProjectList();
    } catch (error) {
      console.error(error);
    } finally {
      submitButton.disabled = false;
    }
  });
});
