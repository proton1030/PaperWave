
var projLocation = '/Users/hanyu/WebstormProjects/myapp/';
var express = require('express');
var bodyParser = require('body-parser');
var session = require('express-session');
var upload = require('../routes/upload');
var pythonShell = require('python-shell');
var myPythonScriptPath = '/py/';
var dbctrl = require('../db/data.js');
var passport = require('passport');
var LocalStrategy = require('passport-local').Strategy;
var crypto = require('crypto');
var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('db/paperwave.db');
var check;



const user = {
    username: 'test',
    password: 'pass',
    id: 1
};




var app = module.exports = express();
app.use(express.static('public'));
app.set('index', __dirname + '/');


app.use(bodyParser.urlencoded({ extended: true }));
app.use(session({
    resave: false, // don't save session if unmodified
    saveUninitialized: false, // don't create session until something stored
    secret: 'shhhh, very secret'
}));

// Session-persisted message middleware

app.use(function(req, res, next){
    var err = req.session.error;
    var msg = req.session.success;
    delete req.session.error;
    delete req.session.success;
    res.locals.message = '';
    if (err) res.locals.message = '<p class="msg error">' + err + '</p>';
    if (msg) res.locals.message = '<p class="msg success">' + msg + '</p>';
    next();
});

// dummy database

var users = {
    tj: { name: 'tj' }
};


function hashPassword(password, salt) {
    var hash = crypto.createHash('sha256');
    hash.update(password);
    hash.update(salt);
    return hash.digest('hex');
}



db.serialize(function() {

    db.run("CREATE TABLE if not exists users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, salt TEXT)");


    // db.each("SELECT rowid AS id, info FROM user_info", function(err, row) {
    //     console.log(row.id + ": " + row.info);
    // });
});



passport.use(new LocalStrategy(function(username, password, done) {
    db.get('SELECT salt FROM users WHERE username = ?', username, function(err, row) {
        if (!row) return done(null, false);
        var hash = hashPassword(password, row.salt);
        db.get('SELECT username, id FROM users WHERE username = ? AND password = ?', username, hash, function(err, row) {
            if (!row) return done(null, false);
            return done(null, row);
        });
    });
}));

passport.serializeUser(function(user, done) {
    return done(null, user.id);
});

passport.deserializeUser(function(id, done) {
    db.get('SELECT id, username FROM users WHERE id = ?', id, function(err, row) {
        if (!row) return done(null, false);
        return done(null, row);
    });
});

// ...

app.post('/auth', passport.authenticate('local', { successRedirect: '/index',
    failureRedirect: '/' }));


// Authenticate using our plain-object database of doom!

// function authenticate(name, pass, fn) {
//     if (!module.parent) console.log('authenticating %s:%s', name, pass);
//     var user = users[name];
//     // query the db for the given username
//     if (!user) {
//         return fn(new Error('cannot find user'))
//     }
//     else {
//     // apply the same algorithm to the POSTed password, applying
//     // the hash against the pass / salt, if there is a match we
//     // found the user
//
//     }
// }

function restrict(req, res, next) {
    if(req.session.user) {
    next();
} else {
    req.session.error = 'Access denied!';
    res.redirect('/');
}
}


app.get('/restricted', restrict, function(req, res){
    res.send('Wahoo! restricted area, click to <a href="/logout">logout</a>');
});

app.get('/logout', function(req, res){
    // destroy the user's session to log them out
    // will be re-created next request
    req.session.destroy(function(){
        res.redirect('/');
    });
});


// app.post('/auth', function(req, res){
//     authenticate(req.body.username, req.body.password, function(err, user){
//         if (user) {
//             // Regenerate session when signing in
//             // to prevent fixation
//             req.session.regenerate(function(){
//                 // Store the user's primary key
//                 // in the session store to be retrieved,
//                 // or in this case the entire user object
//                 console.log('Success');
//                 req.session.user = user;
//                 req.session.success = 'Authenticated as ' + user.name
//                     + ' click to <a href="/logout">logout</a>. '
//                     + ' You may now access <a href="/restricted">/restricted</a>.';
//                 res.render('index');
//             });
//         } else {
//             console.log(err.message);
//             req.session.error = 'Authentication failed, please check your '
//                 + ' username and password.'
//                 + ' (use "tj" and "foobar")';
//             res.redirect('/');
//         }
//     });
// });

app.get('/', function(req, res){

    res.render('index');
});

app.get('/index', function(req, res){

    res.render('index');
});

app.get('/mobile.html', function(req, res){

    res.redirect('showingresult');
});


if (!module.parent) {
    app.listen(3000);
    console.log('Express started on port 3000');
}

app.post('/upload', upload.any(), function(req, res, next){
    // res.write(req.files);


    var ext = '.' + req.files[0].mimetype.split("/")[1];
    if (ext === '.jpeg' || ext === '.png') {
        identifier = req.files[0].filename.split("-")[1];
        identifier = identifier.split(".")[0];
        identifierPath = identifier + "/";
        identifierPathRel = "results/" + identifierPath;

        var options = {
            mode: 'text',
            args: [req.files[0].path, identifier]
        };
        pythonShell.run(myPythonScriptPath+'main.py', options, function(err, results) {
            if (err) {
                console.log(err);
                res.send(err);
            }
            else {
                console.log('Picture ' + identifier + ' transcript succeeded.');
                var optionsAudio = {
                    mode: 'text',
                    args: ['public/results/' + identifierPath + 'grid.csv','public/results/' + identifierPath + 'mix.wav','public/results/' + identifierPath + 'mix.mp3']
                };
                pythonShell.run(myPythonScriptPath+'soundgen.py', optionsAudio, function(err, results){
                    if (err) console.log(err);
                    else {
                        var jsondata = {
                            mp3path: identifierPathRel + "mix.mp3",
                            identifierID: identifier
                        };
                        res.send(jsondata);
                    }
                });
            }
        });



        // res.send(req.files);
    }

});
