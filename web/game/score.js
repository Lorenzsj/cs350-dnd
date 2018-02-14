var scoreState = {
    create: function() {
        /* set background color */
        game.stage.backgroundColor = '#2d2d2d';
        background = game.add.sprite(0, 0, 'background');

        /* draw title */
        var title = game.add.text(80, 72, 'Matching Game', {
                                      font: '72px Arial',
                                      fill: '#ffffff'});
        title.stroke = "#de77ae";
        title.strokeThickness = 16;
        title.setShadow(2, 2, "#333333", 2, true, false);

        /* draw score title */
        var score_title = game.add.text(80, 198,
                                      'Your Score was: ' + score, {
                                      font: '32px Arial',
                                      fill: '#ffffff'});
        score_title.stroke = "#de77ae";
        score_title.strokeThickness = 8;
        score_title.setShadow(2, 2, "#333333", 2, true, false);

        /* draw 'tap anywhere to play again' */
        var description = game.add.text(80, game.world.height-80,
                                      'Tap anywhere to play again', {
                                      font: '25px Arial',
                                      fill: '#ffffff'});
        description.stroke = "#de77ae";
        description.strokeThickness = 8;
        description.setShadow(2, 2, "#333333", 2, true, false);
        description.alpha = .15;

        /* setup tween to make the description fade in and out */
        var tween = game.add.tween(description).to( { alpha: 1 }, 500, "Linear", true, 0, -1);
        tween.yoyo(true, 1000);

        /* play victory sound */
        select = game.add.audio('victory');
        select.play();

        /* on input loop back into play state from start */
        game.input.onDown.addOnce(this.start, this);
    },

    start: function() {
        select = game.add.audio('select');
        select.play();

        game.state.start('play');
    }
};
