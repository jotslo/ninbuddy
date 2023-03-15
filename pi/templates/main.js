function updateDashboard() {
    fetch('/data')
        .then(response => response.json())
        .then(data => {
            const dashboardHeader = document.getElementById('msg');
            dashboardHeader.textContent = data.message;
        }
    );
}

function absorbEvent(event) {
    console.log("absorbed");
    // set 'msg' text to the pointer position
    //var msg = document.getElementById("msg");
   // msg.innerHTML = "x: " + event.touches[0].pageX + ", y: " + event.touches[0].pageY;
    event.returnValue = false;
  }
  
  let div1 = document.querySelector("#game-controller-button");
  div1.addEventListener("touchstart", absorbEvent);
  div1.addEventListener("touchend", absorbEvent);
  div1.addEventListener("touchmove", absorbEvent);
  div1.addEventListener("touchcancel", absorbEvent);

/* iOS re-orientation fix */
if (navigator.userAgent.match(/iPhone/i) || navigator.userAgent.match(/iPad/i)) {
    /* iOS hides Safari address bar */
    window.addEventListener("load",function() {
        setTimeout(function() {
            window.scrollTo(0, 1);
        }, 1000);
    });
}

//setInterval(updateDashboard, 500);