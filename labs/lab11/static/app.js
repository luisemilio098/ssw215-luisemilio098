document.addEventListener('DOMContentLoaded', () => {
  const filterInput = document.getElementById('filter-input');
  const projectCount = document.getElementById('project-count');
  const projectsGrid = document.querySelector('.projects-grid');
  const newProjectForm = document.getElementById('new-project-form');
  const newTitleInput = document.getElementById('new-title');
  const smartCreateForm = document.getElementById('smart-create-form');
  const smartNotesInput = document.getElementById('smart-notes');
  const smartCreateStatus = document.getElementById('smart-create-status');
  const githubImportForm = document.getElementById('github-import-form');
  const repoOwnerInput = document.getElementById('repo-owner');
  const repoNameInput = document.getElementById('repo-name');
  const githubImportStatus = document.getElementById('github-import-status');
  const githubDraftPanel = document.getElementById('github-draft-panel');
  const githubFeedbackForm = document.getElementById('github-feedback-form');
  const githubFeedbackInput = document.getElementById('github-feedback');
  const githubDraftStatus = document.getElementById('github-draft-status');
  const githubBlindRefineButton = document.getElementById('github-blind-refine-button');
  const githubApproveButton = document.getElementById('github-approve-button');
  const githubDraftFields = {
    title: document.getElementById('github-draft-title'),
    summary: document.getElementById('github-draft-summary'),
    technologies: document.getElementById('github-draft-technologies'),
    difficulty: document.getElementById('github-draft-difficulty'),
  };
  let githubSessionId = null;

  if (
    !filterInput || !projectCount || !projectsGrid || !newProjectForm || !newTitleInput
    || !smartCreateForm || !smartNotesInput || !smartCreateStatus || !githubImportForm
    || !repoOwnerInput || !repoNameInput || !githubImportStatus || !githubDraftPanel
    || !githubFeedbackForm || !githubFeedbackInput || !githubDraftStatus
    || !githubBlindRefineButton || !githubApproveButton
    || Object.values(githubDraftFields).some((field) => !field)
  ) {
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

    if (project.technologies) {
      const technologies = document.createElement('p');
      technologies.className = 'project-technologies';
      technologies.textContent = `Technologies: ${project.technologies}`;
      card.append(heading, description, technologies);
    } else {
      card.append(heading, description);
    }

    const author = document.createElement('p');
    author.className = 'project-author';
    author.textContent = `Made by ${project.author_name}`;

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

    card.append(author, actions);
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

  smartCreateForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const submitButton = smartCreateForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    smartCreateStatus.textContent = '';

    try {
      const response = await fetch('/api/projects/smart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ notes: smartNotesInput.value }),
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.error || `Smart create failed with status ${response.status}`);
      }
      const project = await response.json();
      projectsGrid.append(createProjectCard(project));
      smartCreateForm.reset();
      smartCreateStatus.textContent = 'Project created.';
      updateProjectList();
    } catch (error) {
      console.error(error);
      smartCreateStatus.textContent = error.message;
    } finally {
      submitButton.disabled = false;
    }
  });

  const renderGithubDraft = (draft) => {
    githubDraftFields.title.textContent = draft.title;
    githubDraftFields.summary.textContent = draft.summary;
    githubDraftFields.technologies.textContent = draft.technologies.join(', ');
    githubDraftFields.difficulty.textContent = draft.difficulty;
    githubDraftPanel.classList.remove('hidden');
  };

  githubImportForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const submitButton = githubImportForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    githubImportStatus.textContent = '';
    githubDraftPanel.classList.add('hidden');
    githubSessionId = null;

    try {
      const response = await fetch('/api/projects/git-start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          owner: repoOwnerInput.value,
          repo: repoNameInput.value,
        }),
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.error || `GitHub import failed with status ${response.status}`);
      }
      const result = await response.json();
      githubSessionId = result.session_id;
      renderGithubDraft(result.draft);
      githubDraftStatus.textContent = '';
      githubFeedbackForm.reset();
    } catch (error) {
      console.error(error);
      githubImportStatus.textContent = error.message;
    } finally {
      submitButton.disabled = false;
    }
  });

  githubFeedbackForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (!githubSessionId) {
      githubDraftStatus.textContent = 'Fetch a repository draft first.';
      return;
    }

    const submitButton = githubFeedbackForm.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    githubDraftStatus.textContent = '';

    try {
      const response = await fetch('/api/projects/git-refine', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: githubSessionId,
          feedback: githubFeedbackInput.value,
        }),
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.error || `Draft refinement failed with status ${response.status}`);
      }
      const result = await response.json();
      renderGithubDraft(result.draft);
      githubDraftStatus.textContent = 'Draft updated.';
    } catch (error) {
      console.error(error);
      githubDraftStatus.textContent = error.message;
    } finally {
      submitButton.disabled = false;
    }
  });

  githubBlindRefineButton.addEventListener('click', async () => {
    if (!githubSessionId) {
      githubDraftStatus.textContent = 'Fetch a repository draft first.';
      return;
    }

    githubBlindRefineButton.disabled = true;
    githubDraftStatus.textContent = '';

    try {
      const response = await fetch('/api/projects/git-refine-blind', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: githubSessionId,
          feedback: githubFeedbackInput.value,
        }),
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.error || `Blind draft refinement failed with status ${response.status}`);
      }
      const result = await response.json();
      renderGithubDraft(result.draft);
      githubDraftStatus.textContent = 'Draft updated without history.';
    } catch (error) {
      console.error(error);
      githubDraftStatus.textContent = error.message;
    } finally {
      githubBlindRefineButton.disabled = false;
    }
  });

  githubApproveButton.addEventListener('click', async () => {
    if (!githubSessionId) {
      githubDraftStatus.textContent = 'Fetch a repository draft first.';
      return;
    }

    githubApproveButton.disabled = true;
    githubDraftStatus.textContent = '';

    try {
      const response = await fetch('/api/projects/git-commit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: githubSessionId }),
      });

      if (!response.ok) {
        const result = await response.json();
        throw new Error(result.error || `Saving the draft failed with status ${response.status}`);
      }
      const project = await response.json();
      projectsGrid.append(createProjectCard(project));
      githubDraftPanel.classList.add('hidden');
      githubSessionId = null;
      githubImportStatus.textContent = 'Project imported.';
      updateProjectList();
    } catch (error) {
      console.error(error);
      githubDraftStatus.textContent = error.message;
    } finally {
      githubApproveButton.disabled = false;
    }
  });
});
