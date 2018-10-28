// from: http://www.robots.ox.ac.uk/~vedaldi/assets/hidebib.js
function hideallbibs()
{
    var el = document.getElementsByTagName("div") ;
    for (var i = 0 ; i < el.length ; ++i) {
        if (el[i].className == "paper") {
            var bib = el[i].getElementsByTagName("pre") ;
            if (bib.length > 0) {
                bib [0] .style.display = 'none' ;
            }
        }
    }
}

function togglebib(paperId)
{
    var paper = document.getElementById(paperId) ;
    var bib = paper.getElementsByTagName('pre') ;
    var block = document.getElementById(_transId(paperId))
    if (bib.length > 0) {
        if (bib[0].style.display == 'none') {
            bib[0].style.display = 'block' ;
            block.style.display = 'none';
        } else {
            bib[0].style.display = 'none' ;
        }
    }
}

function toggleblock(blockId)
{
    var block = document.getElementById(blockId);
    var bib = document.getElementById(
        _transId(blockId)).getElementsByTagName('pre') ;
    if (block.style.display == 'none') {
        block.style.display = 'block' ;
        if (bib.length > 0) {
            bib[0].style.display = 'none' ;
        }
    } else {
        block.style.display = 'none' ;
    }
}

function hideblock(blockId)
{
    var block = document.getElementById(blockId);
    block.style.display = 'none' ;
}

function _transId(id)
{
    if (id.endsWith('_abs')) {
        return id.substr(0, id.length - 4)
    } else {
        return id + '_abs'
    }
}
