// declare env button, which covers screen to prevent scrolling
const env = document.querySelector("#game-controller-button");

// media query which determines whether orientation is portrait or landscape
var mediaQuery = window.matchMedia("(orientation: portrait)");

// assigned to true or false, depending on whether the device is mobile
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

// socket.io connection for fast communication with server
var socket = io();

// variables that store input packets in various formats
var lastJoystickInput = {}
var inputPacket = {};
var joystickInput = {
    "L_STICK": [0, 0],
    "R_STICK": [0, 0]
}

// determines whether user input can be processed
// must receive a "connected" signal from server first
var readyForInput = false;

// input data & identifiers in order of priority
// uses polygons as boundaries for each button, allowing for error tolerance
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

// determine whether touch point is within boundaries of button polygon
function inside(point, vs) {
    // algorithm derived from:
    // https://stackoverflow.com/questions/22521982/check-if-point-is-inside-a-polygon
    // https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html
    
    // shorthand for point coordinates
    var x = point[0], y = point[1];
    
    // variable to track whether point is inside polygon
    var inside = false;

    // loop through each edge of polygon
    for (var i = 0, j = vs.length - 1; i < vs.length; j = i++) {
        // get coordinates of edge
        var xi = vs[i][0], yi = vs[i][1];
        var xj = vs[j][0], yj = vs[j][1];
        
        // check if point is on edge
        var intersect = ((yi > y) != (yj > y))
            && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
        
        // if point is on edge, update variable accordingly
        if (intersect) inside = !inside;
    }
    
    // return whether point is inside polygon
    return inside;
};

// debug function that displays message in mobile browser
// only used for debugging - not part of final product
function debug(msg) {
    document.getElementById("msg").textContent = msg;
}

// function to set opacity of controls, so they can be hidden
// setting to a really low value (not 0) prevents infinite page loading
function setControlsOpacity(opacity) {
    const controls = document.getElementsByClassName("controls");

    // for each control, set opacity to specified value
    for (var i = 0; i < controls.length; i++) {
        controls[i].style.opacity = opacity;
    }
}

// find input that matches identifier of touch point
// this is used to determine which input to update when touch point moves
function getInputFromIdentifier(identifier) {
    for (const inputKey in inputs) {
        const input = inputs[inputKey];

        // if identifier matches a touch point, return that button name
        if (input["identifier"] == identifier) {
            return inputKey;
        }
    }

    // if no match found, return null
    return null;
}

// get all touch points that are not already being tracked
function getNewestTouches(event) {
    var newTouches = [];

    // for each possible touch point
    for (const touchKey in event.touches) {
        const touch = event.touches[touchKey];
        var isNewTouch = true;

        // for each button type
        for (const inputKey in inputs) {
            const input = inputs[inputKey];

            // if identifier matches a touch point, it's not new
            // so don't add it to list of new touches
            if (input["identifier"] == touch.identifier) {
                isNewTouch = false;
                break;
            }
        }

        // touch is new, so add it to list of new touches
        if (isNewTouch) {
            newTouches.push(touch);
        }
    }

    // return touches that are not already being tracked
    return newTouches;
}

// send ping to server to get latest status each second
// passes whether device is mobile so server can handle correctly
function remainConnected() {
    fetch('/ping-server?' + new URLSearchParams({"is_mobile": isMobile}))
        .then(response => response.json())
        .then(data => {
            const output = document.getElementById("centred-text");

            // if connected to console & mobile device, show controls
            if (data.message == "Connected to console!" && isMobile) {

                // if device is in portrait mode, tell user to rotate
                if (mediaQuery.matches) {
                    readyForInput = false;
                    output.textContent = "Rotate to landscape to play!";
                    setControlsOpacity(0.001); // hide controls (not 0 to prevent infinite page load)
                }

                // otherwise, show controls and allow input from user
                else {
                    readyForInput = true;
                    output.textContent = "";
                    setControlsOpacity(1);
                }
            }

            // if not connected to console, update output with current status
            else {
                readyForInput = false;
                output.textContent = data.message;
                setControlsOpacity(0.001);
            }
        }
    );
}

// send input data to server to be forwarded to switch
function sendInput() {
    if (readyForInput) {

        // only send input data if it has changed, to reduce server load
        // send via socket & update last input sent for future comparisons
        if (JSON.stringify(joystickInput) != lastJoystickInput) {
            socket.emit("joystick-input", joystickInput);
            lastJoystickInput = JSON.stringify(joystickInput);
        }
    }
}


