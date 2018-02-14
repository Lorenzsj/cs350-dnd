var assets;

var loadState = {
    preload: function() {
        /* Display 'Loading...' on screen */
        var loadingLabel = game.add.text(0, 0, 'Loading...', {
                                         font: '30px Courier',
                                         fill: '#ffffff'});

        loadingLabel.anchor.setTo(0.5, 0.5);
        loadingLabel.x = game.world.centerX;
        loadingLabel.y = game.world.centerY;

        /* Load Assets */
        /* Load background */
        game.load.image('background', 'assets/images/background.png');

        /* This is for the emitter in the next state */
        game.load.spritesheet('group', 'assets/images/group.png', 64, 64);

        /* Load button backdrops */
        game.load.image('square-1', 'assets/images/square-1.png');
    	  game.load.image('square-2', 'assets/images/square-2.png');
    	  game.load.image('square-3', 'assets/images/square-3.png');
    	  game.load.image('square-4', 'assets/images/square-4.png');

        /* Dynamically load people's pictures */
        for (let i=0; i<image_labels.length; i++) {
            game.load.image(image_labels[i], image_paths[i]);
        }

        /* Load audio */
        game.load.audio('pop', 'assets/audio/fx/pop.ogg');
        game.load.audio('victory', 'assets/audio/fx/victory.wav');
        game.load.audio('menu_music', 'assets/audio/music/Tbone_and_friends-Pascal_Tatipata.wav');
        game.load.audio('select', 'assets/audio/fx/select.ogg');
        game.load.audio('correct', 'assets/audio/fx/correct.wav');
        game.load.audio('incorrect', 'assets/audio/fx/incorrect.wav');
    },

    create: function() {
        game.state.start('menu');
    }
};
