var emitter;

var menuState = {
    create: function() {
        /* Set background color */
        game.stage.backgroundColor = '#2d2d2d';

        /* Start pop sound */
        pop = game.add.audio('pop', 0.65);
        pop.play();

        /* loop cheesy music the entire time */
        menu_music = game.add.audio('menu_music', 0.65, true);
        menu_music.play();

        /* Load background */
        game.add.image(0, 0, 'background');

        /* Throw pictures of people around the menu screen */
        /* Phaser emitter */
        emitter = game.add.emitter(game.world.centerX, game.world.centerY, 250);

        emitter.makeParticles('group', [0,1,2,3,4,5], 10, true, true);
        emitter.minParticleSpeed.setTo(-200, -300);
        emitter.maxParticleSpeed.setTo(200, -400);
        emitter.gravity = 150;
        emitter.bounce.setTo(0.5, 0.5);
        emitter.angularDrag = 30;

        emitter.start(false, 16000, 400);
        /* End emitter */

        var title = game.add.text(game.world.centerX, -200, 'Matching Game', {
                                      font: '72px Arial',
                                      fill: '#ffffff'});
        title.anchor.setTo(0.5);
        title.stroke = "#de77ae";
        title.strokeThickness = 16;
        title.setShadow(2, 2, "#333333", 2, true, false);

        /* Make title bounce down*/
        game.add.tween(title).to( { y: 122 }, 4000, Phaser.Easing.Bounce.Out, true);

        /* Print description */
        var description = game.add.text(game.world.centerX, game.world.height-80,
                                      'Tap anywhere to play', {
                                      font: '25px Arial',
                                      fill: '#ffffff'});
        description.anchor.setTo(0.5);
        description.stroke = "#de77ae";
        description.strokeThickness = 8;
        description.setShadow(2, 2, "#333333", 2, true, false);
        description.alpha = 0;
        /* End description */

        /* The 'Tap anywhere to play' tween */
        //  Create our tween. This will fade the sprite to alpha 1 over the duration of 2 seconds
        var tween = game.add.tween(description).to( { alpha: 1 }, 500, "Linear", true, 5000, -1);

        //  And this tells it to yoyo, i.e. fade back to zero again before repeating.
        //  The 3000 tells it to wait for 3 seconds before starting the fade back.
        /* End tween */
        tween.yoyo(true, 1000);

        /* On click/touch call start below */
        game.input.onDown.addOnce(this.start, this);
    },

    update: function() {
        /* Give emitter physics */
        game.physics.arcade.collide(emitter);
    },

    start: function() {
        select = game.add.audio('select');
        select.play();

        game.state.start('play');
    }
};
