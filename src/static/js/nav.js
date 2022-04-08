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

// function activeLink() {
//     list.forEach((item) =>
//     item.classList.remove('active'));
//     this.classList.add('active');
//     document.title = this.id;
// }

// list.forEach((item) => 
//     item.addEventListener('click', activeLink));
