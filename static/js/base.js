function openNav(sidenavId) {
  document.getElementById(sidenavId).style.width = "250px";
}

function closeNav(sidenavId) {
  document.getElementById(sidenavId).style.width = "0";
}

function toggleDarkMode() {
  const darkModeStyle = document.getElementById('dark-mode');
  if (darkModeStyle.innerHTML) {
    darkModeStyle.innerHTML = '';
    localStorage.setItem('darkMode', 'disabled');
  } else {
    darkModeStyle.innerHTML = `body { background-color: rgb(34, 34, 34); color: white; }`;
    localStorage.setItem('darkMode', 'enabled');
  }
}
