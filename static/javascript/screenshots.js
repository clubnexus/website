var ival;
var idx = 0;

function changeImage() {
    document.getElementById('screen').src = '/static/img/screenshots/screen'+ (idx + 1) +'.jpg';
    window.clearTimeout(ival);
    ival = setTimeout(nextImage, 3000);
};

changeImage();

function nextImage() {
    idx = (idx + 1) % 22;
    changeImage();
};

function previousImage() {
    idx = (idx - 1) % 22;
    if (idx < 0) idx += 22;
    changeImage();
};
