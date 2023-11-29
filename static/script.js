const canvas = document.createElement('canvas');
let mediaRecorder;
const movie = document.querySelector('#movie');
let chunks = [];
let blob;
document.querySelector('#recode-start').addEventListener('click', recodeStart);
document.querySelector('#recode-stop').addEventListener('click', recodeStop);
document.querySelector('#retake').addEventListener('click', reTake);
document.querySelector('#upload').addEventListener('click', upload);

const constraints = {
    audio: false,
    video: {
        width: 1280,
        height: 720
    }
};

navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
        const video = document.querySelector('#video');
        video.srcObject = stream;
        video.play();
        let mimeType = 'video/mp4';
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = 'video/webm';  // Safariでは対応していない可能性があるので、適切な形式を選択
        }
        const recordingOptions = {
            audioBitsPerSecond: 256 * 1000,
            videoBitsPerSecond: 6000 * 1000,
            mimeType: mimeType
        };
        mediaRecorder = new MediaRecorder(stream, recordingOptions);
        mediaRecorder.ondataavailable = function (e) {
            if (e.data) {
                movie.src = URL.createObjectURL(e.data);
                chunks.push(e.data);
            }
        }
        mediaRecorder.onstop = function (e) {
            blob = new Blob(chunks, { type: mimeType });
            chunks = [];
        }
    })
    .catch(e => {
        console.error(e);
        alert('カメラの設定を許可してください。')
    });

/**
 * 動画撮影の開始
 */
function recodeStart() {
    mediaRecorder.start();
    document.querySelector('#recode-start').classList.add('hidden');
    document.querySelector('#recode-stop').classList.remove('hidden');
}

/**
 * 動画撮影の停止
 */
function recodeStop() {
    mediaRecorder.stop();
    document.querySelector('#movie-div').classList.remove('hidden');
    document.querySelector('#camera-div').classList.add('hidden');
}

function reTake() {
    document.querySelector('#camera-div').classList.remove('hidden');
    document.querySelector('#movie-div').classList.add('hidden');

    document.querySelector('#recode-start').classList.remove('hidden');
    document.querySelector('#recode-stop').classList.add('hidden');
}

function upload() {
    document.querySelector('#upload').classList.add('hidden');
    document.querySelector('#result').classList.remove('hidden');
    document.querySelector('#result').innerHTML = 'アップロード中...';
    const formData = new FormData();
    const uuid = crypto.randomUUID().replace(/-/g, '');
    formData.append('video', blob, uuid + '.webm');
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === 'OK') {
            // キャッシュバスティング用のタイムスタンプをURLに追加
            let cacheBustingURL = result.output_url + '?t=' + new Date().getTime();
            let videoElement = document.createElement('video');
            videoElement.setAttribute('controls', '');
            videoElement.setAttribute('width', '720');
            videoElement.setAttribute('src', cacheBustingURL);  // キャッシュバスティングURLを使用
            document.querySelector('#result').innerHTML = '';
            document.querySelector('#result').appendChild(videoElement);
        } else {
            document.querySelector('#result').innerHTML = 'アップロード失敗';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.querySelector('#result').innerHTML = 'アップロード失敗';
    });
}

