var ival;
var idx = 0;

function changeImage() {
    document.getElementById('screen').src = '/static/img/screenshots/screen'+ (idx + 1) +'.jpg';
    window.clearTimeout(ival);
    ival = setTimeout(nextImage, 3000);
};

changeImage();

function nextImage() {
    idx = (idx + 1) % 20;
    changeImage();
};

function previousImage() {
    idx = (idx - 1) % 20;
    if (idx < 0) idx += 20;
    changeImage();
};
