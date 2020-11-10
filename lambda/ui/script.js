SCOPE = "awscd"
FUNC = "synthesize"

function submitform() {
    const fmt = document.getElementById('fmt_mp3').checked ? 'mp3' : 'wav'
    const player = document.getElementById('player')
    const payload = {
        "scope": SCOPE,
        "text": document.getElementById('ta').value,
        "translate": document.getElementById('translate').checked,
        "format": fmt
    };
    const xhr = new XMLHttpRequest();
    xhr.onload = function () {
        if (xhr.readyState === 4) {
            if (xhr.status === 200) {
                const c = JSON.parse(xhr.response).b64
                player.src = fmt === "mp3" ? "data:audio/mpeg;base64," + c : "data:audio/wav;base64," + c;
                player.autoplay = true;
            } else {
                console.error(xhr.statusText);
            }
        }
    };
    xhr.open('POST', '/Prod/' + FUNC, true);
    xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
    xhr.send(JSON.stringify(payload));
}
