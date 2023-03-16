const boundaries = {
    "L": [[-200, 0], [150, 0], [150, 113], [-200, 113]],
    "ZL": [[150, 0], [312, 0], [312, 86], [150, 86]]
}

function inside(point, vs) {
    // ray-casting algorithm based on
    // https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html
    
    var x = point[0], y = point[1];
    
    var inside = false;
    for (var i = 0, j = vs.length - 1; i < vs.length; j = i++) {
        var xi = vs[i][0], yi = vs[i][1];
        var xj = vs[j][0], yj = vs[j][1];
        
        var intersect = ((yi > y) != (yj > y))
            && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        if (intersect) inside = !inside;
    }
    
    return inside;
};

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
    const point = [1280 * touch.clientX / window.innerWidth, 637 * touch.clientY / window.innerHeight];

    if (inside(point, boundaries["L"])) {
        document.getElementById('msg').textContent = "L";
    } else if (inside(point, boundaries["ZL"])) {
        document.getElementById('msg').textContent = "ZL";
    } else {
        document.getElementById('msg').textContent = "NONE";
    }

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