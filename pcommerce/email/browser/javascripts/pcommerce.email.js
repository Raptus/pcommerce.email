jq('document').ready(function() {
  var delivery = document.getElementById('as_delivery');
  if(delivery) {
    if(delivery.checked) {
      jq('#checkout #billing fieldset .address').hide();
    }
    jq(delivery.parentNode).click(function() {
      if(delivery.checked)
        jq('#checkout #billing fieldset .address').hide();
      else
        jq('#checkout #billing fieldset .address').show();
    });
  }
});