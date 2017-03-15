$(function()
{
    // Variable to store your files
    var files;

    // Add events
    $('input[type=file]').on('change', prepareUpload);
    $('form').on('submit', uploadFiles);

    // Grab the files and set them to our variable
    function prepareUpload(event)
    {
        files = event.target.files;
    }

    // Catch the form submit and upload the files
    function uploadFiles(event)
    {

        event.stopPropagation(); // Stop stuff happening
        event.preventDefault(); // Totally stop stuff happening

        // START A LOADING SPINNER HERE

        // Create a formdata object and add the files
        var data = new FormData();
        $.each(files, function(key, value)
        {
            data.append(key, value);
        });

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: data,
            cache: false,
            // dataType: 'json',
            processData: false, // Don't process the files
            contentType: false, // Set content type to false as jQuery will tell the server its a query string request
            success: function(data, textStatus, jqXHR)
            {
                if(typeof data.error === 'undefined')
                {

                    // $("body").append("<audio controls " +
                    //     "autoplay><source src="+ data.imgpath +"></audio>");

                    $('<p>' +
                        '<div style="background-color: #00A9C1; top: 50px; width: 80%; margin:auto; paddind: auto; overflow: auto" class="card initpaperwave" >'+
                        '<div class="card-content white-text">'+
                        '<span class="card-title">New PaperWave '+ data.identifierID +'</span>'+
                        '<p id="'+ data.identifierID +'" ><audio id="music'+ data.identifierID +'" class="music" autoplay="" preload="true">'+
                        '<source src='+ data.mp3path +'>'+
                        '</audio>'+
                        '<div id="wrapper" style="position:relative">'+
                        '<div id="audioplayer'+ data.identifierID +'" style="width: 90%;height: 60px;margin: auto;margin-top: 50px;background: rgba(77, 133, 222, 0.62);border-radius: 15px;">'+
                        '<button id="pButton'+ data.identifierID +'" class="play" style="height:60px;width: 60px;border: none;background-size: 50% 50%;background-repeat: no-repeat;background-position: center;float:left;"></button>'+
                        '<div id="timeline'+ data.identifierID +'" class="timeline" style="width: 80%;height: 20px;background: rgba(0,0,0,.3);margin-top: 20px;float: left;border-radius: 15px">'+
                        '<div id="playhead'+ data.identifierID +'" class="playhead" style="cursor: pointer;width: 18px;height: 18px;border-radius: 50%;margin-top: 1px;background: black;"></div></div></div></div></p>'+
                        '</div></div></p>').insertAfter($('#uploadcard'));
                    document.getElementById(data.identifierID).addEventListener("DOMContentLoaded", playControl(event, data.identifierID));
                }
                else
                {
                    console.log('ERRORS: ' + data.error);
                }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                console.log('ERRORS: ' + textStatus);
            }
        });
    }

    function submitForm(event, data)
    {
        // Create a jQuery object from the form
        $form = $(event.target);

        // Serialize the form data
        var formData = $form.serialize();

        // You should sterilise the file names
        $.each(data.files, function(key, value)
        {
            console.log('4');
            formData = formData + '&filenames[]=' + value;
            console.log('3');
        });

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            cache: false,
            dataType: 'json',
            success: function(data, textStatus, jqXHR)
            {
                console.log('1');

                // $('#results').html(data);
                // if(typeof data.error === 'undefined')
                // {
                //     // Success so call function to process the form
                //
                //     console.log('SUCCESS: ' + data.success);
                // }
                // else
                // {
                //     // Handle errors here
                //     console.log('ERRORS: ' + data.error);
                // }
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                console.log('2');
                // Handle errors here
                console.log('ERRORS: ' + textStatus);
            },
            complete: function()
            {
                // STOP LOADING SPINNER
            }
        });

    }

    function playControl(event, str) {
        var music = document.getElementById("music"+str); // id for audio element
        var duration; // Duration of audio clip
        var pButton = document.getElementById("pButton"+str); // play button
        var playhead = document.getElementById("playhead"+str); // playhead
        var timeline = document.getElementById("timeline"+str); // timeline

// timeline width adjusted for playhead
        var timelineWidth = timeline.offsetWidth - playhead.offsetWidth;

// play button event listenter
        pButton.addEventListener("click", play);

// timeupdate event listener
        music.addEventListener("timeupdate", timeUpdate, false);

// makes timeline clickable
        timeline.addEventListener("click", function (event) {
            moveplayhead(event);
            music.currentTime = duration * clickPercent(event);
        }, false);

// returns click as decimal (.77) of the total timelineWidth
        function clickPercent(event) {
            return (event.clientX - getPosition(timeline)) / timelineWidth;

        }

// makes playhead draggable
        playhead.addEventListener('mousedown', mouseDown, false);
        window.addEventListener('mouseup', mouseUp, false);

// Boolean value so that audio position is updated only when the playhead is released
        var onplayhead = false;

// mouseDown EventListener
        function mouseDown() {
            onplayhead = true;
            window.addEventListener('mousemove', moveplayhead, true);
            music.removeEventListener('timeupdate', timeUpdate, false);
        }

// mouseUp EventListener
// getting input from all mouse clicks
        function mouseUp(event) {
            if (onplayhead == true) {
                moveplayhead(event);
                window.removeEventListener('mousemove', moveplayhead, true);
                // change current time
                music.currentTime = duration * clickPercent(event);
                music.addEventListener('timeupdate', timeUpdate, false);
            }
            onplayhead = false;
        }

// mousemove EventListener
// Moves playhead as user drags
        function moveplayhead(event) {
            var newMargLeft = event.clientX - getPosition(timeline);

            if (newMargLeft >= 0 && newMargLeft <= timelineWidth) {
                playhead.style.marginLeft = newMargLeft + "px";
            }
            if (newMargLeft < 0) {
                playhead.style.marginLeft = "0px";
            }
            if (newMargLeft > timelineWidth) {
                playhead.style.marginLeft = timelineWidth + "px";
            }
        }

// timeUpdate
// Synchronizes playhead position with current point in audio
        function timeUpdate() {
            var playPercent = timelineWidth * (music.currentTime / duration);
            playhead.style.marginLeft = playPercent + "px";
            if (music.currentTime == duration) {
                pButton.className = "";
                pButton.className = "play";
            }
        }

//Play and Pause
        function play() {
            // start music
            if (music.paused) {
                music.play();
                // remove play, add pause
                pButton.className = "";
                pButton.className = "pause";
            } else { // pause music
                music.pause();
                // remove pause, add play
                pButton.className = "";
                pButton.className = "play";
            }
        }

// Gets audio file duration
        music.addEventListener("canplaythrough", function () {
            duration = music.duration;
        }, false);

// getPosition
// Returns elements left position relative to top-left of viewport
        function getPosition(el) {
            return el.getBoundingClientRect().left;
        }
    }
});


// document.addEventListener("DOMContentLoaded",