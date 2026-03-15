// 深色模式切換
function toggleDark() {
    document.body.classList.toggle('dark-mode');

    // 記住使用者的選擇
    if (document.body.classList.contains('dark-mode')) {
        localStorage.setItem('darkMode', 'enabled');
        document.querySelector('[onclick="toggleDark()"]').textContent = '☀️ 淺色';
    } else {
        localStorage.setItem('darkMode', 'disabled');
        document.querySelector('[onclick="toggleDark()"]').textContent = '🌙 深色';
    }
}

// 頁面載入時恢復上次的設定
window.onload = function () {
    if (localStorage.getItem('darkMode') === 'enabled') {
        document.body.classList.add('dark-mode');
        document.querySelector('[onclick="toggleDark()"]').textContent = '☀️ 淺色';
    }
}