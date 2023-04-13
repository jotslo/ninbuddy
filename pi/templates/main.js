/*

convert joystick input from square to circle to prevent exceeding max input
find solution to reducing latency

implement rotate page
implement waiting for controller to connect page
implement controller connected page


*/

const env = document.querySelector("#game-controller-button");
var readyForInput = false;
var socket = io();

var inputPacket = {};

var joystickInput = {
    "L_STICK": [0, 0],
    "R_STICK": [0, 0]
}

var lastJoystickInput = {}

// input data & identifiers in order of priority
var inputs = {
    "L": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[-200, 0], [150, 0], [150, 113], [-200, 113]]},
    "ZL": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[150, 0], [312, 0], [312, 86], [150, 86]]},
    "R": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[1124, 0], [1500, 0], [1500, 113], [1124, 113]]},
    "ZR": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[958, 0], [1124, 0], [1124, 86], [958, 86]]},

    "A": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[1026, 285], [1500, -180], [1500, 750]]},
    "B": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[1026, 285], [1243, 498], [1134, 606], [921, 391]]},
    "Y": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[1026, 285], [921, 391], [759, 228], [862, 126]]},
    "X": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[1026, 285], [862, 126], [1032, -31], [1192, 124]]},

    "DPAD_UP": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[423, 430], [310, 331], [423, 236], [523, 334]]},
    "DPAD_RIGHT": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[423, 430], [523, 334], [635, 435], [535, 530]]},
    "DPAD_DOWN": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[423, 430], [532, 536], [425, 643], [318, 546]]},
    "DPAD_LEFT": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[423, 430], [310, 333], [210, 434], [312, 535]]},

    "MINUS": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[424, 60], [546, 60], [546, 121], [478, 184], [424, 184]]},
    "PLUS": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[672, 60], [796, 60], [796, 184], [733, 184], [672, 121]]},
    "SCREENSHOT": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[546, 121], [604, 121], [604, 245], [478, 245], [478, 184]]},
    "HOME": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[614, 121], [672, 121], [733, 184], [733, 245], [614, 245]]},

    "L_STICK": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0], 
        "boundaries": [[-300, -300], [492, -300], [492, 800], [-300, 800]]},
    "R_STICK": {"identifier": null, "touchpoint": [0, 0], "userinput": [0, 0],
        "boundaries": [[493, 241], [1095, 241], [1095, 800], [493, 800]]},
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

function debug(msg) {
    document.getElementById("msg").textContent = msg;
}

function updateDashboard() {
    /*fetch('/data')
        .then(response => response.json())
        .then(data => {
            const dashboardHeader = document.getElementById('msg');
            dashboardHeader.textContent = data.message;
        }
    );*/

    socket.emit("get-state");
}

function showInputs() {
    document.getElementById("msg").textContent = "";

    for (const key in inputs) {
        if (inputs[key]["identifier"] != null) {
            document.getElementById("msg").textContent += key + ", ";
        }
    }
}

function getInputFromIdentifier(identifier) {
    for (const inputKey in inputs) {
        const input = inputs[inputKey];

        if (input["identifier"] == identifier) {
            return inputKey;
        }
    }

    return null;
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
            if (inside(point, inputs[key]["boundaries"]) && inputs[key]["identifier"] == null) {
                inputs[key]["identifier"] = touch.identifier;
                inputs[key]["touchpoint"] = point;

                //inputPacket[key] = true;

                if (key.includes("STICK")) {
                    const innerStick = document.getElementById(key + "-inner");
                    const outerStick = document.getElementById(key + "-outer");

                    outerStick.style.left = (point[0] / 12.8 - 7.5) + "%";
                    outerStick.style.top = (point[1] / 6.37 - 15) + "%";

                    innerStick.style.left = (point[0] / 12.8 - 5) + "%";
                    innerStick.style.top = (point[1] / 6.37 - 10) + "%";
                }
                else {
                    socket.emit("button-down", key);
                }

                break;
            }
        }
    }

    // prevent zooming, scrolling, selecting, etc.
    event.returnValue = false;
}

function touchMove(event) {
    const activeTouches = Array.from(event.touches);
    
    for (const touchKey in activeTouches) {
        const touch = event.touches[touchKey];
        const inputKey = getInputFromIdentifier(touch.identifier);

        if (inputKey) {
            if (inputKey.includes("STICK")) {
                const input = inputs[inputKey];
                const point = [1280 * touch.clientX / window.innerWidth,
                    637 * touch.clientY / window.innerHeight];

                const innerStick = document.getElementById(inputKey + "-inner");

                innerStick.style.left = (point[0] / 12.8 - 5) + "%";
                innerStick.style.top = (point[1] / 6.37 - 10) + "%";

                input["userinput"] = [point[0] - input["touchpoint"][0],
                    point[1] - input["touchpoint"][1]];

                joystickInput[inputKey] = input["userinput"];
            }
        }
    }

    // prevent zooming, scrolling, selecting, etc.
    event.returnValue = false;
}

function touchEnd(event) {
    const endedTouches = Array.from(event.changedTouches);

    for (const touchKey in endedTouches) {
        const touch = endedTouches[touchKey];

        for (const key in inputs) {
            if (inputs[key]["identifier"] == touch.identifier) {
                inputs[key]["identifier"] = null;
                inputs[key]["touchpoint"] = [0, 0];
                inputs[key]["userinput"] = [0, 0];

                if (key.includes("STICK")) {
                    joystickInput[key] = [0, 0];

                    const innerStick = document.getElementById(key + "-inner");
                    const outerStick = document.getElementById(key + "-outer");

                    outerStick.style.left = key == "L_STICK" ? "6%" : "53.5%";
                    outerStick.style.top = key == "L_STICK" ? "20%" : "60%";

                    innerStick.style.left = key == "L_STICK" ? "8.5%" : "56%";
                    innerStick.style.top = key == "L_STICK" ? "25%" : "65%";
                }
                else {
                    socket.emit("button-up", key);
                }

                break;
            }
        }
    }

    // prevent zooming, scrolling, selecting, etc.
    event.returnValue = false;
}

env.addEventListener("touchstart", touchStart);
env.addEventListener("touchmove", touchMove);
env.addEventListener("touchend", touchEnd);
env.addEventListener("touchcancel", touchEnd);

function sendInput() {
    /*if (readyForInput) {
        var inputPacket = {};

        for (const key in inputs) {
            inputPacket[key] = {};
            inputPacket[key]["identifier"] = inputs[key]["identifier"] != null ? 1 : 0;
            if (key.includes("STICK")) {
                inputPacket[key]["userinput"] = inputs[key]["userinput"];
            }
        }

        socket.emit("input-packet", inputPacket);
    }*/

    if (readyForInput) {
        if (JSON.stringify(joystickInput) != lastJoystickInput) {
            socket.emit("joystick-input", joystickInput);
            lastJoystickInput = JSON.stringify(joystickInput);
        }
    }
}

// when get-state is received, update the dashboard
socket.on("get-state", function(state) {
    const dashboardHeader = document.getElementById('msg');
    dashboardHeader.textContent = state;
});

socket.on("ready-for-input", function(state) {
    readyForInput = state;
})

if (!/Android|iPhone/i.test(navigator.userAgent)) {
    
}

setInterval(sendInput, 1 / 60);
//setInterval(updateDashboard, 500);