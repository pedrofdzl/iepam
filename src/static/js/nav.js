$(document).ready(function(){
    console.log("JQuery Log")
});

const list = document.querySelectorAll('.list');
const windows = document.querySelectorAll('.container-window');

if(document.getElementById('id-app').textContent == 'main'){
    var url_string = window.location.href;
    var url = new URL(url_string);
    var activeWindow = url.searchParams.get("select");
    var lastSelect = 'Inicio';

    if(activeWindow == 1){
        lastSelect = 'Inicio';
        setWindow('Inicio');
    }
    if(activeWindow == 2){
        lastSelect = 'Capacitaciones';
        setWindow('Capacitaciones');
    }
    if(activeWindow == 3){
        lastSelect = 'Progreso';
        setWindow('Progreso');
    }
    if(activeWindow == 4){
        lastSelect = 'Perfil';
        setWindow('Perfil');
    }

    list.forEach((item) =>
    item.classList.remove('active'));
    document.getElementById(lastSelect).classList.add('active');
}else{
    document.getElementById('navbar-item-01').style.transition = 'none';
    document.getElementById('navbar-item-02').style.transition = 'none';

    list.forEach((item) =>
    item.classList.remove('active'));
    document.getElementById(document.getElementById('id-app').textContent).classList.add('active');

    document.getElementById('InicioA').setAttribute('href', '/?select=1');
    document.getElementById('CapacitacionesA').setAttribute('href', '/?select=2');
    document.getElementById('ProgresoA').setAttribute('href', '/?select=3');
    document.getElementById('PerfilA').setAttribute('href', '/?select=4');
}

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

function setActiveLink(hey) {
    list.forEach((item) =>
    item.classList.remove('active'));
    hey.classList.add('active');
    setWindow(hey.id);
    document.title = hey.id;
}

