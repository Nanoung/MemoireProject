   document.querySelectorAll('.nav-link').forEach(link => {
  link.addEventListener('click', async (e) => {
    e.preventDefault();

    // Changer l’état actif
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
    link.classList.add('active');

    const page = link.getAttribute('data-page');

    // Charger le contenu de la page correspondante
    try {
      const response = await fetch(`pages/${page}.html`);
      const html = await response.text();
      document.getElementById('content').innerHTML = html;
    } catch (error) {
      document.getElementById('content').innerHTML = `<p>Erreur lors du chargement de la page <strong>${page}</strong>.</p>`;
    }
  });
});

// Charger la page par défaut (dashboard)
window.addEventListener('DOMContentLoaded', () => {
  document.querySelector('[data-page="dashboard"]').click();
});