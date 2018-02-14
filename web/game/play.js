var total_time = 30;

var person;
var previous_person;
var answer = 0; // 1-4 depending on location
var answer_index; // person index of the data array

// corner backdrop assets
var top_left;
var top_right;
var bot_left;
var bot_right;

var top_left_text;
var top_right_text;
var bot_left_text;
var bot_right_text;

var timer;
var score;

/* if the random label is the same as the previous person, recurse and try again
   this function is bad aqnd should be replaced  */
function randomPerson() {
    answer_index = Math.floor(Math.random()*image_labels.length);

    label = image_labels[answer_index];

    if (label === previous_person) {
        randomPerson(assets);
    }

    previous_person = label;

    return label;
}

function loadAnswers() {
    var pool = [];

    // fill with possible indexes, excluding answer
    for (var i=0; i<image_labels.length; i++) {
        if (i == answer_index) {
            continue;
        }
        else {
            pool.push(i);
        }
    }

    var wrongPerson = function () {
        if (pool.length == 0) {
             throw "No numbers left";
        }
        // get random index from pool
        var index = Math.floor(pool.length * Math.random());

        // remove index from pool
        var drawn = pool.splice(index, 1);

        return drawn[0];
    };

    /* Assign answer number */
    switch(Math.floor(Math.random() * 4) + 1) {
        case 1: // top-left
            answer = 1;
            top_left_text.setText(student_names[answer_index]);
            top_right_text.setText(student_names[wrongPerson()]);
            bot_left_text.setText(student_names[wrongPerson()]);
            bot_right_text.setText(student_names[wrongPerson()]);
            break;
        case 2: // top-right
            answer = 2;
            top_left_text.setText(student_names[wrongPerson()]);
            top_right_text.setText(student_names[answer_index]);
            bot_left_text.setText(student_names[wrongPerson()]);
            bot_right_text.setText(student_names[wrongPerson()]);
            break;
        case 3: // bot-left
            answer = 3;
            top_left_text.setText(student_names[wrongPerson()]);
            top_right_text.setText(student_names[wrongPerson()]);
            bot_left_text.setText(student_names[answer_index]);
            bot_right_text.setText(student_names[wrongPerson()]);
            break;
        case 4: // bot-right
            answer = 4;
            top_left_text.setText(student_names[wrongPerson()]);
            top_right_text.setText(student_names[wrongPerson()]);
            bot_left_text.setText(student_names[wrongPerson()]);
            bot_right_text.setText(student_names[answer_index]);
            break;
    }
}

/* abstract random person, load new texture */
function loadPerson() {
    person.loadTexture(randomPerson());
    loadAnswers();
}

/* Todo */
function verifyAnswer() {
    return 0;
}

/* handle drag and drop for person */
function checkAnswer() {
    /* check sprite rectangles for intersections */
    /* getBounds() is returned a matrix          */
    if (top_left.getBounds().intersects(person.getBounds())) {
        if (answer == 1) {
            score++;
            correct.play();
            loadPerson();
        }
        else {
            score--;
            incorrect.play();
        }
    }
    else if (top_right.getBounds().intersects(person.getBounds())) {
        if (answer == 2) {
            score++;
            correct.play();
            loadPerson();
        }
        else {
            score--;
            incorrect.play();
        }

    }
    else if (bot_left.getBounds().intersects(person.getBounds())) {
        if (answer == 3) {
            score++;
            correct.play();
            loadPerson();
        }
        else {
            score--;
            incorrect.play();
        }
    }
    else if (bot_right.getBounds().intersects(person.getBounds())) {
        if (answer == 4) {
            score++;
            correct.play();
            loadPerson();
        }
        else {
            score--;
            incorrect.play();
        }
    }

    /* reset to center, regardless of outcome */
    person.x = game.world.centerX;
    person.y = game.world.centerY;
}

function setTime() {
    --timer;
}

