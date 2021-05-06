function crt(key) {
    let create = document.getElementsByName("create");
    create[Number(key)-1].value = 1;
}
function inc(key) {
    let count = document.getElementsByName("count"+key);
    count[0].value = Number(count[0].value)+1;
    let create = document.getElementsByName("create");
    create[Number(key)].value = 0;
    let arr = document.getElementsByName("form_maker"+key);
    arr[0].submit()
}
function dec(key) {
    let count = document.getElementsByName("count"+key);
    count[0].value = Number(count[0].value)-1;
    let create = document.getElementsByName("create");
    create[Number(key)].value = 0;
    let arr = document.getElementsByName("form_maker"+key);
    arr[0].submit()
}
