var MetaUtil = require('../');

var meta = MetaUtil({
    'delay': 1000,
    'start': '194', //file number
    'end': '194' //file number
}).pipe(process.stdout) //outputs to console