var playState = {
    create: function() {
        /* there is a lot of repeated code in this file and it should be organized into reusable functions */

        /* initalize variables */
        /* Switching states does not clear variables,
           therefore we must always clear them before rerunning this state. */

        previous_person = ""; // see above for why this needs to be reset
        timer = total_time;
        score = 0;

        /* set background color */
        game.stage.backgroundColor = '#2d2d2d';

        /* non-input assets */
        background = game.add.sprite(0, 0, 'background');

        /* button backdrops */
        top_left  = game.add.sprite(0, 0, 'square-1');
    	  top_right = game.add.sprite(736, 0, 'square-2');
    	  bot_left  = game.add.sprite(0, 536, 'square-3');
        bot_right = game.add.sprite(736, 536, 'square-4');

        /* load the possible answer's text to the four corners */
        top_left_text = game.add.text(0, 0, "", {
            font: "32px Arial",
            fill: "#ffffff",
            align: "center"});

        top_left_text.stroke = "#de77ae";
        top_left_text.strokeThickness = 8;
        top_left_text.setShadow(2, 2, "#333333", 2, true, false);

        top_right_text = game.add.text(536, 0, "", {
            font: "32px Arial",
            fill: "#ffffff",
            align: "center"});

        top_right_text.stroke = "#de77ae";
        top_right_text.strokeThickness = 8;
        top_right_text.setShadow(2, 2, "#333333", 2, true, false);

        bot_left_text = game.add.text(0, 536, "", {
            font: "32px Arial",
            fill: "#ffffff",
            align: "center"});

        bot_left_text.stroke = "#de77ae";
        bot_left_text.strokeThickness = 8;
        bot_left_text.setShadow(2, 2, "#333333", 2, true, false);

        bot_right_text = game.add.text(536, 536, "", {
            font: "32px Arial",
            fill: "#ffffff",
            align: "center"});

        bot_right_text.stroke = "#de77ae";
        bot_right_text.strokeThickness = 8;
        bot_right_text.setShadow(2, 2, "#333333", 2, true, false);
        /* end people's name text */

        /* load audio */
        correct = game.add.audio('correct');
        incorrect = game.add.audio('incorrect');

        /* input assets */
    	  /* setup boundaries for dragables */
        bounds = new Phaser.Rectangle(0, 0, width, height);

        /* Add person to game world */
        person = game.add.sprite(game.world.centerX, game.world.centerY, randomPerson(assets));
        person.anchor.setTo(0.5);

        /* Add input to person */
        person.inputEnabled = true;
    	  person.input.enableDrag(true);
        person.input.boundsRect = bounds;

        /* below is the most important line of code in the game */
        person.events.onDragStop.add(checkAnswer);

        /* display timer */
        time = game.add.text(game.world.centerX, 22, "0", {
	                         font: "32px Arial",
	                         fill: "#ffffff",
                             align: "center"});
        time.anchor.setTo(0.5, 0.5);
        time.stroke = "#de77ae";
        time.strokeThickness = 8;
        //  Apply the shadow to the Stroke only
        time.setShadow(2, 2, "#333333", 2, true, false);

        /* display score below timer */
        scoreboard = game.add.text(game.world.centerX, 62, "0", {
	                               font: "32px Arial",
	                               fill: "#ffffff",
                                   align: "center"});
        scoreboard.anchor.setTo(0.5, 0.5);
        scoreboard.anchor.setTo(0.5, 0.5);
        scoreboard.stroke = "#de77ae";
        scoreboard.strokeThickness = 8;
        //  Apply the shadow to the Stroke only
        scoreboard.setShadow(2, 2, "#333333", 2, true, false);

        loadPerson(); // this was added to meet deadlines, but a better way to load the entire game should be added
    },

    update: function() {
        /* when game is over, change states */
        if (timer <= 0) {
            game.state.start('score');
        }
        else {
            time.setText(timer, 32, 32);
        }

        /* update score, even if its the same */
        scoreboard.setText(score, 32, 32);
    }
}

/* start timer. vanilla js */
setInterval(setTime, 1000);
