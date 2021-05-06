function sv() {
      let Field = document.getElementsByName("startdate");
      Field[0].value = 'change';
      let arr = document.getElementsByName("MainForm");
      arr[0].submit()
      }
function ev() {
  let Field = document.getElementsByName("enddate");
  Field[0].value = 'change';
  let arr = document.getElementsByName("MainForm");
  arr[0].submit()
  }
function dv() {
  let Field = document.getElementsByName("DelVote");
  Field[0].value = 'change';
  let arr = document.getElementsByName("MainForm");
  arr[0].submit()

  }
function cn() {
  let Field = document.getElementsByName("name");
  Field[0].value = 'change';
  let arr = document.getElementsByName("MainForm");
  arr[0].submit()

  }

function crt() {
  let create = document.getElementsByName("Create");
  create[0].value = 1
}
