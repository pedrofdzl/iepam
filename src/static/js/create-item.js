let action = document.getElementById('action').innerHTML;

if (action == 1) {
    document.getElementById('lectura').classList.add('active');
    hideAll();
    document.getElementById('div-lectura').style.display = 'block';
}
else if (action == 2) {
    document.getElementById('actividad').classList.add('active');
    hideAll();
    document.getElementById('div-actividad').style.display = 'block';
}
else if (action == 3) {
    document.getElementById('video').classList.add('active');
    hideAll();
    document.getElementById('div-video').style.display = 'block';
}
else if (action == 4) {
    document.getElementById('quiz').classList.add('active');
    hideAll();
    document.getElementById('div-quiz').style.display = 'block';
}

function hideAll() {
    document.getElementById('div-lectura').style.display = 'none';
    document.getElementById('div-actividad').style.display = 'none';
    document.getElementById('div-video').style.display = 'none';
    document.getElementById('div-quiz').style.display = 'none';
}