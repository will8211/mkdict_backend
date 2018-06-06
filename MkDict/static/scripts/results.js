/*
 *   JS for Results page and Examples page
 */

// PHP-style GET function

function getVariable(variable) {
    var query = window.location.search.substring(1);
    var vars = query.split("&");
    for (var i=0;i<vars.length;i++) {
        var pair = vars[i].split("=");
        if(pair[0] == variable){
            return pair[1];
        }
    }
   return(false);
}

// Get and play audio files

function preloadImage(url) {
    var img1=new Image();
    img1.src='static/images/sound_blank.svg';
    var img2=new Image();
    img2.src='static/images/sound_playing.svg';
}

var playable = {};

function playAudio(url, imageId, contId) {
    playable[imageId] = false;
    var audio = new Audio(url);
    audio.addEventListener("canplay", function() {
        playable[imageId] = true;
        document.getElementById(imageId).src='static/images/sound_playing.svg';
        spinner.stop();
    }); 
    audio.addEventListener("ended", function() {
        document.getElementById(imageId).src='static/images/sound.svg';
    });
    audio.play();
    setTimeout(function(){
        if (playable[imageId] === false) {
            if (typeof(spinner) != "undefined") {
                spinner.stop();
            }
            //unblank all images
            blankedList = document.getElementsByClassName("blanked");
            for (i=0; i<blankedList.length; i++) {
                    blankedList[i].src='static/images/sound.svg';
                    blankedList[i].classList.remove("blanked");
            }
            //blank target image
            image = document.getElementById(imageId);
            image.src='static/images/sound_blank.svg';
            image.className = "blanked"
            //spin.js object
            var opts = {
                lines: 10, // The number of lines to draw
                length: 7, // The length of each line
                width: 4, // The line thickness
                radius: 5, // The radius of the inner circle
                color: '#4D4D4D', // #rbg or #rrggbb
                speed: 1, // Rounds per second
                trail: 100, // Afterglow percentage
                shadow: false, // Whether to render a shadow
                top: '20%' //top position relative to parent
            };
            var target = document.getElementById(contId);
            spinner = new Spinner(opts).spin(target);
        }
    }, 50);
};

// Google analytics

(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
})(window,document,'script','https://www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-77146708-1', 'auto');
ga('send', 'pageview');

/*
 *  Only for results page ( not examples page)
 */

if (location.pathname === '/results') {

    // Alter tabs' overlap for MOE dict

    if (getVariable('t_dict') === 'moe') {
        window.addEventListener('load', function () {
            var overlapLeft = document.getElementById('overlap_left');
            var overlapRight = document.getElementById('overlap_right');
            overlapLeft.style.setProperty('border-bottom', '14px solid #E37B15');
            overlapRight.style.setProperty('border-bottom', '14px solid #E37B15');
        });
    }

    // Hide and reveal "more information" rows

    $(document).ready(function() {
        var moreImg = "static/images/more.svg";
        var lessImg = "static/images/less.svg";
        var firstEnglish = document.getElementsByClassName('english')[0];
        if (firstEnglish.innerHTML === "") {
            $('.moreless').hide();
        }
        $('.hidden').hide();
        $('.hideshow').click(function() {
            var slave = '#slave' + $(this).attr('Id');
            var thisMoreless = '#moreless' + $(this).attr('Id');
            if ($(slave).is(':hidden')) {
                $('.hidden').hide();
                $('.moreless').attr('src', moreImg);
                $(thisMoreless).attr('src', lessImg);
            } else {
                $(thisMoreless).attr('src', moreImg);
            }
            if (firstEnglish != "") {
                $(slave).toggle(0, 'show');
            }
        }).find('.tai_word').click(function(e) { //exclude headword from click
            return false;
        });
    });

    // Show only appropriate romanization

    function showRoman(roman) {
        $('.POJ').hide();
        $('.TRS').hide();
        $('.DT').hide();
        switch(roman) {
            case 't':
                $('.TRS').css('display', 'inline');
                break;
            case 'd':
                $('.DT').css('display', 'inline');
                break;
            default:
                $('.POJ').css('display', 'inline');
        }
    }
    $(document).ready(function() {
        showRoman(getVariable('roman'));
        $('#roman').change(function() {
            showRoman($('#roman').val());
        });
    });
    
    // Link to other dictionary
    
    if (getVariable('t_dict') === 'moe') {
        window.addEventListener('load', function () {
            var moeTab = document.getElementById('moe_tab');
            var maryknollTab = document.getElementById('maryknoll_tab');
            moeTab.style.setProperty('cursor', 'initial');
            maryknollTab.style.setProperty('cursor', 'pointer');
        });
    }
    
    function switchDict(target, source) {
        var query = document.getElementById('query');
        if ((source === 'radio') && (query.value !== '')) {
            return false;
        }
        if (target === getVariable('t_dict')) {
            return false;
        }
        var url = "results?query=" + getVariable('query') + "&page=1&t_dict=" 
                + target + "&q_type=" + getVariable('q_type') 
                + "&roman=" + getVariable('roman');
        window.location = url
    }

}
