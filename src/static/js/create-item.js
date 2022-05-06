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
else if (action == 5) {
    document.getElementById('resource').classList.add('active');
    hideAll();
    document.getElementById('div-resource').style.display = 'block';
}
else if (action == 6) {
    document.getElementById('hangman').classList.add('active');
    hideAll();
    document.getElementById('div-hangman').style.display = 'block';
}
else if (action == 7) {
    document.getElementById('sopa').classList.add('active');
    hideAll();
    document.getElementById('div-sopa').style.display = 'block';
}
else if (action == 8) {
    document.getElementById('puzzle').classList.add('active');
    hideAll();
    document.getElementById('div-puzzle').style.display = 'block';
}


function hideAll() {
    document.getElementById('div-lectura').style.display = 'none';
    document.getElementById('div-actividad').style.display = 'none';
    document.getElementById('div-video').style.display = 'none';
    document.getElementById('div-quiz').style.display = 'none';
    document.getElementById('div-resource').style.display = 'none'
    document.getElementById('div-hangman').style.display = 'none'
    document.getElementById('div-sopa').style.display = 'none'
    document.getElementById('div-puzzle').style.display = 'none'
}