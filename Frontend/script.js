// Sidebar toggle for desktop
const sidebar = document.getElementById('sidebar');
const collapseBtn = document.getElementById('collapseBtn');
const menuMobile = document.getElementById('menuMobile');
const searchInput = document.getElementById('searchInput');

// Hide sidebar on mobile
menuMobile.addEventListener('click', () => {
  sidebar.classList.toggle('hidden');
});

// Collapse button (desktop)
collapseBtn.addEventListener('click', () => {
  sidebar.classList.toggle('hidden');
  collapseBtn.textContent = sidebar.classList.contains('hidden')
    ? 'Show menu'
    : 'Hide menu';
});

// Simulate search selection process
searchInput.addEventListener('click', () => {
  const type = prompt("Search for a 'doctor' or a 'patient'?");
  if (!type) return;
  const name = prompt(`Enter ${type} name:`);
  if (name) {
    searchInput.value = `${type.toUpperCase()}: ${name}`;
  }
});

// Placeholder for menu buttons
function openPanel(name) {
  alert(`Open panel: ${name} (this will connect to backend soon)`);
}
