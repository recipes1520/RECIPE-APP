function createXmlHttp() {
  var xmlhttp;
  if (window.XMLHttpRequest) {
    xmlhttp = new XMLHttpRequest();
  } else {
    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
  }
  if (!(xmlhttp)) {
    alert("your horrible browser does not support AJAX, get with it man");
  }
  return xmlhttp;
}

// Since we'll be posting parameters to a URL over and over again, we can use this 
// function to simplify the calls.  Also, since these calls are dependent on the
// XML HTTP object's methods, it's not a bad idea to abstract this into a separate
// function so that we can adapt easily if some of the object changes.
function postParameters(xmlHttp, target, parameters) {
  if (xmlHttp) {
    xmlHttp.open("POST", target, true);
    xmlHttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xmlHttp.send(parameters);
  }
}

// We'll call this function to test JSON behavior.  We can have our server create JSON
// objects and pass them back to the client.
function postComment( ) {
  var xmlHttp = createXmlHttp();

  // onreadystatechange will be called every time the state of the XML HTTP object changes
  xmlHttp.onreadystatechange = function() {
  
    // we really only care about 4 (response complete) here.
    if (xmlHttp.readyState == 4) {
      // we parse the content of the response
      var commentObject = JSON.parse(xmlHttp.responseText);
      var commentSection = document.getElementById('commentSection');
      var commentTable = document.createElement('table');
      commentSection.innerHTML += " \
      <table> \
      <tr><td>"+commentObject.author+"</td></tr> \
      <tr><td>"+ new Date().toUTCString()+"</td></tr> \
      <tr><td id=\"rate\">"+commentObject.rating+" out of 5</td></tr> \
      <tr><td><p id=\"comment\">" +commentObject.commentText+"</p></td></tr> \
      </table>";
      
    }
  }


  var rating;
  var radioButtons = document.getElementById('commentForm').rating
  for (i = 0; i < radioButtons.length; i++) {
    if ( radioButtons[i].checked ) {
        rating = radioButtons[i].value;
        break;
    }
  }

  parameters = 'recipeTitle='+ document.getElementById('recipeTitle').value + 
               '&rating='+ rating +
               '&comments='+ document.getElementById('comments').value
               
  postParameters(xmlHttp, '/recipes/submit_comment', parameters);
}