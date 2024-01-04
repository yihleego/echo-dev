const {ipcRenderer} = require('electron')
window.addEventListener('DOMContentLoaded', () => {
    /*const ffi = require('ffi-napi')
    const ref = require('ref-napi');
    const helloLib = ffi.Library('./libhello.dll', {
        'getHelloWorldString': ['string', []]
    });
    const buff = helloLib.getHelloWorldString();
    const res = Buffer.from(buff).toString('utf-8');
    console.log(res);*/

    const btnStart = document.getElementById("btnStart");
    const btnStop = document.getElementById("btnStop");
    btnStart.addEventListener("click", () => {
        console.log("start")
        ipcRenderer.invoke('start')
            .then(res => {
                console.log(res)
            })
    });
    btnStop.addEventListener("click", () => {
        console.log("stop")
        ipcRenderer.invoke('stop')
            .then(res => {
                console.log(res)
            })
    });
})