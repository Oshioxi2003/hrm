function handleLogout(e) {
    e.preventDefault();
    if (confirm('Are you sure you want to logout?')) {
        document.getElementById('logout-form').submit();
    }
}
