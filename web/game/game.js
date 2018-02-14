var width = 800;
var height = 600;

var game = new Phaser.Game(width, height, Phaser.AUTO, 'game');

game.state.add('boot', bootState);
game.state.add('load', loadState);
game.state.add('menu', menuState);
game.state.add('play', playState);
game.state.add('score', scoreState);

game.state.start('boot');
