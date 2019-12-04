var states = [
"Bank of America",
"Accenture",
"Barclays",
"Amazon"
];

$(function() {
  $("input").autocomplete({
    source:[states]
  }); 
});