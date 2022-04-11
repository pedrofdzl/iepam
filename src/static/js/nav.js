$(document).ready(function(){
    console.log("JQuery Log")
});

const list = document.querySelectorAll('.list');
const windows = document.querySelectorAll('.container-window');

if(document.getElementById('id-app').textContent == 'cap'){
    list.forEach((item) =>
    item.classList.remove('active'));
    document.getElementById('Capacitaciones').classList.add('active');
}

if(document.getElementById('id-app').textContent == 'profile'){
    list.forEach((item) =>
    item.classList.remove('active'));
    document.getElementById('Perfil').classList.add('active');
}

if(document.getElementById('id-app').textContent == 'admin'){
    list.forEach((item) =>
    item.classList.remove('active'));
    document.getElementById('Admin').classList.add('active');
}

// function activeLink() {
//     list.forEach((item) =>
//     item.classList.remove('active'));
//     this.classList.add('active');
//     document.title = this.id;
// }

// list.forEach((item) => 
//     item.addEventListener('click', activeLink));
