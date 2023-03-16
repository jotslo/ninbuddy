var c = 0;

function ray_casting(point, polygon){
    var n=polygon.length,
        is_in=false,
        x=point[0],
        y=point[1],
        x1,x2,y1,y2;

    for(var i=0; i < n-1; ++i){
        x1=polygon[i][0];
        x2=polygon[i+1][0];
        y1=polygon[i][1];
        y2=polygon[i+1][1];

        if(y < y1 != y < y2 && x < (x2-x1) * (y-y1) / (y2-y1) + x1){
            is_in=!is_in;
        }
    }

    return is_in;
}

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
    //document.getElementById('msg').textContent = event.touches[0].clientX + ", " + event.touches[0].clientY;
    event.returnValue = false;
}

function touchStart(event) {
    const touch = event.touches[0];
    const point = [touch.clientX / window.innerWidth, touch.clientY / window.innerHeight];

    document.getElementById('msg').textContent = point[0] + ", " + point[1];

    // prevent zooming, scrolling, selecting, etc.
    event.returnValue = false;
}
  
let div1 = document.querySelector("#game-controller-button");
div1.addEventListener("touchstart", touchStart);
div1.addEventListener("touchend", absorbEvent);
div1.addEventListener("touchmove", touchStart);
div1.addEventListener("touchcancel", absorbEvent);

/*var metaViewport = document.querySelector('meta[name="viewport"]');
metaViewport.setAttribute('content', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0, orientation=landscape');*/

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