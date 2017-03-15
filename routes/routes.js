/**
 * Created by hanyu on 3/2/17.
 */
var express = require('express');
var app = module.exports = express();

app.get('/', function(req, res){
    res.render('index');
});