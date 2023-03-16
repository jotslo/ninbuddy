/*
Left Joystick
-300, -300
492, -300
492, 800
-300, 800

Right Joystick
493, 241
1095, 241
1095, 800
493, 800
*/

const env = document.querySelector("#game-controller-button");

var inputs = {
    "L": {"identifier": null,
        "boundaries": [[-200, 0], [150, 0], [150, 113], [-200, 113]]},
    "ZL": {"identifier": null,
        "boundaries": [[150, 0], [312, 0], [312, 86], [150, 86]]},
    "R": {"identifier": null,
        "boundaries": [[1124, 0], [1500, 0], [1500, 113], [1124, 113]]},
    "ZR": {"identifier": null,
        "boundaries": [[958, 0], [1124, 0], [1124, 86], [958, 86]]},
    "A": {"identifier": null,
        "boundaries": [[1026, 285], [1500, -180], [1500, 750]]},
    "B": {"identifier": null,
        "boundaries": [[1026, 285], [1243, 498], [1134, 606], [921, 391]]},
    "Y": {"identifier": null,
        "boundaries": [[1026, 285], [921, 391], [759, 228], [862, 126]]},
    "X": {"identifier": null,
        "boundaries": [[1026, 285], [862, 126], [1032, -31], [1192, 124]]},
    "Up": {"identifier": null,
        "boundaries": [[423, 430], [310, 331], [423, 236], [523, 334]]},
    "Right": {"identifier": null,
        "boundaries": [[423, 430], [523, 334], [635, 435], [535, 530]]},
    "Down": {"identifier": null,
        "boundaries": [[423, 430], [532, 536], [425, 643], [318, 546]]},
    "Left": {"identifier": null,
        "boundaries": [[423, 430], [310, 333], [210, 434], [312, 535]]},
    "Minus": {"identifier": null,
        "boundaries": [[424, 60], [546, 60], [546, 121], [478, 184], [424, 184]]},
    "Plus": {"identifier": null,
        "boundaries": [[672, 60], [796, 60], [796, 184], [733, 184], [672, 121]]},
    "Screenshot": {"identifier": null,
        "boundaries": [[546, 121], [604, 121], [604, 245], [478, 245], [478, 184]]},
    "Home": {"identifier": null,
        "boundaries": [[614, 121], [672, 121], [733, 184], [733, 245], [614, 245]]}
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

function showInputs() {
    document.getElementById("msg").textContent = "";

    for (const key in inputs) {
        if (inputs[key]["identifier"] != null) {
            document.getElementById("msg").textContent += key + ", ";
        }
    }
}

function getNewestTouches(event) {
    var newTouches = [];

    for (const touchKey in event.touches) {
        const touch = event.touches[touchKey];
        var isNewTouch = true;

        for (const inputKey in inputs) {
            const input = inputs[inputKey];

            if (input["identifier"] == touch.identifier) {
                isNewTouch = false;
                break;
            }
        }

        if (isNewTouch) {
            newTouches.push(touch);
        }
    }

    return newTouches;
}

function touchStart(event) {
    const newTouches = getNewestTouches(event);

    for (const touchKey in newTouches) {
        const touch = newTouches[touchKey];
        const point = [1280 * touch.clientX / window.innerWidth,
            637 * touch.clientY / window.innerHeight];
        
        for (const key in inputs) {
            if (inside(point, inputs[key]["boundaries"])) {
                inputs[key]["identifier"] = touch.identifier;
                break;
            }
        }
    }

    // debugging purposes
    showInputs();

    // prevent zooming, scrolling, selecting, etc.
    event.returnValue = false;
}

function touchEnd(event) {
    for (const touchKey in event.changedTouches) {
        const touch = event.changedTouches[touchKey];

        for (const key in inputs) {
            if (inputs[key]["identifier"] == touch.identifier) {
                inputs[key]["identifier"] = null;
                break;
            }
        }
    }

    showInputs();

    // prevent zooming, scrolling, selecting, etc.
    event.returnValue = false;
}

env.addEventListener("touchstart", touchStart);
env.addEventListener("touchmove", touchStart);
env.addEventListener("touchend", touchEnd);
env.addEventListener("touchcancel", touchEnd);

//setInterval(updateDashboard, 500);