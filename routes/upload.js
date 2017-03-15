var multer = require('multer');
var storage = multer.diskStorage({
    // destination: function (req, file, cb) {
    //     cb(null, 'database/')
    // },
    filename: function (req, file, cb) {
        cb(null, file.fieldname + '-' + Date.now() + '.' + file.mimetype.split("/")[1]);
    }
});
var upload = multer({ storage: storage });

module.exports = upload;