// function to handle initial touches
function touchStart(event) {
    // prevent zooming, scrolling, selecting, etc.
    event.returnValue = false;

    // if not ready to take input, don't do anything
    if (!readyForInput) {
        return;
    }

    // get list of new touches
    const newTouches = getNewestTouches(event);

    // for each newly detected touch, get coordinates
    for (const touchKey in newTouches) {
        const touch = newTouches[touchKey];
        const point = [1280 * touch.clientX / window.innerWidth,
            637 * touch.clientY / window.innerHeight];
        
        // for each button, check if touch point is within boundaries
        for (const key in inputs) {
            if (inside(point, inputs[key]["boundaries"]) && inputs[key]["identifier"] == null) {

                // if so, assign identifier and touchpoint so touch can be tracked
                inputs[key]["identifier"] = touch.identifier;
                inputs[key]["touchpoint"] = point;

                // if joystick is touched, move stick to the initial touch point
                // this allows for better control of stick without looking at phone
                if (key.includes("STICK")) {
                    const innerStick = document.getElementById(key + "-inner");
                    const outerStick = document.getElementById(key + "-outer");

                    outerStick.style.left = (point[0] / 12.8 - 7.5) + "%";
                    outerStick.style.top = (point[1] / 6.37 - 15) + "%";

                    innerStick.style.left = (point[0] / 12.8 - 5) + "%";
                    innerStick.style.top = (point[1] / 6.37 - 10) + "%";
                }

                // if not stick, send button down event to server immediately
                // stick input updates 60 times per second separately
                else {
                    socket.emit("button-down", key);
                }

                // stop checking for other buttons
                break;
            }
        }
    }
}

// function to handle movement to existing touch points
function touchMove(event) {
    // prevent zooming, scrolling, selecting, etc.
    event.returnValue = false;

    // if not ready to take input, don't do anything
    if (!readyForInput) {
        return;
    }
    
    // get list of all active touch points
    const activeTouches = Array.from(event.touches);

    // for each active touch point, get its stored info
    for (const touchKey in activeTouches) {
        const touch = event.touches[touchKey];
        const inputKey = getInputFromIdentifier(touch.identifier);

        // if associated input is a joystick, get latest touch point
        if (inputKey) {
            if (inputKey.includes("STICK")) {
                const input = inputs[inputKey];
                const point = [1280 * touch.clientX / window.innerWidth,
                    637 * touch.clientY / window.innerHeight];


                // move inner stick to touch point for visual feedback
                const innerStick = document.getElementById(inputKey + "-inner");
                innerStick.style.left = (point[0] / 12.8 - 5) + "%";
                innerStick.style.top = (point[1] / 6.37 - 10) + "%";

                // store joystick position based on touch point & initial touch point
                // this is used to send joystick input to server
                input["userinput"] = [point[0] - input["touchpoint"][0],
                    point[1] - input["touchpoint"][1]];

                // add to joystick input object to be sent to server
                joystickInput[inputKey] = input["userinput"];
            }
        }
    }
}

function touchEnd(event) {
    // prevent zooming, scrolling, selecting, etc.
    event.returnValue = false;

    // if not ready to take input, don't do anything
    if (!readyForInput) {
        return;
    }

    // get list of ended touches
    const endedTouches = Array.from(event.changedTouches);

    // for each ended touch, get its stored info
    for (const touchKey in endedTouches) {
        const touch = endedTouches[touchKey];

        // if associated input is found, reset its info so it's considered released
        for (const key in inputs) {
            if (inputs[key]["identifier"] == touch.identifier) {
                inputs[key]["identifier"] = null;
                inputs[key]["touchpoint"] = [0, 0];
                inputs[key]["userinput"] = [0, 0];

                // if joystick, move stick back to center
                if (key.includes("STICK")) {
                    joystickInput[key] = [0, 0];

                    const innerStick = document.getElementById(key + "-inner");
                    const outerStick = document.getElementById(key + "-outer");

                    outerStick.style.left = key == "L_STICK" ? "6%" : "53.5%";
                    outerStick.style.top = key == "L_STICK" ? "20%" : "60%";

                    innerStick.style.left = key == "L_STICK" ? "8.5%" : "56%";
                    innerStick.style.top = key == "L_STICK" ? "25%" : "65%";
                }

                // otherwise, send button up event to server for immediate release
                else {
                    socket.emit("button-up", key);
                }

                // stop checking for other buttons
                break;
            }
        }
    }
}

// when page is fully loaded, call functions at each interval
// sendInput - 60/sec - send input data to server to be forwarded to switch
// remainConnected - 1/sec - ping server to get latest state & remain connected
window.addEventListener('load', function() {
    setInterval(sendInput, 1 / 60);
    setInterval(remainConnected, 1000);
});

// when screen is touched in certain ways, call appropriate functions
env.addEventListener("touchstart", touchStart);
env.addEventListener("touchmove", touchMove);
env.addEventListener("touchend", touchEnd);
env.addEventListener("touchcancel", touchEnd);