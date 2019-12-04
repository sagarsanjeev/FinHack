var states = [
"banks",
"bilateral trading",
"Board",
"APA",
"ESMA",
"Commission"
];

$(function() {
  $("input").autocomplete({
    source:[states]
  }); 
});