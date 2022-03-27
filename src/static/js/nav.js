$(document).ready(function(){
    console.log("JQuery Log")
});

const list = document.querySelectorAll('.list');
const windows = document.querySelectorAll('.container-window');

function setWindow(window) {
    windows.forEach((item) => item.style.display = 'none');
    if (window == 'Inicio') {
        document.getElementById('01').style.display = 'block';
    }
    if (window == 'Capacitaciones') {
        document.getElementById('02').style.display = 'block';
    }
    if (window == 'Progreso') {
        document.getElementById('03').style.display = 'block';
    }
    if (window == 'Perfil') {
        document.getElementById('04').style.display = 'block';
    }
}

function activeLink() {
    list.forEach((item) =>
    item.classList.remove('active'));
    this.classList.add('active');
    setWindow(this.id);
    document.title = this.id;
}

list.forEach((item) => 
    item.addEventListener('click', activeLink));

