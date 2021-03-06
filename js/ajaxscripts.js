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
      if( commentObject.userStatus == "false"){
          alert("Must be logged in to comment");
          return;
      } else{
        var commentSection = document.getElementById('commentSection');
        document.getElementById('averageRating').innerText = "Average Rating: " + commentObject.avgRating;
        commentSection.innerHTML += " \
        <table> \
        <tr><td>"+commentObject.author+"</td></tr> \
        <tr><td>"+ new Date().toUTCString()+"</td></tr> \
        <tr><td id=\"rate\">"+commentObject.rating+" out of 5</td></tr> \
        <tr><td><p id=\"comment\">" +commentObject.commentText+"</p></td></tr> \
        </table>";

        document.getElementById('comments').value = "";
        }
      }
      
    }
  


  var rating = -1;
  var radioButtons = document.getElementById('commentForm').rating
  for (i = 0; i < radioButtons.length; i++) {
    if ( radioButtons[i].checked ) {
        rating = radioButtons[i].value;
        break;
    }
  }
  if( rating == -1 || document.getElementById('comments').value == ''){
    alert( "Rating must be selected and a comment must be written.");
    return;
  }

  parameters = 'recipeTitle='+ document.getElementById('recipeTitle').value + 
               '&rating='+ rating +
               '&comments='+ document.getElementById('comments').value;
               
  postParameters(xmlHttp, '/recipes/submit_comment', parameters);
}

function getProfile( ) {
  var xmlHttp = createXmlHttp();

  // onreadystatechange will be called every time the state of the XML HTTP object changes
  xmlHttp.onreadystatechange = function() {
  
    // we really only care about 4 (response complete) here.
    if (xmlHttp.readyState == 4) {
      // we parse the content of the response
      var profileObject = JSON.parse(xmlHttp.responseText);
      var profileSection = document.getElementById('profileSection');
      profileSection.innerHTML = " \
      <table> \
      <tr><td> Email: "+profileObject.email+"</td></tr> \
      </table>";  
    }
  }
  
  parameters = '';
  postParameters(xmlHttp, '/profile', parameters);
}


function addShoppingListItem()
   {
     var item = document.getElementById('shoppingListItem');
     var inputText = item.value.replace(/^\s+/, '').replace(/\s+$/, '');
     if( inputText != ''){
        sendItemUsingAJAX(item.value);
     }   
     // clear input field
     item.value = '';
   }
   
   function sendItemUsingAJAX(item)
   {
     var xmlhttp = new XMLHttpRequest(); 
     if (xmlhttp) {
       xmlhttp.onreadystatechange=function()
       {
         if (xmlhttp.readyState==4 && xmlhttp.status==200)
         {
           var response = xmlhttp.responseText;
           var json = JSON.parse(response);
           
           var shoppingListItems = document.getElementById('shoppingListItems');
           shoppingListItems.innerHTML += '<a href="" id="item_'+json.item_id+'" onclick="buyShoppingListItem('+json.item_id+')">' + json.item + '</a><br>';
         }
       }
       xmlhttp.open("post", "/shoplist", true);
       xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
       xmlhttp.send("action=add&shopitem=" + encodeURIComponent(item));
     }
    }
    
    function buyShoppingListItem(item_id) {
      var xmlhttp = new XMLHttpRequest(); 
     if (xmlhttp) {
       xmlhttp.onreadystatechange=function()
       {
         if (xmlhttp.readyState==4 && xmlhttp.status==200)
         {
           var response = xmlhttp.responseText;
           var json = JSON.parse(response);
           
           var shoppingListItem = document.getElementById('item_' + json.item_id);
           shoppingListItem.style.textDecoration = 'line-through';
         }
       }
       xmlhttp.open("post", "/shoplist", true);
       xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
       xmlhttp.send("action=buy&item_id=" + encodeURIComponent(item_id));
     }
      
      return false;
    }
   
    function loadShoppingList(){
     var xmlhttp = new XMLHttpRequest(); 
     if (xmlhttp) {
       
       xmlhttp.onreadystatechange=function() {
         if (xmlhttp.readyState==4 && xmlhttp.status==200){
           
           var shoppingListObject = JSON.parse(xmlhttp.responseText);
           var shoppingListSection = document.getElementById('shoppingListItems');
           var shoppingListHTML = "";
           var item_list = shoppingListObject.shoppingList;
           for( i in item_list ){
             if (item_list[i].bought == false) {
               shoppingListHTML += ('<a href="#" id="item_'+i+'" onclick="buyShoppingListItem('+i+')">' + item_list[i].name + '</a><br>');
             } else {
               shoppingListHTML += ('<span style="text-decoration: line-through">' + item_list[i].name + '</span><br>');
             }
           }
           shoppingListSection.innerHTML = shoppingListHTML;
         }
       }
       xmlhttp.open("get", "/shoplist", true);
       xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
       xmlhttp.send("action=load");
     }
    }
     
    function clearShoppingList()
    {
     var xmlhttp = new XMLHttpRequest(); 
     if (xmlhttp) {
       xmlhttp.onreadystatechange=function()
       {
         if (xmlhttp.readyState==4 && xmlhttp.status==200)
         {
           var shoppingListItems = document.getElementById('shoppingListItems');
           shoppingListItems.innerHTML = '';
         }
       }
       xmlhttp.open("post", "/shoplist", true);
       xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
       xmlhttp.send("action=clear");
     }
    }

function loadRecipeList(){
     var xmlhttp = new XMLHttpRequest();
     if (xmlhttp) {

       xmlhttp.onreadystatechange=function() {
         if (xmlhttp.readyState==4 && xmlhttp.status==200){

           var recipeListObject = JSON.parse(xmlhttp.responseText);
           var recipeListSection = document.getElementById('myRecipes');
           var recipeListHTML = "";
           var temp;
           var item_list = recipeListObject.titles;
           for( i in item_list ){
             temp = item_list[i].replace(" ", "_");
             recipeListHTML += '<a name="link" href="/recipes/' + temp + '">' + item_list[i] + '</a><br>';
           }
           myRecipes.innerHTML = recipeListHTML;
         }
       }
       xmlhttp.open("get", "/recipelist", true);
       xmlhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
       xmlhttp.send("action=load");
     }
    }