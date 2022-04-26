var url_string = window.location.href
var url = new URL(url_string);
var selection = url.searchParams.get("cursos");
console.log(selection);

if (selection == 'No Tomado') {
    document.getElementById('no_tomadas').classList.add('active');
}else if (selection == 'Cursando') {
    document.getElementById('en_curso').classList.add('active');
}else if (selection == 'Completado') {
    document.getElementById('completadas').classList.add('active');
}else {
    document.getElementById('todas').classList.add('active');
}


function remAll() {
    document.getElementById('todas').classList.remove('active');
    document.getElementById('no_tomadas').classList.remove('active');
    document.getElementById('en_curso').classList.remove('active');
    document.getElementById('completadas').classList.remove('active');
}