function cn() {
  let Field = document.getElementsByName("ChangeName");
  Field[0].value = 'change';
  let create = document.getElementsByName("Create");
  create[0].value = 0;
  let arr = document.getElementsByName("MainForm");
  arr[0].submit()
}
function ce() {
  let Field = document.getElementsByName("ChangeEmail");
  Field[0].value = 'change';
  let create = document.getElementsByName("Create");
  create[0].value = 0;
  let arr = document.getElementsByName("MainForm");
  arr[0].submit()
}
function cp() {
  let Field = document.getElementsByName("ChangePassword");
  Field[0].value = 'change';
  let create = document.getElementsByName("Create");
  create[0].value = 0;
  let arr = document.getElementsByName("MainForm");
  arr[0].submit()
}
function crt() {
  let create = document.getElementsByName("Create");
  create[0].value = 1
}
