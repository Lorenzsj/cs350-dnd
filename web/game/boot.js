var server_data;
var image_paths = [];
var image_labels = [];
var student_names = [];

var bootState = {
    preload: function() {
        /* Replace local JSON with server requested JSON when possible */
        game.load.json('server_data', 'debug.json');
    },

    create: function() {
        /* Load JSON into server_data */
        server_data = game.cache.getJSON('server_data');

        /* Set variables for path and image extension */
        var path = '../images/';
        var ext = '.jpg';

        /* Load JSON data into the following arrays */
        server_data.students.forEach(function(item) {
            image_labels.push(item.user);
            image_paths.push(path+item.user+ext);
            student_names.push(item.name);
        });

        // Move onto loading game files - see load.js
        game.state.start('load');
    }
};
