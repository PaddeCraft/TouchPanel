(function (global) {
    /*
    Simple functions to scale content to fit it's parent
    
    Author: Liudmil Mitev
    License: WTFPL
    Demo: https://jsfiddle.net/oxzxyxqn/7/
    
  */
    function scaleAmountNeededToFit(el, margin = 0) {
        const parentSize = {
            width: el.parentElement.clientWidth - margin * 2,
            height: el.parentElement.clientHeight - margin * 2,
        };

        return Math.min(
            parentSize.width / el.clientWidth,
            parentSize.height / el.clientHeight
        );
    }

    function fitToParent(element, margin) {
        const scale = scaleAmountNeededToFit(element, margin);
        element.style.transformOrigin = "0 0";
        element.style.transform = `translate(${margin}px, ${margin}px) scale(${scale})`;
    }

    global.fitToParent = fitToParent;
})(this);

const pageSizeLookup = {
    1: { r: 3, c: 5 },
    2: { r: 5, c: 7 },
    3: { r: 6, c: 9 },
    4: { r: 10, c: 15 },
};
var pages = [];
var currentPage = "";

function chunk(items, size) {
    // https://futurestud.io/tutorials/split-an-array-into-smaller-array-chunks-in-javascript-and-node-js
    const chunks = [];
    items = [].concat(...items);

    while (items.length) {
        chunks.push(items.splice(0, size));
    }

    return chunks;
}

const socket = io();
socket.on("connect", function () {
    console.log("Connected!");
    socket.emit("loadLandingPage");
});

socket.on("disconnect", function () {
    console.log("Disconnected!");
    document.getElementById("pageselect").innerHTML = "";
    document.getElementById("page").innerText = "Disconnected";
    document.getElementById("main").innerHTML = "<table />";
});

socket.on("loadpage", loadPage);

socket.on("actionError", function (data) {
    alert(
        "An error occured in your action " +
            data.fname +
            ":\n\nException:\n" +
            data.msg
    );
});

function runAction(id, createNew = false) {
    if (!window.editMode) {
        if (!createNew) {
            socket.emit("run", id);
        }
    } else {
        if (createNew) {
            window.open(
                "/edit/btn?mode=new&page=" + currentPage + "&idx=" + id
            );
        } else {
            window.open(
                "/edit/btn?mode=edit&id=" + id + "&page=" + currentPage
            );
        }
    }
}

function requestPage(cuid) {
    socket.emit("loadPage", cuid);
}

function loadPage(page) {
    currentPage = page.cuid;
    document.getElementById("main").style.display = "block";
    document.getElementById("pageselect").style.display = "none";
    document.getElementById("page").innerText = page.name;
    var size = pageSizeLookup["" + page.type];
    size = size.r * size.c;
    var btns = Array.apply(null, Array(size));
    page.buttons.forEach(function (btn) {
        btns[
            btn.index
        ] = `<div class="btn pointer" id="${btn.cuid}" onclick="runAction('${btn.cuid}')"><img src="/icon/${btn.icon}" /><br /><span>${btn.name}</span></div>`;
    });
    btns = btns.map((v, idx) =>
        v === undefined
            ? `<div class="btn" onclick="runAction(${idx}, true)">` +
              (window.editMode
                  ? `<div class="addbtn">Add</div> </div`
                  : "</div>")
            : v
    );
    btns = chunk(btns, pageSizeLookup["" + page.type].c);
    table = document.querySelector("table");
    table.innerHTML = "";
    btns.forEach(function (row) {
        tr = document.createElement("tr");
        row.forEach(function (btn) {
            td = document.createElement("td");
            td.innerHTML = btn;
            tr.appendChild(td);
        });
        table.appendChild(tr);
    });
    document.getElementById("pageselect").innerHTML = "";
    page.pages.forEach(function (pge) {
        document.getElementById(
            "pageselect"
        ).innerHTML += `<p onclick=requestPage("${pge.cuid}") class="pointer">${pge.name}</p>`;
    });
    document.getElementById(
        "pageselect"
    ).innerHTML += `<p onclick="window.open('/edit/page?mode=new')" class="pointer">New page</p>`;
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("pagesel").addEventListener("click", function () {
        document.getElementById("main").style.display = "none";
        document.getElementById("pageselect").style.display = "block";
    });
});
