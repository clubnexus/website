// important: never use 'ad' here, since it gets blocked by adblock
k = 'top2d';
var __list = [k + '1', k + '2'];

function generatetop2d()
{
    var img = __list[Math.floor(Math.random() * __list.length)];
    document.getElementById('top2d').src = '/static/img/' + img + '.png';
};

generatetop2d();
