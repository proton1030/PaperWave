/**
 * Created by hanyu on 2/23/17.
 */

var sqlite3 = require('sqlite3').verbose();
var db = new sqlite3.Database('db/paperwave.db');
var check;
db.serialize(function() {

    db.run("CREATE TABLE if not exists users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT, salt TEXT)");


    // db.each("SELECT rowid AS id, info FROM user_info", function(err, row) {
    //     console.log(row.id + ": " + row.info);
    // });
});

db.close();
